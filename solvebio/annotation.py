"""Annotations are genomic samples that have been annotated.
   See https://www.solvebio.com/docs/api/?python#annotations
"""

from client import client
from conversion import class_to_api_name, json
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
        return response

    @classmethod
    def all(cls):
        "Lists all annotations (that you have access to) in a paginated form"
        response = client.request('get', Annotation.class_url())
        return response

    def __init__(self, id=None):
        super(SolveObject, self).__init__()
        self.id = id

    def instance_url(self):
        return '{0}/{1}'.format(self.class_url(), self.id)

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

if __name__ == '__main__':
    # print(Annotation.class_url())
    # print(Annotation.retrieve(1))
    print Annotation.class_url()
    x = Annotation.all()
    # print json
    print str(x)
    if len(x) > 5: print(x[0:5])
