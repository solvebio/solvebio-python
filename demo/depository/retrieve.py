#!/usr/bin/env python
# Simple use of solvebio.Depository.retrieve

import solvebio

# solvebio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print( 'Please set solvebio.api_key. Hint: solvebio.rb login')
    import sys
    sys.exit(1)

depo = solvebio.Depository.retrieve('ClinVar')
print(depo)
