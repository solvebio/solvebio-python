from __future__ import absolute_import

from solvebio.test.helper import SolveBioTestCase
from solvebio.errors import SolveError
from solvebio.resource import DatasetImport
from solvebio.client import client


class ErrorTests(SolveBioTestCase):

    def test_solve_error(self):
        ds_id = '510113719950913753'
        try:
            # two errors get raised
            DatasetImport.create(
                dataset_id=ds_id,
                manifest=dict(files=[dict(filename='soemthing.md')])
            )
        except SolveError as e:
            resp = e.json_body
            self.assertIn(f'Invalid pk "{ds_id}" - object does not exist.', resp.get('dataset_id'))
            self.assertIn(f"Each file must have an URL.", resp.get('manifest'))


class ErrorTestsAuth(SolveBioTestCase):

    def test_no_body(self):
        # Remove auth
        auth = client._auth
        client._auth = None
        try:
            client.whoami()
        except SolveError as e:
            self.assertTrue('Error: Authentication credentials were not'
                            in str(e), e)

        client._auth = auth
