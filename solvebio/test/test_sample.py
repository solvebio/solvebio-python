import unittest
import os

from solvebio.errors import SolveError
from solvebio.resource import Sample


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
               os.environ['SOLVEBIO_API_KEY'].startswith(
            '0cedb161d'):
            self.assertRaises(SolveError, lambda: Sample.retrieve(1))
        else:
            all = Sample.all()
            self.assertTrue(all.total > 1,
                            "Sample.all() returns more than one value")
        return

if __name__ == "__main__":
    unittest.main()
