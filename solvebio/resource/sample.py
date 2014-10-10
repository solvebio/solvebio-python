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
    def create(cls, **params):
        """Creates a new sample from the specified VCF URL or
        path. You may provide either a vcf_url or vcf_file but not
        both. To upload a sample using the vcf_file parameter, you
        must use Content-Type: multipart/form-data."""
        response = client.request('post', Sample.class_url(), params)
        return response
        return convert_to_solve_object(response)

    def instance_url(self):
        return '{0}/{1}'.format(self.class_url(), self.id)

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)
