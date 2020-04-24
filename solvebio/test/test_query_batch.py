from __future__ import absolute_import

from .helper import SolveBioTestCase


class BatchQueryTest(SolveBioTestCase):
    def setUp(self):
        super(BatchQueryTest, self).setUp()
        self.dataset = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)

    def test_invalid_batch_query(self):
        queries = [
            self.dataset.query(limit=1, fields=['bogus_field']),
            self.dataset.query(limit=10).filter(bogus_id__gt=100000)
        ]

        results = self.client.BatchQuery(queries).execute()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['status_code'], 400)
        self.assertEqual(results[1]['status_code'], 400)

    def test_batch_query(self):
        queries = [
            self.dataset.query(limit=1),
            self.dataset.query(limit=10).filter(mamit_trnadb__gt=1),
            self.dataset.query(limit=100),
        ]
        results = self.client.BatchQuery(queries).execute()
        self.assertEqual(len(results), 3)
        self.assertEqual(len(results[0]['results']), 1)
        self.assertEqual(len(results[1]['results']), 10)
        self.assertEqual(len(results[2]['results']), 100)
