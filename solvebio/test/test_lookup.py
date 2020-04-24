from __future__ import absolute_import

from .helper import SolveBioTestCase


class LookupTests(SolveBioTestCase):

    def setUp(self):
        super(LookupTests, self).setUp()
        self.dataset = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)

    def test_lookup_error(self):
        # Check that incorrect lookup results in empty list.
        lookup_one = self.dataset.lookup('test')
        self.assertEqual(lookup_one, [])

        lookup_two = self.dataset.lookup('test', 'nothing')
        self.assertEqual(lookup_two, [])

    def test_lookup_correct(self):
        # Check that lookup with specific sbid is correct.
        records = list(self.dataset.query(limit=2))
        record_one = records[0]
        record_two = records[1]
        sbid_one = record_one['_id']
        sbid_two = record_two['_id']

        lookup_one = self.dataset.lookup(sbid_one)
        self.assertEqual(lookup_one[0], record_one)

        lookup_two = self.dataset.lookup(sbid_two)
        self.assertEqual(lookup_two[0], record_two)

        # Check that combining sbids returns list of correct results.
        joint_lookup = self.dataset.lookup(sbid_one, sbid_two)
        self.assertEqual(joint_lookup[0], record_one)
        self.assertEqual(joint_lookup[1], record_two)
