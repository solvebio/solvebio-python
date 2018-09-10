# Add common solvebio classes and methods our namespace here so that
# inside the ipython shell users don't have run imports
import solvebio  # noqa
from solvebio import Annotator  # noqa
from solvebio import Application  # noqa
from solvebio import Beacon  # noqa
from solvebio import BeaconSet  # noqa
from solvebio import BatchQuery  # noqa
from solvebio import Dataset  # noqa
from solvebio import DatasetCommit  # noqa
from solvebio import DatasetExport  # noqa
from solvebio import DatasetField  # noqa
from solvebio import DatasetImport  # noqa
from solvebio import DatasetMigration  # noqa
from solvebio import DatasetTemplate  # noqa
from solvebio import Expression  # noqa
from solvebio import Filter  # noqa
from solvebio import GenomicFilter  # noqa
from solvebio import Manifest  # noqa
from solvebio import Object  # noqa
from solvebio import Query  # noqa
from solvebio import SolveClient  # noqa
from solvebio import SolveError  # noqa
from solvebio import User  # noqa
from solvebio import Vault  # noqa
from solvebio import Task  # noqa
from solvebio import VaultSyncTask  # noqa
from solvebio import ObjectCopyTask  # noqa
from solvebio import SavedQuery  # noqa
from solvebio.utils.printing import pager  # noqa

# Add some convenience functions to the interactive shell
from solvebio.cli.auth import login  # noqa
from solvebio.cli.auth import logout  # noqa
from solvebio.cli.auth import whoami  # noqa
from solvebio.cli.auth import get_credentials  # noqa

# Always try to log the user in when launching the shell
if solvebio.api_key:
    login(api_key=solvebio.api_key)
else:
    login()
