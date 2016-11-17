import solvebio

# create a depository, version and dataset
depository = solvebio.Depository.create(
    title="SampleDataImport",
    create_dataset=True
)
# get newly created dataset
dataset = depository.latest_version().datasets().objects()[0]

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
