"""Solvebio Annotation API Resource"""
from ..client import client
from .apiresource import ListableAPIResource, SingletonAPIResource
from .solveobject import convert_to_solve_object


class Annotation(ListableAPIResource, SingletonAPIResource):
    """
    Annotations are genomic samples that have been annotated.
    See https://www.solvebio.com/docs/api/?python#annotations
    """

    @classmethod
    def create(cls, **params):
        "Creates a new annotation for the specified sample."
        response = client.request('post', Annotation.class_url(), params)
        return convert_to_solve_object(response)
