"""Solvebio Object API resource"""
import os
import re
import base64
import binascii
import mimetypes
import sys
import time
from datetime import datetime

import requests
import six
from requests.packages.urllib3.util.retry import Retry

from solvebio.errors import SolveError
from solvebio.errors import NotFoundError
from solvebio.errors import FileUploadError
from solvebio.utils.md5sum import md5sum
from solvebio.utils.files import separate_filename_extension

from ..client import client

from .solveobject import convert_to_solve_object

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource
from .apiresource import DownloadableAPIResource

if sys.version_info >= (3, 9, 0):
    from collections.abc import Iterable
else:
    from collections import Iterable # noqa


class Object(CreateableAPIResource,
             ListableAPIResource,
             DeletableAPIResource,
             SearchableAPIResource,
             UpdateableAPIResource,
             DownloadableAPIResource):
    """
    An object is a resource in a Vault.  It has three possible types,
    though more may be added later: folder, file, and SolveBio Dataset.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('object_type', 'Type'),
        ('full_path', 'Full Path'),
        ('description', 'Description'),
    )

    # Regex describing an object path.
    PATH_RE = re.compile(r'^[^\/]*(?P<path>(\/[^\/]*)+)$')

    @classmethod
    def validate_full_path(cls, full_path, **kwargs):
        """Helper method to parse a full or partial path and
        return a full path as well as a dict containing path parts.

        Uses the following rules when processing the path:

            * If no domain, uses the current user's account domain
            * If no vault, uses the current user's personal vault.
            * If no path, uses '/' (vault root)

        Returns a tuple containing:

            * The validated full_path
            * A dictionary with the components:
                * domain: the domain of the vault
                * vault: the name of the vault, without domain
                * vault_full_path: domain:vault
                * path: the object path within the vault
                * parent_path: the parent path to the object
                * parent_full_path: the parent full path to the object
                * filename: the object's filename (if any)
                * full_path: the validated full path

        The following components may be overridden using kwargs:

            * vault
            * path

        Object paths (also known as "paths") must begin with a forward slash.

        The following path formats are supported:

            domain:vault:/path -> object "path" in the root of "domain:vault"
            domain:vault/path  -> object "path" in the root of "domain:vault"
            vault:/path        -> object "path" in the root of "vault"
            vault/path         -> object "path" in the root of "vault"
            ~/path             -> object "path" in the root of personal vault
            vault/             -> root of "vault"
            ~/                 -> root of your personal vault

        The following two formats are not supported:

            path               -> invalid/ambiguous path (exception)
            vault:path         -> invalid/ambiguous path (exception)
            vault:path/path    -> unsupported, interpreted as domain:vault/path

        """
        from solvebio.resource.vault import Vault

        _client = kwargs.pop('client', None) or cls._client or client

        if not full_path:
            raise Exception(
                'Invalid path: ',
                'Full path must be in one of the following formats: '
                '"vault:/path", "domain:vault:/path", or "~/path"')

        # Parse the vault's full_path, using overrides if any
        input_vault = kwargs.get('vault') or full_path
        try:
            vault_full_path, path_dict = \
                Vault.validate_full_path(input_vault, client=_client)
        except Exception as err:
            raise Exception('Could not determine vault from "{0}": {1}'
                            .format(input_vault, err))

        if kwargs.get('path'):
            # Allow override of the object_path.
            full_path = '{0}:/{1}'.format(vault_full_path, kwargs['path'])

        match = cls.PATH_RE.match(full_path)
        if match:
            object_path = match.groupdict()['path']
        else:
            raise Exception(
                'Cannot find a valid object path in "{0}". '
                'Full path must be in one of the following formats: '
                '"vault:/path", "domain:vault:/path", or "~/path"'
                .format(full_path))

        # Remove double slashes
        object_path = re.sub('//+', '/', object_path)
        if object_path != '/':
            # Remove trailing slash
            object_path = object_path.rstrip('/')

        path_dict['path'] = object_path
        path_dict['full_path'] = '{domain}:{vault}:{path}'.format(**path_dict)

        # Assumes no trailing slash, will be '' if is a vault root
        path_dict['filename'] = os.path.basename(object_path)

        # Will be / if parent is vault root
        path_dict['parent_path'] = os.path.dirname(object_path)
        path_dict['parent_full_path'] = '{vault_full_path}:{parent_path}' \
            .format(**path_dict)

        return path_dict['full_path'], path_dict

    @classmethod
    def get_by_path(cls, path, **params):
        assert_type = params.pop('assert_type', None)
        params.update({'path': path})
        obj = cls._retrieve_helper('object', 'path', path, **params)
        if obj and assert_type and obj['object_type'] != assert_type:
            raise SolveError(
                "Expected a {} but found a {} at {}"
                .format(assert_type, obj['object_type'], path))

        return obj

    @classmethod
    def get_by_full_path(cls, full_path, **params):
        # Don't pop client from params since **params is used below
        _client = params.get('client', None) or cls._client or client
        full_path, _ = cls.validate_full_path(full_path, client=_client)
        assert_type = params.pop('assert_type', None)
        params.update({'full_path': full_path})
        obj = cls._retrieve_helper('object', 'full_path', full_path,
                                   **params)
        if obj and assert_type and obj['object_type'] != assert_type:
            raise SolveError(
                "Expected a {} but found a {} at {}"
                .format(assert_type, obj['object_type'], full_path))

        return obj

    @classmethod
    def get_or_create_by_full_path(cls, full_path, **kwargs):
        from solvebio import Vault
        from solvebio import Object

        _client = kwargs.pop('client', None) or cls._client or client
        create_vault = kwargs.pop('create_vault', False)
        create_folders = kwargs.pop('create_folders', True)

        # Check for object type assertion, if not explicitly added, see
        # if user has passed object_type, as their intent was to get/create
        # an object of that type.
        assert_type = kwargs.pop('assert_type',
                                 kwargs.get('object_type', None))

        try:
            return cls.get_by_full_path(
                full_path, assert_type=assert_type, client=_client)
        except NotFoundError:
            pass

        # Object type required when creating Object
        object_type = kwargs.get('object_type')
        if not object_type:
            raise Exception("'object_type' is required when creating a new "
                            "Object. Pass one of: file, folder, dataset")

        # TODO should we require file contents?
        # Technically a user could then use this object to the call
        # upload_file()
        # if object_type == 'file' and not kwargs.get('content'):
        #     raise Exception('')

        # Object not found, create it step-by-step
        full_path, parts = Object.validate_full_path(full_path, client=_client)

        if create_vault:
            vault = Vault.get_or_create_by_full_path(
                '{0}:{1}'.format(parts['domain'], parts['vault']),
                client=_client)
        else:
            vaults = Vault.all(account_domain=parts['domain'],
                               name=parts['vault'],
                               client=_client)
            if len(vaults.solve_objects()) == 0:
                raise Exception(
                    'Vault with name {0}:{1} does not exist. Pass '
                    'create_vault=True to auto-create'.format(
                        parts['domain'], parts['vault'])
                )
            vault = vaults.solve_objects()[0]

        # Create the folders to hold the object if they do not already exist.
        object_path = parts['path']
        curr_path = os.path.dirname(object_path)
        folders_to_create = []
        new_folders = []
        id_map = {'/': None}

        while curr_path != '/':
            try:
                obj = Object.get_by_path(curr_path,
                                         vault_id=vault.id,
                                         assert_type='folder',
                                         client=_client)
                id_map[curr_path] = obj.id
                break
            except NotFoundError:
                if not create_folders:
                    raise Exception('Folder {} does not exist.  Pass '
                                    'create_folders=True to auto-create '
                                    'missing folders')

                folders_to_create.append(curr_path)
                curr_path = '/'.join(curr_path.split('/')[:-1])
                if curr_path == '':
                    break

        for folder in reversed(folders_to_create):
            new_folder = Object.create(
                object_type='folder',
                vault_id=vault.id,
                filename=os.path.basename(folder),
                parent_object_id=id_map[os.path.dirname(folder)],
                client=_client
            )
            new_folders.append(new_folder)
            id_map[folder] = new_folder.id

        if os.path.dirname(object_path) == '/':
            parent_folder_id = None
        elif new_folders:
            parent_folder_id = new_folders[-1].id
        else:
            parent_folder_id = id_map[os.path.dirname(object_path)]

        return Object.create(filename=os.path.basename(object_path),
                             vault_id=vault.id,
                             parent_object_id=parent_folder_id,
                             client=_client,
                             **kwargs)

    @staticmethod
    def _get_timestamp(date_format="%Y-%m-%d_%Hh%Mm%Ss_%Z"):
        return datetime.now().strftime(date_format)

    def _archive(self, archive_folder):
        if not self.object_type == "file":
            raise NotImplementedError("Object archiving is only supported for files, not {}".format(self.object_type))

        # Create timestamped archive filename
        timestamp = self._get_timestamp()

        base_filename, file_extension, compression = separate_filename_extension(self.filename)
        archive_filename = u'{base_filename}_{timestamp}{extension}{compression}'.format(
            base_filename=base_filename,
            timestamp=timestamp,
            extension=file_extension,
            compression=compression)

        # Create parent archive nested directory paths
        archive_path = os.path.join(archive_folder, os.path.dirname(self.path).lstrip("/"), archive_filename)

        # Ensure no errors with archive full path
        Object.validate_full_path(self.vault.full_path + ":/" + archive_path)

        # Create all parent folders if they don't already exist
        archive_parent_folder = os.path.dirname(archive_path).lstrip("/")
        if archive_parent_folder != "":
            folders = archive_parent_folder.split("/")
            parent_folder_path = self.vault.full_path + ":"
            for folder in folders:
                folder_full_path = os.path.join(parent_folder_path, folder)
                parent_folder = Object.create_folder(self.vault, folder_full_path)
                parent_folder_path = parent_folder.full_path
            self.parent_object_id = parent_folder.id
        else:
            self.parent_object_id = None

        print("Archiving file {} to {}".format(self.full_path, archive_path))
        # Multiple saves are needed as parent object ID
        # and filename cannot be updated in the same API call
        self.save()
        self.filename = archive_filename
        return self.save()

    @classmethod
    def create_folder(cls, vault, full_path, tags=None, **kwargs):
        """Create a folder if not exists.

        Args:
            vault (Vault): A Vault object.
            full_path (str): Full path including vault name.
            tags (list[str]): List of tags to put on folder.
            client: SolveBio client configuration to use.
        Returns:
            Object: New folder object
        Raises:
            SolveError: if a file or dataset object already exists
                at the given full_path.
        """
        _client = kwargs.pop('client', None) or cls._client or client

        full_path, path_dict = Object.validate_full_path(full_path, client=_client)
        folder_name = path_dict["filename"]

        try:
            new_obj = Object.get_by_full_path(full_path, client=_client)
            if not new_obj.is_folder:
                raise SolveError(
                    "Object type {} already exists at location: {}".format(
                        new_obj.object_type, full_path
                    )
                )
        except NotFoundError:
            # Create the folder
            if path_dict["parent_path"] == "/":
                parent_object_id = None
            else:
                parent = Object.get_by_full_path(
                    path_dict["parent_full_path"], assert_type="folder", client=_client
                )
                parent_object_id = parent.id

            # Make the API call
            print("Creating folder {}".format(full_path))
            new_obj = Object.create(
                vault_id=vault.id,
                parent_object_id=parent_object_id,
                object_type="folder",
                filename=folder_name,
                tags=tags or [],
                client=_client
            )

            print("Notice: Folder created for {0} at {1}".format(folder_name, new_obj.path))

        return new_obj

    def create_shortcut(self, shortcut_full_path, **kwargs):
        """Create a shortcut to the current object at shortcut_full_path

        Args:
            shortcut_full_path (str): Full path including vault name.
            tags (list[str]): List of tags to put on shortcut.
        Returns:
            Object: New shortcut object
        Raises:
            SolveError: if a object already exists at the given shortcut_full_path.
        """
        _client = kwargs.pop('client', None) or self._client or client
        full_path, path_dict = Object.validate_full_path(shortcut_full_path, client=_client)

        try:
            existing_object = Object.get_by_full_path(full_path, client=_client)
            if existing_object:
                raise SolveError(
                    "Object type {} already exists at location: {}".format(
                        existing_object.object_type, full_path
                    )
                )
        except NotFoundError:

            target = {
                'id': self.id,
                'object_type': self.object_type
            }

            shortcut = Object.get_or_create_by_full_path(full_path=shortcut_full_path,
                                                         object_type="shortcut",
                                                         target=target,
                                                         client=_client)

            print("Notice: Shortcut created at {}".format(shortcut.path))

        return shortcut

    @classmethod
    def upload_file(cls, local_path, remote_path, vault_full_path, **kwargs):
        from solvebio import Vault
        from solvebio import Object

        _client = kwargs.pop('client', None) or cls._client or client

        local_path = os.path.expanduser(local_path)

        # Get vault
        vault = Vault.get_by_full_path(vault_full_path, client=_client)

        # Get MD5 and check if multipart upload is needed
        multipart_threshold = kwargs.get(
            "multipart_threshold", 64 * 1024 * 1024
        )  # 64MB default
        local_md5, _ = md5sum(local_path, multipart_threshold=multipart_threshold)

        # Get a mimetype of file
        mime_tuple = mimetypes.guess_type(local_path)
        # If a file is compressed get a compression type, otherwise a file type
        mimetype = mime_tuple[1] if mime_tuple[1] else mime_tuple[0]
        # Get file size
        size = os.path.getsize(local_path)
        if size == 0:
            print('WARNING: skipping empty object: {}'.format(local_path))
            return False

        # Check if object exists already and compare md5sums
        full_path, path_dict = Object.validate_full_path(
            os.path.join('{}:{}'.format(vault.full_path, remote_path),
                         os.path.basename(local_path)), client=_client)
        try:
            obj = cls.get_by_full_path(full_path, client=_client)
            if not obj.is_file:
                print('WARNING: A {} currently exists at {}'
                      .format(obj.object_type, full_path))
            else:
                # Check against md5sum of remote file
                if obj.md5 == local_md5:
                    print('WARNING: File {} (md5sum {}) already exists, '
                          'not uploading'.format(full_path, local_md5))
                    return obj
                else:
                    if kwargs.get('archive_folder'):
                        obj._archive(kwargs['archive_folder'])
                    else:
                        print('WARNING: File {} exists on SolveBio with different '
                              'md5sum (local: {} vs remote: {}) Uploading anyway, '
                              'but not overwriting.'
                              .format(full_path, local_md5, obj.md5))
        except NotFoundError:
            obj = None
            pass

        # Lookup parent object
        if kwargs.get('follow_shortcuts') and obj and obj.is_file:
            vault_id = obj.vault_id
            parent_object_id = obj.parent_object_id
            filename = obj.filename
        else:
            vault_id = vault.id
            filename = os.path.basename(local_path)
            if path_dict['parent_path'] == '/':
                parent_object_id = None
            else:
                parent_obj = Object.get_by_full_path(
                    path_dict['parent_full_path'], assert_type='folder',
                    client=_client
                )
                parent_object_id = parent_obj.id

        description = kwargs.get('description')

        # Create the file, and upload it to the Upload URL
        obj = Object.create(
            vault_id=vault_id,
            parent_object_id=parent_object_id,
            object_type='file',
            filename=filename,
            md5=local_md5,
            mimetype=mimetype,
            size=size,
            description=description,
            tags=kwargs.get('tags', []) or [],
            client=_client
        )
        print('Notice: File created for {0} at {1}'.format(local_path,
                                                           obj.path))
        print('Notice: Upload initialized')

        # Check if multipart upload is needed
        if hasattr(obj, "is_multipart") and obj.is_multipart:
            return cls._upload_multipart(obj, local_path, local_md5, **kwargs)
        else:
            return cls._upload_single_file(obj, local_path, **kwargs)

    @classmethod
    def _upload_single_file(cls, obj, local_path, **kwargs):
        """Handle single-part upload for smaller files"""
        import mimetypes

        # Get a mimetype of file
        mime_tuple = mimetypes.guess_type(local_path)
        # If a file is compressed get a compression type, otherwise a file type
        mimetype = mime_tuple[1] if mime_tuple[1] else mime_tuple[0]
        # Get file size
        size = os.path.getsize(local_path)

        # Get MD5 for single part upload
        local_md5, _ = md5sum(local_path, multipart_threshold=None)

        upload_url = obj.upload_url

        headers = {
            'Content-MD5': base64.b64encode(binascii.unhexlify(local_md5)),
            'Content-Type': mimetype,
            'Content-Length': str(size),
        }

        # Use a session with a retry policy to handle connection errors.
        session = requests.Session()
        max_retries = 5
        retry = Retry(
            total=max_retries,
            read=max_retries,
            connect=max_retries,
            backoff_factor=2,
            status_forcelist=(500, 502, 503, 504, 400),
            allowed_methods=["HEAD", "OPTIONS", "GET", "PUT", "POST"]
        )
        session.mount(
            'https://', requests.adapters.HTTPAdapter(max_retries=retry))

        # Handle retries when upload fails due to an exception such as SSLError
        n_retries = 0
        while True:
            try:
                upload_resp = session.put(upload_url,
                                          data=open(local_path, 'rb'),
                                          headers=headers)
            except Exception as e:
                if n_retries == max_retries:
                    obj.delete(force=True)
                    raise FileUploadError(str(e))

                n_retries += 1
                print('WARNING: Retrying ({}/{}) failed upload for {}: {}'.format(
                    n_retries, max_retries, local_path, e))
                time.sleep(2 * n_retries)
            else:
                break

        if upload_resp.status_code != 200:
            print('WARNING: Upload status code for {0} was {1}'.format(
                local_path, upload_resp.status_code
            ))
            # Clean up the failed upload
            obj.delete(force=True)
            raise FileUploadError(upload_resp.content)
        else:
            print('Notice: Successfully uploaded {0} to {1}'.format(local_path,
                                                                    obj.path))

        return obj

    @classmethod
    def _upload_multipart(cls, obj, local_path, local_md5, **kwargs):
        """Handle multipart upload for larger files"""
        _client = kwargs.get("client") or cls._client or client
        print(f"Notice: Upload ID {obj.upload_id}")
        try:
            # Get presigned URLs from the object
            presigned_urls = obj.presigned_urls

            print(
                "Notice: Starting multipart upload with {} parts...".format(
                    len(presigned_urls)
                )
            )

            # Step 2: Upload each part using presigned URLs
            parts = []
            with open(local_path, "rb") as f:
                for part_info in presigned_urls:
                    part_number = part_info.part_number
                    start_byte = part_info.start_byte
                    end_byte = part_info.end_byte
                    part_size = part_info.size
                    upload_url = part_info.upload_url

                    print(
                        "Notice: Uploading part {}/{}... (bytes {}-{})".format(
                            part_number, len(presigned_urls), start_byte, end_byte
                        )
                    )

                    # Seek to start position and read the exact part size
                    f.seek(start_byte)
                    chunk_data = f.read(part_size)
                    if not chunk_data:
                        break

                    # Upload part with retry logic
                    session = requests.Session()
                    retry = Retry(
                        total=3,
                        backoff_factor=2,
                        status_forcelist=(500, 502, 503, 504),
                        allowed_methods=["PUT"],
                    )
                    session.mount(
                        "https://", requests.adapters.HTTPAdapter(max_retries=retry)
                    )

                    headers = {
                        "Content-Length": str(len(chunk_data)),
                    }

                    upload_resp = session.put(
                        upload_url, data=chunk_data, headers=headers
                    )

                    if upload_resp.status_code != 200:
                        raise FileUploadError(
                            "Failed to upload part {}: {}".format(
                                part_number, upload_resp.content
                            )
                        )

                    # Get ETag from response
                    etag = upload_resp.headers.get("ETag", "").strip('"')
                    parts.append({"part_number": part_number, "etag": etag})

            # Step 3: Complete multipart upload
            print("Notice: Completing multipart upload....")
            complete_data = {
                "upload_id": obj.upload_id,
                "physical_object_id": obj.upload_key,
                "parts": parts,
            }

            print(f"Notice: {complete_data}")

            complete_resp = _client.post("/v2/complete_multi_part", complete_data)

            if "message" in complete_resp:
                print(
                    "Notice: Successfully uploaded {0} to {1} with multipart upload.".format(
                        local_path, obj.path
                    )
                )
                return obj
            else:
                raise Exception(complete_resp)

        except Exception as e:
            # Clean up failed upload - best effort cleanup
            try:
                _client.delete(
                    obj.instance_url() + "/multipart-upload",
                    {},
                )
            except Exception:
                pass  # Best effort cleanup

            obj.delete(force=True)
            raise FileUploadError("Multipart upload failed: {}".format(str(e)))

    def _object_list_helper(self, **params):
        """Helper method to get objects within"""

        if not self.is_folder:
            raise SolveError(
                "Only folders contain child objects. This is a {}"
                .format(self.object_type))

        params['vault_id'] = self.vault_id
        if 'recursive' in params:
            params['ancestor_id'] = self.id
            params['limit'] = 1000
        else:
            params['parent_object_id'] = self.id

        items = self.all(client=self._client, **params)
        return items

    def files(self, **params):
        return self._object_list_helper(object_type='file', **params)

    def folders(self, **params):
        return self._object_list_helper(object_type='folder', **params)

    def datasets(self, **params):
        return self._object_list_helper(object_type='dataset', **params)

    def objects(self, **params):
        return self._object_list_helper(**params)

    def ls(self, **params):
        return self.objects(**params)

    def __getattr__(self, name):
        """Shortcut to access attributes of the underlying Dataset resource"""
        from solvebio.resource import Dataset

        # Valid override attributes that let Object act like a Dataset
        valid_dataset_attrs = [
            # query data
            'lookup', 'beacon',
            # transform data
            'import_file', 'export', 'migrate',
            # dataset meta
            'fields', 'template', 'imports', 'commits',
            # helpers
            'activity', 'saved_queries'
        ]

        try:
            return self[name]
        except KeyError as err:
            if name in valid_dataset_attrs and self['object_type'] == "dataset":
                return getattr(
                    Dataset(self['id'], client=self._client), name)

            raise AttributeError(*err.args)

    @property
    def dataset(self):
        """ Returns the dataset object """
        from solvebio import Dataset
        if not self.is_dataset:
            raise SolveError(
                "Only dataset objects have a Dataset resource. This is a {}"
                .format(self.object_type))

        return Dataset.retrieve(self['id'], client=self._client)

    @property
    def parent(self):
        """ Returns the parent object """
        if self['parent_object_id']:
            return self.retrieve(self['parent_object_id'], client=self._client)

        return None

    @property
    def vault(self):
        """ Returns the vault object """
        from . import Vault
        return Vault.retrieve(self['vault_id'], client=self._client)

    @property
    def is_dataset(self):
        return self.object_type == 'dataset'

    @property
    def is_folder(self):
        return self.object_type == 'folder'

    @property
    def is_file(self):
        return self.object_type == 'file'

    @property
    def is_shortcut(self):
        return self.object_type == 'shortcut'

    def get_target(self, return_none_target=True):
        if not self.is_shortcut:
            raise SolveError("Only shortcut objects have a target resource. This is a {}".format(self.object_type))
        target = self['target']
        if not target:
            if return_none_target:
                return None
            else:
                raise SolveError("Shortcut target not found.")

        try:
            if target['object_type'] == 'url':
                return target['url']
            elif target['object_type'] == 'vault':
                from . import Vault
                return Vault.retrieve(target['id'], client=self._client)
            else:
                return Object.retrieve(target['id'], client=self._client)
        except SolveError as e:
            if e.status_code == 404:
                raise NotFoundError
            else:
                raise e

    @property
    def data_url(self):
        return '/v2/objects/{}/data'.format(self.solvebio_id)

    def has_tag(self, tag):
        """Return True if object contains tag"""

        def lowercase(x):
            return x.lower()

        return lowercase(str(tag)) in map(lowercase, self.tags)

    def tag(self, tags, remove=False, dry_run=False, apply_save=True):
        """Add or remove tags on an object"""

        def is_iterable_non_string(arg):
            """python2/python3 compatible way to check if arg is an iterable but not string"""

            return isinstance(arg, Iterable) and not isinstance(arg, six.string_types)

        if not is_iterable_non_string(tags):
            tags = [str(tags)]
        else:
            tags = [str(tag) for tag in tags]

        if remove:
            removal_tags = [tag for tag in tags if self.has_tag(tag)]
            if removal_tags:
                print('{}Notice: Removing tags: {} from object: {}'
                      .format('[Dry Run] ' if dry_run else '',
                              ', '.join(removal_tags), self.full_path))

                tags_for_removal = [tag for tag in tags if self.has_tag(tag)]
                updated_tags = [tag for tag in self.tags if tag not in tags_for_removal]
            else:
                print('{}Notice: Object {} does not contain any of the '
                      'following tags: {}'.format(
                          '[Dry Run] ' if dry_run else '',
                          self.full_path, ', '.join(tags)))
                return False
        else:
            new_tags = [tag for tag in tags if not self.has_tag(tag)]
            if new_tags:
                print('{}Notice: Adding tags: {} to object: {}'
                      .format('[Dry Run] ' if dry_run else '',
                              ', '.join(new_tags), self.full_path))
                updated_tags = self.tags + new_tags
            else:
                print('{}Notice: Object {} already contains these tags: {}'
                      .format('[Dry Run] ' if dry_run else '',
                              self.full_path, ', '.join(tags)))
                return False

        if not dry_run and apply_save:
            self.tags = updated_tags
            self.save()

        return True

    def untag(self, tags, dry_run=False, apply_save=True):
        """Remove tags on an object"""

        return self.tag(tags=tags, remove=True, dry_run=dry_run, apply_save=apply_save)

    def query(self, **params):
        """
        Return the Query or QueryFile object depending on object type
        that represents query results against an object.
        """
        from solvebio.resource.dataset import Dataset
        from solvebio.query import QueryFile

        if self.is_dataset:
            return Dataset(self['id'], client=self._client).query(**params)
        elif self.is_file:
            return QueryFile(self['id'], client=self._client, **params)
        else:
            raise SolveError('The functionality is only supported for files and datasets. '
                             'This is a {}.'.format(self.object_type))

    def archive(self, storage_class=None, follow=False):
        """
        Archive this dataset
        """
        if not self.is_dataset:
            raise SolveError("Only dataset objects can be archived.")

        # The default archive storage class is called "Archive"
        if not storage_class:
            storage_class = "Archive"

        # Updating storage class is only available at the objects endpoint
        self.storage_class = storage_class
        self.save()

        if follow:
            self.dataset.activity(follow=True)

    def restore(self, storage_class=None, follow=False, **kwargs):
        """
        Restore this dataset
        """
        if not self.is_dataset:
            raise SolveError("Only datasets can be restored.")

        # By default, datasets will be restored to Standard-IA
        if not storage_class:
            storage_class = "Standard-IA"

        # Updating storage class is only available at the objects endpoint
        self.storage_class = storage_class
        self.save()

        if follow:
            self.dataset.activity(follow=True)

    def enable_global_beacon(self):
        """
        Enable Global Beacon for this object (datasets only).
        """
        if not self.is_dataset:
            raise SolveError("Only dataset objects can be Global Beacons.")

        return self._client.post(self.instance_url() + '/beacon', {})

    def disable_global_beacon(self):
        """
        Disable Global Beacon for this object (datasets only).
        """
        if not self.is_dataset:
            raise SolveError("Only dataset objects can be Global Beacons.")

        return self._client.delete(self.instance_url() + '/beacon', {})

    def get_global_beacon_status(self, raise_on_disabled=False):
        """
        Retrieves the Global Beacon status for this object (datasets only).
        """
        if not self.is_dataset:
            raise SolveError("Only dataset objects can be Global Beacons.")

        try:
            return self._client.get(self.instance_url() + '/beacon', {})
        except SolveError:
            if raise_on_disabled:
                raise
            return None

    def list_versions(self, include_deleted=True):
        """
        Returns all the versions for this object.
        Only file objects can have versions.
        """
        if not self.is_file:
            raise SolveError("Only file objects can have versions.")

        _client = self._client
        url = self.instance_url() + '/versions'
        params = {"show_deleted": include_deleted}
        response = _client.get(url, params)
        results = convert_to_solve_object(response, client=_client)
        # set up tabulate:
        if len(results.data) > 0:
            list_fields = getattr(results.data[0], 'LIST_FIELDS', None)
            if list_fields:
                fields, headers = list(zip(*list_fields))
                results.set_tabulate(fields, headers=headers, sort=False)
        return results

    def delete_version(self, version_id):
        """
        Marks the specified version as deleted.
        Only file objects can have versions.
        """
        if not self.is_file:
            raise SolveError("Only file objects can have versions.")

        url = self.instance_url() + '/versions/{}'.format(version_id)
        return self._client.delete(url, {})

    def undelete_version(self, version_id):
        """
        Marks the specified version as not deleted.
        Only file objects can have versions.
        """
        if not self.is_file:
            raise SolveError("Only file objects can have versions.")

        url = self.instance_url() + '/versions/{}'.format(version_id)
        return self._client.request('PUT', url)

    def restore_version(self, version_id):
        """
        Sets the current version to the specified version.
        This is done by creating a new version with the same content as the specified version.
        Only file objects can have versions.
        """
        if not self.is_file:
            raise SolveError("Only file objects can have versions.")

        url = self.instance_url() + '/versions/current'
        data = {"version_id": version_id}
        return self._client.post(url, data=data)
