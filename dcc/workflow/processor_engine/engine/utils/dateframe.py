"""
The "defensive" Pandas logic found at the start of apply_null_handling—such as resetting the index 
to RangeIndex and flattening multi-index columns—will be moved into helper functions here to keep the engine code clean.
"""