"""Solvebio Task API Resource"""
from .apiresource import ListableAPIResource


class Task(ListableAPIResource):
    """
    Tasks are operations on datasets or vaults.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('task_display_name', 'Task Type'),
        ('task_id', 'Task ID'),
        ('description', 'Description'),
        ('status', 'Status'),
        ('created_at', 'Created'),
    )

    def follow(self):
        # Get object status but do not loop
        self.child_object().follow(loop=False)

    def child_object(self):
        from solvebio.resource import types
        child_klass = types.get(self.task_type.split('.')[1])
        return child_klass.retrieve(self.task_id)
