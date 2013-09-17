"""
Solve Select
^^^^^^^^^^^^

The `select` function returns a "lazy" SolveSelect statement which is a
class-based query builder that can generate a JSON query string.

"""
from .filters import Filter
from ..client import client


class SolveSelectError(Exception):
    """Base class for errors with Solve Select requests."""
    pass


class InvalidFieldActionError(SolveSelectError):
    """Raise this when the field action doesn't exist"""
    pass


class Select(object):
    """A lazy Select API request.

    Does not get evaluated until forced to by iterating or doing a len().

    Generates JSON for the API call.
    """
    RANGE_ACTIONS = ['gt', 'gte', 'lt', 'lte']

    def __init__(self, namespace):
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
        filter once with the resulting F instance.
        """
        self._results_cache = None
        self._namespace = namespace
        self._path = self._path_from_namespace(namespace)
        self.filters = []

    def filter(self, *filters, **kwargs):
        self.filters = list(filters)
        if kwargs:
            self.filters += [Filter(**kwargs)]
        return self

    def _path_from_namespace(self, namespace):
        if namespace.startswith('solve.data.'):
            namespace = namespace[11:]
        return namespace.replace('.', '/')

    def __repr__(self):
        try:
            return '<Select {0}>'.format(repr(self._build_query()))
        except RuntimeError:
            # This happens when you're debugging _build_query and try
            # to repr the instance you're calling it on. Then that
            # calls _build_query and ...
            return repr(self.filters)

    def _build_query(self):
        qs = {}
        if not self.filters:
            return qs

        filters = self._process_filters(self.filters)
        if len(filters) > 1:
            qs['filter'] = {'and': filters}
        else:
            qs['filter'] = filters[0]

        # if self.start:
        #     qs['from'] = self.start
        # if self.stop is not None:
        #     qs['size'] = self.stop - self.start
        # print qs
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
                    raise InvalidFieldActionError(
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
                    raise InvalidFieldActionError(
                        '%s is not a valid field action' % field_action)

        return rv

    def __iter__(self):
        pass

    def __len__(self):
        """
        Executes search and returns the number of results you'd get.

        Executes search and returns number of results as an integer.

        :returns: integer

        For example:

        >>> s = Select().query(name__prefix='Jimmy')
        >>> count = len(s)
        >>> results = s().execute()
        >>> count = len(results)
        True

        .. Note::

           This is very different than calling ``.count()``. If you
           call ``.count()`` you get the total number of results
           that Elasticsearch thinks matches your search. If you call
           ``len(s)``, then you get the number of results you'd get
           if you executed the search. This factors in slices and
           default from and size values.

        """
        return len(self._do_search())

    def count(self):
        """
        Executes search and returns number of results as an integer.

        :returns: integer

        For example:

        >>> s = Select().query(name__prefix='Jimmy')
        >>> count = s.count()

        """
        if self._results_cache:
            return self._results_cache.count
        else:
            return self[:0]._request()['hits']['total']

    def to_python(self, obj):
        """Converts strings in a data structure to Python types

        It converts datetime-ish things to Python datetimes.

        Override if you want something different.

        :arg obj: Python datastructure

        :returns: Python datastructure with strings converted to
            Python types

        .. Note::

           This does the conversion in-place!

        """
        if isinstance(obj, dict):
            for key, val in obj.items():
                obj[key] = self.to_python(val)
        elif isinstance(obj, list):
            return [self.to_python(item) for item in obj]
        return obj

    def _request(self):
        """
        Executes select and returns a `SelectResult` object.

        :returns: `SelectResult` instance

        For example:

        >>> s = Select(chromosome='1')
        >>> results = s.execute()
        """
        if not self._results_cache:
            response = client.post_dataset_select(self._path, self._build_query())
            results = self.to_python(response.json().get('hits', {}).get('hits', []))
            self._results_cache = SelectResult(response, results)
        return self._results_cache


class SelectResult(object):
    """
    After executing a search, this is the class that manages the
    results.

    :property took: the amount of time the search took
    :property count: the total results
    :property response: the raw search response
    :property results: the search results from the response if any

    When you iterate over this object, it returns the individual
    search results in the shape you asked for (object, tuple, dict,
    etc) in the order returned by Elasticsearch.

    Example::

        s = Select(chromosome='1')
        results = s.execute()

        # Shows how long the select took
        print results.took

        # Shows the raw response
        print results.results

    """

    def __init__(self, response, results):
        self.response = response.json()
        self.took = self.response.get('took', 0)
        self.count = self.response.get('hits', {}).get('total', 0)
        self.results = results
        self.set_objects(self.results)

    def set_objects(self, results):
        # key = 'fields' if self.fields else '_source'
        key = '_source'
        self.objects = [decorate_with_metadata(DictResult(r[key]), r)
                        for r in results]

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)


class DictResult(dict):
    pass


def decorate_with_metadata(obj, result):
    """Return obj decorated with result-scope metadata."""
    # Elasticsearch id
    obj._id = result.get('_id', 0)
    # Source data
    obj._source = result.get('_source', {})
    # The search result score
    obj._score = result.get('_score')
    # The document type
    obj._type = result.get('_type')
    # Explanation structure
    obj._explanation = result.get('_explanation', {})
    # Highlight bits
    obj._highlight = result.get('highlight', {})
    return obj


class SelectProcessor(object):
    def __init__(self, json):
        pass
