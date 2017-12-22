from __future__ import absolute_import
# from solvebio.resource import Vault

from .helper import SolveBioTestCase


class ObjectTests(SolveBioTestCase):

    def test_object_paths(self):
        vaults = self.client.Vault.all()
        for vault in vaults:
            for file_ in list(vault.ls().solve_objects())[:5]:
                o_path, _ = self.client.Object.validate_path(file_.full_path)
                self.assertEqual(o_path, file_.full_path)

    def test_object_path_cases(self):

        user = self.client.User.retrieve()
        domain = user.account.domain
        user_vault = '{0}:user-{1}'.format(domain, user.id)
        test_cases = [
            ['{0}:myVault'.format(domain), '{0}:myVault:/'.format(domain)],
            ['acme:myVault', 'acme:myVault:/'],
            ['myVault', '{0}:/myVault'.format(user_vault)],
            ['acme:myVault:/uploads_folder', 'acme:myVault:/uploads_folder'],
            ['acme:myVault:/uploads_folder', 'acme:myVault:/uploads_folder'],
            ['acme:myVault/uploads_folder', 'acme:myVault:/uploads_folder'],
            ['myVault:/uploads_folder', '{0}:myVault:/uploads_folder'.format(domain)],  # noqa
            ['/uploads_folder', '{0}:/uploads_folder'.format(user_vault)],
            [':/uploads_folder', '{0}:/uploads_folder'.format(user_vault)],
            ['myVault/uploads_folder', '{0}:/myVault/uploads_folder'.format(user_vault)],  # noqa
        ]
        for case, expected in test_cases:
            print case
            p, _ = self.client.Object.validate_path(case)
            self.assertEqual(p, expected)

        error_test_cases = [
            '',
            'myDomain:myVault:/the/heack',
            'oops:myDomain:myVault',
        ]
        for case in error_test_cases:
            with self.assertRaises(Exception):
                v, v_paths = self.client.Vault.validate_path(case)
