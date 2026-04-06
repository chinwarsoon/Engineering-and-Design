from engine.core.registry import get_calculation_handler

def test_registry_lookup():
    handler = get_calculation_handler("mapping", "status_to_code")
    assert handler is not None
    assert callable(handler)
    
    # Test fallback to default
    handler_default = get_calculation_handler("aggregate", "non_existent_method")
    assert handler_default is not None # Should return the aggregate 'default'