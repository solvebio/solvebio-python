import solvebio

solvebio.login()

# Create a dataset
dataset = solvebio.Dataset.get_or_create(
    'Test Vault',           # The name of the vault to use
    '/SampleImport/1.0.0',  # The folder that will contain your dataset
    'SampleDataset',        # The name of your dataset
    create_vault=True,      # Create the vault if does not already exist
)

# Create a manifest object and a file to it
manifest = solvebio.Manifest()
manifest.add_file('path/to/file.vcf.gz')

# Create the import and automatically approve it
imp = solvebio.DatasetImport.create(
    dataset_id=dataset.id,
    manifest=manifest.manifest,
    auto_approve=True)

# Prints updates as the data is processed
# and indexed into SolveBio
imp.follow()

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
    data_records=new_records,
    auto_approve=True)

imp.follow()
