#!/usr/bin/env python
# Simple use of solvebio.DatsetField.retrieve

import solvebio

# solvebio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print('Please set solvebio.api_key. Hint: solvebio login')
    import sys
    sys.exit(1)

fields = solvebio.DatasetField.retrieve(1)
print(fields)
