import unittest
import json
import sys
import tempfile
from pathlib import Path

# Setup paths to import from dcc/workflow
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "workflow"
if str(WORKFLOW_PATH) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_PATH))

# Mocking initiation_engine logging since it might not be in path or might fail
class MockLogging:
    @staticmethod
    def status_print(*args, **kwargs): pass
    @staticmethod
    def debug_print(*args, **kwargs): pass

sys.modules['initiation_engine'] = MockLogging

from schema_engine.loader import RefResolver, SchemaDependencyGraph, CircularDependencyError

class TestDependencyGraph(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.test_dir.name)
        self.schema_dir = self.root / "config" / "schemas"
        self.schema_dir.mkdir(parents=True)
        
        # Create project_setup.json
        self.project_setup_path = self.schema_dir / "project_setup.json"
        self.project_setup = {
            "schema_files": []
        }
        
    def tearDown(self):
        self.test_dir.cleanup()

    def _add_schema(self, name, content):
        path = self.schema_dir / f"{name}.json"
        with open(path, 'w') as f:
            json.dump(content, f)
        self.project_setup["schema_files"].append({"filename": f"{name}.json"})
        with open(self.project_setup_path, 'w') as f:
            json.dump(self.project_setup, f)

    def test_basic_dependency(self):
        self._add_schema("schema_a", {"$ref": "schema_b.json"})
        self._add_schema("schema_b", {})
        
        resolver = RefResolver(self.project_setup_path, [self.schema_dir])
        graph = SchemaDependencyGraph(resolver)
        graph.build_graph()
        
        self.assertIn("schema_b", graph.get_dependencies("schema_a"))
        self.assertEqual(graph.get_resolution_order(), ["schema_b", "schema_a"])

    def test_custom_dcc_ref(self):
        self._add_schema("schema_a", {
            "parameters": {
                "status": {"$ref": {"schema": "schema_b", "code": "X", "field": "Y"}}
            }
        })
        self._add_schema("schema_b", {})
        
        resolver = RefResolver(self.project_setup_path, [self.schema_dir])
        graph = SchemaDependencyGraph(resolver)
        graph.build_graph()
        
        self.assertIn("schema_b", graph.get_dependencies("schema_a"))

    def test_schema_references(self):
        self._add_schema("schema_a", {
            "schema_references": {
                "ref_b": "schema_b.json"
            }
        })
        self._add_schema("schema_b", {})
        
        resolver = RefResolver(self.project_setup_path, [self.schema_dir])
        graph = SchemaDependencyGraph(resolver)
        graph.build_graph()
        
        self.assertIn("schema_b", graph.get_dependencies("schema_a"))

    def test_circular_dependency(self):
        self._add_schema("schema_a", {"$ref": "schema_b.json"})
        self._add_schema("schema_b", {"$ref": "schema_a.json"})
        
        resolver = RefResolver(self.project_setup_path, [self.schema_dir])
        graph = SchemaDependencyGraph(resolver)
        graph.build_graph()
        
        self.assertIsNotNone(graph.detect_cycles())
        with self.assertRaises(CircularDependencyError):
            graph.get_resolution_order()

    def test_complex_graph(self):
        # A -> B, A -> C
        # B -> D
        # C -> D
        # D -> E
        self._add_schema("schema_a", {"allOf": [{"$ref": "schema_b.json"}, {"$ref": "schema_c.json"}]})
        self._add_schema("schema_b", {"$ref": "schema_d.json"})
        self._add_schema("schema_c", {"$ref": "schema_d.json"})
        self._add_schema("schema_d", {"$ref": "schema_e.json"})
        self._add_schema("schema_e", {})
        
        resolver = RefResolver(self.project_setup_path, [self.schema_dir])
        graph = SchemaDependencyGraph(resolver)
        graph.build_graph()
        
        order = graph.get_resolution_order()
        self.assertEqual(order[-1], "schema_a")
        self.assertEqual(order[0], "schema_e")
        self.assertLess(order.index("schema_d"), order.index("schema_b"))
        self.assertLess(order.index("schema_d"), order.index("schema_c"))

if __name__ == "__main__":
    unittest.main()
