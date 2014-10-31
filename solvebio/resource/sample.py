"""Solvebio API Resource for Samples"""

from .annotation import Annotation
from .apiresource import DeletableAPIResource, DownloadableAPIResource, \
    ListableAPIResource
from ..client import client
from ..errors import SolveError
from .solveobject import convert_to_solve_object


class Sample(DeletableAPIResource, DownloadableAPIResource,
             ListableAPIResource):
    """
    Samples are VCF files uploaded to the SolveBio API. We currently
    support uncompressed, extension `.vcf`, and gzip-compressed, extension
    `.vcf.gz`, VCF files. Any other extension will be rejected.
    """

    """Defines *create()*, *create_from_file()* and
    *create_from_url()* methods which allow one to upload a (VCF) file
    to be stored on the system.
    """

    @classmethod
    def create(cls, genome_build, **params):
        if 'vcf_url' in params:
            if 'vcf_file' in params:
                raise TypeError('Specified both vcf_url and vcf_file; ' +
                                'use only one')
            return cls.create_from_url(genome_build, params['vcf_url'])
        elif 'vcf_file' in params:
            return cls.create_from_file(genome_build, params['vcf_file'])
        else:
            raise TypeError('Must specify exactly one of vcf_url or ' +
                            'vcf_file parameter')

    @classmethod
    def create_from_file(cls, genome_build, vcf_file):
        """Creates from the specified file.  The data of
        the should be in VCF format."""

        files = {'vcf_file': open(vcf_file, 'rb')}
        params = {'genome_build': genome_build}
        response = client.post(cls.class_url(), params, files=files)
        return convert_to_solve_object(response)

    @classmethod
    def create_from_url(cls, genome_build, vcf_url):
        """Creates from the specified URL.  The data of
        the should be in VCF format."""

        params = {'genome_build': genome_build,
                  'vcf_url': vcf_url}
        try:
            response = client.post(cls.class_url(), params)
        except SolveError as response:
            pass
        return convert_to_solve_object(response)

    def annotate(self):
        return Annotation.create(sample_id=self.id)
