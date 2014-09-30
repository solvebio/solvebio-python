#!/usr/bin/env python
# Simple use of solvebio.Query with simple equality tests, sometimes
# with "and" or "or"

import solvebio

# SolveBio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print( 'Please set SolveBio.api_key. Hint: solvebio login')
    import sys
    sys.exit(1)

ds = solvebio.Dataset.retrieve('ClinVar/2.0.0-1/Variants')

results = ds.query.filter(hg19_start__in = (148562304, 148459988))
print(results)

# Here is the same thing but a little more inefficiently

# filters2 = solvebio.Filter(hg19_start = 148459988) | \
#   solvebio.Filter(hg19_start = 148562304)

# results = ds.query(filters = filters2)

# print('=' * 10)
# print(results)
