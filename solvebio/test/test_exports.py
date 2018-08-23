from __future__ import absolute_import
# import hashlib
from solvebio import Filter

from .helper import SolveBioTestCase

# from os import path, remove


class ExportsTests(SolveBioTestCase):
    """
    Test exporting SolveBio Query object.
    """
    def setUp(self):
        super(ExportsTests, self).setUp()
        filters = Filter(rgd_id='RGD:2645')
        self.dataset = self.client.Dataset.get_by_full_path(
            'solvebio:public:/HGNC/3.0.0-2016-11-10/HGNC')
        self.query = self.dataset.query(filters=filters, fields=['rgd_id'],
                                        genome_build='GRCh37', limit=10)

    """
    # Removing this test
    # since it generates an export each time.
    # TODO mock this in the future
    def test_csv_exporter(self):

        # CSV exports are compressed
        test_file = '/tmp/test_export.csv'
        reference_file = 'solvebio/test/data/test_export.csv'
        export = self.query.export(follow=True, format='csv')
        export.download(test_file)

        self.assertTrue(export.dataset.id, self.dataset.id)
        self.assertTrue(path.isfile(test_file))
        self.assertEqual(
            hashlib.sha1(open(test_file, 'rb').read()).hexdigest(),
            hashlib.sha1(open(reference_file, 'rb').read()).hexdigest()
        )
        remove(test_file)
    """
