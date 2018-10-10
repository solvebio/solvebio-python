from __future__ import absolute_import

from .helper import SolveBioTestCase


class APIResourceTests(SolveBioTestCase):

    def test_apiresource_iteration(self):
        public_vault = self.client.Vault.get_by_full_path('solvebio:public')
        n_folders = len(list(public_vault.folders(depth=0)))

        folder_iter = public_vault.folders(depth=0)
        for i, j in enumerate(folder_iter):
            pass
        self.assertTrue(i == n_folders - 1)

        # Iterating again should be the same
        for i, j in enumerate(folder_iter):
            pass
        self.assertTrue(i == n_folders - 1)
