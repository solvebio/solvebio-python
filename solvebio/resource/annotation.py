"""Solvebio Annotation API Resource"""
from .apiresource import CreateableAPIResource, DownloadableAPIResource, \
    ListableAPIResource


class Annotation(CreateableAPIResource, DownloadableAPIResource,
                 ListableAPIResource):
    """
    Annotations are genomic samples that have been annotated.
    See https://www.solvebio.com/docs/api/?python#annotations
    """
