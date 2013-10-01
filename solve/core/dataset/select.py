"""
Solve Select
^^^^^^^^^^^^

The `select` function returns a "lazy" SolveSelect statement which is a
class-based query builder that can generate a JSON query string.

"""
from .filters import Filter
from ..client import client
from ..solvelog import solvelog
from ..utils.printing import red, pretty_int
from ..utils.tabulate import tabulate


class SelectError(Exception):
    """Base class for errors with Solve Select requests."""
    pass


class Select(object):
    """Select API request wrapper.
    Generates JSON for the API call.
    """
    RANGE_ACTIONS = ['gt', 'gte', 'lt', 'lte']

    def __init__(self, namespace, *filters, **kwargs):
        self._namespace = namespace
        self._path = self._path_from_namespace(namespace)
        self._filters = []
        self.filter(*filters, **kwargs)

    def rewind(self):
        self._rows_received = 0
        self._scroll_id = None
        self._row_cache = []

    def filter(self, *filters, **kwargs):
        """
        Returns a new Select instance with the query args combined with
        existing set with AND.

        kwargs are simply passed to a new Filter object and combined to any
        other filters with AND.

        By default, everything is combined using AND. If you provide
        multiple filters in a single filter call, those are ANDed
        together. If you provide multiple filters in multiple filter
        calls, those are ANDed together.

        If you want something different, use the F class which supports
        ``&`` (and), ``|`` (or) and ``~`` (not) operators. Then call
        filter once with the resulting Filter instance.
        """
        self.rewind()

        for f in list(filters):
            if not isinstance(f, Filter):
                solvelog.warning('Filter non-keyword arguments must be Filter objects.')
            else:
                self._filters.append(f)

        if kwargs:
            self._filters += [Filter(**kwargs)]

        return self

    def _path_from_namespace(self, namespace):
        if namespace.startswith('solve.data.'):
            namespace = namespace[11:]
        return namespace.replace('.', '/')

    def __repr__(self):
        """
        Prints a summary of the Select object.
        """
        try:
            sample = SelectResult(self._row_cache[0])
        except IndexError:
            # No results
            return """<Select on %s (empty)>"""
        else:
            return """<Select on %s>

%s

... %s more results.""" % (self._namespace,
                        tabulate([sample.values()], sample.keys()),
                        pretty_int(self._rows_total - 1))

    def _build_query(self):
        qs = {}

        # If there's a scroll_id, attempt to use it
        if self._scroll_id:
            qs = {'scroll_id': self._scroll_id}
        elif self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                qs['filter'] = {'and': filters}
            else:
                qs['filter'] = filters[0]

        return qs

    def _split_field_action(self, s):
        """Takes a string and splits it into field and action

        Example::

        >>> _split_field_action('foo__bar')
        'foo', 'bar'
        >>> _split_field_action('foo')
        'foo', None

        """
        if '__' in s:
            return s.rsplit('__', 1)
        return s, None

    def _process_filters(self, filters):
        """Takes a list of filters and returns JSON

        :arg filters: list of Filters, (key, val) tuples, or dicts

        :returns: list of JSON API filters

        """
        rv = []
        for f in filters:
            if isinstance(f, Filter):
                if f.filters:
                    rv.extend(self._process_filters(f.filters))
                    continue

            elif isinstance(f, dict):
                key = f.keys()[0]
                val = f[key]
                key = key.strip('_')

                if key not in ('or', 'and', 'not', 'filter'):
                    raise SelectError(
                        '%s is not a valid connector' % f.keys()[0])

                if 'filter' in val:
                    filter_filters = self._process_filters(val['filter'])
                    if len(filter_filters) == 1:
                        filter_filters = filter_filters[0]
                    rv.append({key: {'filter': filter_filters}})
                else:
                    rv.append({key: self._process_filters(val)})

            else:
                key, val = f
                key, field_action = self._split_field_action(key)

                # TODO: handle custom filter processing?
                # handler_name = 'process_filter_{0}'.format(field_action)
                # if field_action and hasattr(self, handler_name):
                #     rv.append(getattr(self, handler_name)(
                #             key, val, field_action))

                if key.strip('_') in ('or', 'and', 'not'):
                    connector = key.strip('_')
                    rv.append({connector: self._process_filters(val.items())})

                elif field_action is None:
                    if val is None:
                        rv.append({'missing': {
                                    'field': key, "null_value": True}})
                    else:
                        rv.append({'term': {key: val}})

                elif field_action in ('startswith', 'prefix'):
                    rv.append({'prefix': {key: val}})

                elif field_action == 'in':
                    rv.append({'in': {key: val}})

                elif field_action in self.RANGE_ACTIONS:
                    rv.append({'range': {key: {field_action: val}}})

                elif field_action == 'range':
                    # defaults to inclusive
                    lower, upper = val
                    rv.append({'range': {key: {'gte': lower, 'lte': upper}}})

                else:
                    raise SelectError(
                        '%s is not a valid field action' % field_action)

        return rv

    def total(self):
        """
        Executes search and returns number of results as an integer.

        :returns: integer

        For example:

        >>> s = Select().query(name__prefix='Jimmy')
        >>> count = s.total()

        """
        if not self._scroll_id:
            self.execute()
        return self._rows_total

    def __len__(self):
        """
        Executes search and returns number of cached results.

        :returns: integer

        .. Note::

           This is very different than calling ``.count()``. If you
           call ``.count()`` you get the total number of results
           that will be returned via iteration.
        """
        if not self._scroll_id:
            self.execute()
        return len(self._row_cache)

    def __iter__(self):
        """
        Execute a search and iterate through the result set.
        Once the cached result set is exhausted, repeat search.
        """
        # TODO: should rewind be optional?
        self.rewind()
        return self.execute()

    def __getitem__(self, key):
        """
        Handle indexed lookups of cached rows.
        """
        try:
            if type(key) == slice:
                return [SelectResult(r) for r in self._row_cache[key]]
            else:
                return SelectResult(self._row_cache[key])
        except (KeyError, IndexError):
            print red('Slicing of Select objects is not fully supported. Please iterate instead.')

    def next(self):
        """
        Allows the Select object to be an iterable.
        """
        if len(self._row_cache) == 0:
            if self._rows_received < self._rows_total:
                # If result cache is empty, request more
                self.execute()
            else:
                # no more rows to fetch!
                raise StopIteration
        else:
            return SelectResult(self._row_cache.pop())

    def execute(self):
        """
        Executes select and returns self (Select)

        Always sends a query, regardless of state.

        :returns: the resulting row objects
        """
        # TODO: handle no scroll_id, no rows...
        response = client.post_dataset_select(self._path, self._build_query())
        self._scroll_id = response['scroll_id']
        self._rows_total = response['total']
        self._rows_received += len(response['results'])
        response['results'].reverse()  # setup for pop()ing
        self._row_cache = response['results'] + self._row_cache
        return self


class SelectResult(object):
    ignored_fields = ['uuid', 'file_uuid', 'keys', 'values']

    def __init__(self, obj):
        for k, v in obj.items():
            if k not in self.ignored_fields:
                self.__dict__[k] = v

    def __getitem__(self, name):
        return self.__dict__[name]

    def __repr__(self):
        # return tabulate([self.values()], self.keys())
        return str(self.values())

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()
