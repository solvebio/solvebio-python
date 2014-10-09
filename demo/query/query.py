#!/usr/bin/env python
# Simple use of solvebio.query

import solvebio
import solvebio.resource

# SolveBio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print('Please set SolveBio.api_key. Hint: solvebio login')
    import sys
    sys.exit(1)

dataset = solvebio.Dataset.retrieve('Clinvar/2.0.0-1/Variants')
print(dataset.query())
