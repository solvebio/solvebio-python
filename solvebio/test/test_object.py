from __future__ import absolute_import

import uuid

import mock

from .helper import SolveBioTestCase
from solvebio.test.client_mocks import fake_object_create, fake_object_save
from solvebio.test.client_mocks import fake_dataset_create


class ObjectTests(SolveBioTestCase):

    def test_object_paths(self):
        vaults = self.client.Vault.all()
        for vault in vaults:
            for file_ in list(vault.ls().solve_objects())[:5]:
                o_path, _ = self.client.Object.validate_full_path(
                    file_.full_path)
                self.assertEqual(o_path, file_.full_path)

                # assert path is gettable
                self.client.Object.get_by_full_path(o_path)

        with self.assertRaises(Exception):
            self.client.Object.get_by_full_path('what/is/this')

    def test_object_output(self):

        case = 'acme:myVault/uploads_folder'
        expected = 'acme:myVault:/uploads_folder'
        p, path_dict = self.client.Object.validate_full_path(case)

        self.assertEqual(p, expected)
        self.assertEqual(path_dict['full_path'], expected)
        self.assertEqual(path_dict['path'], '/uploads_folder')
        self.assertEqual(path_dict['parent_path'], '/')
        self.assertEqual(path_dict['parent_full_path'], 'acme:myVault:/')
        self.assertEqual(path_dict['filename'], 'uploads_folder')
        self.assertEqual(path_dict['domain'], 'acme')
        self.assertEqual(path_dict['vault'], 'myVault')
        self.assertEqual(path_dict['vault_full_path'], 'acme:myVault')

    def test_object_path_cases(self):

        user = self.client.User.retrieve()
        domain = user.account.domain
        user_vault = '{0}:user-{1}'.format(domain, user.id)
        test_cases = [
            ['acme:myVault:/uploads_folder', 'acme:myVault:/uploads_folder'],
            ['acme:myVault/folder1/project: ABCD',
             'acme:myVault:/folder1/project: ABCD'],
            ['myVault/folder1/project: ABCD',
             '{0}:myVault:/folder1/project: ABCD'.format(domain)],
            ['myVault:/uploads_folder', '{0}:myVault:/uploads_folder'.format(domain)],  # noqa
            # New full path formats
            ['~/uploads_folder', '{0}:/uploads_folder'.format(user_vault)],
            ['~/', '{0}:/'.format(user_vault)],
            ['myVault/uploads_folder', '{0}:myVault:/uploads_folder'.format(domain)],  # noqa
            ['acme:myVault/uploads_folder', 'acme:myVault:/uploads_folder'],
        ]
        for case, expected in test_cases:
            p, _ = self.client.Object.validate_full_path(case)
            self.assertEqual(p, expected)

        error_test_cases = [
            '',
            '/hello',
            'myVault',
            'oops:myDomain:myVault',
            '{0}:myVault'.format(domain),
            'acme:myVault'
        ]
        for case in error_test_cases:
            with self.assertRaises(Exception):
                v, v_paths = self.client.Object.validate_full_path(case)

    def test_object_path_cases_with_overrides(self):
        user = self.client.User.retrieve()
        domain = user.account.domain
        user_vault = '{0}:user-{1}'.format(domain, user.id)

        test_cases = [
            'acme:myVault:/folder',
            'myVault:/folder',
            'myVault/folder',
            '/folder',
        ]

        for case in test_cases:
            p, _ = self.client.Object.validate_full_path(case, vault='foobar')
            expected = '{0}:foobar:/folder'.format(domain)
            self.assertEqual(p, expected)

            p, _ = self.client.Object.validate_full_path(case, vault='foo:bar')
            expected = 'foo:bar:/folder'
            self.assertEqual(p, expected)

            p, _ = self.client.Object.validate_full_path(
                case, vault='foo:bar', path='/baz')
            expected = 'foo:bar:/baz'
            self.assertEqual(p, expected)

            p, _ = self.client.Object.validate_full_path(
                case, vault='foo:bar', path='/baz/bon')
            expected = 'foo:bar:/baz/bon'
            self.assertEqual(p, expected)

        # Test cases where just the path changes
        case = 'acme:myVault:/folder'
        p, _ = self.client.Object.validate_full_path(case, path='foo/bar/baz')
        expected = 'acme:myVault:/foo/bar/baz'
        self.assertEqual(p, expected)

        case = '~/folder'
        p, _ = self.client.Object.validate_full_path(case, path='foo/bar/baz')
        expected = '{0}:/foo/bar/baz'.format(user_vault)
        self.assertEqual(p, expected)

    @mock.patch('solvebio.resource.Object.create')
    def test_object_has_tag(self, ObjectMock):
        ObjectMock.side_effect = fake_object_create

        tags = ["foo", "bar", "BIZ"]
        obj = self.client.Object.create(name='blah', tags=tags)
        self.assertEqual(obj.tags, tags)
        self.assertTrue(obj.has_tag("FOO"))
        self.assertTrue(obj.has_tag("foo"))
        self.assertTrue(obj.has_tag("BAr"))
        self.assertTrue(obj.has_tag("BAr"))
        self.assertTrue(obj.has_tag("biz"))
        self.assertFalse(obj.has_tag("BAz"))
        self.assertFalse(obj.has_tag("baz"))

        obj = self.client.Object.create(name='blah_untagged')
        self.assertEqual(obj.tags, [])
        self.assertFalse(obj.has_tag("foo"))

    @mock.patch('solvebio.resource.Dataset.create')
    @mock.patch('solvebio.resource.Object.create')
    def test_object_dataset_getattr(self, ObjectCreate, DatasetCreate):
        ObjectCreate.side_effect = fake_object_create
        DatasetCreate.side_effect = fake_dataset_create

        valid_attrs = [
            'lookup', 'beacon',
            'import_file', 'export', 'migrate',
            'fields', 'template', 'imports', 'commits',
            'activity', 'saved_queries'
        ]

        ds = self.client.Dataset.create(name='foo')
        ds_obj = self.client.Object.create(name='foo_dataset',
                                           object_type='dataset')
        file_ = self.client.Object.create(name='foo_file',
                                          object_type='file')
        folder_ = self.client.Object.create(name='foo_folder',
                                            object_type='folder')
        for attr in valid_attrs:
            self.assertTrue(getattr(ds, attr))
            self.assertTrue(getattr(ds_obj, attr))
            with self.assertRaises(AttributeError):
                getattr(file_, attr)
            with self.assertRaises(AttributeError):
                getattr(folder_, attr)

        # Test that any old attr doesnt work
        fake_attr = 'foobar'
        for obj in [file_, folder_, ds, ds_obj]:
            with self.assertRaises(AttributeError):
                getattr(obj, fake_attr)

    @mock.patch('solvebio.resource.Object.create')
    @mock.patch('solvebio.resource.Object.save')
    def test_object_remove_tag(self, ObjectCreate, ObjectSave):
        ObjectCreate.side_effect = fake_object_create
        ObjectSave.side_effect = fake_object_save

        tags = ['tag1', 'tag2', 'tag3']
        file_ = self.client.Object.create(filename='foo_file',
                                          object_type='file',
                                          tags=tags)
        for tag in tags:
            self.assertTrue(file_.has_tag(tag))

        tags_for_removal = ['tag1', 'tag2']
        file_.tag(tags=tags_for_removal, remove=True, apply_save=True)

        # test that given tags are removed
        for tag in tags_for_removal:
            self.assertFalse(file_.has_tag(tag))

        updated_tags = [tag for tag in tags if tag not in tags_for_removal]

        # test that tags which have not been removed are still there
        for tag in updated_tags:
            self.assertTrue(file_.has_tag(tag))

    @mock.patch('solvebio.resource.Object.create')
    @mock.patch('solvebio.resource.Object.save')
    def test_object_untag(self, ObjectCreate, ObjectSave):
        ObjectCreate.side_effect = fake_object_create
        ObjectSave.side_effect = fake_object_save

        tags = ['tag1', 'tag2', 'tag3']
        file_ = self.client.Object.create(filename='foo_file',
                                          object_type='file',
                                          tags=tags)
        for tag in tags:
            self.assertTrue(file_.has_tag(tag))

        tags_for_untagging = ['tag1', 'tag2']
        file_.untag(tags=tags_for_untagging, apply_save=True)

        # test that given tags are untagged
        for tag in tags_for_untagging:
            self.assertFalse(file_.has_tag(tag))

        updated_tags = [tag for tag in tags if tag not in tags_for_untagging]

        # test that tags which have not been untagged are still there
        for tag in updated_tags:
            self.assertTrue(file_.has_tag(tag))

    @mock.patch('solvebio.resource.Object.create')
    @mock.patch('solvebio.resource.Object.save')
    def test_object_add_tag_non_iterable_or_string(self, ObjectCreate, ObjectSave):
        ObjectCreate.side_effect = fake_object_create
        ObjectSave.side_effect = fake_object_save

        # test that a string is added propery
        tags = 'tag1'
        file_ = self.client.Object.create(filename='foo_file',
                                          object_type='file')
        file_.tag(tags)
        self.assertTrue(file_.has_tag(tags))

        # test that non iterable (e.g. integer) added properly
        tags = 1
        file_.tag(tags)
        self.assertTrue(file_.has_tag(tags))

    def test_object_set_metadata(self):
        folder = self.client.Object.\
            get_or_create_by_full_path('~/{}'.format(uuid.uuid4()), object_type='folder')
        metadata = folder.metadata

        metadata['foo_1'] = 'bar_1'
        folder.save()

        # Test that item has been set successfully
        self.assertTrue(metadata.get('foo_1') == 'bar_1')

        metadata = {'foo_2': 'bar_2'}
        self.assertTrue(metadata.get('foo_2') == 'bar_2')

        # Test that direct assignement overrides SolveBio object type with the given dictionary
        self.assertTrue(len(metadata) == 1 and
                        metadata.pop('foo_2') == 'bar_2' and
                        len(metadata) == 0)

        folder.delete(force=True)

    def test_object_set_metadata_empty_dict_list(self):
        folder = self.client.Object. \
            get_or_create_by_full_path('~/{}'.format(uuid.uuid4()), object_type='folder')

        folder.metadata['foo'] = 'bar'
        folder.save()

        folder.metadata = {}
        folder.save()

        # Test that 'metadata' is an empty dict
        self.assertTrue(folder.metadata == {})

        folder.metadata = []
        folder.save()

        # Test that 'metadata' is an empty list
        self.assertTrue(folder.metadata == [])

        folder.delete(force=True)

    def test_object_serialize_metadata(self):
        tpl = self.client.DatasetTemplate()
        tpl.name = "test"
        res = tpl.serialize(tpl)
        self.assertEqual(res, {'name': 'test'})

        tpl.metadata = {"hello": "world"}
        res = tpl.serialize(tpl)
        self.assertEqual(res, {'metadata': {'hello': 'world'}, 'name': 'test'})

    @mock.patch('solvebio.resource.Object.create')
    @mock.patch('solvebio.client.SolveClient.post')
    def test_object_query(self, SolveClientPost, ObjectCreate):
        ObjectCreate.side_effect = fake_object_create
        valid_response = {
            'took': 100,
            'total': 2,
            'results': [{'foo': 1}, {'bar': 2}]
        }

        file = self.client.Object.create(filename='foo_file.json',
                                         object_type='file',
                                         size=100)
        from .. import SolveClient
        file._client = SolveClient()

        SolveClientPost.return_value = valid_response
        resp = file.query()

        self.assertEqual(list(resp), valid_response['results'])
