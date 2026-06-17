"""EKS Core engine - Registry, revision management, config, and schema loading."""
from .config_registry import ConfigRegistry
from .revision import RevisionManager
from .schema_loader import SchemaLoader, load_eks_config

try:
    from .registry import DocumentRegistry
except ImportError:
    DocumentRegistry = None

__version__ = "1.0.0"
