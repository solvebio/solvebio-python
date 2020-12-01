from __future__ import absolute_import

from .helper import SolveBioTestCase
from solvebio.errors import SolveError
from solvebio.resource import DatasetImport
from solvebio.client import client


class ErrorTests(SolveBioTestCase):

    def test_solve_error(self):
        try:
            # two errors get raised
            DatasetImport.create(
                dataset_id='510113719950913753',
                manifest=dict(files=[dict(filename='soemthing.md')])
            )
        except SolveError as e:
            self.assertTrue('Error (dataset_id):' in str(e), e)
            self.assertTrue('Invalid dataset' in str(e), e)
            self.assertTrue('Error (manifest):' in str(e), e)
            self.assertTrue('Each file must' in str(e), e)


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
