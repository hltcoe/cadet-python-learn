import argparse
import logging
import cadet_python_learn as cpl


class RandomLearner(cpl.Learner):
    def __init__(self, session_id, annotation_units, language, fetch_client):
        super(RandomLearner, self).__init__(session_id, annotation_units, language, fetch_client)

    def add_annotations(self, annotations):
        pass

    def train(self):
        pass

    def rank(self):
        print(self.session_id)


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

    learner = RandomLearner.factory("xyz", [], "en", None)
    learner.rank()


if __name__ == '__main__':
    main()
