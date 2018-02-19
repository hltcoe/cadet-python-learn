#!/usr/bin/env python3

from setuptools import setup
import sys

MIN_PYTHON = (3, 0)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python {}.{} or later is required.\n".format(*MIN_PYTHON))

__author__ = 'Cash Costello'
__version__ = '0.1'

setup(
    name='cadet python learn',
    version=__version__,
    description='Library for building a CADET active learning server.',
    long_description=open('README.md').read(),
    author=__author__,
    author_email='cash.costello@jhuapl.edu',
    license='BSD',
    packages=['cadet_python_learn'],
    package_dir={'cadet_python_learn': 'src'},
    include_package_data=True,
    classifiers=[
    ],
    install_requires=[
        'concrete'
    ]
)