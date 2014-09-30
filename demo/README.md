# Intro

SolveBio aims to provide robust access to highly curated biological datasets. While our datasets do not conform to any proprietary formats, they are organized in a systematic way.

*Depositories* (data repositories) are simply versioned containers of datasets

A depository contains many versions, which in turn contain many datasets. Each dataset represents an independent “datastore”. Datasets store semi-structured data similar to typical “NoSQL” databases.

The [depository folder](https://github.com/solvebio/solvebio-python/blob/demos/demo/depository) has examples involving retrieving, getting version information or listing depositories.

*Datasets* are access points to data. Dataset names are unique within versions of a depository. The
[dataset folder](https://github.com/solvebio/solvebio-python/blob/demos/demo/dataset) has programs for retrieving properties of a dataset.

However, issuing queries on a dataset is probably what you will most want to do. The [query folder](https://github.com/solvebio/solvebio-python/blob/demos/demo/query) contains examples of queries.
