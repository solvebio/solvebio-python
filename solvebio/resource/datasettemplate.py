from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource

from . import DatasetField

import re
import inspect
from itertools import dropwhile


class DatasetTemplate(CreateableAPIResource, ListableAPIResource,
                      UpdateableAPIResource, DeletableAPIResource):
    """
    DatasetTemplates contain the schema of a Dataset, including some
    properties and all the fields.
    """
    RESOURCE = '/v2/dataset_templates'

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('description', 'Description'),
    )

    def __init__(self, *args, **kwargs):
        super(DatasetTemplate, self).__init__(*args, **kwargs)

        self.fields = kwargs.get('fields') or []
        for attr in dir(self):
            if attr.startswith('__'):
                continue

            func = getattr(self, attr, None)
            if getattr(func, "field", None):
                self.fields.append(func.field)

    def get_or_create(self, **params):
        objects = self.all(**params).solve_objects()
        if objects:
            # TODO: Raise exception?
            return objects[0]
        else:
            return self.create(**params)

    @property
    def import_params(self):
        """
        Get DatasetImport parameters from a template
        and format them correctly.
        """
        return {
            'target_fields': self.fields,
            'reader_params': self.reader_params,
            'entity_params': self.entity_params,
            'annotator_params': self.annotator_params,
            'validation_params': self.validation_params
        }

    @staticmethod
    def field(*args, **kwargs):
        def get_function_body(func):
            source_lines = inspect.getsourcelines(func)[0]
            source_lines = dropwhile(lambda x: x.startswith('@'), source_lines)
            source = ''.join(source_lines)
            pattern = re.compile(
                r'(async\s+)?def\s+\w+\s*\(.*?\)\s*:\s*(.*)',
                flags=re.S)
            lines = pattern.search(source).group(2).splitlines()
            if len(lines) == 1:
                body = lines[0]
            else:
                # Dedent the code
                indentation = len(lines[1]) - len(lines[1].lstrip())
                body = '\n'.join(
                    [lines[0]] +
                    [line[indentation:] for line in lines[1:]]
                )

            # Remove any return statement
            return body.replace('return ', '')

        def decorator(f):
            kwargs['name'] = f.__name__
            kwargs['expression'] = get_function_body(f)
            f.field = DatasetField(*args, **kwargs)
            return f

        return decorator
