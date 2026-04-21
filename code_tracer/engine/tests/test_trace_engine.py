"""
Unit tests for the trace engine functionality.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tracer.core.trace_engine import TraceEngine, start_trace, stop_trace, get_trace_data, is_tracing
from tracer.utils.trace_filters import should_trace_file, filter_trace_data, format_trace_for_display


class TestTraceEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = TraceEngine()
    
    def test_trace_engine_initialization(self):
        """Test that the trace engine initializes correctly."""
        self.assertFalse(self.engine.enabled)
        self.assertEqual(len(self.engine.trace_calls), 0)
        self.assertEqual(len(self.engine.call_stack), 0)
        self.assertEqual(self.engine.total_calls, 0)
        self.assertEqual(self.engine.total_time, 0.0)
    
    def test_start_stop_tracing(self):
        """Test starting and stopping tracing."""
        self.assertFalse(is_tracing())
        
        start_trace()
        self.assertTrue(is_tracing())
        
        stop_trace()
        self.assertFalse(is_tracing())
    
    def test_should_trace_file_function(self):
        """Test the file filtering logic."""
        # Test basic inclusion/exclusion
        self.assertTrue(should_trace_file("/home/user/project/script.py", 
                                         include_paths=["/home/user/project"]))
        self.assertFalse(should_trace_file("/home/user/project/script.py", 
                                          exclude_paths=["/home/user/project"]))
        
        # Test stdlib exclusion
        import os
        stdlib_file = os.__file__  # Get actual path to os.py in this environment
        self.assertFalse(should_trace_file(stdlib_file, 
                                           exclude_stdlib=True))
        self.assertTrue(should_trace_file(stdlib_file, 
                                          exclude_stdlib=False))
        
        # Test site-packages inclusion
        self.assertTrue(should_trace_file("/home/user/.local/lib/python3.8/site-packages/requests/api.py",
                                         exclude_stdlib=True))
    
    def test_simple_function_trace(self):
        """Test tracing a simple function call."""
        def test_func(x):
            y = x * 2
            return y + 1
        
        start_trace()
        try:
            result = test_func(5)
            self.assertEqual(result, 11)
        finally:
            stop_trace()
        
        trace_data = get_trace_data()
        self.assertGreaterEqual(trace_data['stats']['total_calls'], 1)
        
        # Check that we captured the function call
        calls = trace_data['calls']
        test_func_found = False
        for call_data in calls.values():
            if call_data.get('function_name') == 'test_func':
                test_func_found = True
                self.assertIn('x', call_data.get('locals', {}))
                self.assertEqual(call_data.get('locals', {}).get('x'), 5)
                break
        
        self.assertTrue(test_func_found, "test_func should be found in trace data")
    
    def test_nested_function_trace(self):
        """Test tracing nested function calls."""
        def inner_func(a):
            b = a + 1
            return b * 2
        
        def outer_func(x):
            y = inner_func(x)
            return y - 3
        
        start_trace()
        try:
            result = outer_func(4)
            self.assertEqual(result, 7)  # ((4+1)*2)-3 = (5*2)-3 = 10-3 = 7
            # inner_func(4) = (4+1)*2 = 10
            # outer_func(4) = 10 - 3 = 7
            self.assertEqual(result, 7)
        finally:
            stop_trace()
        
        trace_data = get_trace_data()
        self.assertGreaterEqual(trace_data['stats']['total_calls'], 2)
        
        # Check call hierarchy
        calls = trace_data['calls']
        outer_call_ids = []
        inner_call_ids = []
        
        for call_id, call_data in calls.items():
            if call_data.get('function_name') == 'outer_func':
                outer_call_ids.append(call_id)
            elif call_data.get('function_name') == 'inner_func':
                inner_call_ids.append(call_id)
        
        self.assertGreater(len(outer_call_ids), 0)
        self.assertGreater(len(inner_call_ids), 0)
        
        # Check that inner_func was called from outer_func
        inner_call_data = calls[inner_call_ids[0]]
        self.assertEqual(inner_call_data.get('parent_id'), outer_call_ids[0])
    
    def test_trace_data_serialization(self):
        """Test that trace data can be converted to dictionaries properly."""
        def sample_func(param):
            local_var = param * 2
            return local_var
        
        start_trace()
        try:
            sample_func(3)
        finally:
            stop_trace()
        
        trace_data = get_trace_data()
        
        # Check that we can serialize the data
        calls_dict = trace_data.get('calls', {})
        self.assertGreater(len(calls_dict), 0)
        
        # Check a sample call for expected fields
        for call_id, call_data in calls_dict.items():
            if call_data.get('function_name') == 'sample_func':
                self.assertIn('call_id', call_data)
                self.assertIn('function_name', call_data)
                self.assertIn('filename', call_data)
                self.assertIn('lineno', call_data)
                self.assertIn('locals', call_data)
                self.assertIn('globals', call_data)
                self.assertIn('start_time', call_data)
                self.assertIn('return_value', call_data)
                self.assertEqual(call_data.get('return_value'), 6)
                break
    
    def test_exception_tracing(self):
        """Test that exceptions are properly traced."""
        def failing_func():
            raise ValueError("Test exception")
        
        start_trace()
        try:
            try:
                failing_func()
            except ValueError:
                pass  # Expected
        finally:
            stop_trace()
        
        trace_data = get_trace_data()
        calls = trace_data['calls']
        
        # Find the failing function call
        failing_call = None
        for call_data in calls.values():
            if call_data.get('function_name') == 'failing_func':
                failing_call = call_data
                break
        
        self.assertIsNotNone(failing_call)
        self.assertIsNotNone(failing_call.get('exception'))
        self.assertIn('ValueError', failing_call.get('exception', ''))
    
    def test_filter_trace_data(self):
        """Test filtering of trace data."""
        def project_func():
            return "project"
        
        def stdlib_func():
            return "stdlib"
        
        start_trace()
        try:
            project_func()
            stdlib_func()  # This will actually call many stdlib functions
        finally:
            stop_trace()
        
        trace_data = get_trace_data()
        
        # Filter to only include our project files
        filtered_data = filter_trace_data(
            trace_data,
            include_paths=[os.path.dirname(__file__)],  # Include test directory
            exclude_stdlib=True
        )
        
        # Should have fewer calls after filtering
        self.assertLessEqual(
            len(filtered_data.get('calls', {})),
            len(trace_data.get('calls', {}))
        )
    
    def test_format_trace_for_display(self):
        """Test formatting trace data for UI display."""
        # Ensure tracing is stopped and data is cleared before we begin
        stop_trace()
        from tracer.core.trace_engine import _trace_engine
        _trace_engine.clear()
        
        def display_func(x):
            y = x * 2
            return y
        
        start_trace()
        try:
            display_func(5)
        finally:
            stop_trace()
        
        trace_data = get_trace_data()
        formatted = format_trace_for_display(trace_data)
        
        self.assertGreater(len(formatted), 0)
        
        # Check that we have the expected fields
        func_record = None
        for record in formatted:
            if record.get('function') == 'display_func':
                func_record = record
                break
        
        self.assertIsNotNone(func_record)
        self.assertEqual(func_record.get('function'), 'display_func')
        self.assertEqual(func_record.get('depth'), 0)  # Should be top-level
        self.assertIsInstance(func_record.get('locals_count'), int)
        self.assertIsInstance(func_record.get('globals_count'), int)


if __name__ == '__main__':
    unittest.main()