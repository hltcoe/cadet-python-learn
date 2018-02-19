import abc


class Learner(object):
    """
    Interface for the CADET Active Learner
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
