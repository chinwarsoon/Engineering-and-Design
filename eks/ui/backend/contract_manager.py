"""UIContractManager — Validation and serialization for UI contracts.

Per Appendix G §7.3, all contracts implement validate and serialize methods.

Revision: 0.1
Date: 2026-07-01
Author: System
"""

import json
from pathlib import Path
from typing import Any, Dict, Type, Union
from .contracts import (
    DocumentSelectionContract,
    PipelineConfigContract,
    QueryRequestContract,
    QueryResponseContract,
)

_CONTRACT_TYPE_MAP: Dict[str, Type] = {
    "DocumentSelectionContract": DocumentSelectionContract,
    "PipelineConfigContract": PipelineConfigContract,
    "QueryRequestContract": QueryRequestContract,
    "QueryResponseContract": QueryResponseContract,
}


class UIContractManager:
    """Validates UI contracts and handles JSON serialization."""

    @staticmethod
    def validate_document_selection(contract: DocumentSelectionContract) -> bool:
        """Validate DocumentSelectionContract fields.

        Checks:
        - data_dir must be a non-empty string pointing to an existing directory.
        - file_types must be a list of non-empty strings.
        - max_files must be positive.
        """
        if not contract.data_dir or not isinstance(contract.data_dir, str):
            return False
        if not Path(contract.data_dir).is_dir():
            return False
        if contract.file_types is not None:
            if not isinstance(contract.file_types, list):
                return False
            if not all(isinstance(ft, str) and ft for ft in contract.file_types):
                return False
        if contract.max_files < 1:
            return False
        return True

    @staticmethod
    def validate_pipeline_config(contract: PipelineConfigContract) -> bool:
        """Validate PipelineConfigContract fields.

        Checks:
        - workers must be >= 1.
        - health_threshold must be between 0.0 and 1.0.
        """
        if contract.workers < 1:
            return False
        if not (0.0 <= contract.health_threshold <= 1.0):
            return False
        return True

    @staticmethod
    def serialize_to_json(contract: Any) -> dict:
        """Serialize any contract dataclass to a JSON-compatible dict."""
        return _dataclass_to_dict(contract)

    @staticmethod
    def deserialize_from_json(data: dict, contract_type: str) -> Any:
        """Deserialize a dict to the specified contract type.

        Args:
            data: Dictionary of field values.
            contract_type: One of the keys in _CONTRACT_TYPE_MAP.

        Returns:
            An instance of the matching contract dataclass.

        Raises:
            ValueError: If contract_type is unknown.
        """
        cls = _CONTRACT_TYPE_MAP.get(contract_type)
        if cls is None:
            raise ValueError(
                f"Unknown contract type '{contract_type}'. "
                f"Valid types: {list(_CONTRACT_TYPE_MAP.keys())}"
            )
        return cls(**data)


def _dataclass_to_dict(obj: Any) -> dict:
    """Recursively convert a dataclass instance to a plain dict."""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            result[field_name] = _dataclass_to_dict(value)
        return result
    if isinstance(obj, list):
        return [_dataclass_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    return obj
