"""
Schema-to-DDL for EKS - Auto-generate SQL DDL from JSON schema definitions.
T1.36: Replaces hard-coded DDL in registry.py with schema-driven generation.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ..logging.logger import EKSLogger, log_depth


JSON_TO_SQL_TYPE_MAP = {
    "string": "VARCHAR",
    "boolean": "BOOLEAN",
    "integer": "INTEGER",
    "number": "DOUBLE",
    "array": "JSON",
    "object": "JSON",
}

SQLITE_DEFAULT_MAP = {
    "VARCHAR": "'{default}'",
    "BOOLEAN": "{default}",
    "INTEGER": "{default}",
    "DOUBLE": "{default}",
    "JSON": "'{default}'",
}


class SchemaToDDL:
    """
    Generates SQL DDL (CREATE TABLE, ALTER TABLE) from JSON schema definitions.
    Reads document_metadata_def, project_metadata_def, document_element_def
    from eks_doc_base_schema.json.
    """

    def __init__(self, doc_base_schema: Dict[str, Any], logger: Optional[EKSLogger] = None):
        self.schema = doc_base_schema
        self.definitions = doc_base_schema.get("definitions", {})
        self.logger = logger or EKSLogger("SchemaToDDL", level=2)

    @log_depth
    def generate_documents_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the documents table by merging
        project_metadata_def and document_metadata_def properties.
        The 'id' column is always PRIMARY KEY (document identifier).
        Project metadata fields (project_title, project_number) are always
        nullable for backward compatibility — documents can be registered
        before project metadata is known.
        """
        self.logger.status("Generating documents table DDL from schema definitions")

        project_props = self.definitions.get("project_metadata_def", {}).get("properties", {})
        document_props = self.definitions.get("document_metadata_def", {}).get("properties", {})

        all_props = {}
        all_props.update(project_props)
        all_props.update(document_props)

        required_fields = set()
        for def_name in ["project_metadata_def", "document_metadata_def"]:
            req = self.definitions.get(def_name, {}).get("required", [])
            required_fields.update(req)

        always_nullable = {"project_title", "project_number", "area", "discipline", "department"}

        # T1.99.150 (I186): id is a UUID (stored as VARCHAR in DuckDB, system-generated)
        columns = ["id VARCHAR PRIMARY KEY"]
        for col_name, col_schema in all_props.items():
            effective_required = required_fields - always_nullable
            col_def = self._resolve_column(col_name, col_schema, effective_required)
            columns.append(col_def)

        col_lines = ",\n                ".join(columns)
        ddl = f"""
            CREATE TABLE IF NOT EXISTS documents (
                {col_lines}
            )"""
        return ddl

    @log_depth
    def generate_document_elements_ddl(self) -> str:
        """
        Generate CREATE TABLE DDL for the document_elements table from
        document_element_def.
        """
        self.logger.status("Generating document_elements table DDL from schema definition")

        el_def = self.definitions.get("document_element_def", {})
        props = el_def.get("properties", {})
        required_fields = set(el_def.get("required", []))

        columns = []
        for col_name, col_schema in props.items():
            col_def = self._resolve_column(col_name, col_schema, required_fields)
            columns.append(col_def)

        col_lines = ",\n                ".join(columns)
        ddl = f"""
            CREATE TABLE IF NOT EXISTS document_elements (
                {col_lines}
            )"""
        return ddl

    @log_depth
    def generate_indexes(self) -> List[str]:
        """Generate index creation statements for documents and document_elements."""
        # T1.99.150 (I186): Composite index on business key for fast lookup
        # since id is now UUID and (document_number, revision) is no longer unique.
        return [
            "CREATE INDEX IF NOT EXISTS idx_doc_business_key ON documents(document_number, revision)",
            "CREATE INDEX IF NOT EXISTS idx_elements_doc_id ON document_elements(doc_id)",
            "CREATE INDEX IF NOT EXISTS idx_elements_type ON document_elements(element_type)",
        ]

    @log_depth
    def generate_migration_ddl(self, table_name: str, existing_columns: set) -> List[str]:
        """
        Generate ALTER TABLE ADD COLUMN statements for columns that exist
        in the schema but are missing from the database.
        """
        self.logger.info(f"Checking schema drift for table '{table_name}'")

        if table_name == "documents":
            project_props = self.definitions.get("project_metadata_def", {}).get("properties", {})
            document_props = self.definitions.get("document_metadata_def", {}).get("properties", {})
            all_props = {}
            all_props.update(project_props)
            all_props.update(document_props)
            required_fields = set()
            for def_name in ["project_metadata_def", "document_metadata_def"]:
                req = self.definitions.get(def_name, {}).get("required", [])
                required_fields.update(req)
            # T1.99.164 (I196): Apply always_nullable override for migration DDL
            # — matches generate_documents_ddl() behavior so that columns added
            # via ALTER TABLE get the same nullability as columns created via
            # CREATE TABLE.
            always_nullable = {"project_title", "project_number", "area", "discipline", "department"}
            required_fields = required_fields - always_nullable
        elif table_name == "document_elements":
            el_def = self.definitions.get("document_element_def", {})
            all_props = el_def.get("properties", {})
            required_fields = set(el_def.get("required", []))
        else:
            return []

        stmts = []
        for col_name, col_schema in all_props.items():
            if col_name not in existing_columns:
                col_def = self._resolve_column(col_name, col_schema, required_fields)
                stmts.append(f"ALTER TABLE {table_name} ADD COLUMN {col_def}")
                self.logger.info(f"Migration: Adding column '{col_name}' to {table_name}")

        return stmts

    def _resolve_column(self, col_name: str, col_schema: Dict[str, Any],
                        required_fields: set) -> str:
        """
        Resolve a JSON schema property to a SQL column definition string.
        Handles $ref resolution, type mapping, defaults, nullability,
        and format-based type overrides (e.g., date-time → TIMESTAMP).
        """
        resolved = self._resolve_ref(col_schema)
        json_type = resolved.get("type", "string")
        fmt = resolved.get("format", "")

        if fmt == "date-time":
            sql_type = "TIMESTAMP"
        elif json_type == "string" and col_name == "ingested_at":
            sql_type = "TIMESTAMP"
        else:
            sql_type = JSON_TO_SQL_TYPE_MAP.get(json_type, "VARCHAR")

        parts = [col_name, sql_type]

        if col_name == "ingested_at" and sql_type == "TIMESTAMP":
            parts.append("DEFAULT CURRENT_TIMESTAMP")
        else:
            default = resolved.get("default")
            if default is not None:
                if sql_type == "BOOLEAN":
                    sql_val = "TRUE" if default else "FALSE"
                    parts.append(f"DEFAULT {sql_val}")
                elif sql_type in ("INTEGER", "DOUBLE"):
                    parts.append(f"DEFAULT {default}")
                else:
                    parts.append(f"DEFAULT '{default}'")

        # DuckDB: columns are NULL by default — only emit NOT NULL constraints
        if col_name in required_fields:
            parts.append("NOT NULL")

        return " ".join(parts)

    def _resolve_ref(self, schema_fragment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve $ref references in a schema fragment. Follows one level of
        $ref to extract type, default, and enum information.
        """
        if "$ref" in schema_fragment:
            ref_path = schema_fragment["$ref"]
            ref_def = self._lookup_ref(ref_path)
            if ref_def:
                return ref_def
        return schema_fragment

    def _lookup_ref(self, ref_path: str) -> Optional[Dict[str, Any]]:
        """
        Look up a $ref path (e.g., '#/definitions/document_type_code' or
        'eks_doc_base_schema.json#/definitions/file_type_code').
        """
        if ref_path.startswith("#/definitions/"):
            def_name = ref_path.split("/")[-1]
            return self.definitions.get(def_name)
        elif "#/definitions/" in ref_path:
            def_name = ref_path.split("/")[-1]
            return self.definitions.get(def_name)
        return None

    @staticmethod
    def load_doc_base_schema(config_dir: Path) -> Dict[str, Any]:
        """Load eks_doc_base_schema.json from config_dir/schemas/ or config_dir/."""
        schema_path = config_dir / "schemas" / "eks_doc_base_schema.json"
        if not schema_path.exists():
            schema_path = config_dir / "eks_doc_base_schema.json"
        if not schema_path.exists():
            raise FileNotFoundError(
                f"eks_doc_base_schema.json not found in {config_dir} or its schemas/ subdirectory"
            )
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)


def generate_all_ddl(config_dir: Path) -> Tuple[str, str, List[str]]:
    """
    Convenience function: load schema and generate all DDL.
    Returns (documents_ddl, document_elements_ddl, index_statements).
    """
    schema = SchemaToDDL.load_doc_base_schema(config_dir)
    gen = SchemaToDDL(schema)
    docs_ddl = gen.generate_documents_ddl()
    els_ddl = gen.generate_document_elements_ddl()
    indexes = gen.generate_indexes()
    return docs_ddl, els_ddl, indexes
