SolveBio Import Shortcut Example
======================

Make sure you're using the newest version of SolveBio with `pip install solvebio --upgrade`

The SolveBio Python client provides a simple shortcut to import data.

Your DOMAIN is the subdomain of your SolveBio account. You can find your domain by going to [SolveBio](https://my.solvebio.com/organization/people) - your organization name is your domain.

To run the example commands, download the [example_input.json](https://github.com/solvebio/solvebio-python/blob/master/examples/import/example_input.json) and [example_template.json](https://github.com/solvebio/solvebio-python/blob/master/examples/import/example_template.json) files.

In bash:
```bash
solvebio import DOMAIN:ExampleDepo/1.0.0/ExampleDataset example_input.json --create-dataset --auto-approve
```

If you want to add SolveBio entities to your data, you can with a template file (you can also do it later on the SolveBio web interface).
```
solvebio import DOMAIN:ExampleDepo/1.0.0/ExampleEntityDataset example_input.json --create-dataset --auto-approve --template-file example_template.json
```

To get a full list of the arguments options available, try
```
solvebio import -h
```
