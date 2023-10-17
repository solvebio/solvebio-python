from __future__ import absolute_import

from solvebio import Dataset
from solvebio.test.helper import SolveBioTestCase


class AdsTests(SolveBioTestCase):

    def test_asdasd(self):
        #Dataset.get_or_create_by_full_path('quartzbio:Public:/ClinVar/5.2.0-20210110/Variants-GRCH38')

        Dataset.get_or_create_by_full_path("admin-qb-int-dev:test:/ClinVar/5.2.0-20230930/test_dataset_creation")
