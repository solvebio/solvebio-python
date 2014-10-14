# -*- coding: utf-8 -*-
"""
Samples are VCF files uploaded to the SolveBio API. We currently
support uncompressed (extension “.vcf”) and gzip-compressed (extension
“.vcf.gz”) VCF files. Any other extension will be rejected.
"""
from ..client import client

from .util import class_to_api_name, json
from .solveobject import SolveObject, convert_to_solve_object


class Sample(SolveObject):
    @classmethod
    def class_url(cls):
        "Returns a versioned URI string for this class"
        # FIXME: DRY with other class_url routines
        return "/v1/{0}".format(class_to_api_name(cls.__name__))

    @classmethod
    def retrieve(cls, id):
        "Retrieves a specific sample by ID."
        response = client.request('get', cls(id).instance_url())
        return convert_to_solve_object(response)

    @classmethod
    def all(cls):
        "Lists all samples (that you have access to) in a paginated form."
        response = client.request('get', Sample.class_url())
        return convert_to_solve_object(response)

    @classmethod
    def create(cls, genome_build, **params):
        """Creates a new sample from the specified URL or file
        path. The data of the URL or file should be in VCF format.
        You may provide either a VCF URL via vcf_url=... or VCF file
        via vcf_file=... but not both.
        """
        if 'vcf_url' in params:
            if 'vcf_file' in params:
                raise TypeError('Specified both vcf_url and vcf_file; use only one')
            return Sample.create_from_url(genome_build, params['vcf_url'])
        elif 'vcf_file' in params:
            return Sample.create_from_file(genome_build, params['vcf_file'])
        else:
            raise TypeError('Must specify exactly one of vcf_url or vcf_file parameter')


    @classmethod
    def create_from_file(cls, genome_build, vcf_file):
        """Creates a new sample from the specified file.  The data of
        the should be in VCF format."""

        files= {'vcf_file': open(vcf_file, 'rb')}
        params = {'genome_build': genome_build }
        response = client.request('post', Sample.class_url(), params=params,
                                  files=files)
        return convert_to_solve_object(response)

    @classmethod
    def create_from_url(cls, genome_build, vcf_url):
        """Creates a new sample from the specified URL.  The data of
        the should be in VCF format.
        """
        params = {'genome_build': genome_build,
                  'vcf_url'     : vcf_url}
        response = client.request('post', Sample.class_url(), params=params)
        return convert_to_solve_object(response)

    @classmethod
    def delete(cls, id):
        """Creates a new sample from the specified URL.  The data of
        the should be in VCF format.
        """
        response = client.request('delete', cls(id).instance_url())
        return convert_to_solve_object(response)

    def instance_url(self):
        return '{0}/{1}'.format(self.class_url(), self.id)

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)
