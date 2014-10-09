"""Glues together all SolveObjects"""
# For the future...
# from Depository import Depository
# from DepositoryVersion import DepositoryVersion
# from Dataset import Dataset
# from DatasetField import DatasetField
from resource import Depository, DepositoryVersion, Dataset, User, ListObject, DatasetField
from solveobject import types

types = {
    'Depository': Depository,
    'DepositoryVersion': DepositoryVersion,
    'Dataset': Dataset,
    'DatasetField': DatasetField,
    'User': User,
    'list': ListObject
}
