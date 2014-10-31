"""Solvebio Annotation API Resource"""
from .apiresource import CreateableAPIResource, DeletableAPIResource, \
    DownloadableAPIResource, ListableAPIResource


class Annotation(CreateableAPIResource, DeletableAPIResource,
                 DownloadableAPIResource, ListableAPIResource):
    """
    Annotations are genomic samples that have been annotated.
    See https://www.solvebio.com/docs/api/?python#annotations
    """
