from __future__ import absolute_import

from .depository import Depository
from .depositoryversion import DepositoryVersion
from .apiresource import ListObject
from .user import User
from .dataset import Dataset
from .datasetfield import DatasetField


types = {
    'Dataset': Dataset,
    'DatasetField': DatasetField,
    'Depository': Depository,
    'DepositoryVersion': DepositoryVersion,
    'User': User,
    'list': ListObject
}
