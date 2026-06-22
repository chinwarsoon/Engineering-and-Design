"""EKS Core engine - Registry, revision management, config, and schema loading."""
from .config_registry import ConfigRegistry
from .revision import RevisionManager
from .schema_loader import SchemaLoader, load_eks_config
from .schema_to_ddl import SchemaToDDL
from .file_scanner import FileScanner
from .pipeline_orchestrator import PipelineOrchestrator
from .review_manager import ManualReviewManager

try:
    from .registry import DocumentRegistry
except ImportError:
    DocumentRegistry = None

__version__ = "1.0.0"
