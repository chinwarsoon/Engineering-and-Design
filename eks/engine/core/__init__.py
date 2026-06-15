"""EKS Core engine - Registry, revision management, config, and schema loading."""
from .config_registry import ConfigRegistry
from .registry import DocumentRegistry
from .revision import RevisionManager
from .schema_loader import SchemaLoader, load_eks_config

__version__ = "1.0.0"
