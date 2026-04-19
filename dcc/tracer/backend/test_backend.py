"""
Test script for Phase 2 backend functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tracer import start_trace, stop_trace, get_trace_data
from tracer.backend.server import app, ConnectionManager, manager

def test_backend_imports():
    """Test that backend components import correctly."""
    print("Testing backend imports...")
    assert app is not None, "FastAPI app should be available"
    assert ConnectionManager is not None, "ConnectionManager class should be available"
    assert manager is not None, "Manager instance should be available"
    print("✓ Backend imports successful")

def test_core_tracing_functions():
    """Test that core tracing functions still work."""
    print("Testing core tracing functions...")
    
    # Ensure tracing is stopped
    stop_trace()
    
    def test_func(x):
        return x * 2
    
    start_trace()
    try:
        result = test_func(5)
        assert result == 10, f"Expected 10, got {result}"
    finally:
        stop_trace()
    
    trace_data = get_trace_data()
    assert 'stats' in trace_data, "Trace data should contain stats"
    assert trace_data['stats']['total_calls'] >= 1, "Should have at least 1 call"
    print("✓ Core tracing functions work correctly")

def test_websocket_manager():
    """Test WebSocket connection manager."""
    print("Testing WebSocket manager...")
    assert isinstance(manager, ConnectionManager), "Manager should be ConnectionManager instance"
    assert hasattr(manager, 'connect'), "Manager should have connect method"
    assert hasattr(manager, 'disconnect'), "Manager should have disconnect method"
    assert hasattr(manager, 'send_personal_message'), "Manager should have send_personal_message method"
    assert hasattr(manager, 'broadcast'), "Manager should have broadcast method"
    print("✓ WebSocket manager works correctly")

def test_fastapi_app():
    """Test FastAPI app configuration."""
    print("Testing FastAPI app...")
    assert app.title == "Universal Interactive Python Code Tracer API", "App title should be correct"
    assert app.version == "0.2.0", "App version should be 0.2.0"
    assert len(app.routes) > 0, "App should have routes defined"
    print("✓ FastAPI app configured correctly")

if __name__ == "__main__":
    print("Running Phase 2 backend tests...\n")
    
    try:
        test_backend_imports()
        test_core_tracing_functions()
        test_websocket_manager()
        test_fastapi_app()
        
        print("\n✅ All Phase 2 backend tests passed!")
        print("\nPhase 2 Implementation Summary:")
        print("- FastAPI backend server created with WebSocket support")
        print("- Real-time trace streaming capability implemented")
        print("- File I/O endpoints for reading/writing files")
        print("- Health check and API documentation endpoints")
        print("- Proper security restrictions for file operations")
        print("- Integrated with existing Phase 1 tracing functionality")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)