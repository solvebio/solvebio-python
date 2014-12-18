
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

List all available depositories:

    Depository.all()


Depositories are versioned containers of datasets. There are many versions of each depository, and each version may have one or more datasets.

To list all datasets from all depositories:

    Dataset.all()


Pass "latest=True" to get all the latest versions of each dataset:

    Dataset.all(latest=True)


To retrieve a dataset by its full name ("ClinVar/3.0.0-2014-12-05/Variants"):

    Dataset.retrieve('ClinVar/3.0.0-2014-12-05/Variants')

By leaving out the version (for example: "ClinVar/Variants"), you get a quick shortcut to the latest version of any dataset.
**Be careful here: you should always specify an exact version in your production code**.


## Query a Dataset

Every dataset in SolveBio can be queried the same way. You can build queries manually in the Python shell, or use our visual Workbench (https://www.solvebio.com/workbench).

In this example, we will query the latest Variants dataset from ClinVar.

    dataset = Dataset.retrieve('ClinVar/Variants')
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

Some SolveBio datasets allow querying by genome build. We call these "genomic datasets". To find out if a dataset is genomic, and what genome builds are supported:

    dataset.is_genomic
    > True
    dataset.genome_builds
    > ['GRCh38', 'GRCh37']


By default, build 'GRCh37' will be selected if it is available. If not, the most recent build will be selected by default. To manually select a genome build when querying, specify the build as a query parameter:

    dataset.query(genome_build='GRCh38')


On genomic datasets, you may query by position (single nucleotide) or by range:

    dataset.query(genome_build='GRCh37').position('chr1', 976629)
    > ...
    dataset.query(genome_build='GRCh37').range('chr1', 976629, 1000000)
    > ...


Position and range queries return all results that overlap with the specified coordinate(s).
Add the parameter `exact=True` to request exact matches.


    dataset.query(genome_build='GRCh37').position('chr1', 883516, exact=True)
    > ...
    dataset.query(genome_build='GRCh37').range('chr9', 136289550, 136289579, exact=True)
    > ...


## Next Steps

To learn more about a dataset and its fields, use `dataset.help()`.
For more information on queries and filters, see the API reference: https://www.solvebio.com/docs/api?python


