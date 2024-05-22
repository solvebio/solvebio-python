from __future__ import absolute_import

import uuid

from .helper import SolveBioTestCase


class APIResourceTests(SolveBioTestCase):

    def test_apiresource_iteration(self):
        public_vault = self.client.Vault.get_by_full_path('quartzbio:public')
        n_folders = len(list(public_vault.folders(depth=0)))

        folder_iter = public_vault.folders(depth=0)
        for i, j in enumerate(folder_iter):
            pass
        self.assertTrue(i == n_folders - 1)

        # Iterating again should be the same
        for i, j in enumerate(folder_iter):
            pass
        self.assertTrue(i == n_folders - 1)

    def test_apiresource_serialize_metadata(self):
        folder_no_metadata = self.client.Object.\
            get_or_create_by_full_path('~/{}'.format(uuid.uuid4()), object_type='folder')

        metadata = folder_no_metadata.metadata
        foo_tuple = ('foo', 'bar')

        # foo key-value pair is not in 'metadata' object
        self.assertFalse(foo_tuple in metadata.items())

        metadata['foo'] = 'bar'
        params = folder_no_metadata.serialize(folder_no_metadata)

        # Test that foo key-value pair is set as value to 'metadata'
        # key in 'params' dict that will be serialized
        self.assertTrue(foo_tuple in params['metadata'].items())

        folder_with_metadata = self.client.Object.\
            get_or_create_by_full_path('~/{}'.format(uuid.uuid4()),
                                       object_type='folder',
                                       metadata=dict([foo_tuple]))

        metadata = folder_with_metadata.metadata
        foo_1_tuple = ('foo1', 'bar1')

        # foo_1 key-value pair is not in 'metadata' object
        self.assertFalse(foo_1_tuple in metadata.items())

        metadata['foo1'] = 'bar1'

        params = folder_with_metadata.serialize(folder_with_metadata)
        params_items = params['metadata'].items()

        # Test that both foo and foo_1 key-value pairs are set as value to 'metadata'
        # key in 'params' dict that will be serialized
        self.assertTrue(foo_tuple in params_items)
        self.assertTrue(foo_1_tuple in params_items)
