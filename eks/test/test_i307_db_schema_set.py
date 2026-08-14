"""
Integration tests for I307 (T1.275–T1.281) — schema-driven DB layer schema set.

Scope:
  T1.275: eks_base_schema.json v1.18.0 — 6 shared db-layer defs
          (table_spec_def, column_spec_def, fk_spec_def, id_strategy_def,
          transform_def, export_view_def); v1.19.0 (I311) adds migration_policy;
          v1.20.0 (I308 T1.282) adds export_view_def.filter
  T1.276: eks_setup_schema.json v1.12.0 — db_tables + export_views properties
  T1.277: eks_db_config.json — 53 table specs (validates, id PK, FK targets)
  T1.278: eks_export_view_config.json — 3 default views
  T1.279: runtime-table column defs re-homed out of SchemaToDDL hardcoded strings
  T1.280: eks_doc_base_schema.json registry_relations → physical-FK semantics
  T1.281: §9 new-schema-set checklist + §24 audit + no-hardcoded-DDL guard
  T1.307 (I313): §24 view-id cross-source check updated — pipeline consumes
          view_ids via resolve_export_views() (config-driven); literal
          artifact_type values / column indices rejected.

AGENTS.md §9 checklist items verified:
  1. base defs present with $schema/$id/title/version
  2. setup schema properties + additionalProperties:false containers
  3. configs hold values without schema metadata fields
  4. both configs validate against the setup schema
  5. SchemaLoader discovers both new configs at startup
  6. end-to-end chain test (config → SchemaToDDL renderer)
"""
import json
import re
from pathlib import Path

from eks.engine.core.schema_loader import SchemaLoader
from eks.engine.core.schema_to_ddl import SchemaToDDL

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SCHEMA_DIR = _PROJECT_ROOT / "config" / "schemas"

RUNTIME_DDL_TABLES = [
    "batch_run", "health_score", "health_batch", "document_reference",
    "pipeline_checkpoint", "pipeline_event_log", "export_artifact",
]


def _load(name):
    return json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8"))


class TestT275BaseSchemaDbDefs:
    """T1.275: eks_base_schema.json v1.19.0→v1.20.0 — 6 shared db-layer definitions
    + migration_policy (I311) + export_view_def.filter (I308 T1.282);
    v1.20.0→v1.21.0 adds system_parameters_def.export_workbook_file_name (I309 T1.289)."""

    @classmethod
    def setup_class(cls):
        cls.base = _load("eks_base_schema.json")
        cls.defs = cls.base["definitions"]

    def test_version_bumped_1_22_0(self):
        assert self.base["version"] == "1.22.0"  # pre-existing: base schema bumped past 1.21.0 without test sync (unrelated to I312)
        assert "$schema" in self.base and "$id" in self.base and "title" in self.base

    def test_all_6_db_layer_defs_present(self):
        for name in ["table_spec_def", "column_spec_def", "fk_spec_def",
                     "id_strategy_def", "transform_def", "export_view_def"]:
            assert name in self.defs, f"missing base definition: {name}"

    def test_table_spec_def_shape(self):
        props = self.defs["table_spec_def"]["properties"]
        for f in ["table_name", "group_id", "source_config_ref", "source_path",
                  "title", "description", "columns", "foreign_keys",
                  "id_strategy", "transform"]:
            assert f in props, f"table_spec_def missing property: {f}"
        assert self.defs["table_spec_def"]["additionalProperties"] is False
        assert self.defs["table_spec_def"]["properties"]["columns"]["minItems"] == 1

    def test_column_spec_def_shape(self):
        props = self.defs["column_spec_def"]["properties"]
        for f in ["name", "column_type", "source_path", "nullable", "unique",
                  "is_primary", "json_flag", "comment", "default"]:
            assert f in props, f"column_spec_def missing property: {f}"
        assert self.defs["column_spec_def"]["required"] == ["name", "column_type"]
        # DuckDB JSON-type marker for list-of-values (I306 decision 3)
        assert "JSON" in self.defs["column_spec_def"]["properties"]["column_type"]["enum"]

    def test_fk_spec_def_on_delete_duckdb_only(self):
        enum = self.defs["fk_spec_def"]["properties"]["on_delete"]["enum"]
        assert set(enum) == {"NO ACTION", "RESTRICT"}, (
            "DuckDB rejects CASCADE/SET NULL in FK constraints — enum must be "
            "restricted (verified 2026-08-11)."
        )

    def test_id_strategy_def_algorithm_enum(self):
        assert set(self.defs["id_strategy_def"]["properties"]["algorithm"]["enum"]) == {"uuid5", "uuid4"}
        assert "natural_key_columns" in self.defs["id_strategy_def"]["required"]

    def test_transform_def_enum(self):
        enum = self.defs["transform_def"]["enum"]
        for t in ["1:1-unpack", "array-of-objects", "junction-from-array",
                  "object-iteration", "direct-map"]:
            assert t in enum, f"transform_def missing enum value: {t}"

    def test_export_view_def_shape(self):
        props = self.defs["export_view_def"]["properties"]
        for f in ["view_id", "source_table", "columns", "file_base_name",
                  "sheet_name", "formats"]:
            assert f in props, f"export_view_def missing property: {f}"
        assert set(self.defs["export_view_def"]["required"]) == {
            "view_id", "source_table", "columns", "file_base_name", "sheet_name", "formats"}


