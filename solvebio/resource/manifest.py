# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import os
import glob

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import solvebio


class Manifest(object):
    """
    Manifests aren't strictly resources, they represent a list
    of remote files (URLs) with additional information that
    can be used for validation (size and MD5).
    """
    manifest = None

    def __init__(self):
        self.manifest = {'files': []}

    def add_file(self, path):
        print("Uploading file: {0}".format(path))
        upload = solvebio.Upload.create(path=path)
        print("Successfuly uploaded file {0} (id:{1} size:{2} md5:{3})"
              .format(path, upload.id, upload.size, upload.md5))

        self.manifest['files'].append({
            'name': upload.filename,
            'format': upload.format,
            'size': upload.size,
            'md5': upload.md5,
            'base64_md5': upload.base64_md5,
            'url': upload.download_url()
        })

    def add_url(self, url, **kwargs):
        self.manifest['files'].append({
            'url': url,
            'name': kwargs.get('name'),
            'format': kwargs.get('format'),
            'size': kwargs.get('size'),
            'md5': kwargs.get('md5'),
            'base64_md5': kwargs.get('base64_md5')
        })

    def add(self, *args):
        """
        Add one or more files or URLs to the manifest.
        If files contains a glob, it is expanded.

        All files are uploaded to SolveBio. The Upload
        object is used to fill the manifest.
        """
        def _is_url(path):
            p = urlparse(path)
            return bool(p.scheme)

        for path in args:
            path = os.path.expanduser(path)
            if _is_url(path):
                self.add_url(path)
            elif os.path.isfile(path):
                self.add_file(path)
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    self.add_file(f)
            elif glob.glob(path):
                for f in glob.glob(path):
                    self.add_file(f)
            else:
                raise ValueError(
                    'Manifest path: "{0}" is not valid. '
                    'Manifest paths must be files, directories, or URLs. '
                    'The following extensions are supported: '
                    '.vcf .vcf.gz .json .json.gz'.format(path))
