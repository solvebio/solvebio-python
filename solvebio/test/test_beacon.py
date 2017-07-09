from __future__ import absolute_import
from solvebio.resource import Dataset

from .helper import SolveBioTestCase


class BeaconTests(SolveBioTestCase):

    def test_beacon_request(self):
        """
        Check that current Clinvar/Variants returns correct
        fields for beacon
        """
        # dataset = Dataset.retrieve('ClinVar/Variants')
        dataset = Dataset.get_by_full_path(
            'solvebio:python_client_testing:'
            '/ClinVar/3.7.0-2015-12-06/Variants',
            force_use_v1=True)

        beacon = dataset.beacon(genome_build='GRCh37',
                                chromosome='6',
                                # coordinate=50432798,  # prod
                                coordinate=51612854,  # staging
                                allele='G', force_use_v1=True)

        check_fields = ['query', 'exist', 'total']

        for f in check_fields:
            self.assertTrue(f in beacon)

        """
        Check that Clinvar/Variants version 3.7.0-2015-12-06
        returns true for specific case
        """

        dataset = Dataset.get_by_full_path(
            'solvebio:python_client_testing:'
            'ClinVar/3.7.0-2015-12-06/Variants',
            force_use_v1=True)

        beacontwo = dataset.beacon(genome_build='GRCh37',
                                   chromosome='13',
                                   coordinate=113803460,
                                   allele='T', force_use_v1=True)

        self.assertTrue(beacontwo['exist'])
        self.assertEqual(beacontwo['total'], 1)
