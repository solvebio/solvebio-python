from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest
from django.views.generic.base import View
from django.template import loader, RequestContext, TemplateDoesNotExist

from solvebio.contrib.django_solvebio import SolveBio
from solvebio.errors import SolveError
from solvebio.client import client

import json


class DashboardView(View):
    """
    Renders a SolveBio dashboard (loaded by solvebio.js into an iframe).
    """
    def get(self, request, *args, **kwargs):
        try:
            tpl = loader.get_template(
                'solvebio/{0}.html'.format(kwargs.get('dashboard')))
        except TemplateDoesNotExist:
            return HttpResponseNotFound(
                '<h1>SolveBio dashboard not found</h1>')

        return HttpResponse(tpl.render(RequestContext(request, {})))


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
        params = {p: request.GET.get(p) for p in self.valid_params
                  if p in request.GET}

        if 'filters' in params:
            params['filters'] = json.loads(params['filters'])

        return self._handle_query(params, **kwargs)

    def post(self, request, *args, **kwargs):
        # POST request data must be JSONified
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest(
                json.dumps({'detail': 'Error parsing JSON request body.'},
                           content_type='application/json'))

        params = {p: data.get(p) for p in self.valid_params if p in data}
        return self._handle_query(params, **kwargs)

    def _handle_query(self, params, **kwargs):
        try:
            dataset = SolveBio.get_dataset(kwargs.get('dataset').rstrip('/'))
            # get a raw response to avoid decoding and re-encoding json
            response = client.request('post', dataset._data_url(),
                                      params=params, raw=True)
        except SolveError as e:
            return HttpResponseBadRequest(json.dumps({'detail': str(e)}),
                                          content_type='application/json')

        return HttpResponse(response.content, content_type='application/json')
