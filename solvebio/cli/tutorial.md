
     ____        _           ____  _
    / ___|  ___ | |_   _____| __ )(_) ___
    \___ \ / _ \| \ \ / / _ \  _ \| |/ _ \
     ___) | (_) | |\ V /  __/ |_) | | (_) |
    |____/ \___/|_| \_/ \___|____/|_|\___/
                                For Python


# Welcome to the SolveBio Python Tutorial!

First, open the SolveBio Python shell by typing "solvebio".

The SolveBio Shell is based on IPython. When you log in, it will automatically pick up your API key.
You can always type "solvebio.help()" within the shell open up the online documentation.

View this tutorial online: https://www.solvebio.com/docs/python-tutorial


## Navigate the Library


To list all available vaults, run:

    Vault.all()


Vaults are like filesystems on a computer.  They can contain files,
folders, and a special SolveBio-specific object called a Dataset.

To list all datasets from all vaults, run:

    Dataset.all()

To retrieve a dataset by its full path, send your account domain, the vault
name, and the dataset path, all separated by a colon:

    Dataset.get_by_full_path('acme:test-vault:/path/to/my/dataset')

Similarly, to retrieve a publicly available dataset, use the `solvebio`
account domain, the `public` vault, and the appropriate dataset path:

    Dataset.get_by_full_path('solvebio:public:/ICGC/3.0.0-23/Donor')

SolveBio maintains a list of publicly available datasets.  To list them,
run:

    vault = Vault.get_by_full_path('solvebio:public')
    vault.datasets()

You can browse any Vault from the client simply by calling the appropriate
methods on a Vault object:

    vault = Vault.get_by_full_path('solvebio:public')
    vault.files()
    vault.folders()
    vault.datasets()
    vault.ls()  # Includes files, folders, and datatsets


Every user has a dedicated, non-shareable, personal vault which is private
to them.  This vault can be obtained by running:

    vault = Vault.get_personal_vault()
    vault.name
    > 'user-3000'  # This is automatically generated based on your User ID
                   # and cannot be changed.


The objects contained in a vault (files, folders, and datasets) can be
retrieved directly using the Object class, or via the `objects` property of a
Vault instance:

    Object.retrieve(488353213969592764)
    Object.all(path='/1000G')
    Object.all(path='/1000G', vault_id=7205)
    Object.all(path='/1000G', vault_name='public')

    vault = Vault.get_personal_vault()
    vault.objects.all(path='/1000G')
    vault.objects.all(query='GRC')


## Query a Dataset

Every dataset in SolveBio can be queried the same way. You can build queries manually in the Python shell, or use our visual Workbench (https://www.solvebio.com/workbench).

In this example, we will query the latest Variants dataset from ClinVar.

    dataset = Dataset.get_by_full_path('solvebio:public:/ClinVar/3.7.4-2017-01-04/Variants-GRCh38')
    dataset.query()


The "query()" function returns a Python iterator so you can loop through all the results easily.

To examine a single result more closely, you may treat the query response as a list of dictionaries:

    dataset.query()[0]


You can also slice the result set like any other Python list:

    dataset.query()[0:100]


## Filter a Dataset

To narrow down your query, you can filter on any field. For example, to get all variants in ClinVar that are Pathogenic, you would filter on the `clinical_significance` field for "Pathogenic":

    dataset.query().filter(clinical_significance='Pathogenic')


By default, adding more filters will result in a boolean AND query (all filters must match):

    dataset.query().filter(clinical_significance='Pathogenic', review_status='single')


Use the "Filter" class to do more advanced filtering. For example, combine a few filters using boolean OR:

    filters = Filter(clinical_significance='Pathogenic') | Filter(clinical_significance='Benign')
    dataset.query().filter(filters)


## Genomic Datasets

Some SolveBio datasets are suffixed with a genome build (GRCh37, GRCh38,
NCBI36) to indicate they are genomic datasets.  Please ensure that you
are using the dataset whose genomic build is compatible with your other
tools and procedures.

On genomic datasets, you may query by position (single nucleotide) or by range:

    dataset.query().position('chr1', 976629)
    > ...
    dataset.query().range('chr1', 976629, 1000000)
    > ...


Position and range queries return all results that overlap with the specified coordinate(s).
Add the parameter `exact=True` to request exact matches.


    dataset.query().position('chr1', 883516, exact=True)
    > ...
    dataset.query().range('chr9', 136289550, 136289579, exact=True)
    > ...


## Next Steps

For more information on queries and filters, see the API reference: https://docs.solvebio.com/guides/quickstarts/python/
