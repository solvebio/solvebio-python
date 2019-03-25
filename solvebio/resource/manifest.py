# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import os
import glob

from six.moves.urllib.parse import urlparse

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

    def add_file(self, path, **kwargs):
        default_upload_path = solvebio.Vault.get_or_create_uploads_path()
        vault = solvebio.Vault.get_personal_vault()
        print("Uploading file: {0} to {1}".format(path, default_upload_path))
        file_ = solvebio.Object.upload_file(path, default_upload_path,
                                            vault.full_path)
        print("Successfuly uploaded file {0} (id:{1} size:{2} md5:{3})"
              .format(path, file_.id, file_.size, file_.md5))

        self.manifest['files'].append({
            'object_id': file_.id,
            'name': file_.filename,
            'md5': file_.md5,
            'size': file_.size,
            'reader_params': kwargs.get('reader_params'),
            'entity_params': kwargs.get('entity_params'),
            'validation_params': kwargs.get('validation_params')
        })

    def add_url(self, url, **kwargs):
        manifest_item = dict(url=url, **kwargs)
        self.manifest['files'].append(manifest_item)

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
                    'Path: "{0}" is not a valid format or does not exist. '
                    'Manifest paths must be files, directories, or URLs.'
                    .format(path)
                )
