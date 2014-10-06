import solvebio

# solvebio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print( 'Please set solvebio.api_key. Hint: solvebio login')
    import sys
    sys.exit(1)

# Load the Dataset object
dataset = solvebio.Dataset.retrieve('ClinVar/1.0.0/ClinVar')

# Print the Dataset
print(dataset)

# Get help (fields/facets)
dataset.help()

# Query the dataset (filterless)
q = dataset.query()

# Filter by gene symbol
dataset.query(filters=solvebio.Filter(gene_symbols="BRCA2"))

# Filter shortcut
dataset.query().filter(gene_symbols="BRCA2")

# Multiple keyword filter (boolean 'or')
filters = solvebio.Filter(gene_symbols="BRCA2") | solvebio.Filter(gene_symbols="BRCA1")
dataset.query(filters=filters)

# Same as above 'or' in one go using 'in'
dataset.query().filter(gene_symbols__in=["BRCA2", "BRCA1"])

# Range filter. Like 'in' for a contiguous numeric range
dataset.query(filters=solvebio.RangeFilter(
    build="hg19", chromosome="13", start=32200000, end=32500000))
