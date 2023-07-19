from __future__ import absolute_import

import unittest

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

    def test_vault_paths(self):
        user = self.client.User.retrieve()
        domain = user.account.domain
        user_vault = 'user-{0}'.format(user.id)

        vaults = self.client.Vault.all()
        for vault in vaults:
            v, v_paths = self.client.Vault.validate_full_path(vault.full_path)
            self.assertEqual(v, vault.full_path)

        test_cases = [
            ['myVault/', '{0}:myVault'.format(domain)],
            ['myVault', '{0}:myVault'.format(domain)],
            ['{0}:myVault'.format(domain), '{0}:myVault'.format(domain)],
            ['acme:myVault', 'acme:myVault'],
            ['myVault/folder1/folder2: xyz', '{0}:myVault'.format(domain)],
            ['acme:myVault/folder1/folder2: xyz', 'acme:myVault'],
            ['acme:myVault:/folder1/folder2: xyz', 'acme:myVault'],
            # The following are the "new" vault/path formats:
            ['~/', '{0}:{1}'.format(domain, user_vault)],
            ['acme:myVault/uploads_folder', 'acme:myVault'],
            ['myVault/uploads_folder', '{0}:myVault'.format(domain)],
        ]
        for case, expected in test_cases:
            v, v_paths = self.client.Vault.validate_full_path(case)
            self.assertEqual(v, expected)

        error_test_cases = [
            '',
            '/',
            ':',
            ':/',
            '::/',
            'x:',
            # Underscore in domain
            'my_Domain:myVault:/the/heack',
            # Space in domain
            'my Domain:my:Vault:/the/heack',
            # Too many colons
            'myDomain:my:Vault:/the/heack',
            'oops:myDomain:myVault',
        ]
        for case in error_test_cases:
            with self.assertRaises(Exception):
                v, v_paths = self.client.Vault.validate_full_path(case)

    @unittest.skip("Skip because API Host on GH pipelines doesn't support versioning.")
    def test_vault_versioning(self):
        vault = self.client.Vault.get_personal_vault()
        initial_versioning_status = vault["versioning"]
        assert initial_versioning_status in ["enabled", "disabled", "suspended"]

        self.addCleanup(VaultTests.clean_up_after_vault_versioning, vault, initial_versioning_status)

        vault.enable_versioning()
        assert "enabled" == vault["versioning"]
        vault.disable_versioning()
        assert "disabled" == vault["versioning"]
        vault.suspend_versioning()
        assert "suspended" == vault["versioning"]

    @staticmethod
    def clean_up_after_vault_versioning(vault, versioning_status):
        if versioning_status == "enabled":
            vault.enable_versioning()
        elif versioning_status == "disabled":
            vault.disable_versioning()
        elif versioning_status == "suspended":
            vault.suspend_versioning()
        assert versioning_status == vault["versioning"]
