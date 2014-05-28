from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.base import View

from solvebio.contrib.django_solvebio import SolveBio
from solvebio.errors import SolveError
from solvebio.client import client

try:
    import json
except ImportError:
    from django.utils import simplejson as json


class DatasetQueryView(View):
    """
    Proxies queries using the Python SolveBio client.
    """
    valid_params = ('mode', 'limit', 'offset', 'debug', 'fields', 'filters')

    def dispatch(self, request, *args, **kwargs):
        if not SolveBio.is_enabled():
            return HttpResponseBadRequest(
                json.dumps({'detail': 'SolveBio is disabled. Please enable it '
                                      'before querying this view.'}),
                content_type='application/json')

        return super(DatasetQueryView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        dataset_name = kwargs.get('dataset').rstrip('/')
        params = {p: request.GET.get(p) for p in self.valid_params
                  if p in request.GET}

        try:
            dataset = SolveBio.get_dataset(dataset_name)
            # get a raw response to avoid decoding and re-encoding json
            response = client.request('post', dataset._data_url(),
                                      params=params, raw=True)
        except SolveError as e:
            return HttpResponseBadRequest(json.dumps({'detail': str(e)}),
                                          content_type='application/json')

        return HttpResponse(response.content, content_type='application/json')
