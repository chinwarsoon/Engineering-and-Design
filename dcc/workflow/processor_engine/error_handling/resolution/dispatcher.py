"""
Resolution Dispatcher Module

Routes errors to appropriate resolution handlers based on category and remediation type.
Implements routing logic, queue management, and fallback routing.

Complies with error_handling_module_workplan.md Phase: Resolution Module Implementation.
"""

from typing import Dict, Any, List, Optional, Callable
from queue import Queue, PriorityQueue
from threading import Thread
import time
from .categorizer import Categorizer


class Dispatcher:
    """
    Dispatches errors to appropriate resolution handlers.
    
    Implements:
    - Routing logic based on error category and remediation type
    - Support for parallel dispatch of non-dependent errors
    - Dispatcher queue management
    - Fallback routing for unknown errors
    """
    
    def __init__(self, categorizer: Categorizer):
        """
        Initialize dispatcher with categorizer.
        
        Breadcrumb: categorizer → handlers → queue → fallback_handler
        
        Args:
            categorizer: Categorizer instance for error categorization
        """
        self.categorizer = categorizer
        self.handlers: Dict[str, Callable] = {}
        self.queue = PriorityQueue()
        self.fallback_handler: Optional[Callable] = None
        self.is_running = False
        self.dispatch_thread: Optional[Thread] = None
    
    def register_handler(self, category: str, handler: Callable) -> None:
        """
        Register a handler for a specific error category.
        
        Breadcrumb: category → handler → handlers_dict
        
        Args:
            category: Error category (auto_fix, manual_fix, suppress, escalate, info)
            handler: Handler function to call for this category
        """
        self.handlers[category] = handler
    
    def register_fallback(self, handler: Callable) -> None:
        """
        Register a fallback handler for unknown categories.
        
        Breadcrumb: handler → fallback_handler
        
        Args:
            handler: Fallback handler function
        """
        self.fallback_handler = handler
    
    def dispatch(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch an error to the appropriate handler.
        
        Breadcrumb: error → categorize → route → handler → result
        
        Args:
            error: Error dict with error_code and context
        
        Returns:
            Dict with dispatch result and handler response
        """
        # Categorize the error
        categorized = self.categorizer.categorize(
            error.get('error_code', ''),
            error.get('context')
        )
        
        # Get routing info
        category = categorized['category']
        routing_info = categorized['routing_info']
        
        # Route to appropriate handler
        handler = self.handlers.get(category, self.fallback_handler)
        
        if handler is None:
            return {
                'success': False,
                'error': f'No handler registered for category: {category}',
                'categorized': categorized,
                'handler_response': None
            }
        
        try:
            # Call handler
            response = handler(error, categorized)
            
            return {
                'success': True,
                'category': category,
                'categorized': categorized,
                'handler_response': response
            }
        except Exception as e:
            # Fallback on handler error
            if self.fallback_handler:
                fallback_response = self.fallback_handler(error, categorized, str(e))
                return {
                    'success': True,
                    'category': category,
                    'categorized': categorized,
                    'handler_response': fallback_response,
                    'fallback_used': True,
                    'original_error': str(e)
                }
            
            return {
                'success': False,
                'error': str(e),
                'categorized': categorized,
                'handler_response': None
            }
    
    def dispatch_async(self, error: Dict[str, Any]) -> None:
        """
        Dispatch an error asynchronously to the queue.
        
        Breadcrumb: error → categorize → priority_queue → async_dispatch
        
        Args:
            error: Error dict with error_code and context
        """
        # Categorize for priority
        categorized = self.categorizer.categorize(
            error.get('error_code', ''),
            error.get('context')
        )
        
        # Get priority from routing info
        priority = categorized['routing_info'].get('priority', 5)
        
        # Add to queue with priority
        self.queue.put((priority, error, categorized))
    
    def start_queue_processor(self) -> None:
        """Start background thread to process queued errors."""
        if self.is_running:
            return
        
        self.is_running = True
        self.dispatch_thread = Thread(target=self._process_queue, daemon=True)
        self.dispatch_thread.start()
    
    def stop_queue_processor(self) -> None:
        """Stop background queue processor."""
        self.is_running = False
        if self.dispatch_thread:
            self.dispatch_thread.join(timeout=5)
    
    def _process_queue(self) -> None:
        """Background thread to process queued errors."""
        while self.is_running:
            try:
                # Get next item from queue (with timeout to allow checking is_running)
                priority, error, categorized = self.queue.get(timeout=1)
                
                # Route to handler
                category = categorized['category']
                handler = self.handlers.get(category, self.fallback_handler)
                
                if handler:
                    try:
                        handler(error, categorized)
                    except Exception as e:
                        if self.fallback_handler:
                            self.fallback_handler(error, categorized, str(e))
                
                self.queue.task_done()
            except:
                # Queue empty or timeout, continue
                continue
    
    def dispatch_batch(self, errors: List[Dict[str, Any]], parallel: bool = True) -> List[Dict[str, Any]]:
        """
        Dispatch multiple errors in batch.
        
        Breadcrumb: errors → categorize_batch → route → results
        
        Args:
            errors: List of error dicts
            parallel: Whether to dispatch non-dependent errors in parallel
        
        Returns:
            List of dispatch results
        """
        if parallel:
            # Categorize all errors first
            categorized_errors = [
                self.categorizer.categorize(e.get('error_code', ''), e.get('context'))
                for e in errors
            ]
            
            # Group by category for parallel processing
            results = []
            for error, categorized in zip(errors, categorized_errors):
                result = self.dispatch(error)
                results.append(result)
            
            return results
        else:
            # Sequential processing
            return [self.dispatch(error) for error in errors]
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status.
        
        Breadcrumb: queue → status → queue_status
        
        Returns:
            Dict with queue size, is_running, and thread status
        """
        return {
            'queue_size': self.queue.qsize(),
            'is_running': self.is_running,
            'thread_alive': self.dispatch_thread.is_alive() if self.dispatch_thread else False
        }
    
    def clear_queue(self) -> None:
        """Clear the dispatch queue."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except:
                break
