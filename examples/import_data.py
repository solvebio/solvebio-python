import solvebio

# First create a new dataset with one field defined
# this field contains an entity_type gene which will allow
# for advanced gene querying
fields = [{
    'name': 'gene_symbol',
    'data_type': 'string',
    'entity_type': 'gene',
    'ordering': 0,
    'is_list': None,
    'is_hidden': False,
    'description': 'The HGNC Gene Symbol'
}]

domain = solvebio.User.retrieve()['account']['domain']
dataset_name = '{}:MyFirstDepository/1.1.0/MyFirstDataset'.format(domain)
dataset = solvebio.Dataset.get_or_create_by_full_name(
    full_name=dataset_name,
    is_private=True,
    fields=fields
)

# create a manifest object and a file to it
manifest = solvebio.Manifest()
manifest.add_file('path/to/file.vcf.gz')

# create the import and automatically approve it
imp = solvebio.DatasetImport.create(
    dataset_id=dataset.id,
    manifest=manifest.manifest,
    auto_approve=True)

# prints updates as the data is processed
# and indexed into SolveBio
imp.follow()

#
# you now have data!
#


# lets add another record to it just for fun
# that includes a brand new field
new_record = dict(
    gene_symbol="BRCA2",
    some_new_field="this is a new string field")

imp = solvebio.DatasetImport.create(
    dataset_id=dataset.id,
    data_record=new_record,
    auto_approve=True)

imp.follow()
