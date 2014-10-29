from test_helper import unittest
import os

import solvebio
from solvebio.resource import Sample


@unittest.skipIf(solvebio.api_host == 'https://api.solvebio.com',
                                      "annotation creation")
class SampleAccessTest(unittest.TestCase):

    # FIXME: DRY routine with test_sample_access.py
    def check_response(self, response, expect, msg):
        subset = [(key, response[key]) for
                  key in [x[0] for x in expect]]
        self.assertEqual(subset, expect, msg)

    def test_insert_delete(self):
        all = Sample.all()
        total = all.total
        vcf_url = "http://downloads.solvebio.com/vcf/small_sample.vcf.gz"
        expect = [
            ('class_name', 'Sample'),
            ('annotations_count', 0),
            ('description', ''),
            ('genome_build', 'hg19'),
            ('vcf_md5', 'a03e39e96671a01208cffd234812556d'),
            ('vcf_size', 12124), ]
        response = Sample.create(genome_build='hg19', vcf_url=vcf_url)
        self.check_response(response, expect,
                            'create sample.vcf.gz from url')
        all = Sample.all()
        self.assertEqual(all.total, total + 1, "After uploading an url")
        total = total + 1
        vcf_file = os.path.join(os.path.dirname(__file__),
                                "data/sample.vcf.gz")
        response = Sample.create(genome_build='hg19', vcf_file=vcf_file)
        expect = [
            ('class_name', 'Sample'),
            ('annotations_count', 0),
            ('description', ''),
            ('genome_build', 'hg19'),
            ('vcf_md5', '83acd96171c72ab2bb35e9c52961afd9'),
            ('vcf_size', 592), ]

        self.check_response(response, expect,
                            'create sample.vcf.gz from a file')
        self.assertEqual(all.total, total, "After uploading a file")

        sample = Sample.retrieve(response.id)
        delete_response = sample.delete()
        self.assertEqual(delete_response.deleted, True,
                         'response.deleted should be True')
        all = Sample.all()
        self.assertEqual(all.total, total, "After deleting a file")

if __name__ == "__main__":
    unittest.main()
