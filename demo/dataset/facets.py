#!/usr/bin/env python
# Simple use of solvebio.DatsetField.retrieve ... facets

import solvebio

# solvebio.api_key = 'set-me-correctly'
if not solvebio.api_key:
    print( 'Please set solvebio.api_key. Hint: solvebio login')
    import sys
    sys.exit(1)

# Get the "allelic origin for this variation' facet by id, 691.
fields = solvebio.DatasetField.retrieve(691).facets
print(fields)
