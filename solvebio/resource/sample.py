"Solvebio Sample API Resource"
import os
import requests
from ..client import client, _handle_api_error, _handle_request_error

from ..import SolveError
from .util import json
from .solveobject import convert_to_solve_object
from .resource import APIResource

def conjure_file(url, path):
    """Make up a file name based on info in url and path.
    path can be a full path, a directory name, or None.
    If path is None, we'll use use the current directory plus any
    name we find in url. If path is a directory well use that plus
    the name found in url. If it a non-directory string, we'll
    ignore any filename found in url and use that.
    """
    values = url.split('%3B%20filename%3D')
    if len(values) != 2:
        # FIXME: Perhaps we want a more unique name?
        short_name = 'download.gz'
    else:
        short_name = values[1]
    if path:
        if os.path.isdir(path):
            path = os.path.join(path, short_name)
    else:
        path = short_name
    return path


class Sample(APIResource):
    """
    Samples are VCF files uploaded to the SolveBio API. We currently
    support uncompressed (extension '.vcf') and gzip-compressed (extension
    '.vcf.gz') VCF files. Any other extension will be rejected.
    """

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
                raise TypeError('Specified both vcf_url and vcf_file; ' +
                                'use only one')
            return Sample.create_from_url(genome_build, params['vcf_url'])
        elif 'vcf_file' in params:
            return Sample.create_from_file(genome_build, params['vcf_file'])
        else:
            raise TypeError('Must specify exactly one of vcf_url or ' +
                            'vcf_file parameter')

    @classmethod
    def create_from_file(cls, genome_build, vcf_file):
        """Creates a new sample from the specified file.  The data of
        the should be in VCF format."""

        files = {'vcf_file': open(vcf_file, 'rb')}
        params = {'genome_build': genome_build}
        response = client.request('post', Sample.class_url(), params=params,
                                  files=files)
        return convert_to_solve_object(response)

    @classmethod
    def create_from_url(cls, genome_build, vcf_url):
        """Creates a new sample from the specified URL.  The data of
        the should be in VCF format.
        """
        params = {'genome_build': genome_build,
                  'vcf_url': vcf_url}
        try:
            response = client.request('post', Sample.class_url(), params=params)
        except SolveError as response:
            pass
        return convert_to_solve_object(response)

    @classmethod
    def delete(cls, id):
        """Delete the sample with the id. The id is that returned by a
        create, or found by listing all samples.
        """
        try:
            response = client.request('delete', cls(id).instance_url())
        except SolveError as response:
            pass
        return convert_to_solve_object(response)

    @classmethod
    def download(cls, id, path=None):
        """Download the sample with the id. The id is that returned by a
        create, or found by listing all samples.
        """
        download_url = cls(id).instance_url() + '/download'
        response = client.request('get', download_url, allow_redirects=False)
        if 302 != response.status_code:
            # Some kind of error. We expect a redirect
            return None
        download_url = response.headers['location']
        download_path = conjure_file(download_url, path)

        # FIXME: refactor and combine with code in client
        try:
            response = requests.request(method='get', url=download_url)
        except Exception as e:
            _handle_request_error(e)

        if not (200 <= response.status_code < 400):
            _handle_api_error(response)

        with open(download_path, 'wb') as fileobj:
            fileobj.write(response._content)

        return convert_to_solve_object(response)

    @classmethod
    def retrieve(cls, id):
        "Retrieves a specific sample by ID."
        response = client.request('get', cls(id).instance_url())
        return convert_to_solve_object(response)

    def instance_url(self):
        return '{0}/{1}'.format(self.class_url(), self.id)

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)
