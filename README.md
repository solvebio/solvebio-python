[![Build Status](https://travis-ci.org/solvebio/solvebio-python.svg?branch=master)](http://travis-ci.org/solvebio/solvebio-python)


SolveBio Python Client
======================

This is the SolveBio Python package and command-line interface (CLI).
This module has been tested on Python 2.6+, Python 3.1+ and PyPy.

For more information about SolveBio visit [solvebio.com](https://www.solvebio.com).


Compatibility
-------------

This version of the Python Client is compatible with Vault-based datasets
only (released on July 28th, 2017).


Dependencies (Ubuntu)
--------------------

When installing SolveBio on Ubuntu (version 14 and up), you may need the
following dependencies:

* libgnutls-dev
* libcurl4-gnutls-dev

To install them, run:

    sudo apt-get install libcurl4-gnutls-dev libgnutls-dev


Guided Installation
-------------------

To use our guided installer, open up your terminal paste this:

    curl -skL install.solvebio.com/python | bash



Manual Installation
-------------------

You may want to first install `gnureadline` and `IPython`:

    pip install gnureadline
    pip install ipython


Install `solvebio` using `pip`:

    pip install solvebio


To log in, type:

    solvebio login

Enter your credentials and you should be good to go!

Just type `solvebio` to enter the SolveBio Python shell or `solvebio tutorial`
for a quick guide on using SolveBio.


Installing from Git
-------------------

    pip install -e git+https://github.com/solvebio/solvebio-python.git#egg=solve



Development
-----------

    git clone https://github.com/solvebio/solvebio-python.git
    cd solve-python/
    python setup.py develop

To run tests use nosetest

    nosetests solvebio.test.test_dataset

Or install tox and run that:

    pip install tox
    tox

To tag new versions:

    git tag `cat solvebio/version.py | cut -d "'" -f 2`
    git push --tags origin master


Migrating to Version 2
----------------------

Version 2 of the Python client removes support for the `Depository` and
`DepositoryVersion` classes, and adds support for the `Vault` and `Object`
classes.

A vault is similar to a filesystem in that it provides a folder-based
hierarchy in which additional folders, files, and SolveBio Datasets can be
stored.  The folders, files, and SolveBio Datasets in a vault are
collectively referred to as "objects" and can be accessed using the
`Vault` or `Object` classes.

Vaults have an advanced permission model that provides for three different
levels of access: read, write, and admin.  Permissions are settable through
the SolveBio UI.  For detailed information on the permission model, please
visit this link:

https://support.solvebio.com/hc/en-us/articles/227732207

As part of the migration onto Version 2, SolveBio has automatically applied
the permissions set on Depositories to the new Vaults which we have created to
replace them.

It is likely that any scripts you have written which utilize the
Python client will need to be modified to be compatible with Version 2.
Below is an exhaustive list of all the things that have changed in the
user-facing methods of the client.  If you encounter any issues migrating
your code, please submit a support ticket and we would be happy to assist you.

### Naming Conventions

It is useful to know the different names for the various entities (or combined
entities) that are available via the Client.  The naming conventions are
as follows:

```

solvebio:public:/ClinVar/3.7.0-2015-12-06/Variants-GRCh37
+------+
(1)
         +----+
         (2)
+-------------+
(3)
                +---------------------------------------+
                (4)
                                          +-------------+
                                          (5)
+-------------------------------------------------------+
(6)
```
```
(1) - Account Domain
(2) - Vault Name
(3) - Vault Full Path
(4) - Object Path
(5) - Object Filename
(6) - Object Full Path

```

### Changes in V2

1. Dataset creation changes

```
Old: Dataset.get_or_create_by_full_name(full_name)
New: Dataset.get_or_create_by_full_path(account_domain:vault_name:/parent/path/dataset_name)
```

For example, if you belong to the "acme" domain, then to create a dataset
named named "EGFR_analysis" in the "/July-2017" folder of the "Research" vault,
make the following call:

```
Dataset.get_or_create_by_full_path('Research:/July_2017/EGFR_analysis')
Dataset.get_or_create_by_full_path('Acme:Research:/July_2017/EGFR_analysis')
```

If you wish to auto-create the vault, add the `create_vault=True` flag.
If you wish to auto-create the folder(s), add the `create_folders=True` flag.

You can optionally leave off the account domain in front, but note that this
will not work if your object path includes a colon:

```
Dataset.get_or_create_by_full_path('Research:/July_2017/EGFR_analysis')
```

If you wish to automatically create the vault if it does not exist, add the
`create_vault=True` flag.

2.  Dataset retrieval changes

A dataset's "full_path" is a triplet consisting of account domain, vault
name, and the dataset's path in the vault (see above).  Retrieval of a dataset
by its full path can be performed in a single call:

```
Dataset.get_by_full_path("account_domain:vault_name:object_path")
Dataset.get_by_full_path("solvebio:public:/ICGC/3.0.0-23/Donor")
```

In order to get the full path of an existing dataset, search for datasets
within a vault.

```
# Get all of the Clinvar datasets that are version 3 and above
v = Vault.get_by_full_path('solvebio:public')
v.datasets(query='Clinvar/3')
```

3.  Removal of `genome_build` filter

The `genome_build` field on the Dataset entity is no longer a supported
filter.  The genome build of public datasets is now indicated in the dataset
name, e.g. `Variants-GRCh38`.

```
Dataset.get_by_full_path("solvebio:public:/ClinVar/3.7.0-2015-12-06/Variants-GRCh38")
```

4.  Removal of `Depository` and `DepositoryVersion` classes.

`Depository` has been replaced by the `Vault` class.

`DepositoryVersion` was functionality is now provided by the `Object` class.
Objects are files, folders, or SolveBio
Datasets that exist inside a vault.  As part of your account's migration onto
Version 2 of SolveBio, we have automatically moved datasets located in
Depository "X" and DepositoryVersion "Y" to a Vault named "X" and a folder named
"Y".  If the dataset being migrated had the `genome_build` property set, the
dataset was renamed to `$original_name-$genome_build`.  Otherwise, the name
remained unchanged.

5.  Renaming of "objects" to "solve_objects"

The `objects` property of a resource has been renamed `solve_objects`.

6.  The `import` and `create-dataset` command-line utilities now require
`--vault` and `--path` arguments.  The `dataset` argument (`test-dataset`
below) no longer can contain slashes.

```
create-dataset --capacity=small --vault=test --path=/  test-dataset
```

7. Removal of DatasetCommit approval. The `auto_approve`, `is_approved` and
`approved_by` attributes have been removed. The `/approve` endpoint has also
been removed. All commits will be approved automatically.


Vault Browsing
--------------
### Browse

List all the vaults you currently have access to.


```
Vault.all()
```

### Your Personal Vault

Each user has a personal vault that is accessible to that user only.  Other
users cannot list the contents of this vault, cannot access the objects
contained in it, and cannot modify it in any way.  To provide access to
objects stored in your personal vault, you must copy the objects into a
different vault.

Your personal dataset can be retrieved using the following method:

```
Vault.get_personal_vault()
```


### Shortcuts
Browsing the contents of a vault can be easily performed using the following
shortcuts.

First, retrieve a vault:

```
vault = Vault.get_personal_vault()
vault = Vault.get_by_full_path('solvebio:public')
vault = Vault.get_by_full_path('your_account_domain:vault_name')
vault = Vault.get_by_full_path('vault_name')  # Searches inside your account domain
```


Then, call the appropriate method:

```
vault.files()
vault.folders()
vault.datasets()
vault.objects()                 # Includes files, folders, and datasets

vault.files(filename='hello.txt')   # Can pass filters to all of these methods
```


Search for files, folders, and datasets in a vault using the `search` method:

```
vault.search('hello')
vault.search('hello', object_type='folder')
vault.search('hello', object_type='file')
vault.search('hello', object_type='dataset')
```

Creation
--------
```
Vault.get_or_create_by_full_path('acme:test1')
Vault.get_or_create_by_full_path('test1')
```

File Upload
-----------
```
v = Vault.get_personal_vault()
v.upload_file('analysis.tsv', '/')
>>> Notice: Successfully uploaded analysis.tsv to /analysis.tsv
```

Re-uploading the same file to the same path auto-increments the filename on
the server.  This is required because no two objects can have the same full
path.

```
v = Vault.get_personal_vault()
v.upload_file('analysis.tsv', '/')
>>> Notice: Successfully uploaded analysis.tsv to /analysis-1.tsv
```


Deletion
--------

Deletion of any object requires a confirmation from the user.
You can disable this confirmation by passing the `force=True` flag.

```
folder = Object.retrieve(504311238004931284)
folder.delete()
>>> Are you sure you want to delete this object? [y/N] n
>>> Not performing deletion.
```
```
folder.delete(force=True)
```

Enhanced Command-Line File Uploading
------------------------------------

A new command-line method called "upload" has been added.  This method
allows users to upload a file or folder to a vault.  If a folder is
uploaded, calling the "upload" method again will result in a cross-checking
of the local folder and SolveBio folder, and upload/create only the
local files and folders that do not already exist on SolveBio.

```
solvebio upload --vault analysis --path=/july_2017  local/foo/bar
```

This command will create a folder named `/july_2017/bar` in the `analysis`
vault, and upload everything inside `local/foo/bar` on the local machine to
`/july_2017/bar` in that vault.

Note that comparison is performed by filename, not by file content.  Thus, the
"upload" command will never replace a remote file with a local file of the same
name but with updated contents.
