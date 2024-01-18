"""This module offers the DeepDiff, DeepSearch, grep, Delta and DeepHash classes."""
# flake8: noqa
__version__ = '6.7.1'
import logging

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)8s %(message)s')


from .diff import DeepDiff
from .search import DeepSearch, grep
from .deephash import DeepHash
from .delta import Delta
from .path import extract, parse_path
