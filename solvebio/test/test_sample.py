import os

from solvebio.resource import Sample
from .helper import SolveBioTestCase


class SampleTest(SolveBioTestCase):
    sample_meta = [
        ('class_name', 'Sample'),
        ('annotations_count', 0),
        ('description', ''),
        ('genome_build', 'hg19'),
        ('vcf_md5', '83acd96171c72ab2bb35e9c52961afd9'),
        ('vcf_size', 592),
    ]

    def test_sample_url(self):
        self.assertEqual(Sample.class_url(), '/v1/samples',
                         'Sample.class_url()')

    def test_create_from_url(self):
        vcf_url = "https://github.com/solvebio/solvebio-python/" + \
                  "raw/master/solvebio/test/data/sample.vcf.gz"
        sample = Sample.create(genome_build='hg19', vcf_url=vcf_url)
        self.check_response(sample, self.sample_meta,
                            'Create Sample from URL')
        self.check_response(Sample.retrieve(sample.id), self.sample_meta,
                            'Sample.retrieve(1)')

    def test_create_from_file(self):
        vcf_file = os.path.join(os.path.dirname(__file__),
                                "data/sample.vcf.gz")
        sample = Sample.create(genome_build='hg19', vcf_file=vcf_file)
        self.check_response(sample, self.sample_meta,
                            'Create a Sample from a file')
        self.check_response(Sample.retrieve(sample.id), self.sample_meta,
                            'Sample.retrieve(1)')

    def test_sample_error_params(self):
        for params in [(), ('hg19')]:
            self.assertRaises(TypeError, lambda: Sample.create(*params))
            self.assertRaises(TypeError,
                              lambda: Sample.create_from_file(*params))
            self.assertRaises(TypeError,
                              lambda: Sample.create_from_url(*params))

        for params in [{}, {'vcf_file': 'a', 'vcf_url': 'b'}]:
            self.assertRaises(TypeError,
                              lambda: Sample.create('hg19', *params))
