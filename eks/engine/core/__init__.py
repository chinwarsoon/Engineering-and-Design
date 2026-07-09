"""EKS Core engine - Registry, revision management, config, schema loading, and setup validation.
Revision 1.2.0 — T1.77–T1.78: ProjectSetupValidator with dependency probe, output-path validation, error codes."""
from .config_registry import ConfigRegistry
from .revision import RevisionManager
from .schema_loader import SchemaLoader, load_eks_config
from .schema_to_ddl import SchemaToDDL
from .file_scanner import FileScanner
from .pipeline_orchestrator import PipelineOrchestrator
from .review_manager import ManualReviewManager
from .setup_validator import ProjectSetupValidator

try:
    from .registry import DocumentRegistry
except ImportError:
    DocumentRegistry = None

__version__ = "1.2.0"
