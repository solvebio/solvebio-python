import solvebio

solvebio.login()

vault = solvebio.Vault.get_personal_vault()

# The folders that will contain your dataset
path = '/SampleImport/1.0.0'

# The name of your dataset
dataset_name = 'SampleDataset'

# Create a dataset
dataset = solvebio.Object.get_or_create_by_full_path(
    '{0}:/{1}/{2}'.format(vault.name, path, dataset_name),
)

# Create a manifest object and a file to it
manifest = solvebio.Manifest()
manifest.add_file('path/to/file.vcf.gz')

# Create the import
imp = solvebio.DatasetImport.create(
    dataset_id=dataset.id,
    manifest=manifest.manifest
)

# Prints updates as the data is processed
# and indexed into SolveBio
dataset.activity(follow=True)

#
# You now have data!
#

# Let's add some more records that include a new field
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
    data_records=new_records
)
dataset.activity(follow=True)
