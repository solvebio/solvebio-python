"""Solvebio ObjectCopyTask API Resource"""
import time
from .apiresource import ListableAPIResource
from .apiresource import CreateableAPIResource
from .apiresource import UpdateableAPIResource
from .task import Task


class ObjectCopyTask(CreateableAPIResource,
                     ListableAPIResource,
                     UpdateableAPIResource):
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('status', 'Status'),
        ('source_vault_id', 'Source Vault'),
        ('target_vault_id', 'Target Vault'),
        ('source_object_id', 'Source'),
        ('target_object_id', 'Target'),
        ('created_at', 'Created'),
    )

    def follow(self, loop=True, sleep_seconds=Task.SLEEP_WAIT_DEFAULT):
        if self.status == 'queued':
            print("Waiting for Object Copy task (id = {0}) to start..."
                  .format(self.id))

        _status = self.status
        while self.status in ['queued', 'running']:
            if self.status != _status:
                print("Object Copy task is now {0} (was {1})"
                      .format(self.status, _status))
                _status = self.status

            if self.status == 'running':
                print("Object Copy task '{0}' is {1}"
                      .format(self.id, self.status))

            if not loop:
                return

            time.sleep(sleep_seconds)
            self.refresh()

        if self.status == 'completed':
            print("Object Copy task complete!")
