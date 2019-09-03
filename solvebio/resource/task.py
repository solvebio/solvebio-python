"""Solvebio Task API Resource"""
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource


class Task(ListableAPIResource, UpdateableAPIResource):
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

    SLEEP_WAIT_DEFAULT = 5.0

    @property
    def child_object(self):
        """ Get Task child object class """
        from . import types
        child_klass = types.get(self.task_type.split('.')[1])
        return child_klass.retrieve(self.task_id, client=self._client)

    def follow(self, sleep_seconds=SLEEP_WAIT_DEFAULT):
        """ Follow the child object but do not loop """
        self.child_object.follow(loop=False, sleep_seconds=sleep_seconds)

    def cancel(self):
        """ Cancel a task """
        _status = self.status
        self.status = "canceled"
        try:
            self.save()
        except:
            # Reset status to what it was before
            # status update failure
            self.status = _status
            raise
