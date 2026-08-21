"""
Integration tests for I298–I299, I301–I305 — GROUP 12 pipeline runtime tables,
ontology relation drift resolution, version stamps, template counts,
and project_definition setup schema.

Scope:
  I298 (T1.261): pipeline_checkpoint table + insert_checkpoint/get_checkpoint CRUD
  I299 (T1.262): pipeline_event_log table + insert_events batch flush
  I301 (T1.264): export_artifact table + insert_artifact CRUD
  I302: version banner stamps B.1 v1.5, B.2 v1.6
  I303: twrp_spec_c expected_elements = [section, table, image]
  I304: eks_project_definition_setup_schema.json exists and validates
  I305: ontology relationships 16→18, all 7 trigger relations registered
"""
import unittest
import tempfile
import json
from pathlib import Path

from eks.engine.core import DocumentRegistry
from eks.engine.core.schema_to_ddl import SchemaToDDL

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class _FakeLogger:
    """Minimal logger for test registry."""
    def __init__(self, run_id: str = "test"):
        self.run_id = run_id
        self.level = 1

    def status(self, message, context=None): pass

    def info(self, message, context=None): pass

    def warning(self, message, context=None): pass

    def debug(self, message, context=None): pass

    def error(self, message, context=None): pass


class TestI298PipelineCheckpoint(unittest.TestCase):
    """I298 (T1.261): pipeline_checkpoint DDL + CRUD."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)

    def _make_registry(self, name: str):
        reg_path = self.test_dir / name
        if reg_path.exists():
            reg_path.unlink()
        return reg_path, DocumentRegistry(db_path=str(reg_path), logger=_FakeLogger())

    def test_checkpoint_ddl_shape(self):
        """I298(1): pipeline_checkpoint DDL has id + job_id + phase + state."""
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl = SchemaToDDL(schema).generate_pipeline_checkpoint_ddl()
        self.assertIn("pipeline_checkpoint", ddl)
        for col in ["id VARCHAR PRIMARY KEY", "job_id VARCHAR", "phase VARCHAR",
                     "state JSON", "created_at TIMESTAMP"]:
            self.assertIn(col, ddl, f"Missing column in DDL: {col}")

    def test_table_created_in_runtime_db(self):
        """I298(2): pipeline_checkpoint exists in freshly initialized registry."""
        reg_path, reg = self._make_registry("test_i298_tbl.db")
        try:
            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                rows = {r[0] for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables"
                ).fetchall()}
            finally:
                conn.close()
            self.assertIn("pipeline_checkpoint", rows)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_insert_get_roundtrip(self):
        """I298(3): insert_checkpoint → get_checkpoint round-trip."""
        reg_path, reg = self._make_registry("test_i298_roundtrip.db")
        try:
            state = '{"phase":"A","status":"IN_PROGRESS","discovered":12}'
            cid = reg.insert_checkpoint("job-X", "A", state)
            self.assertIsNotNone(cid)

            row = reg.get_checkpoint("job-X", "A")
            self.assertIsNotNone(row)
            self.assertEqual(row["job_id"], "job-X")
            self.assertEqual(row["phase"], "A")
            self.assertIn("discovered", row["state"])
        finally:
            if reg_path.exists():
                reg_path.unlink()


class TestI299PipelineEventLog(unittest.TestCase):
    """I299 (T1.262): pipeline_event_log DDL + batch insert."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)

    def _make_registry(self, name: str):
        reg_path = self.test_dir / name
        if reg_path.exists():
            reg_path.unlink()
        return reg_path, DocumentRegistry(db_path=str(reg_path), logger=_FakeLogger())

    def test_event_log_ddl_shape(self):
        """I299(1): pipeline_event_log DDL has id + job_id + level + message."""
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl = SchemaToDDL(schema).generate_pipeline_event_log_ddl()
        self.assertIn("pipeline_event_log", ddl)
        for col in ["id VARCHAR PRIMARY KEY", "job_id VARCHAR", "timestamp TIMESTAMP",
                     "level VARCHAR", "message TEXT"]:
            self.assertIn(col, ddl, f"Missing column in DDL: {col}")

    def test_table_created_in_runtime_db(self):
        """I299(2): pipeline_event_log exists in freshly initialized registry."""
        reg_path, reg = self._make_registry("test_i299_tbl.db")
        try:
            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                rows = {r[0] for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables"
                ).fetchall()}
            finally:
                conn.close()
            self.assertIn("pipeline_event_log", rows)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_insert_events_batch_flush(self):
        """I299(3): insert_events with batch of 3 events writes to DB."""
        reg_path, reg = self._make_registry("test_i299_events.db")
        try:
            events = [
                {"timestamp": "2026-08-10T12:00:00", "level": "INFO",
                 "category": "pipeline", "context": "job-X", "module": "test",
                 "message": "Pipeline started"},
                {"timestamp": "2026-08-10T12:01:00", "level": "WARN",
                 "category": "phase_a", "context": "job-X", "module": "test",
                 "message": "Phase A warnings"},
                {"timestamp": "2026-08-10T12:10:00", "level": "ERROR",
                 "category": "phase_c", "context": "job-X", "module": "test",
                 "message": "Phase C flagged"},
            ]
            reg.insert_events("job-X", events)

            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                rows = conn.execute(
                    "SELECT COUNT(*) FROM pipeline_event_log WHERE job_id = 'job-X'"
                ).fetchone()
                self.assertEqual(rows[0], 3)
            finally:
                conn.close()
        finally:
            if reg_path.exists():
                reg_path.unlink()


