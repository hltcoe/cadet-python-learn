import argparse
import cadet_python_learn as cpl
from concrete.util.learn_wrapper import ActiveLearnerServerServiceWrapper
import logging
import random


class RandomLearner(cpl.Learner):
    """
    Perform a random shuffle on the annotation units
    """
    def __init__(self, session_id, annotation_units, language, fetch_client):
        super(RandomLearner, self).__init__(session_id, annotation_units, language, fetch_client)

    def add_annotations(self, annotations):
        logging.info("RandomLearner.add_annotation() has been called")

    def train(self):
        logging.info("RandomLearner.train() has been called")

    def rank(self):
        logging.info("RandomLearner.rank() has been called")
        random.shuffle(self.annotation_units)
        return self.annotation_units


def main():
    logging.basicConfig(
        format='%(asctime)-15s %(levelname)s: %(message)s',
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(description='CADET ActiveLearner service demo')
    parser.add_argument('-p', '--port', type=int, required=True,
                        help='Port on the server listens on')
    parser.add_argument('--fetch-host', type=str, default='localhost',
                        help='Hostname of the fetch server')
    parser.add_argument('--fetch-port', type=int, required=True,
                        help='Port of the fetch server')
    parser.add_argument('--retrain-interval', type=int, default=10,
                        help='Number of Annotations that trigger model retraining')
    args = parser.parse_args()

    logging.info('Serving on %d...' % args.port)

    handler = cpl.LearnerHandler(args.fetch_host, args.fetch_port, args.retrain_interval, RandomLearner.factory)
    server = ActiveLearnerServerServiceWrapper(handler)
    server.serve(None, args.port)


if __name__ == '__main__':
    main()
