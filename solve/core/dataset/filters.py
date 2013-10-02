"""
Solve Filters
^^^^^^^^^^^^^

Each set of kwargs in a `Filter` are ANDed together:

* `<field>=''` uses a term filter (exact term)
* `<field>__in=[]` uses a terms filter (match any)

String terms are not analyzed and are always assumed to be exact matches.

Numeric columns can be selected by range using:

    * `<field>__gt`: greater than
    * `<field>__gte`: greater than or equal to
    * `<field>__lt`: less than
    * `<field>__lte`: less than or equal to

Examples:

    result_set = TCGA.somatic_mutations.select(gene__in=['BRCA', 'GATA3'],
                                               chr='3',
                                               start__gt=10000,
                                               end__lte=20000)


Range lookups:


SNV lookups (where start == end):

    lo [           *   ] hi

    start_position >= lo AND end_position <= hi


CNV lookups (start != end):

We should allow for overlap detection in these cases.

    lo [       ******   ] hi
       [          ******]***
    ***[*****           ]


    start_position >= lo AND start_position <= hi
    OR (if allow_overlap... otherwise AND)
    end_position >= lo AND end_position <= hi


The `select` function returns a "lazy" SolveSelect statement which is a
class-based query builder that can generate a JSON query string.

"""
import copy


class Filter(object):
    """
    Filter objects.

    Makes it easier to create filters cumulatively using ``&`` (and),
    ``|`` (or) and ``~`` (not) operations.

    For example::

        f = F()
        f &= F(price='Free')
        f |= F(style='Mexican')

    creates a filter "price = 'Free' or style = 'Mexican'".

    """
    def __init__(self, **filters):
        """Creates a Filter"""
        filters = filters.items()
        if len(filters) > 1:
            self.filters = [{'and': filters}]
        else:
            self.filters = filters

    def __repr__(self):
        return '<Filter {0}>'.format(self.filters)

    def _combine(self, other, conn='and'):
        """
        OR and AND will create a new Filter, with the filters from both Filter
        objects combined with the connector `conn`.
        """
        f = Filter()

        self_filters = copy.deepcopy(self.filters)
        other_filters = copy.deepcopy(other.filters)

        if not self.filters:
            f.filters = other_filters
        elif not other.filters:
            f.filters = self_filters
        elif conn in self.filters[0]:
            f.filters = self_filters
            f.filters[0][conn].extend(other_filters)
        elif conn in other.filters[0]:
            f.filters = other_filters
            f.filters[0][conn].extend(self_filters)
        else:
            f.filters = [{conn: self_filters + other_filters}]

        return f

    def __or__(self, other):
        return self._combine(other, 'or')

    def __and__(self, other):
        return self._combine(other, 'and')

    def __invert__(self):
        f = Filter()
        self_filters = copy.deepcopy(self.filters)
        if len(self_filters) == 0:
            f.filters = []
        elif (len(self_filters) == 1
              and isinstance(self_filters[0], dict)
              and self_filters[0].get('not', {}).get('filter', {})):
            f.filters = self_filters[0]['not']['filter']
        else:
            f.filters = [{'not': {'filter': self_filters}}]
        return f


class Range(Filter):
    """
    Range objects.

    Makes it easier to do range filters.

        Range('<field_start>', '<field_end>', start, end, overlaps=True)

    expands to ANDed range filters:

        field_start >= start AND field_start <= end
            (overlaps ? OR : AND)
        field_end >= start AND field_end <= hi

    """
    def __init__(self, field_start, field_end, start, end, overlaps=True):
        super(Range, self).__init__(
            **{
                ('and', 'or')[overlaps]: {
                    field_start + '__range': [start, end],
                    field_end + '__range': [start, end]
                }
            })
