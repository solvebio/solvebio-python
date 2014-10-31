from solvebio.resource import Depository, DepositoryVersion

from .helper import SolveBioTestCase


class DepositoryTests(SolveBioTestCase):
    """
    Test Depository and DepositoryVersions.
    """

    def test_depositories(self):
        depos = Depository.all()
        depo = depos.data[0]
        self.assertTrue('id' in depo,
                        'Should be able to get id in deposiory')

        depo2 = Depository.retrieve(depo.id)
        self.assertEqual(depo, depo2,
                         "Retrieving dataset id {0} found by all()"
                         .format(depo.id))

        check_fields = set(['class_name', 'created_at',
                            'description', 'external_resources',
                            'full_name', 'id',
                            'is_private', 'is_restricted',
                            'latest_version',
                            'latest_version_id',
                            'name', 'title', 'updated_at',
                            'url', 'versions_count', 'versions_url'])

        self.assertSetEqual(set(depo), check_fields)

        depo_version_id = depo.versions().data[0].id
        depo_version = DepositoryVersion.retrieve(depo_version_id)

        check_fields = set(['class_name', 'created_at',
                            'datasets_url', 'depository',
                            'depository_id', 'description',
                            'full_name', 'id', 'latest',
                            'name', 'released', 'released_at',
                            'title', 'updated_at', 'url'])

        self.assertSetEqual(set(depo_version), check_fields)
