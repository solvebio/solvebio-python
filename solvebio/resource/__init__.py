from __future__ import absolute_import

from .depository import Depository
from .depositoryversion import DepositoryVersion
from .apiresource import ListObject
from .user import User
from .dataset import Dataset
from .datasetfield import DatasetField
from .datasetimport import DatasetImport
from .datasetcommit import DatasetCommit
from .datasettemplate import DatasetTemplate
from .upload import Upload


types = {
    'Dataset': Dataset,
    'DatasetImport': DatasetImport,
    'DatasetCommit': DatasetCommit,
    'DatasetTemplate': DatasetTemplate,
    'DatasetField': DatasetField,
    'Depository': Depository,
    'DepositoryVersion': DepositoryVersion,
    'Upload': Upload,
    'User': User,
    'list': ListObject
}
