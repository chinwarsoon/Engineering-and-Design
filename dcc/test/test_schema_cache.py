"""
Unit tests for SchemaCache.
Verifies L1/L2/L3 caching, TTL, and invalidation.
"""

import json
import time
import shutil
import unittest
from pathlib import Path
from dcc.workflow.schema_engine.loader.schema_cache import SchemaCache

class TestSchemaCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("./test_cache_dir")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        self.cache = SchemaCache(cache_dir=self.test_dir, l1_ttl=1, l2_ttl=2)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_l1_cache(self):
        data = {"test": "data"}
        self.cache.set("key1", data)
        
        # Immediate hit
        self.assertEqual(self.cache.get("key1"), data)
        self.assertEqual(self.cache.get_metrics()["l1_hits"], 1)

    def test_l1_ttl(self):
        data = {"test": "data"}
        self.cache.set("key1", data)
        
        # Wait for L1 TTL (1s)
        time.sleep(1.1)
        
        # Calling get() should trigger expiration check and return None if not in L2
        # But set() also sets L2, so it should return from L2 and promote to L1
        cached = self.cache.get("key1")
        self.assertEqual(cached, data)
        self.assertEqual(self.cache.get_metrics()["l2_hits"], 1)
        
        # Now it should be back in L1
        self.assertIn("key1", self.cache.l1_cache)

    def test_l2_persistence(self):
        data = {"test": "data"}
        self.cache.set("key1", data)
        
        # Clear L1 to force L2 check
        self.cache.clear(level=1)
        self.assertEqual(self.cache.get("key1"), data)
        self.assertEqual(self.cache.get_metrics()["l2_hits"], 1)

    def test_disk_invalidation(self):
        # Create a dummy schema file
        schema_file = self.test_dir / "schema.json"
        data = {"v": 1}
        with schema_file.open('w') as f:
            json.dump(data, f)
            
        self.cache.set("schema", data, schema_file)
        
        # Modify file on disk
        time.sleep(0.1) # Ensure mtime difference
        with schema_file.open('w') as f:
            json.dump({"v": 2}, f)
            
        # Get should now return None (invalidated)
        self.assertIsNone(self.cache.get("schema", schema_file))
        self.assertEqual(self.cache.get_metrics()["invalidations"], 1)

    def test_l3_cache(self):
        self.cache.set_l3("graph", {"nodes": []})
        self.assertEqual(self.cache.get_l3("graph"), {"nodes": []})

if __name__ == "__main__":
    unittest.main()
