from __future__ import absolute_import

from .helper import SolveBioTestCase


class BeaconTests(SolveBioTestCase):

    def test_beacon_request(self):
        """
        Check that current Clinvar/Variants returns correct
        fields for beacon
        """
        dataset = self.client.Dataset.get_by_full_path(
            'solvebio:public:/ClinVar/3.7.0-2015-12-06/Variants-GRCh37')

        beacon = dataset.beacon(chromosome='6',
                                # coordinate=50432798,  # prod
                                coordinate=51612854,  # staging
                                allele='G')

        check_fields = ['query', 'exist', 'total']

        for f in check_fields:
            self.assertTrue(f in beacon)

        # Check that Clinvar/Variants version 3.7.0-2015-12-06
        # returns true for specific case

        dataset = self.client.Dataset.get_by_full_path(
            'solvebio:public:/ClinVar/3.7.0-2015-12-06/Variants-GRCh37')

        beacontwo = dataset.beacon(chromosome='13',
                                   coordinate=113803460,
                                   allele='T')

        self.assertTrue(beacontwo['exist'])
        self.assertEqual(beacontwo['total'], 1)
