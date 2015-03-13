"""Solvebio API Resource for Samples"""

from .annotation import Annotation
from .apiresource import DeletableAPIResource, DownloadableAPIResource, \
    ListableAPIResource
from ..client import client
from .solveobject import convert_to_solve_object

import time
import os


class Sample(DeletableAPIResource, DownloadableAPIResource,
             ListableAPIResource):
    """
    Samples are VCF files uploaded to the SolveBio API. We currently
    support uncompressed, extension `.vcf`, and gzip-compressed, extension
    `.vcf.gz`, VCF files. Any other extension will be rejected.
    """

    @classmethod
    def create(cls, genome_build, **params):
        if ('vcf_url' in params and 'vcf_file' in params) or \
                ('vcf_url' not in params and 'vcf_file' not in params):
            raise TypeError(
                'Please specify either a "vcf_url" or "vcf_file".')

        if 'vcf_url' in params:
            return cls.create_from_url(genome_build, **params)
        elif 'vcf_file' in params:
            return cls.create_from_file(genome_build, **params)

    @classmethod
    def create_from_file(cls, genome_build, vcf_file):
        """
        Creates from the specified VCF file.
        """
        params = {
            'genome_build': genome_build
        }
        files = {
            'vcf_file': open(os.path.expanduser(vcf_file), 'rb')
        }
        response = client.post(cls.class_url(), params, files=files)
        return convert_to_solve_object(response)

    @classmethod
    def create_from_url(cls, genome_build, vcf_url):
        """
        Creates a Sample from the specified URL.
        """
        params = {
            'genome_build': genome_build,
            'vcf_url': vcf_url
        }

        response = client.post(cls.class_url(), params)
        return convert_to_solve_object(response)

    def annotate(self, wait=False):
        a = Annotation.create(sample_id=self.id)

        if wait:
            while a.status in ['queued', 'running']:
                time.sleep(1)
                a.refresh()

        return a
