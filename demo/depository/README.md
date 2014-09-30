# Depositories

A *depository* (or data repository) is like a source code repository,
but for datasets. Depositories have one or more versions, which in
turn contain one or more datasets. Typically, depositories contain a
series of datasets that are compatible with each other (i.e. they come
from the same data source or project).

Right now, all depositories are curated by the SolveBio team.

* retrieve a depository

    The [retrieve.py](https://github.com/solvebio/solvebio-ruby/blob/demos/demo/depository/retrieve.py) Ruby program shows how to retrieve a single depository

* listing a depository

    The [all.py](https://github.com/solvebio/solvebio-ruby/blob/demos/demo/depository/all.py) Ruby program shows how to list all depositories

* list all versions of a depository

    The [versions-all.py](https://github.com/solvebio/solvebio-ruby/blob/demos/demo/depository/all.py) Ruby program shows how to list all versions
    of a depository

See also the [SolveBio Depository API](https://www.solvebio.com/docs/api/#depositories)
