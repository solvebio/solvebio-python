"""Glues together all SolveObjects"""
# For the future...
# from Dataset import Dataset
# from DatasetField import DatasetField
from depository import Depository
from depositoryversion import DepositoryVersion
from resource import Dataset, User, \
    ListObject, DatasetField
from .annotation import Annotation
from .sample     import Sample


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
