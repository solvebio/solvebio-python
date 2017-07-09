from __future__ import absolute_import

from .apiresource import ListObject
from .user import User
from .dataset import Dataset
from .datasetfield import DatasetField
from .datasetimport import DatasetImport
from .datasetexport import DatasetExport
from .datasetcommit import DatasetCommit
from .datasetmigration import DatasetMigration
from .datasettemplate import DatasetTemplate
from .manifest import Manifest
from .object import Object
from .upload import Upload
from .vault import Vault


types = {
    'Dataset': Dataset,
    'DatasetImport': DatasetImport,
    'DatasetExport': DatasetExport,
    'DatasetCommit': DatasetCommit,
    'DatasetMigration': DatasetMigration,
    'DatasetTemplate': DatasetTemplate,
    'DatasetField': DatasetField,
    'Manifest': Manifest,
    'Object': Object,
    'Upload': Upload,
    'User': User,
    'Vault': Vault,
    'list': ListObject
}
