from __future__ import absolute_import
from solvebio.resource import Dataset
from solvebio.resource import DepositoryVersion

from .helper import SolveBioTestCase


class ChangeLogTests(SolveBioTestCase):

    def test_changelog_dataset(self):
        """
        First check if version 3.7.0-2015-12-06 returns a suitable
        changelog compared to its most current version
        """

        dataset = Dataset.retrieve('ClinVar/3.7.0-2015-12-06/Clinvar')

        clog = dataset.changelog()

        check_fields = ['attributes', 'to_dataset', 'from_dataset', 'fields']

        for f in check_fields:
            self.assertTrue(f in clog)

        """
        Check if changelog between 3.7.0-2015-12-06 and 3.6.0-2015-09-04
        returns
        correct dictionary
        """

        clogtwo = dataset.changelog('3.6.0-2015-09-04')

        final_changelog = {"attributes": {"documents_count": [145359, 157003]},
                           "to_dataset": "ClinVar/3.7.0-2015-12-06/ClinVar",
                           "from_dataset": "ClinVar/3.6.0-2015-09-04/ClinVar",
                           "fields": {"removed": [], "added": ["sbid"],
                                      "changed": {}}}

        self.assertEqual(final_changelog, clogtwo)

    def test_changelog_depository(self):

        """
        Check if changelog between DepositoryVersion Clinvar/3.7.0-2015-12-06
        is correct with most current depository
        """
        depo = DepositoryVersion.retrieve('ClinVar/3.7.0-2015-12-06')

        clogdepo = depo.changelog()

        check_fields = ['to_version', 'from_version', 'datasets']

        for f in check_fields:
            self.assertTrue(f in clogdepo)

        """
        Check if Clinvar/3.7.0-2015-12-06 and Clinvar/3.6.0-2015-09-04 match
        specified changelog
        """

        clogtwo = depo.changelog('3.6.0-2015-09-04')

        final_changelog = {"to_version": "ClinVar/3.7.0-2015-12-06",
                           "from_version": "ClinVar/3.6.0-2015-09-04",
                           "datasets": {"removed": [], "added": ["combined"], "changed": {"clinvar": {"attributes": {"documents_count": [145359, 157003]}, "to_dataset": "ClinVar/3.7.0-2015-12-06/ClinVar", "from_dataset": "ClinVar/3.6.0-2015-09-04/ClinVar", "fields": {"removed": [], "added": ["sbid"], "changed": {}}}, "variants": {"attributes": {"documents_count": [121752, 131904]}, "to_dataset": "ClinVar/3.7.0-2015-12-06/Variants", "from_dataset": "ClinVar/3.6.0-2015-09-04/Variants", "fields": {"removed": [], "added": ["sbid"], "changed": {}}}, "submissions": {"attributes": {"documents_count": [158548, 172006]}, "to_dataset": "ClinVar/3.7.0-2015-12-06/Submissions", "from_dataset": "ClinVar/3.6.0-2015-09-04/Submissions", "fields": {"removed": [], "added": ["sbid"], "changed": {}}}}}}  # noqa
        self.assertEqual(final_changelog, clogtwo)
