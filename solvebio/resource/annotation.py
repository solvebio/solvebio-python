"""Solvebio Annotation API Resource"""
from ..client import client

from .util import json
from .solveobject import convert_to_solve_object
from .resource import APIResource

class Annotation(APIResource):
    """
    Annotations are genomic samples that have been annotated.
    See https://www.solvebio.com/docs/api/?python#annotations
    """
    @classmethod
    def retrieve(cls, id):
        "Retrieves a specific annotation by ID."
        response = client.request('get', cls(id).instance_url())
        return convert_to_solve_object(response)

    @classmethod
    def all(cls):
        "Lists all annotations (that you have access to) in a paginated form"
        response = client.request('get', Annotation.class_url())
        return convert_to_solve_object(response)

    @classmethod
    def create(cls, **params):
        "Creates a new annotation for the specified sample."
        response = client.request('post', Annotation.class_url(), params)
        return response
        return convert_to_solve_object(response)

    def instance_url(self):
        return '{0}/{1}'.format(self.class_url(), self.id)

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)
