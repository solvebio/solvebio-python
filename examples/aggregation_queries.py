import solvebio
from solvebio import Dataset
from solvebio import Annotator

solvebio.login(api_key = "your_key_here")

# Find the number of genes per gene symbol in ClinVar
Clinvar_path = "solveBio:public:/ClinVar/3.7.4-2017-01-30/Combined-GRCh37"
dataset = Dataset.get_by_full_path(Clinvar_path)

gene_symbols = dataset.query().facets(gene_symbol={'limit': 10000})['gene_symbol']
# Transform list of lists to records for annotation
gene_symbols = [{'gene_symbol': g[0], 'num': g[1]} for g in gene_symbols]

fields = {
    'items': {
        # Calculate the number of unique terms in field 'clinical_significance'
        'expression': """
        dataset_field_terms_count('{0}', 'clinical_significance',
                                  filters=[['gene_symbol', record.gene_symbol]])
        """.format(Clinvar_path),
        'data_type': 'integer'
    }
}
ann = Annotator(fields, include_errors = False)
# annotate() returns a generator, execute it with list(a)
result = list(ann.annotate(gene_symbols, chunk_size = 1000))

# Calculate the number of variants per gene_symbol, clinical significance, and submitter
variants = []

submitters = dataset.query().facets('submitter')['submitter']
for submitter in submitters:
    print(submitter)
    clinical_significances = dataset.query().filter(submitter = submitter[0]).facets('clinical_significance')['clinical_significance']

    for clinical_significance in clinical_significances:
        gene_symbols = dataset.query().filter(submitter = submitter[0], clinical_significance = clinical_significance[0]).facets('gene_symbol')['gene_symbol']

        for gene_symbol in gene_symbols:
            variants.append({
            'submitter': submitter[0],
            'clinical_significance': clinical_significance[0],
            'gene_symbol': gene_symbol[0],
            'variants': gene_symbol[1]
            })

print(variants)
