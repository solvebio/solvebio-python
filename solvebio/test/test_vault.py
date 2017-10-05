from __future__ import absolute_import
# from solvebio.resource import Vault

from .helper import SolveBioTestCase


class VaultTests(SolveBioTestCase):

    def test_vaults(self):
        vaults = self.client.Vault.all()
        vault = vaults.data[0]
        self.assertTrue('id' in vault,
                        'Should be able to get id in vault')

        vault2 = self.client.Vault.retrieve(vault.id)
        self.assertEqual(vault, vault2,
                         "Retrieving vault id {0} found by all()"
                         .format(vault.id))

        check_fields = [
            'account_id', 'created_at', 'description', 'has_children',
            'has_folder_children', 'id', 'is_deleted', 'is_public',
            'last_synced', 'name', 'permissions', 'provider',
            'require_unique_paths', 'updated_at', 'url', 'user_id',
            'vault_properties', 'vault_type'
        ]

        for f in check_fields:
            self.assertTrue(f in vault, '{0} field is present'.format(f))
