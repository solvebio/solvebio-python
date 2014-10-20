import os
import tempfile
import unittest


from solvebio.resource import Sample


class SampleTest(unittest.TestCase):

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

        # TODO: check unauthorized access
        return

    def test_sample(self):
        self.assertEqual(Sample.class_url(), '/v1/samples',
                         'Sample.class_url()')

        return

    def test_sample_download(self):
        all = Sample.all()
        if all.total == 0:
            return unittest.skip("no samples found to download")
        sample = all.data[0]
        response = Sample.download(sample.id, tempfile.tempdir)
        self.assertEqual(response.status_code, 200,
                         "Download sample file status ok")
        self.assertTrue(os.path.exists(response.filename),
                        "Download sample file on filesystem")
        os.remove(response.filename)
        return


if __name__ == "__main__":
    unittest.main()
