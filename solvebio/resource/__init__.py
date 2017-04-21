from __future__ import absolute_import

from .depository import Depository
from .depositoryversion import DepositoryVersion
from .apiresource import ListObject
from .user import User
from .dataset import Dataset
from .datasetfield import DatasetField
from .datasetimport import DatasetImport
from .datasetexport import DatasetExport
from .datasetcommit import DatasetCommit
from .datasetmigration import DatasetMigration
from .datasettemplate import DatasetTemplate
from .upload import Upload
from .manifest import Manifest


types = {
    'Dataset': Dataset,
    'DatasetImport': DatasetImport,
    'DatasetExport': DatasetExport,
    'DatasetCommit': DatasetCommit,
    'DatasetMigration': DatasetMigration,
    'DatasetTemplate': DatasetTemplate,
    'DatasetField': DatasetField,
    'Depository': Depository,
    'DepositoryVersion': DepositoryVersion,
    'Upload': Upload,
    'Manifest': Manifest,
    'User': User,
    'list': ListObject
}
