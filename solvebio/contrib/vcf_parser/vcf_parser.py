# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from vcf.parser import VCFReader


class ExpandingVCFParser(object):
    """
    Expands multiple alleles in a VCF record to one row per allele.

    Please note that this parser DOES NOT include the reference allele
    as a record. Also, no validation/conversion is done for chromosome,
    or allele fields.

    Requires PyVCF 0.6.8+ (pip install PyVCF).
    """
    DEFAULT_BUILD = 'GRCh37'

    def __init__(self, infile, **kwargs):
        self._file = infile
        self._line_number = -1
        self._reader = None
        self._next = []
        self.genome_build = kwargs.get('genome_build', 'GRCh37')
        self.reader_class = kwargs.get('reader_class', VCFReader)
        self.reader_kwargs = kwargs.get(
            'reader_kwargs', {'strict_whitespace': True})

    @property
    def reader(self):
        if not self._reader:
            self._file.seek(0)
            # Add 'strict_whitespace' kwarg to force PyVCF to split
            # on '\t' only. This enables proper handling
            # of INFO fields with spaces.
            self._reader = self.reader_class(
                self._file,
                **self.reader_kwargs
            )
        return self._reader

    @property
    def file(self):
        return self._file

    def close(self):
        self._file.close()

    def __iter__(self):
        return self

    def __enter__(self):
        """For use as a context manager"""
        return self

    def __exit__(self, *args):
        self.close()
        return False

    def next(self):
        """
        Expands multiple alleles into one record each
        using an internal buffer (_next).
        """

        def _alt(alt):
            """Parses the VCF row ALT object."""
            # If alt is '.' in VCF, PyVCF returns None, convert back to '.'
            if not alt:
                return '.'
            else:
                return str(alt)

        if not self._next:
            row = self.reader.next()
            alternate_alleles = map(_alt, row.ALT)

            for allele in alternate_alleles:
                self._next.append(
                    self.row_to_dict(
                        row,
                        allele=allele,
                        alternate_alleles=alternate_alleles))

            # Source line number, only increment if reading a new row.
            self._line_number += 1

        return self._next.pop()

    def row_to_dict(self, row, allele, alternate_alleles):
        """Return a parsed dictionary for JSON."""

        def _variant_sbid(**kwargs):
            """Generates a SolveBio variant ID (SBID)."""
            return '{build}-{chromosome}-{start}-{stop}-{allele}'\
                .format(**kwargs).upper()

        if allele == '.':
            # Try to use the ref, if '.' is supplied for alt.
            allele = row.REF or allele

        return {
            'genomic_coordinates': {
                'build': self.genome_build,
                'chromosome': row.CHROM,
                'start': row.POS,
                'stop': row.POS + len(row.REF) - 1
            },
            'allele': allele,
            'row_id': row.ID,
            'reference_allele': row.REF,
            'alternate_alleles': alternate_alleles,
            'info': row.INFO,
            'qual': row.QUAL,
            'filter': row.FILTER
        }

if __name__ == '__main__':
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python {0} sample.vcf".format(sys.argv[0]))
        sys.exit(1)

    infile = open(sys.argv[1], 'rb')
    for row in ExpandingVCFParser(infile, genome_build='GRCh37'):
        print(json.dumps(row))

    sys.exit(0)
