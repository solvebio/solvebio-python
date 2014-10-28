"""Test Depository, DepositoryVersions"""
from test_helper import unittest
from solvebio.resource import Depository, DepositoryVersion


class DepoStuffTest(unittest.TestCase):

    def test_depostuff(self):
        depos = Depository.all()
        if depos.total == 0:
            return unittest.skip('no depositories found')
        # print "depos.total %s" % [depos.total]  # compare with ruby
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

if __name__ == "__main__":
    unittest.main()