class TestI301ExportArtifact(unittest.TestCase):
    """I301 (T1.264): export_artifact DDL + CRUD."""

    @classmethod
    def setUpClass(cls):
        cls.config_dir = _PROJECT_ROOT / "config" / "schemas"
        cls.test_dir = _PROJECT_ROOT / "test_output"
        cls.test_dir.mkdir(exist_ok=True)

    def _make_registry(self, name: str):
        reg_path = self.test_dir / name
        if reg_path.exists():
            reg_path.unlink()
        return reg_path, DocumentRegistry(db_path=str(reg_path), logger=_FakeLogger())

    def test_export_artifact_ddl_shape(self):
        """I301(1): export_artifact DDL has id + job_id + artifact_type + file_path."""
        schema = SchemaToDDL.load_doc_base_schema(self.config_dir)
        ddl = SchemaToDDL(schema).generate_export_artifact_ddl()
        self.assertIn("export_artifact", ddl)
        for col in ["id VARCHAR PRIMARY KEY", "job_id VARCHAR",
                     "artifact_type VARCHAR", "file_path VARCHAR",
                     "created_at TIMESTAMP", "row_count INTEGER"]:
            self.assertIn(col, ddl, f"Missing column in DDL: {col}")

    def test_table_created_in_runtime_db(self):
        """I301(2): export_artifact exists in freshly initialized registry."""
        reg_path, reg = self._make_registry("test_i301_tbl.db")
        try:
            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                rows = {r[0] for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables"
                ).fetchall()}
            finally:
                conn.close()
            self.assertIn("export_artifact", rows)
        finally:
            if reg_path.exists():
                reg_path.unlink()

    def test_insert_artifact(self):
        """I301(3): insert_artifact records export metadata."""
        reg_path, reg = self._make_registry("test_i301_artifact.db")
        try:
            aid = reg.insert_artifact(
                "job-X", "discovery_inventory",
                "/tmp/eks_export_phase_a.csv", row_count=42
            )
            self.assertIsNotNone(aid)

            import duckdb
            conn = duckdb.connect(str(reg_path))
            try:
                row = conn.execute(
                    "SELECT id, job_id, artifact_type, file_path, row_count, created_at "
                    "FROM export_artifact WHERE job_id = 'job-X'"
                ).fetchone()
                self.assertEqual(row[2], "discovery_inventory")  # artifact_type
                self.assertEqual(row[4], 42)  # row_count
            finally:
                conn.close()
        finally:
            if reg_path.exists():
                reg_path.unlink()


class TestI303TemplateElements(unittest.TestCase):
    """I303 (T1.266): twrp_spec_c expected_elements populated, carrier v2.3.1."""

    @classmethod
    def setUpClass(cls):
        cls.schema_path = _PROJECT_ROOT / "config" / "schemas" / "eks_document_type_schema.json"

    def test_carrier_version_is_2_3_1(self):
        """I303(1): Carrier version is v2.3.1."""
        data = json.loads(self.schema_path.read_text())
        self.assertEqual(data.get("version"), "2.3.1")

    def test_spec_c_has_3_elements(self):
        """I303(2): twrp_spec_c expected_elements = [section, table, image]."""
        data = json.loads(self.schema_path.read_text())
        templates = data.get("document_templates", {})
        spec = templates.get("twrp_spec_c", {})
        self.assertIsNotNone(spec)
        elems = spec.get("expected_elements", [])
        self.assertEqual(len(elems), 3)
        self.assertIn("section", elems)
        self.assertIn("table", elems)
        self.assertIn("image", elems)
        self.assertEqual(spec.get("threshold"), 3)

    def test_all_6_templates_have_elements(self):
        """I303(3): No template has 0 expected_elements."""
        data = json.loads(self.schema_path.read_text())
        templates = data.get("document_templates", {})
        self.assertEqual(len(templates), 6)
        for tid, tdef in templates.items():
            elems = tdef.get("expected_elements", [])
            self.assertGreater(len(elems), 0,
                               f"Template {tid} has 0 expected_elements")


