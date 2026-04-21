"""
CLI Entry Point for Universal Interactive Python Code Tracer - Phase 6
Provides a pip-installable command to launch the tracer on any directory.
"""

import sys
import os
import argparse
import subprocess
import webbrowser
import time
import signal
from pathlib import Path

def setup_environment():
    """Setup the environment for the CLI."""
    # Add the tracer package to the path
    tracer_path = Path(__file__).parent.parent
    if str(tracer_path) not in sys.path:
        sys.path.insert(0, str(tracer_path))
    
    # Add workflow path for engine imports
    workflow_path = tracer_path.parent / 'workflow'
    if str(workflow_path) not in sys.path:
        sys.path.insert(0, str(workflow_path))

def start_backend_server(host='127.0.0.1', port=8000, reload=False):
    """Start the FastAPI backend server."""
    try:
        import uvicorn
        from tracer.backend.server import app
        
        print(f"Starting Universal Interactive Python Code Tracer Backend...")
        print(f"Server will be available at http://{host}:{port}")
        print(f"API documentation available at http://{host}:{port}/docs")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except ImportError as e:
        print(f"Error: Required dependencies not installed. {e}")
        print("Please install required packages: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

def launch_frontend(host='127.0.0.1', port=8000):
    """Launch the frontend in the default web browser."""
    url = f"http://{host}:{port}"
    print(f"Launching frontend at {url}...")
    
    # Give the server a moment to start
    time.sleep(2)
    
    try:
        webbrowser.open(url)
        print("Frontend launched in default browser")
    except Exception as e:
        print(f"Could not automatically launch browser: {e}")
        print(f"Please manually open {url} in your web browser")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Universal Interactive Python Code Tracer - A standalone tool for visualizing, tracing, and editing Python code pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tracer                    # Start the tracer with default settings
  tracer --host 0.0.0.0     # Start tracer accessible on all network interfaces
  tracer --port 3000        # Start tracer on port 3000
  tracer --reload           # Start tracer with auto-reload (development mode)
  tracer --no-browser       # Start tracer without automatically opening browser
        """
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind the server to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind the server to (default: 8000)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development (default: False)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not automatically open the browser (default: False)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Universal Interactive Python Code Tracer v0.6.0'
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Import tracer to verify it works
    try:
        from tracer import __version__, __description__
        print(f"{__description__}")
        print(f"Version: {__version__}")
        print()
    except ImportError as e:
        print(f"Error: Could not import tracer module: {e}")
        sys.exit(1)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print('\nShutting down Universal Interactive Python Code Tracer...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Launch frontend unless disabled
    if not args.no_browser:
        # Launch browser in a separate thread/process to not block server start
        import threading
        browser_thread = threading.Thread(
            target=launch_frontend,
            args=(args.host, args.port)
        )
        browser_thread.daemon = True
        browser_thread.start()
    
    # Start the server (this will block until interrupted)
    try:
        start_backend_server(
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except KeyboardInterrupt:
        print('\nShutting down Universal Interactive Python Code Tracer...')
        sys.exit(0)

if __name__ == '__main__':
    main()