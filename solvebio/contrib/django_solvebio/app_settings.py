import solvebio
from django.conf import settings

API_KEY = getattr(settings, 'SOLVEBIO_API_KEY', solvebio.api_key)
solvebio.api_key = API_KEY

API_HOST = getattr(settings, 'SOLVEBIO_API_HOST', solvebio.api_host)
solvebio.api_host = API_HOST

DATASETS = getattr(settings, 'SOLVEBIO_DATASETS', {})
DATASET_MODEL = getattr(settings,
                        'SOLVEBIO_DATASET_MODEL',
                        'django_solvebio.Dataset')
