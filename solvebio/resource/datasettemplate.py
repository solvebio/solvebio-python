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
        self.fields = self.__init_fields(**kwargs)

    @classmethod
    def __init_fields(cls, *args, **kwargs):
        fields = kwargs.get("fields") or []
        for attr in dir(cls):
            if attr.startswith("__"):
                continue

            func = getattr(cls, attr, None)
            if getattr(func, "field", None):
                fields.append(func.field)

        return fields

    @classmethod
    def create(cls, **params):
        params["fields"] = cls.__init_fields(**params)
        return super(DatasetTemplate, cls).create(**params)

    @classmethod
    def get_or_create_by_name(cls, name, **params):
        objects = cls.all(name=name, **params).solve_objects()
        if objects:
            return objects[0]

        return cls.create(name=name, **params)

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
            # Remove comments
            source = re.sub(r'(?m)^ *#.*\n?', '', source)
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
