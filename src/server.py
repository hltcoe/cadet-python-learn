import logging
import threading
import time
from concrete.access import FetchCommunicationService
from concrete.access.ttypes import FetchRequest
from concrete.learn import ActiveLearnerServerService
from concrete.util.learn_wrapper import ActiveLearnerClientClientWrapper
from concrete.util.thrift_factory import factory as thrift_factory


class BrokerClient:
    def __init__(self, session_id, contact):
        """
        Args:
        - `session_id`: concrete.uuid.UUID object
        - `contact`: concrete.services.AsyncContactInfo object
        """
        self.session_id = session_id
        self.host = contact.host
        self.port = contact.port

    def send(self, annotation_units):
        """
        Send the ranked list to the broker
        Args:
        - `annotation_units`: List of concrete.learn.AnnotationUnitIdentifier objects
        """
        with ActiveLearnerClientClientWrapper(self.host, self.port) as client:
            client.submitSort(self.session_id, annotation_units)


class FetchClient:
    def __init__(self, host, port):
        """
        Args:
        - `host`: String specifying FetchCommunicationService hostname
        - `port`: Integer specifying FetchCommunicationService port number
        """
        self.host = host
        self.port = port

    def get(self, communication_ids):
        """
        Args:
        - `communication_ids`: List of CommunicationID strings

        Returns:
        - List of Communications
        """
        socket = thrift_factory.createSocket(self.host, int(self.port))
        transport = thrift_factory.createTransport(socket)
        protocol = thrift_factory.createProtocol(transport)
        client = FetchCommunicationService.Client(protocol)
        transport.open()

        fetch_request = FetchRequest()
        fetch_request.communicationIds = communication_ids
        fetch_result = client.fetch(fetch_request)
        return fetch_result.communications


class Handler(ActiveLearnerServerService.Iface):
    def __init__(self, fetch_host, fetch_port, retrain_interval, learner_factory):
        """
        - `fetch_host`: String specifying FetchCommunicationService hostname
        - `fetch_port`: Integer specifying FetchCommunicationService port number
        - `retrain_interval`: Integer for how many annotations to wait for before retraining
        - `learner_factory`: Factory that produces Learner instances
        """
        self.session_to_learner_task = {}
        self.fetch_client = FetchClient(fetch_host, fetch_port)
        self.retrain_interval = retrain_interval
        self.learner_factory = learner_factory

    def addAnnotations(self, session_id, annotations):
        """Implementation of ActiveLeanerServerService.addAnnotations()

        Args:
        - `session_id`: concrete.uuid.UUID object
        - `annotations`: List of concrete.learn.Annotation objects

        Returns:
        - Boolean
        """
        logging.info('ActiveLearnerServerService.addAnnotations() called with %d annotations' %
                     len(annotations))

        if session_id.uuidString not in self.session_to_learner_task:
            logging.warning("Unable to find Session with ID '%s'" % session_id.uuidString)
            return False

        return self.session_to_learner_task[session_id.uuidString].addAnnotations(annotations)

    def start(self, session_id, task, contact):
        """Implementation of ActiveLeanerServerService.start()

        Args:
        - `sessionId`: concrete.uuid.UUID object
        - `task`: concrete.learn.AnnotationTask object
        - `contact`: concrete.services.AsyncContactInfo object

        Returns:
        - Boolean
        """
        # The start() function is passed a list of Communication *IDs* (in the
        # task.units data structure), while the addAnnotations() function is
        # passed a list of *Communications*.
        logging.info("ActiveLearnerServerService.start()")
        logging.info("ActiveLearnerClientService - host='%s', port=%d" % (contact.host, contact.port))

        broker_client = BrokerClient(contact.host, contact.port)
        learner = self.learner_factory(session_id, task.units, task.language, self.fetch_client, broker_client)
        self.session_to_learner_task[session_id.uuidString] = learner

        #learner.

        return True

    def stop(self, sessionId):
        logging.info("ActiveLearnerServerService.stop(sessionId='%s')" % sessionId.uuidString)

        if sessionId.uuidString not in self.session_to_learner_task:
            logging.warning("ActiveLearnerServerService.stop unable to find Session with ID '%s'" %
                            sessionId.uuidString)
            return
        else:
            # Stop LearnerTask thread for this sessionId
            self.session_to_learner_task[sessionId.uuidString].stop()
            self.session_to_learner_task[sessionId.uuidString].join()

            # Remove sessionId
            del self.session_to_learner_task[sessionId.uuidString]


class LearnerTask(threading.Thread):
    def __init__(self, session_id, task, contact, fetch_client, retrain_interval, learner_class):
        """
        Args:
        - `sessionId`: concrete.uuid.UUID object
        - `task`: concrete.learn.AnnotationTask object
        - `contact`: concrete.services.AsyncContactInfo object
        - `fetch_client`: FetchClient object
        - `retrain_interval`: Integer for how many annotations to wait for before retraining
        - `learner_class`: Instance of a class that implements the Learner interface
        """
        self.session_id = session_id
        self.task = task
        self.contact = contact
        self.fetch_client = fetch_client
        self.retrain_interval = retrain_interval
        self.learner_class = learner_class

        self.annotations = []
        self.broker_client = BrokerClient(session_id, contact)
        self.commIds = self._getCommIds(task)
        self.learner = None

        threading.Thread.__init__(self)
        self.running = False

    def _getCommIds(self, task):
        """
        Args:
        - `task`: concrete.learn.AnnotationTask object

        Returns:
        - List of CommunicationID strings
        """
        return [unit.communicationId for unit in task.units]

    def _getCommunications(self, commIds):
        """
        Args:
        - `commIds`: List of CommunicationID strings

        Returns:
        - List of Communications
        """
        return self.fetch_client.get(commIds)

    def addAnnotations(self, annotations):
        """
        Args:
        - `annotations`: List of concrete.learn.Annotation objects

        Returns:
        - Boolean
        """
        for annotation in annotations:
            # TODO: something with each Communication
            logging.info("  Communication ID: '%s'" % annotation.communication.id)

        # TODO: Use Python's queue data structure?
        self.annotations.extend(annotations)
        return True

    def run(self):
        self.running = True
        self.learner = self.learner_class(
            self._getCommunications(self.commIds),
            self.task.language,
            self.session_id.uuidString)
        unit_list = self.learner.rank()
        if self.running:
            self.broker_client.send(unit_list)
        while self.running:
            if len(self.annotations) >= self.retrain_interval:
                self.learner.loadAnnotations(self.annotations)
                self.annotations = []
                self.learner.train()
                unit_list = self.learner.rank()
                if not self.running:
                    continue
                self.broker_client.send(unit_list)
            time.sleep(0.1)
        logging.info("Session '%s' stopped, exiting LearnerTask.run()" % self.session_id.uuidString)

    def start(self):
        logging.info("LearnerTask.start() called for session '%s'" % self.session_id.uuidString)
        super(LearnerTask, self).start()

    def stop(self):
        logging.info("LearnerTask.stop() called for session '%s'" % self.session_id.uuidString)
        self.running = False
