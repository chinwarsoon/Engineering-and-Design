import pytest
from engine.schema.dependency import resolve_calculation_order

def test_circular_dependency_error():
    # Setup a loop: A depends on B, B depends on A
    columns = {
        'Col_A': {'is_calculated': True, 'calculation': {'source_column': 'Col_B'}},
        'Col_B': {'is_calculated': True, 'calculation': {'source_column': 'Col_A'}}
    }
    
    with pytest.raises(ValueError, match="Circular"):
        resolve_calculation_order(columns)