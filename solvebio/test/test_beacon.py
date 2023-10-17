from __future__ import absolute_import

from solvebio.test.helper import SolveBioTestCase


class BeaconTests(SolveBioTestCase):

    TEST_DATASET_FULL_PATH = 'quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH38'

    def test_beacon_request(self):
        """
        Check that current Clinvar/Variants returns correct
        fields for beacon
        """
        dataset = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)
        beacon = dataset.beacon(chromosome='6',
                                     coordinate=51612854,  # staging
                                     allele='G')

        check_fields = ['query', 'exist', 'total']

        for f in check_fields:
            self.assertTrue(f in beacon)

        # Check that Clinvar/Variants version 3.7.0-2015-12-06
        # returns true for specific case

        dataset = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)
        beacontwo = dataset.beacon(chromosome='13',
                                   coordinate=113803460,
                                   allele='T')

        self.assertTrue(beacontwo['exist'])
        self.assertEqual(beacontwo['total'], 1)
