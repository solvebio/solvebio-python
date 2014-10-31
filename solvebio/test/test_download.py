import os
import hashlib

from solvebio.resource import Sample
from .helper import SolveBioTestCase


def md5_file(fileobj, blocksize=65535):
    hasher = hashlib.md5()
    fileobj.seek(0)
    buf = fileobj.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)
        buf = fileobj.read(blocksize)

    return hasher.hexdigest()


class DownloadTest(SolveBioTestCase):
    def test_sample_download(self):
        vcf_file = os.path.join(os.path.dirname(__file__),
                                "data/sample.vcf.gz")
        sample = Sample.create(genome_build='hg19', vcf_file=vcf_file)

        # Downloads to a temporary dir
        response = sample.download()
        self.assertEqual(response.status_code, 200,
                         "Download sample file status ok")
        self.assertTrue(os.path.exists(response.filename),
                        "Download sample file on filesystem")
        vcf_md5 = md5_file(open(response.filename, 'rb'))
        self.assertEqual(vcf_md5, sample.vcf_md5,
                         "Downloaded file MD5")
        os.remove(response.filename)
