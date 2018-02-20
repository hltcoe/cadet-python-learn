CADET Active Learning Library
===============================
This library makes it easy to build an active learning server.
Developers implement a single interface and the library handles all the communications.

This is a python3 only library.

Installation
---------------
The library will eventually be available on PyPI.
Until then install with pip locally:
```
pip3 install .
```

Development Guide
-----------------
The Learner is initialized with a list of annotation units.
An annotation unit is a sentence in a communication or the entire communication.
The Learner sorts the list to maximize the value of user annotations.
The updated list is sent to CADET and controls the order the user sees the items to annotate.
The new annotations are sent to the Learner when available.
The Learner then update its internal model and updates the sort of the list.
The number of annotations between training cycles is controlled by the retrain interval parameter.

An example implementation might look like this:
```python
import cadet_python_learn as cpl

class ExampleLearner(cpl.Learner):
    def __init__(self, session_id, annotation_units, language, fetch_client):
        # you can add additional arguments needed for your model
        super(ExampleLearner, self).__init__(session_id, annotation_units, language, fetch_client)
        # you can load model information or other initialization here
        self.annotations = []
        self.units = annotation_units
        self.communications = self.load_comms()

    def add_annotations(self, annotations):
        # you probably just want to keep a list of all annotations
        self.annotations.extend(annotations)

    def train(self):
        # this is called once the number of new annotations has reached the retrain interval
        self.model.train(self.annotations)

    def rank(self):
        # use your model to sort the annotation units and return
        return sorted_units
```

Demo
-----------------
There is a demo server in the `demo` directory.
It implements the interface with random shuffles.

To run it, take a look at its arguments
```
python3 run.py --help
```

Example command line:
```
python3 demo/run.py -p 9999 --fetch-port 9090
```
This launches the server on port 9999.
It gets communications from a fetch server running on localhost at port 9090.
It sorts the annotation units after every 10 annotations.