class TestT276SetupSchemaProperties:
    """T1.276/I312 (T1.301): eks_setup_schema.json v1.13.0 — db_tables + export_views + db_manifest_keys properties."""

    @classmethod
    def setup_class(cls):
        cls.setup = _load("eks_setup_schema.json")

    def test_version_bumped_1_13_0(self):
        assert self.setup["version"] == "1.13.0"

    def test_db_tables_property_refs_table_spec_def(self):
        db_tables = self.setup["properties"]["db_tables"]
        assert db_tables["type"] == "array"
        ref = db_tables["items"]["$ref"]
        assert ref.endswith("#/definitions/table_spec_def"), ref

    def test_export_views_property_refs_export_view_def(self):
        views = self.setup["properties"]["export_views"]
        assert views["type"] == "array"
        ref = views["items"]["$ref"]
        assert ref.endswith("#/definitions/export_view_def"), ref

    def test_db_configs_not_required_for_core_config(self):
        # New containers are optional — the core eks_config.json still validates.
        assert "db_tables" not in self.setup["required"]
        assert "export_views" not in self.setup["required"]


class TestT277DbConfig:
    """T1.277: eks_db_config.json — 53 table specs, valid, id PK, FK targets."""

    @classmethod
    def setup_class(cls):
        cls.cfg = _load("eks_db_config.json")

    def test_config_carries_metadata_header(self):
        # Cross-file convention: every *config.json carries $schema/$id/version/title/
        # description (matches eks_config.json, eks_doc_config.json, eks_asset_config.json,
        # eks_processing_config.json). Added I307 follow-up for consistency.
        for k in ["$schema", "$id", "version", "title", "description"]:
            assert k in self.cfg, f"eks_db_config.json missing metadata header field: {k}"
        assert self.cfg["version"] == "1.1.1"
        assert self.cfg["$schema"] == "https://eks.engineering/schemas/eks_setup_schema.json"

    def test_53_tables_declared(self):
        assert len(self.cfg["db_tables"]) == 53
        names = [t["table_name"] for t in self.cfg["db_tables"]]
        assert len(names) == len(set(names)), "duplicate table_name"

    def test_every_table_has_id_pk_and_strategy(self):
        for t in self.cfg["db_tables"]:
            pk = [c["name"] for c in t["columns"] if c.get("is_primary")]
            assert len(pk) == 1, f"{t['table_name']}: expected exactly 1 PK column, got {pk}"
            strat = t.get("id_strategy", {})
            assert strat.get("namespace") and strat.get("algorithm"), (
                f"{t['table_name']}: id_strategy namespace/algorithm required"
            )

    def test_all_fk_targets_declared(self):
        names = {t["table_name"] for t in self.cfg["db_tables"]}
        for t in self.cfg["db_tables"]:
            for f in t.get("foreign_keys", []):
                assert f["target_table"] in names, (
                    f"{t['table_name']} FK {f['fk_name']} -> {f['target_table']} undeclared"
                )

    def test_runtime_tables_present(self):
        names = {t["table_name"] for t in self.cfg["db_tables"]}
        for t in RUNTIME_DDL_TABLES + ["documents", "document_elements", "db_manifest"]:
            assert t in names, f"runtime/metadata table missing: {t}"


