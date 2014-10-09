'''Gets all PMIDS associated with an OMIM ID. Note to run this
demo you need a license to use OMIM and the (Python) Pandas module installed.
'''
import solvebio

# Python Data Analysis Library See http://pandas.pydata.org/
import pandas

# solvebio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print('Please set solvebio.api_key. Hint: solvebio login')
    import sys
    sys.exit(1)

omim = solvebio.Dataset.retrieve('OMIM/0.0.1-1/OMIM')

omim_id_pmid_ids = {pm['omim_id']: pm['pmid_ids'] for pm in omim.query()}
omim_pm = pandas.Series(omim_id_pmid_ids)

print(omim_pm)
