"""EKS Core engine - Registry, revision management, config, schema loading, and setup validation.
Revision 1.4.0 — T1.99.131: Added FilePropertyResult, FilePropertyExtractor, extract_file_properties exports (Appendix J)."""
from .config_registry import ConfigRegistry
from .revision import RevisionManager
from .schema_loader import SchemaLoader, load_eks_config
from .schema_to_ddl import SchemaToDDL
from .file_scanner import FileScanner
from .pipeline_orchestrator import PipelineOrchestrator
from .review_manager import ManualReviewManager
from .setup_validator import ProjectSetupValidator
from .filename_parser import FilenameParser, FilenameParseResult, parse_filename
from .file_property_parser import FilePropertyResult, FilePropertyExtractor, extract_file_properties

try:
    from .registry import DocumentRegistry
except ImportError:
    DocumentRegistry = None

__version__ = "1.4.0"
