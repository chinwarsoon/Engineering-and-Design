"""
Core tracing engine for the Universal Interactive Python Code Tracer.
Implements sys.settrace-based instrumentation to capture execution events.
"""

import sys
import time
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class FrameInfo:
    """Information captured from a frame during tracing."""
    filename: str
    lineno: int
    function_name: str
    locals_: Dict[str, Any] = field(default_factory=dict)
    globals_: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.perf_counter)


@dataclass
class CallEvent:
    """Represents a function call event."""
    frame_info: FrameInfo
    call_id: str
    parent_id: Optional[str] = None
    depth: int = 0
    start_time: float = field(default_factory=time.perf_counter)
    end_time: Optional[float] = None
    return_value: Any = None
    exception: Optional[BaseException] = None


class TraceEngine:
    """
    Main tracing engine that intercepts Python execution events.
    Uses sys.settrace to monitor function calls, lines, and returns.
    """
    
    def __init__(self):
        self.enabled = False
        self.trace_calls = {}  # call_id -> CallEvent
        self.call_stack = []   # Stack of active call IDs
        self.next_call_id = 0
        self.lock = threading.RLock()
        self.original_trace = None
        
        # Performance tracking
        self.total_calls = 0
        self.total_time = 0.0
        
    def clear(self):
        """Clear all trace data and reset counters."""
        with self.lock:
            self.trace_calls.clear()
            self.call_stack.clear()
            self.next_call_id = 0
            self.total_calls = 0
            self.total_time = 0.0
        
    def trace_function(self, frame, event, arg):
        """
        Trace function called by sys.settrace for each execution event.
        
        Args:
            frame: Current frame object
            event: One of 'call', 'line', 'return', 'exception'
            arg: Argument depending on event type
            
        Returns:
            The trace_function itself (to continue tracing)
        """
        if not self.enabled:
            return None
            
        try:
            if event == 'call':
                return self._handle_call(frame)
            elif event == 'return':
                return self._handle_return(frame, arg)
            elif event == 'exception':
                return self._handle_exception(frame, arg)
            # 'line' events can be handled if needed for line-by-line tracing
        except Exception:
            # Never let tracing errors break the traced program
            pass
            
        return self.trace_function
    
    def _handle_call(self, frame) -> Optional[Callable]:
        """Handle function call event."""
        with self.lock:
            call_id = self._generate_call_id()
            parent_id = self.call_stack[-1] if self.call_stack else None
            depth = len(self.call_stack)
            
            # Extract frame information
            frame_info = FrameInfo(
                filename=frame.f_code.co_filename,
                lineno=frame.f_lineno,
                function_name=frame.f_code.co_name,
                locals_=dict(frame.f_locals),
                globals_=dict(frame.f_globals),
                timestamp=time.perf_counter()
            )
            
            call_event = CallEvent(
                frame_info=frame_info,
                call_id=call_id,
                parent_id=parent_id,
                depth=depth
            )
            
            self.trace_calls[call_id] = call_event
            self.call_stack.append(call_id)
            self.total_calls += 1
            
        return self.trace_function
    
    def _handle_return(self, frame, arg) -> Optional[Callable]:
        """Handle function return event."""
        with self.lock:
            if self.call_stack:
                call_id = self.call_stack.pop()
                if call_id in self.trace_calls:
                    call_event = self.trace_calls[call_id]
                    call_event.end_time = time.perf_counter()
                    call_event.return_value = arg
                    
                    # Update performance metrics
                    if call_event.start_time and call_event.end_time:
                        call_duration = call_event.end_time - call_event.start_time
                        self.total_time += call_duration
                        
        return self.trace_function
    
    def _handle_exception(self, frame, arg) -> Optional[Callable]:
        """Handle exception event."""
        with self.lock:
            if self.call_stack:
                call_id = self.call_stack[-1]  # Don't pop yet, let return handle it
                if call_id in self.trace_calls:
                    call_event = self.trace_calls[call_id]
                    call_event.exception = arg  # arg is the exception instance
                    
        return self.trace_function
    
    def _generate_call_id(self) -> str:
        """Generate a unique call ID."""
        with self.lock:
            self.next_call_id += 1
            return f"call_{self.next_call_id:06d}"
    
    def start_tracing(self):
        """Start the tracing engine."""
        if not self.enabled:
            self.enabled = True
            self.original_trace = sys.gettrace()
            sys.settrace(self.trace_function)
    
    def stop_tracing(self):
        """Stop the tracing engine."""
        if self.enabled:
            self.enabled = False
            sys.settrace(self.original_trace)
            self.original_trace = None
    
    def get_trace_data(self) -> Dict[str, Any]:
        """Get collected trace data for analysis."""
        with self.lock:
            # Build call tree from trace data
            call_tree = self._build_call_tree()
            
            return {
                'calls': {call_id: self._call_event_to_dict(event) 
                         for call_id, event in self.trace_calls.items()},
                'call_tree': call_tree,
                'stats': {
                    'total_calls': self.total_calls,
                    'total_time': self.total_time,
                    'active_calls': len(self.call_stack)
                }
            }
    
    def _call_event_to_dict(self, call_event: CallEvent) -> Dict[str, Any]:
        """Convert CallEvent to dictionary for serialization."""
        return {
            'call_id': call_event.call_id,
            'parent_id': call_event.parent_id,
            'depth': call_event.depth,
            'function_name': call_event.frame_info.function_name,
            'filename': call_event.frame_info.filename,
            'lineno': call_event.frame_info.lineno,
            'locals': call_event.frame_info.locals_,
            'globals': call_event.frame_info.globals_,
            'start_time': call_event.start_time,
            'end_time': call_event.end_time,
            'duration': (call_event.end_time - call_event.start_time) 
                       if call_event.end_time and call_event.start_time else None,
            'return_value': call_event.return_value,
            'exception': str(call_event.exception) if call_event.exception else None
        }
    
    def _build_call_tree(self) -> Dict[str, Any]:
        """Build hierarchical call tree from flat call events."""
        # Create nodes for each call
        nodes = {}
        root_nodes = []
        
        for call_id, event in self.trace_calls.items():
            node = {
                'call_id': call_id,
                'function_name': event.frame_info.function_name,
                'filename': event.frame_info.filename,
                'lineno': event.frame_info.lineno,
                'children': [],
                'start_time': event.start_time,
                'end_time': event.end_time,
                'duration': (event.end_time - event.start_time) 
                           if event.end_time and event.start_time else None,
                'return_value': event.return_value,
                'exception': str(event.exception) if event.exception else None
            }
            nodes[call_id] = node
        
        # Build tree structure
        for call_id, event in self.trace_calls.items():
            node = nodes[call_id]
            parent_id = event.parent_id
            
            if parent_id is None or parent_id not in nodes:
                # Root level call
                root_nodes.append(node)
            else:
                # Child node
                parent_node = nodes[parent_id]
                parent_node['children'].append(node)
        
        return root_nodes


# Global trace engine instance
_trace_engine = TraceEngine()


def start_trace():
    """Start global tracing."""
    _trace_engine.start_tracing()


def stop_trace():
    """Stop global tracing."""
    _trace_engine.stop_tracing()


def get_trace_data():
    """Get collected trace data."""
    return _trace_engine.get_trace_data()


def is_tracing():
    """Check if tracing is currently enabled."""
    return _trace_engine.enabled


if __name__ == "__main__":
    # Simple test
    def test_function(x):
        y = x * 2
        return y + 1
    
    def outer_function(a):
        b = test_function(a)
        return b * 2
    
    print("Starting trace...")
    start_trace()
    
    try:
        result = outer_function(5)
        print(f"Result: {result}")
    finally:
        stop_trace()
    
    print("Trace data:")
    trace_data = get_trace_data()
    print(f"Total calls: {trace_data['stats']['total_calls']}")
    print(f"Total time: {trace_data['stats']['total_time']:.6f}s")