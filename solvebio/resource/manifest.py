# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import os
import glob

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

    def add_files(self, files):
        """
        Add one or more local files to the manifest.
        If files contains a glob, it is expanded.

        All files are uploaded to SolveBio. The Upload
        object is used to fill the manifest.
        """
        for path in files:
            if os.path.isfile(path):
                self.add_file(path)
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    self.add_file(f)
            else:
                for f in glob.glob(path):
                    self.add_file(f)
