from __future__ import absolute_import

import os
import time

from .helper import SolveBioTestCase
from solvebio.cli.main import main
from solvebio import Depository
from solvebio import DatasetTemplate


class WhoAmITests(SolveBioTestCase):

    def test_whoami(self):
        email, token = main(['whoami'])
        self.assertEqual(token, os.environ.get('SOLVEBIO_API_KEY'))


class CLITests(SolveBioTestCase):

    def test_create_dataset(self):
        # TODO mock client responses or allow
        # for hard cleanup of template and dataset/depo
        # return
        template_path = os.path.join(os.path.dirname(__file__),
                                     "data/template.json")
        dataset_full_name = \
            'test-client-{0}/1.0.0/test-{0}'.format(int(time.time()))
        args = ['create-dataset', dataset_full_name,
                   '--template-file', template_path,
                   '--capacity', 'medium']  # noqa
        ds = main(args)
        self.assertEqual(ds.full_name, dataset_full_name)

        # does hard delete of template
        tpl = DatasetTemplate.retrieve(
            ds.tags[0].replace('template-', ''))
        tpl.delete()

        # does soft delete of depo
        depo = Depository.retrieve(ds.depository_id)
        depo.delete(soft=False)
