import abc


class Learner(object):
    """
    Interface for the CADET Active Learner

    The Learner sorts annotation units. An annotation unit could be a full communication
    or a single sentence. It receives annotations as they are available from the user.
    Asynchronously, it builds a model and sorts the annotation units according to that
    model.

    Currently, CADET requires that all annotation units are returned by rank().
    This requirement will be relaxed in the next version.

    In order to rank the annotation units, the Learner must request the underlying
    communications from the fetch server.

    rank() is called once on start up of a session in case the Learner begins with
    a default model. Return None if you don't want to change the initial sort order.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, session_id, annotation_units, language, fetch_client):
        """Initialize a Learner

        Args:
        - `session_id`: Unique identifier for this learning session
        - `annotation_units`: List of concrete.services.AnnotationUnitIdentifier objects
        - `language`: String specifying language
        - `fetch_client`: Client for the fetch service
        """
        self.session_id = session_id
        self.annotation_units = annotation_units
        self.language = language
        self.fetch_client = fetch_client

    @classmethod
    def factory(cls, session_id, annotation_units, language, fetch_client):
        return cls(session_id, annotation_units, language, fetch_client)

    @abc.abstractmethod
    def add_annotations(self, annotations):
        """Add a set of annotations (provided by the user)

        Args:
        - `annotations`: List of concrete.learn.Annotation instances
        """
        raise NotImplementedError

    @abc.abstractmethod
    def train(self):
        """(Re)train model based on annotations passed to add_annotations()
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rank(self):
        """Return an ordered list of annotation units

        Returns:
        - List of concrete.services.AnnotationUnitIdentifier objects
        """
        raise NotImplementedError
