"""
CLI Entry Point for Discovery Engine.

This module provides a command-line interface for running the discovery engine
independently, implementing the CLI Entry Point pattern per Appendix F.

Revision: 0.1
Date: 2026-06-30
Author: System
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engine.core.base import EngineInput, EngineOutput


class DiscoveryEngineCLI:
    """CLI interface for discovery engine."""
    
    def __init__(self):
        """Initialize CLI parser."""
        self.parser = argparse.ArgumentParser(
            description="EKS Discovery Engine - Independent execution via CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Scan data directory
  python discovery_cli.py --data-dir ./data --scan
  
  # Validate project setup
  python discovery_cli.py --data-dir ./data --validate
  
  # Resume from checkpoint
  python discovery_cli.py --data-dir ./data --checkpoint checkpoint.json
            """
        )
        self._setup_arguments()
    
    def _setup_arguments(self):
        """Setup CLI arguments."""
        self.parser.add_argument(
            "--data-dir",
            type=Path,
            required=True,
            help="Input data directory to scan"
        )
        self.parser.add_argument(
            "--config-file",
            type=Path,
            default=Path("eks/config/eks_config.json"),
            help="Configuration file path (default: eks/config/eks_config.json)"
        )
        self.parser.add_argument(
            "--schema-dir",
            type=Path,
            default=Path("eks/config/schemas"),
            help="Schema directory (default: eks/config/schemas)"
        )
        self.parser.add_argument(
            "--output-dir",
            type=Path,
            default=Path("output"),
            help="Output directory (default: output)"
        )
        self.parser.add_argument(
            "--scan",
            action="store_true",
            help="Scan data directory for documents"
        )
        self.parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate project setup"
        )
        self.parser.add_argument(
            "--checkpoint",
            type=Path,
            help="Resume from checkpoint file"
        )
        self.parser.add_argument(
            "--save-checkpoint",
            type=Path,
            help="Save checkpoint to file for resume capability"
        )
        self.parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
    
    def run(self, args: Optional[list] = None) -> EngineOutput:
        """
        Run the CLI.
        
        Args:
            args: Command-line arguments (None for sys.argv)
            
        Returns:
            EngineOutput with execution results
        """
        parsed_args = self.parser.parse_args(args)
        
        # Create engine input
        input_data = self._create_engine_input(parsed_args)
        
        # Load checkpoint if provided
        if parsed_args.checkpoint:
            checkpoint_state = self._load_checkpoint(parsed_args.checkpoint)
            input_data.checkpoint_state = checkpoint_state
        
        # TODO: Implement actual discovery engine execution
        # For now, return a placeholder output
        output = EngineOutput(
            run_id=input_data.run_id,
            status="SUCCESS",
            output_files=[],
            metadata={
                "engine": "DiscoveryEngine",
                "data_dir": str(parsed_args.data_dir),
                "scan": parsed_args.scan,
                "validate": parsed_args.validate
            },
            errors=[],
            checkpoint_state={},
            telemetry={}
        )
        
        # Save checkpoint if requested
        if parsed_args.save_checkpoint:
            self._save_checkpoint(parsed_args.save_checkpoint, output.checkpoint_state)
        
        # Print output
        if parsed_args.verbose:
            print(json.dumps(output.to_dict(), indent=2))
        
        return output
    
    def _create_engine_input(self, args) -> EngineInput:
        """Create EngineInput from CLI arguments."""
        import uuid
        
        return EngineInput(
            run_id=str(uuid.uuid4()),
            data_dir=args.data_dir,
            config_file=args.config_file,
            schema_dir=args.schema_dir,
            output_dir=args.output_dir,
            parameters={
                "scan": args.scan,
                "validate": args.validate,
                "verbose": args.verbose
            }
        )
    
    def _load_checkpoint(self, checkpoint_path: Path) -> dict:
        """Load checkpoint state from file."""
        try:
            with open(checkpoint_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load checkpoint: {e}")
            return {}
    
    def _save_checkpoint(self, checkpoint_path: Path, state: dict):
        """Save checkpoint state to file."""
        try:
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_path, 'w') as f:
                json.dump(state, f, indent=2)
            print(f"Checkpoint saved to {checkpoint_path}")
        except Exception as e:
            print(f"Warning: Failed to save checkpoint: {e}")


def main():
    """Main entry point for CLI."""
    cli = DiscoveryEngineCLI()
    output = cli.run()
    
    # Exit with appropriate code
    if output.status == "SUCCESS":
        sys.exit(0)
    elif output.status == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
