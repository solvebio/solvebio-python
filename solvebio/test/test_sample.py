import unittest
import os

from solvebio import Sample, SolveError


class SampleTest(unittest.TestCase):

    def test_sample_error_params(self):
        for params in [(), ('hg19')]:
            self.assertRaises(TypeError, lambda: Sample.create(*params))
            self.assertRaises(TypeError,
                              lambda: Sample.create_from_file(*params))
            self.assertRaises(TypeError,
                              lambda: Sample.create_from_url(*params))
        for params in [{},  {'vcf_file': 'a', 'vcf_url': 'b'}]:
            self.assertRaises(TypeError,
                              lambda: Sample.create('hg19', *params))
        return

    def test_sample(self):
        self.assertEqual(Sample.class_url(), '/v1/samples',
                         'Sample.class_url()')

        if 'SOLVEBIO_API_KEY' in os.environ and \
               os.environ['SOLVEBIO_API_KEY'].startswith('0cedb161d'):
            self.assertRaises(SolveError, lambda: Sample.retrieve(1))
        all = Sample.all()
        self.assertTrue(len(all) > 1,
                        "Sample.all() returns more than one value")
        return

    if 'TEST_SOLVEBIO_API_UPDATE' in os.environ:

        def check_response(self, response, expect, msg):
            subset = [(key, response[key]) for
                      key in [x[0] for x in expect]]
            self.assertEqual(subset, expect, msg)

        def test_retrieve(self):
            expect = [
                ('class_name', 'Sample'),
                ('annotations_count', 4),
                ('id', 1),
                ('description', ''),
                ('genome_build', 'hg19'),
                ('vcf_md5', 'a03e39e96671a01208cffd234812556d'),
                ('vcf_size', 12124), ]
            self.check_response(Sample.retrieve(1), expect, 'Sample.retrieve(1)')
            return

        def test_insert_delete(self):
            all = Sample.all()
            total = all.total
            vcf_url = "https://github.com/solvebio/solvebio-python/" + \
            "raw/feature/annotation/solvebio/test/data/sample.vcf.gz"
            expect = [
                ('class_name', 'Sample'),
                ('annotations_count', 0),
                ('description', ''),
                ('genome_build', 'hg19'),
                ('vcf_md5', '83acd96171c72ab2bb35e9c52961afd9'),
                ('vcf_size', 592), ]
            response = Sample.create(genome_build='hg19', vcf_url=vcf_url)
            self.check_response(response, expect,
                                'create sample.vcf.gz from url')
            all = Sample.all()
            self.assertEqual(all.total, total+1, "After uploading an url")
            total = total+1
            vcf_file = "./data/sample.vcf.gz"
            response = Sample.create(genome_build='hg19', vcf_file=vcf_file)
            self.check_response(response, expect,
                                'create sample.vcf.gz from a file')
            self.assertEqual(all.total, total, "After uploading a file")

            response = Sample.delete(response.id)
            all = Sample.all()
            self.assertEqual(all.total, total, "After deleting a file")
            return

if __name__ == "__main__":
    unittest.main()
