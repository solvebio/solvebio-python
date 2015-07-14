from __future__ import absolute_import
from solvebio.resource import Depository

from .helper import SolveBioTestCase


class DepositoryTests(SolveBioTestCase):

    def test_depositories(self):
        # TODO: use TEST_DATASET_NAME.split('/')[0]
        depos = Depository.all()
        depo = depos.data[0]
        self.assertTrue('id' in depo,
                        'Should be able to get id in depository')

        depo2 = Depository.retrieve(depo.id)
        self.assertEqual(depo, depo2,
                         "Retrieving dataset id {0} found by all()"
                         .format(depo.id))

        check_fields = ['class_name', 'created_at',
                        'description', 'external_resources',
                        'full_name', 'id',
                        'is_private', 'is_restricted',
                        'latest_version',
                        'latest_version_id',
                        'name', 'title', 'updated_at',
                        'url', 'versions_count', 'versions_url',
                        'permissions']

        for f in check_fields:
            self.assertTrue(f in depo)
