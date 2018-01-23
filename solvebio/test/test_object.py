from __future__ import absolute_import
# from solvebio.resource import Vault

from .helper import SolveBioTestCase


class ObjectTests(SolveBioTestCase):

    def test_object_paths(self):
        vaults = self.client.Vault.all()
        for vault in vaults:
            for file_ in list(vault.ls().solve_objects())[:5]:
                o_path, _ = self.client.Object.validate_full_path(
                    file_.full_path)
                self.assertEqual(o_path, file_.full_path)

                # assert path is gettable
                self.client.Object.get_by_full_path(o_path)

        with self.assertRaises(Exception):
            self.client.Object.get_by_full_path('what/is/this')

    def test_object_path_cases(self):

        user = self.client.User.retrieve()
        domain = user.account.domain
        user_vault = '{0}:user-{1}'.format(domain, user.id)
        test_cases = [
            ['acme:myVault:/uploads_folder', 'acme:myVault:/uploads_folder'],
            ['acme:myVault/folder1/project: ABCD',
             'acme:myVault:/folder1/project: ABCD'],
            ['myVault/folder1/project: ABCD',
             '{0}:myVault:/folder1/project: ABCD'.format(domain)],
            ['myVault:/uploads_folder', '{0}:myVault:/uploads_folder'.format(domain)],  # noqa
            # New full path formats
            ['~/uploads_folder', '{0}:/uploads_folder'.format(user_vault)],
            ['~/', '{0}:/'.format(user_vault)],
            ['myVault/uploads_folder', '{0}:myVault:/uploads_folder'.format(domain)],  # noqa
            ['acme:myVault/uploads_folder', 'acme:myVault:/uploads_folder'],
        ]
        for case, expected in test_cases:
            p, _ = self.client.Object.validate_full_path(case)
            self.assertEqual(p, expected)

        error_test_cases = [
            '',
            '/hello',
            'myVault',
            'oops:myDomain:myVault',
            '{0}:myVault'.format(domain),
            'acme:myVault'
        ]
        for case in error_test_cases:
            with self.assertRaises(Exception):
                v, v_paths = self.client.Object.validate_full_path(case)

    def test_object_path_cases_with_overrides(self):
        user = self.client.User.retrieve()
        domain = user.account.domain
        user_vault = '{0}:user-{1}'.format(domain, user.id)

        test_cases = [
            'acme:myVault:/folder',
            'myVault:/folder',
            'myVault/folder',
            '/folder',
        ]

        for case in test_cases:
            p, _ = self.client.Object.validate_full_path(case, vault='foobar')
            expected = '{0}:foobar:/folder'.format(domain)
            self.assertEqual(p, expected)

            p, _ = self.client.Object.validate_full_path(case, vault='foo:bar')
            expected = 'foo:bar:/folder'
            self.assertEqual(p, expected)

            p, _ = self.client.Object.validate_full_path(
                case, vault='foo:bar', path='/baz')
            expected = 'foo:bar:/baz'
            self.assertEqual(p, expected)

            p, _ = self.client.Object.validate_full_path(
                case, vault='foo:bar', path='/baz/bon')
            expected = 'foo:bar:/baz/bon'
            self.assertEqual(p, expected)

        # Test cases where just the path changes
        case = 'acme:myVault:/folder'
        p, _ = self.client.Object.validate_full_path(case, path='foo/bar/baz')
        expected = 'acme:myVault:/foo/bar/baz'
        self.assertEqual(p, expected)

        case = '~/folder'
        p, _ = self.client.Object.validate_full_path(case, path='foo/bar/baz')
        expected = '{0}:/foo/bar/baz'.format(user_vault)
        self.assertEqual(p, expected)
