"""
Interceptor Framework Module

Provides AOP-style decoration framework for error handling.
Allows transparent interception of function calls for error tracking,
logging, validation, and remediation.
"""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class InterceptionContext:
    """Context passed to interceptors during function execution."""
    func_name: str
    func_module: str
    args: tuple
    kwargs: dict
    layer: Optional[str] = None
    phase: Optional[str] = None
    error_codes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Set during execution
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    exception: Optional[Exception] = None
    result: Any = None
    
    def add_error_code(self, code: str) -> None:
        """Add an error code to the context."""
        if code not in self.error_codes:
            self.error_codes.append(code)
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Get execution duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None


class Interceptor:
    """
    AOP-style interceptor framework for error handling.
    
    Allows registration of before/after/around advice for functions.
    Used to implement:
    - Error tracking decorators
    - Logging decorators  
    - Validation decorators
    - Remediation decorators
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize interceptor."""
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self._before_handlers: List[Callable] = []
        self._after_handlers: List[Callable] = []
        self._around_handlers: List[Callable] = []
        self._error_handlers: List[Callable] = []
    
    def before(self, handler: Callable) -> Callable:
        """Register a before handler. Returns the handler for chaining."""
        self._before_handlers.append(handler)
        return handler
    
    def after(self, handler: Callable) -> Callable:
        """Register an after handler. Returns the handler for chaining."""
        self._after_handlers.append(handler)
        return handler
    
    def around(self, handler: Callable) -> Callable:
        """Register an around handler. Returns the handler for chaining."""
        self._around_handlers.append(handler)
        return handler
    
    def on_error(self, handler: Callable) -> Callable:
        """Register an error handler. Returns the handler for chaining."""
        self._error_handlers.append(handler)
        return handler
    
    def intercept(
        self,
        layer: Optional[str] = None,
        phase: Optional[str] = None,
        error_family: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Decorator to intercept a function.
        
        Args:
            layer: Validation layer (L1-L5)
            phase: Processing phase (P1, P2, P2.5, P3)
            error_family: Error family for categorization
            metadata: Additional metadata
        
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create interception context
                ctx = InterceptionContext(
                    func_name=func.__name__,
                    func_module=func.__module__,
                    args=args,
                    kwargs=kwargs,
                    layer=layer,
                    phase=phase,
                    metadata=metadata or {}
                )
                
                # Execute before handlers
                for handler in self._before_handlers:
                    handler(ctx)
                
                # Execute around handlers or the function
                ctx.start_time = datetime.utcnow()
                
                try:
                    if self._around_handlers:
                        # Around handlers wrap the function execution
                        result = self._execute_with_around_handlers(func, ctx)
                    else:
                        result = func(*args, **kwargs)
                    
                    ctx.result = result
                    ctx.end_time = datetime.utcnow()
                    
                except Exception as e:
                    ctx.exception = e
                    ctx.end_time = datetime.utcnow()
                    
                    # Execute error handlers
                    for handler in self._error_handlers:
                        handler(ctx)
                    
                    raise
                
                finally:
                    # Execute after handlers
                    for handler in self._after_handlers:
                        handler(ctx)
                
                return ctx.result
            
            # Attach metadata to the wrapper for introspection
            wrapper._interceptor_metadata = {
                "layer": layer,
                "phase": phase,
                "error_family": error_family,
                "original_func": func
            }
            
            return wrapper
        return decorator
    
    def _execute_with_around_handlers(
        self,
        func: Callable,
        ctx: InterceptionContext
    ) -> Any:
        """
        Execute function with around handlers.
        
        Around handlers form a chain where each handler can:
        1. Do something before the next handler
        2. Call the next handler (or original function)
        3. Do something after the next handler
        """
        def chain(index: int) -> Any:
            if index >= len(self._around_handlers):
                # Chain ends - execute the original function
                return func(*ctx.args, **ctx.kwargs)
            
            handler = self._around_handlers[index]
            
            # Create proceed function for this handler
            def proceed():
                return chain(index + 1)
            
            # Execute handler with proceed callback
            return handler(ctx, proceed)
        
        return chain(0)
    
    def clear_handlers(self) -> None:
        """Clear all registered handlers."""
        self._before_handlers.clear()
        self._after_handlers.clear()
        self._around_handlers.clear()
        self._error_handlers.clear()
    
    def get_handler_count(self) -> Dict[str, int]:
        """Get count of registered handlers by type."""
        return {
            "before": len(self._before_handlers),
            "after": len(self._after_handlers),
            "around": len(self._around_handlers),
            "error": len(self._error_handlers)
        }


# Global singleton instance
_interceptor = Interceptor()


def intercept(
    layer: Optional[str] = None,
    phase: Optional[str] = None,
    error_family: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Convenience decorator for function interception.
    
    Args:
        layer: Validation layer (L1-L5)
        phase: Processing phase (P1, P2, P2.5, P3)
        error_family: Error family for categorization
        metadata: Additional metadata
    
    Returns:
        Decorator function
    
    Example:
        @intercept(layer="L3", phase="P1", error_family="Anchor")
        def validate_anchor_columns(df):
            # validation logic
            pass
    """
    return _interceptor.intercept(layer, phase, error_family, metadata)


def register_before(handler: Callable) -> Callable:
    """Register a global before handler."""
    return _interceptor.before(handler)


def register_after(handler: Callable) -> Callable:
    """Register a global after handler."""
    return _interceptor.after(handler)


def register_around(handler: Callable) -> Callable:
    """Register a global around handler."""
    return _interceptor.around(handler)


def register_on_error(handler: Callable) -> Callable:
    """Register a global error handler."""
    return _interceptor.on_error(handler)


def get_interceptor() -> Interceptor:
    """Get the global interceptor instance."""
    return _interceptor
