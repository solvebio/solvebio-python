"""Solvebio VaultSyncTask API Resource"""
import time
from .apiresource import ListableAPIResource
from .apiresource import CreateableAPIResource
from .apiresource import UpdateableAPIResource
from .task import Task


class VaultSyncTask(CreateableAPIResource,
                    ListableAPIResource,
                    UpdateableAPIResource):
    RESOURCE = '/v2/vault_sync_tasks'

    LIST_FIELDS = (
        ('id', 'ID'),
        ('status', 'Status'),
        ('vault_id', 'Vault'),
        ('created_at', 'Created'),
    )

    def follow(self, loop=True, sleep_seconds=Task.SLEEP_WAIT_DEFAULT):
        if self.status == 'queued':
            print("Waiting for Vault sync (id = {0}) to start..."
                  .format(self.id))

        _status = self.status
        while self.status in ['queued', 'running']:
            if self.status != _status:
                print("Vault sync is now {0} (was {1})"
                      .format(self.status, _status))
                _status = self.status

            if self.status == 'running':
                print("Vault sync '{0}' is {1}"
                      .format(self.id, self.status))

            if not loop:
                return

            time.sleep(sleep_seconds)
            self.refresh()

        if self.status == 'completed':
            print("Vault complete!")
