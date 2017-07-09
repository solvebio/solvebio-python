import solvebio

# find your solvebio domain
solvebio.login()
user = solvebio.User.retrieve()
my_domain = user['account']['domain']

# create a dataset
# TODO - fix this broken example
dataset_name = '{0}:SampleImport/1.0.0/SampleImport'.format(my_domain)
dataset = solvebio.Dataset.get_or_create_by_full_name(dataset_name)

# create a manifest object and a file to it
manifest = solvebio.Manifest()
manifest.add_file('path/to/file.vcf.gz')

# create the import and automatically approve it
imp = solvebio.DatasetImport.create(
    dataset_id=dataset.id,
    manifest=manifest.manifest,
    auto_approve=True)

# Prints updates as the data is processed
# and indexed into SolveBio
imp.follow()

#
# you now have data!
#

# lets add some more records that include a new field
new_records = [
    {
        'gene_symbol': 'BRCA2',
        'some_new_field': 'a new string field'
    },
    {
        'gene_symbol': 'CFTR',
        'some_new_field': 'that new field'
    }
]

imp = solvebio.DatasetImport.create(
    dataset_id=dataset.id,
    data_records=new_records,
    auto_approve=True)

imp.follow()
