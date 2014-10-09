#!/usr/bin/env python
# Simple use of solvebio.query with a range filter

import solvebio

# SolveBio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print( 'Please set SolveBio.api_key. Hint: solvebio login')
    import sys
    sys.exit(1)

ds = solvebio.Dataset.retrieve('ClinVar/2.0.0-1/Variants')

# Find ClinVar Varints records where hg19_start is between
# 140,000,000, 140,000,500.
# However get only the first result.
results = ds.query(hg19_start_range = (140000000, 140000500), limit=1)

print(results)
