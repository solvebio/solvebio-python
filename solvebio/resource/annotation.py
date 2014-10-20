"""Solvebio Annotation API Resource"""
from .apiresource import CreateableAPIResource, ListableAPIResource, \
    SingletonAPIResource


class Annotation(CreateableAPIResource, ListableAPIResource,
                 SingletonAPIResource):
    """
    Annotations are genomic samples that have been annotated.
    See https://www.solvebio.com/docs/api/?python#annotations
    """
