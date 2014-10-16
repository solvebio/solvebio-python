"""
Annotations are genomic samples that have been annotated.
See https://www.solvebio.com/docs/api/?python#annotations
"""
from ..client import client

from util import class_to_api_name, json
from solveobject import SolveObject, convert_to_solve_object


class Annotation(SolveObject):
    @classmethod
    def class_url(cls):
        "Returns a versioned URI string for this class"
        # FIXME: DRY with other class_url routines
        return "/v1/{0}".format(class_to_api_name(cls.__name__))

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
