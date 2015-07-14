from __future__ import absolute_import
from solvebio.resource import DepositoryVersion

from .helper import SolveBioTestCase


class DepositoryVersionTests(SolveBioTestCase):

    def test_depositoryversions(self):
        dvs = DepositoryVersion.all()
        dv = dvs.data[0]
        self.assertTrue('id' in dv,
                        'Should be able to get id in depositoryversion')

        dv2 = DepositoryVersion.retrieve(dv.id)
        self.assertEqual(dv, dv2,
                         "Retrieving depository id {0} found by all()"
                         .format(dv.id))

        check_fields = set(['class_name', 'created_at',
                            'datasets_url', 'depository',
                            'depository_id', 'description',
                            'full_name', 'id', 'latest',
                            'name', 'is_released', 'released_at',
                            'title', 'updated_at', 'url',
                            'changelog_url'])
        self.assertSetEqual(set(dv), check_fields)

    """
    #TODO add another version of TEST_DATASET so we can test changelog
    def test_depositoryversion_changelog(self):
        dv = DepositoryVersion.all().data[0]
        resp = dv.changelog()
        self.assertTrue(resp, resp)
    """
