import sys

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
from solvebio.cli.auth import login, logout, whoami, get_credentials  # noqa

# If an API key is set in solvebio.api_key, use that.
# Otherwise, look for credentials in the local file,
# Otherwise, ask the user to log in.
if solvebio.api_key or get_credentials():
    _, solvebio.api_key = whoami()
else:
    login()

if not solvebio.api_key:
    sys.stdout.write("No authentication credentials found.\n")
