"""Solvebio API Resource for Samples"""

from .apiresource import DownloadableAPIResource, ListableAPIResource, \
    UploadableAPIResource


class Sample(DownloadableAPIResource, ListableAPIResource,
             UploadableAPIResource):
    """
    Samples are VCF files uploaded to the SolveBio API. We currently
    support uncompressed, extension `.vcf`, and gzip-compressed, extension
    `.vcf.gz`, VCF files. Any other extension will be rejected.
    """