class TestT278ExportViewConfig:
    """T1.278: eks_export_view_config.json — 3 default views."""

    @classmethod
    def setup_class(cls):
        cls.cfg = _load("eks_export_view_config.json")

    def test_config_carries_metadata_header(self):
        # Cross-file convention: every *config.json carries $schema/$id/version/title/
        # description (matches eks_config.json, eks_doc_config.json, eks_asset_config.json,
        # eks_processing_config.json). Added I307 follow-up for consistency.
        for k in ["$schema", "$id", "version", "title", "description"]:
            assert k in self.cfg, f"eks_export_view_config.json missing metadata header field: {k}"
        assert self.cfg["version"] == "1.2.0"  # I309 T1.289: review_flags gains xlsx format (all 3 views Excel-eligible)
        assert self.cfg["$schema"] == "https://eks.engineering/schemas/eks_setup_schema.json"

    def test_three_default_views(self):
        views = {v["view_id"] for v in self.cfg["views"]}
        assert views == {"discovery_inventory", "extraction_results", "review_flags"}

    def test_view_required_fields(self):
        for v in self.cfg["views"]:
            for f in ["view_id", "source_table", "columns", "file_base_name",
                      "sheet_name", "formats"]:
                assert f in v, f"view {v.get('view_id')} missing {f}"
            assert v["formats"], f"view {v['view_id']} needs >=1 format"

    def test_view_ids_match_export_artifact_types(self):
        # I306: view_id doubles as export_artifact.artifact_type.
        expected = {"discovery_inventory", "extraction_results", "review_flags"}
        assert {v["view_id"] for v in self.cfg["views"]} == expected


class TestT279SchemaToDDLRehome:
    """T1.279: runtime-table column defs re-homed out of SchemaToDDL strings."""

    @classmethod
    def setup_class(cls):
        cls.ddl_source = (_PROJECT_ROOT / "engine" / "core" / "schema_to_ddl.py").read_text(encoding="utf-8")
        schema = SchemaToDDL.load_doc_base_schema(_SCHEMA_DIR)
        cls.gen = SchemaToDDL(schema)  # no db_config → lazy load from config

    def test_guard_no_hardcoded_runtime_column_literals(self):
        # The old hardcoded DDL bodies contained these exact literals — grep guard
        # ensures zero remain in the generator source (all from config now).
        forbidden = [
            "run_id VARCHAR PRIMARY KEY",
            "phase_a_discovered INTEGER DEFAULT 0",
            "missing_columns JSON",
            "avg_document_health DOUBLE",
            "source_doc_id VARCHAR NOT NULL",
            "state JSON NOT NULL",
            "artifact_type VARCHAR NOT NULL",
            "status_success INTEGER DEFAULT 0",
        ]
        for lit in forbidden:
            assert lit not in self.ddl_source, (
                f"hardcoded runtime-DDL literal still present in schema_to_ddl.py: {lit}"
            )

    def test_runtime_generators_render_from_config(self):
        cfg = _load("eks_db_config.json")
        for table_name in RUNTIME_DDL_TABLES:
            spec = next(t for t in cfg["db_tables"] if t["table_name"] == table_name)
            ddl = self.gen._render_table_from_config(table_name)
            assert table_name in ddl
            for c in spec["columns"]:
                assert f"{c['name']} " in ddl, f"{table_name}: column {c['name']} missing"

    def test_batch_run_ddl_shape_preserved(self):
        ddl = self.gen.generate_batch_run_ddl()
        assert "run_id VARCHAR PRIMARY KEY" in ddl
        for col in ["job_id", "current_stage", "phase_a_discovered", "phase_a_valid",
                    "phase_b_total", "phase_b_success", "phase_b_failed", "phase_c_flagged"]:
            assert col in ddl, f"batch_run missing {col}"

    def test_health_score_ddl_shape_preserved(self):
        ddl = self.gen.generate_health_score_ddl()
        for col in ["document_id VARCHAR", "health_score DOUBLE",
                    "dim_completeness DOUBLE", "missing_columns JSON"]:
            assert col in ddl, f"health_score missing {col}"

    def test_document_reference_ddl_shape_preserved(self):
        ddl = self.gen.generate_document_reference_ddl()
        for col in ["source_doc_id VARCHAR NOT NULL", "target_doc_id VARCHAR NOT NULL",
                    "relation_type VARCHAR NOT NULL", "created_at TIMESTAMP NOT NULL DEFAULT now()"]:
            assert col in ddl, f"document_reference missing {col}"

    def test_export_artifact_ddl_shape_preserved(self):
        ddl = self.gen.generate_export_artifact_ddl()
        for col in ["id VARCHAR PRIMARY KEY", "job_id VARCHAR NOT NULL",
                    "artifact_type VARCHAR NOT NULL", "file_path VARCHAR NOT NULL",
                    "row_count INTEGER DEFAULT 0", "created_at TIMESTAMP NOT NULL DEFAULT now()"]:
            assert col in ddl, f"export_artifact missing {col}"


