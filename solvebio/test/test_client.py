# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .helper import SolveBioTestCase


class TestClient(SolveBioTestCase):

    def test_client_resources(self):
        resources = [
            'Annotator',
            'BatchQuery',
            'Beacon',
            'BeaconSet',
            'Dataset',
            'DatasetCommit',
            'DatasetExport',
            'DatasetField',
            'DatasetImport',
            'DatasetMigration',
            'DatasetTemplate',
            'Expression',
            'Filter',
            'GenomicFilter',
            'Manifest',
            'Object',
            'ObjectCopyTask',
            'Query',
            'Task',
            'User',
            'Vault',
            'VaultSyncTask',
        ]
        for r in resources:
            cls = getattr(self.client, r, None)
            self.assertTrue(cls)
            self.assertEqual(self.client, cls._client)
