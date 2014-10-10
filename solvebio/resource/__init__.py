"""Glues together all SolveObjects"""
# For the future...
# from Depository import Depository
# from DepositoryVersion import DepositoryVersion
# from Dataset import Dataset
# from DatasetField import DatasetField
from .resource import Depository, DepositoryVersion, Dataset, User, \
    ListObject, DatasetField
from .annotation import Annotation
from .sample     import Sample


types = {
    'Annotation': Annotation,
    'Dataset': Dataset,
    'DatasetField': DatasetField,
    'Depository': Depository,
    'DepositoryVersion': DepositoryVersion,
    'Sample': DepositoryVersion,
    'User': User,
    'list': ListObject
}
