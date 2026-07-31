"""EKS Core engine - Registry, revision management, config, schema loading, and setup validation.
Revision 1.5.0 — T1.193: Added ProjectDefinitionResolver, ProjectConfigurationRegistry, RuntimeProjectConfiguration and 17 domain exports (Appendix L)."""
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

from .project_definition import (
    ProjectDefinitionResolver,
    ProjectConfigurationRegistry,
    RuntimeProjectConfiguration,
    ProjectDomain,
    LifecycleDomain,
    EngineeringDomain,
    StandardsDomain,
    DocumentDomain,
    ParsingDomain,
    ChunkingDomain,
    EmbeddingsDomain,
    MetadataDomain,
    AssetsDomain,
    OntologyDomain,
    RetrievalDomain,
    PromptsDomain,
    ValidationDomain,
    SecurityDomain,
    RuntimeProfilesDomain,
    RuntimeMetadata,
)

from eks import __version__
