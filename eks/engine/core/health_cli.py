"""
CLI Entry Point for Health Scorer Engine.

This module provides a command-line interface for running the health scorer engine
independently, implementing the CLI Entry Point pattern per Appendix F.

Revision: 0.2
Date: 2026-08-12
Author: opencode
Summary: 0.2: I311 (T1.298) — added --db-check/--db-apply/--db-force args;
          --db-check short-circuits via the migration gate (exit 0); mode
          transferred into DocumentRegistry (U292).
0.1: Initial HealthScorerEngineCLI.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from eks.engine.core.base import EngineInput, EngineOutput, ErrorRecord
from eks.engine.logging.logger import EKSLogger


class HealthScorerEngineCLI:
    """CLI interface for health scorer engine."""
    
    def __init__(self):
        """Initialize CLI parser."""
        self.parser = argparse.ArgumentParser(
            description="EKS Health Scorer Engine - Independent execution via CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Score a single document
  python health_cli.py --data-dir ./data --document-id DOC001
  
  # Score all documents
  python health_cli.py --data-dir ./data --batch
  
  # Resume from checkpoint
  python health_cli.py --data-dir ./data --checkpoint checkpoint.json
            """
        )
        self._setup_arguments()
    
    def _setup_arguments(self):
        """Setup CLI arguments."""
        self.parser.add_argument(
            "--data-dir",
            type=Path,
            required=True,
            help="Input data directory"
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
            "--document-id",
            type=str,
            help="Single document ID to score"
        )
        self.parser.add_argument(
            "--batch",
            action="store_true",
            help="Score all documents in registry"
        )
        self.parser.add_argument(
            "--threshold",
            type=float,
            default=0.70,
            help="Health score threshold (default: 0.70)"
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
        # I311 (T1.298): migration-gate flags — same surface as the main CLI.
        from eks.engine.pipeline_engine.cli import add_db_migration_args
        add_db_migration_args(self.parser)
    
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
        
        # Scores documents already registered in the DuckDB document registry
        # (populated by discovery / the pipeline) using HealthScorer.
        logger = EKSLogger("HealthScorerEngineCLI", level=3 if parsed_args.verbose else 1)
        errors: list = []
        result: dict = {}
        try:
            from eks.engine.eks_engine_pipeline import bootstrap_pipeline
            from eks.engine.core.registry import DocumentRegistry
            from eks.engine.core.health_scorer import HealthScorer

            project_root = Path(__file__).resolve().parent.parent.parent.parent
            config_dir = parsed_args.config_file.parent if parsed_args.config_file else None
            boot = bootstrap_pipeline(
                project_root,
                config_dir=config_dir,
                logger=logger,
                skip_readiness=True,
                debug=parsed_args.verbose,
            )
            # I311 (T1.298): --db-check runs the migration gate read-only and exits.
            from eks.engine.pipeline_engine.cli import resolve_db_migration_mode, run_db_check_only
            db_mode = resolve_db_migration_mode(parsed_args)
            if db_mode == "check":
                _resolved = boot["resolved_paths"]
                db_path = Path(_resolved.get("output_dir", project_root / "eks" / "output")) / "eks_registry.db"
                sys.exit(run_db_check_only(db_path, _resolved.get("config_dir"), logger))
            db_apply_mode = db_mode if db_mode in ("apply", "force") else None
            registry = DocumentRegistry(
                logger=logger,
                pre_generated_ddl=boot.get("pre_generated_ddl"),
                migration_mode=db_apply_mode,
            )
            scorer = HealthScorer(logger=logger)

            if parsed_args.document_id:
                doc = registry.get_document(parsed_args.document_id)
                if doc is None:
                    errors.append(ErrorRecord(
                        "HealthScorerError",
                        f"Document not found in registry: {parsed_args.document_id}",
                    ))
                else:
                    result = {
                        "mode": "single",
                        "document_id": parsed_args.document_id,
                        "score": scorer.score(doc),
                    }
            else:
                docs = registry.list_documents(latest_only=False)
                if not docs:
                    errors.append(ErrorRecord(
                        "HealthScorerError",
                        "No documents found in registry to score (run discovery first).",
                    ))
                else:
                    batch = scorer.score_batch(docs)
                    batch["mode"] = "batch"
                    batch["threshold"] = parsed_args.threshold
                    result = batch
        except Exception as e:
            errors.append(ErrorRecord(
                "HealthScorerEngineError", str(e),
                context={"document_id": parsed_args.document_id},
            ))

        status = "FAILED" if errors else "SUCCESS"
        output = EngineOutput(
            run_id=input_data.run_id,
            status=status,
            output_files=[],
            metadata={
                "engine": "HealthScorerEngine",
                "data_dir": str(parsed_args.data_dir),
                "document_id": parsed_args.document_id,
                "batch": parsed_args.batch,
                "threshold": parsed_args.threshold,
                "result": result,
            },
            errors=errors,
            checkpoint_state={},
            telemetry={},
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
                "document_id": args.document_id,
                "batch": args.batch,
                "threshold": args.threshold,
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
    cli = HealthScorerEngineCLI()
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
