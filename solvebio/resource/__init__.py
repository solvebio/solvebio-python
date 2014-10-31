"""Glues together all SolveObjects"""
# __package__ = 'solvebio.resource'

from .depository import Depository
from .depositoryversion import DepositoryVersion
from .apiresource import ListObject
from .annotation import Annotation
from .sample import Sample
from .user import User
from .dataset import Dataset
from .datasetfield import DatasetField


types = {
    'Annotation': Annotation,
    'Dataset': Dataset,
    'DatasetField': DatasetField,
    'Depository': Depository,
    'DepositoryVersion': DepositoryVersion,
    'Sample': Sample,
    'User': User,
    'list': ListObject
}