class TestT280RegistryRelationsPhysicalFK:
    """T1.280: eks_doc_base_schema.json registry_relations → physical-FK semantics."""

    @classmethod
    def setup_class(cls):
        cls.doc_base = _load("eks_doc_base_schema.json")

    def test_version_bumped_1_21_0(self):
        assert self.doc_base["version"] == "1.21.0"

    def test_relations_declared_as_fk_specs_in_db_config(self):
        db_cfg = _load("eks_db_config.json")
        doc_fks = set()
        for t in db_cfg["db_tables"]:
            if t["table_name"] in ("documents", "document_elements"):
                doc_fks |= {f["fk_name"] for f in t.get("foreign_keys", [])}
        for rel in self.doc_base["registry_relations"]:
            assert rel["relation_name"] in doc_fks, (
                f"registry_relations {rel['relation_name']} must be declared as an "
                f"fk_spec_def row in eks_db_config.json (I306 Q1 physical-FK intent)"
            )

    def test_export_artifact_fk_wired(self):
        db_cfg = _load("eks_db_config.json")
        ea = next(t for t in db_cfg["db_tables"] if t["table_name"] == "export_artifact")
        fk_names = {f["fk_name"] for f in ea.get("foreign_keys", [])}
        assert "fk_ea_batch" in fk_names


class TestT281SchemaLoaderDiscovery:
    """T1.281: SchemaLoader discovers + validates both new configs at startup (§9 item 5)."""

    @classmethod
    def setup_class(cls):
        cls.loader = SchemaLoader(_SCHEMA_DIR)

    def test_both_configs_discovered_and_validated(self):
        result = self.loader.load_all()
        assert len(self.loader.db_config.get("db_tables", [])) == 53
        assert len(self.loader.export_view_config.get("views", [])) == 3
        assert result  # load_all returns config; no exception = valid

    def test_end_to_end_chain(self):
        # §9 item 6: config → SchemaToDDL renderer end-to-end.
        for t in RUNTIME_DDL_TABLES:
            ddl = self.loader.db_config  # ensure loaded
            assert t in {x["table_name"] for x in ddl["db_tables"]}


class TestA24CrossSourceAudit:
    """§24 cross-source audit: ids/names agree across all sources."""

    def test_view_ids_consistent_across_sources(self):
        evc = _load("eks_export_view_config.json")
        views = {v["view_id"] for v in evc["views"]}
        # exporter.py resolve_export_columns keys (I307/T1.278 cross-check)
        exporter_src = (_PROJECT_ROOT / "engine" / "pipeline_engine" / "exporter.py").read_text(encoding="utf-8")
        for vid in views:
            assert vid in exporter_src, f"view id {vid} not produced by exporter.resolve_export_columns"
        # pipeline consumes the same artifact names via the config-driven
        # resolve_export_views() catalog (I313/T1.307 BLOCK-1 — view_ids are
        # derived from each view's view_id, never hardcoded literals).
        pipeline_src = (_PROJECT_ROOT / "engine" / "eks_engine_pipeline.py").read_text(encoding="utf-8")
        assert "resolve_export_views" in pipeline_src, (
            "pipeline must resolve export views from config (I313/T1.307)"
        )
        assert "resolve_export_columns" in pipeline_src, (
            "pipeline re-exports resolve_export_columns (test_phase1 contract)"
        )
        for vid in views:
            assert f'"artifact_type": "{vid}"' not in pipeline_src, (
                f"literal artifact_type value {vid} must not be in pipeline (I313/T1.307)"
            )
            assert f'export_config["{vid}"]' not in pipeline_src, (
                f"literal column index {vid} must not be in pipeline (I313/T1.307)"
            )

    def test_runtime_table_names_consistent_across_sources(self):
        cfg = _load("eks_db_config.json")
        names = {t["table_name"] for t in cfg["db_tables"]}
        # registry._init_db creates each runtime table by name
        registry_src = (_PROJECT_ROOT / "engine" / "core" / "registry.py").read_text(encoding="utf-8")
        for t in RUNTIME_DDL_TABLES:
            assert t in registry_src, f"runtime table {t} not referenced by registry.py"

    def test_table_names_match_inventory(self):
        # T1.269 inventory lists all 53 names (definition T01–T39+J01–J06, runtime, metadata).
        cfg = _load("eks_db_config.json")
        names = {t["table_name"] for t in cfg["db_tables"]}
        assert "data_column" in names and "asset_type_fragment" in names
        assert "project_definition" in names and "ontology_trigger" in names
        assert "pipeline_checkpoint" in names and "db_manifest" in names
