# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from vcf.parser import Reader
from vcf.parser import RESERVED_INFO


class VCFReader(Reader):
    """
    Subclasses the standard PyVCF VCFReader to fix issues with
    parsing quoted INFO fields, as well as issues with NaN fields in VCFs.
    """

    def _parse_info(self, info_str):
        if info_str == '.':
            return {}

        entries = info_str.split(';')
        retdict = {}

        for entry in entries:
            entry = entry.split('=', 1)
            _id = entry[0]
            try:
                entry_type = self.infos[_id].type
            except KeyError:
                try:
                    entry_type = RESERVED_INFO[_id]
                except KeyError:
                    if entry[1:]:
                        entry_type = 'String'
                    else:
                        entry_type = 'Flag'

            if entry_type == 'Integer':
                vals = entry[1].split(',')
                try:
                    val = self._map(int, vals)
                # Allow specified integers to be flexibly parsed as floats.
                # Handles cases with incorrectly specified header types.
                except ValueError:
                    val = self._map(float, vals)
                    # Convert NaN to None. NaN breaks JSON
                    # convertion code downstream.
                    val = map(lambda x: x if x == x else None, val)
            elif entry_type == 'Float':
                vals = entry[1].split(',')
                val = self._map(float, vals)
                # Convert NaN to None. NaN breaks JSON
                # convertion code downstream.
                val = map(lambda x: x if x == x else None, val)
            elif entry_type == 'Flag':
                val = True
            elif entry_type in ('String', 'Character'):
                try:
                    # Support quoted strings (test if string is quoted).
                    if entry[1][0] + entry[1][-1] in ['""', "''"]:
                        val = [entry[1]]
                    else:
                        # Commas are reserved characters indicating
                        # multiple values.
                        vals = entry[1].split(',')
                        val = self._map(str, vals)
                except IndexError:
                    entry_type = 'Flag'
                    val = True
            try:
                if self.infos[_id].num == 1 and entry_type not in ('Flag',):
                    val = val[0]
            except KeyError:
                pass

            retdict[_id] = val

        return retdict


class ExpandingVCFParser(object):
    """
    Expands multiple alleles in a VCF record to one row per allele.

    Please note that this parser DOES NOT include the reference allele
    as a record. Also, no validation/conversion is done for chromosome,
    or allele fields.

    Requires PyVCF 0.6.8+ (pip install PyVCF).
    """
    DEFAULT_BUILD = 'GRCh37'

    def __init__(self, fsock=None, **kwargs):
        self._reader = None
        self._line_number = -1
        self._next = []
        # Default INFO field parser is pass-through
        self._parse_info = lambda x: x
        self.genome_build = kwargs.pop('genome_build', 'GRCh37')
        self.reader_class = kwargs.pop('reader_class', VCFReader)

        self.reader_kwargs = kwargs
        # Set default reader kwargs
        if fsock:
            self.reader_kwargs['fsock'] = fsock
        if 'strict_whitespace' not in self.reader_kwargs:
            self.reader_kwargs['strict_whitespace'] = True

    @property
    def reader(self):
        if not self._reader:
            # Add 'strict_whitespace' kwarg to force PyVCF to split
            # on '\t' only. This enables proper handling
            # of INFO fields with spaces.
            self._reader = self.reader_class(
                **self.reader_kwargs
            )

            # Setup extra INFO field parsing
            if self._reader.metadata.get('SnpEffCmd'):
                # Only proceed if ANN description exists (ANN fields)
                # The field keys may vary between SnpEff versions:
                # http://snpeff.sourceforge.net/VCFannotationformat_v1.0.pdf
                # Here we find them dynamically in the VCF header:
                ann_info = self._reader.infos.get('ANN')
                if ann_info:
                    self._parse_info = self._parse_info_snpeff
                    # The infos['ANN'] description looks like:
                    #    Functional annotations: 'A | B | C'
                    # where A, B, and C are ANN keys.
                    self._snpeff_ann_fields = []
                    for field in ann_info.desc.split('\'')[1].split('|'):
                        # Field names should not contain [. /]
                        self._snpeff_ann_fields.append(
                            field.strip()
                            .replace('.', '_')
                            .replace('/', '_')
                            .replace(' ', ''))

        return self._reader

    def _parse_info_snpeff(self, info):
        """
        Specialized INFO field parser for SnpEff ANN fields.
        Requires self._snpeff_ann_fields to be set.
        """
        ann = info.pop('ANN', []) or []
        # Overwrite the existing ANN with something parsed
        # Split on '|', merge with the ANN keys parsed above.
        # Ensure empty values are None rather than empty string.
        items = []
        for a in ann:
            # For multi-allelic records, we may have already
            # processed ANN. If so, quit now.
            if isinstance(a, dict):
                info['ANN'] = ann
                return info

            values = [i or None for i in a.split('|')]
            item = dict(zip(self._snpeff_ann_fields, values))

            # Further split the Annotation field by '&'
            if item.get('Annotation'):
                item['Annotation'] = item['Annotation'].split('&')

            items.append(item)

        info['ANN'] = items
        return info

    @property
    def file(self):
        return self.reader._reader

    def close(self):
        self.file.close()

    def __enter__(self):
        """For use as a context manager"""
        return self

    def __exit__(self, *args):
        self.close()
        return False

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

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
            row = next(self.reader)
            alternate_alleles = list(map(_alt, row.ALT))

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

        genomic_coordinates = {
            'build': self.genome_build,
            'chromosome': row.CHROM,
            'start': row.POS,
            'stop': row.POS + len(row.REF) - 1
        }

        # SolveBio standard variant format
        variant_sbid = _variant_sbid(allele=allele,
                                     **genomic_coordinates)

        return {
            'genomic_coordinates': genomic_coordinates,
            'variant': variant_sbid,
            'allele': allele,
            'row_id': row.ID,
            'reference_allele': row.REF,
            'alternate_alleles': alternate_alleles,
            'info': self._parse_info(row.INFO),
            'qual': row.QUAL,
            'filter': row.FILTER
        }


if __name__ == '__main__':
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python {0} sample.vcf".format(sys.argv[0]))
        sys.exit(1)

    parser = ExpandingVCFParser(filename=sys.argv[1], genome_build='GRCh37')
    for row in parser:
        print(json.dumps(row))

    parser.close()
    sys.exit(0)