class TestI304ProjectDefinitionSetupSchema(unittest.TestCase):
    """I304 (T1.267): eks_project_definition_setup_schema.json exists + validates."""

    @classmethod
    def setUpClass(cls):
        cls.schema_dir = _PROJECT_ROOT / "config" / "schemas"

    def test_setup_schema_exists(self):
        """I304(1): eks_project_definition_setup_schema.json file exists."""
        path = self.schema_dir / "eks_project_definition_setup_schema.json"
        self.assertTrue(path.exists(), f"Missing: {path}")

    def test_setup_schema_valid_json(self):
        """I304(2): Setup schema is valid JSON with required fields."""
        path = self.schema_dir / "eks_project_definition_setup_schema.json"
        data = json.loads(path.read_text())
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertIn("$id", data)
        self.assertIn("$schema", data)
        self.assertIn("allOf", data)
        # Must reference base schema
        allof = data["allOf"]
        self.assertTrue(any(
            "eks_base_schema.json" in str(ref) for ref in allof
        ), "Setup schema must reference eks_base_schema.json")

    def test_config_references_setup_schema(self):
        """I304(3): project_definition_config $schema points to setup schema."""
        path = self.schema_dir / "eks_project_definition_config.json"
        data = json.loads(path.read_text())
        self.assertIn("eks_project_definition_setup_schema.json", data.get("$schema", ""))
        self.assertEqual(data.get("version"), "1.6.0")


class TestI305OntologyRelationDrift(unittest.TestCase):
    """I305 (T1.268): REFERENCES_ASSET + HAS_FORMAT added, all 7 triggers resolved."""

    @classmethod
    def setUpClass(cls):
        cls.ontology_path = _PROJECT_ROOT / "config" / "schemas" / "eks_ontology_config.json"
        cls.doc_config_path = _PROJECT_ROOT / "config" / "schemas" / "eks_doc_config.json"

    def test_ontology_version_1_9_0(self):
        """I305(1): Ontology version is v1.10.0 (I316/Q4 extended 18→21)."""
        data = json.loads(self.ontology_path.read_text())
        self.assertEqual(data.get("version"), "1.10.0")

    def test_relationships_count_18(self):
        """I305(2): Ontology relationships array has 21 rows (18→21 I316/Q4)."""
        data = json.loads(self.ontology_path.read_text())
        rels = data.get("relationships", [])
        self.assertEqual(len(rels), 21)

    def test_references_asset_added(self):
        """I305(3): REFERENCES_ASSET is a standalone relation with inverse REFERENCED_ASSET_BY."""
        data = json.loads(self.ontology_path.read_text())
        rels = data.get("relationships", [])
        ref_asset = [r for r in rels if r.get("name") == "REFERENCES_ASSET"]
        self.assertEqual(len(ref_asset), 1)
        self.assertEqual(ref_asset[0].get("inverse"), "REFERENCED_ASSET_BY")

    def test_has_format_added(self):
        """I305(4): HAS_FORMAT is a standalone relation with inverse FORMAT_OF."""
        data = json.loads(self.ontology_path.read_text())
        rels = data.get("relationships", [])
        has_fmt = [r for r in rels if r.get("name") == "HAS_FORMAT"]
        self.assertEqual(len(has_fmt), 1)
        self.assertEqual(has_fmt[0].get("inverse"), "FORMAT_OF")

    def test_all_7_trigger_relations_registered(self):
        """I305(5): All 7 ontology_trigger relation values resolve to registered relations."""
        doc = json.loads(self.doc_config_path.read_text())
        onto = json.loads(self.ontology_path.read_text())
        onto_names = {r["name"] for r in onto["relationships"]}
        # Also include inverse names
        onto_inverses = {r.get("inverse", "") for r in onto["relationships"] if r.get("inverse")}
        all_onto_names = onto_names | onto_inverses

        triggers = doc.get("ontology_triggers", {})
        trigger_relations = set(triggers.values())
        expected = {"IS_A", "SUPERSEDES", "REFERENCES_ASSET", "PRODUCED_BY",
                     "HAS_FORMAT", "REFERENCES_DOC", "HAS_STAGE"}
        self.assertEqual(trigger_relations, expected,
                         f"Trigger relations {trigger_relations} != expected {expected}")

        unresolved = trigger_relations - onto_names
        self.assertEqual(len(unresolved), 0,
                         f"Trigger relations not in ontology primary names: {unresolved}")


if __name__ == "__main__":
    unittest.main()
