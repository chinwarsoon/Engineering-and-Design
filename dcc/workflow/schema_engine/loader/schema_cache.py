"""
Multi-level caching system for JSON schemas.

Implements Phase G of the Recursive Schema Loader Workplan:
- L1: In-Memory (TTL-based, content-hash validation)
- L2: Disk Cache (Persistent across runs, mtime validation)
- L3: Session Cache (Graph and resolution order)

Complies with agent_rule.md Section 4 (Module design).
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# Lazy imports to break circular dependency with initiation_engine
_status_print = None
_debug_print = None
_DEBUG_LEVEL = 1

def _get_debug_level() -> int:
    global _DEBUG_LEVEL
    try:
        from initiation_engine.utils.logging import DEBUG_LEVEL
        _DEBUG_LEVEL = DEBUG_LEVEL
    except ImportError:
        pass
    return _DEBUG_LEVEL

def status_print(msg: str) -> None:
    if _get_debug_level() >= 1:
        print(f"STATUS: {msg}")

def debug_print(msg: str, level: int = 1) -> None:
    if _get_debug_level() >= level:
        print(f"DEBUG[{level}]: {msg}")


class SchemaCache:
    """
    Multi-level cache for JSON schemas.
    
    Level 1: In-Memory (fastest, volatile, TTL default: 5 min)
    Level 2: Disk Cache (persistent, mtime-validated, TTL default: 1 hour)
    Level 3: Session Cache (graph and resolution data)
    """
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        l1_ttl: int = 300,  # 5 minutes
        l2_ttl: int = 3600  # 1 hour
    ):
        """
        Initialize multi-level cache.
        
        Breadcrumb: cache_dir → l1_cache → l2_cache → initialized
        
        Args:
            cache_dir: Directory for L2 disk cache
            l1_ttl: Time-to-live for L1 in-memory cache (seconds)
            l2_ttl: Time-to-live for L2 disk cache (seconds)
        """
        # L1 Cache: key -> (data, expiry_timestamp, content_hash)
        self.l1_cache: Dict[str, Tuple[Dict[str, Any], float, str]] = {}
        # L3 Cache: session-specific data (e.g., dependency graphs)
        self.l3_cache: Dict[str, Any] = {}
        
        # Metrics tracking
        self.metrics = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "invalidations": 0
        }
        
        if cache_dir is None:
            # Default to .cache/schemas in project root
            # Assuming we are in dcc/workflow/schema_engine/loader/
            try:
                from ..utils.paths import safe_resolve
                self.cache_dir = safe_resolve(Path(__file__).parent.parent.parent.parent.parent / ".cache" / "schemas")
            except ImportError:
                # Fallback if relative import fails during standalone testing
                self.cache_dir = Path.cwd() / ".cache" / "schemas"
        else:
            self.cache_dir = Path(cache_dir)
            
        self.l1_ttl = l1_ttl
        self.l2_ttl = l2_ttl
        
        # Ensure cache directory exists
        try:
            if not self.cache_dir.exists():
                self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            debug_print(f"Warning: Could not create cache directory {self.cache_dir}: {e}", level=1)
            
        debug_print(f"SchemaCache initialized (L1 TTL: {l1_ttl}s, L2 TTL: {l2_ttl}s)", level=2)
        
    def _generate_key(self, key: str) -> str:
        """Generate a safe filename key using MD5."""
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def _get_content_hash(self, data: Dict[str, Any]) -> str:
        """Generate a stable hash for JSON data."""
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        
    def get(self, key: str, schema_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """
        Get schema from cache, checking L1 then L2.
        
        Breadcrumb: key → check_l1 → check_l2 → result
        
        Args:
            key: Cache key (schema name or URI)
            schema_path: Optional path to original file for mtime validation
            
        Returns:
            Cached schema data or None if not found/expired
        """
        now = time.time()
        
        # Breadcrumb: Check L1 Cache
        if key in self.l1_cache:
            data, expiry, content_hash = self.l1_cache[key]
            
            # Check TTL and Disk sync
            if now < expiry:
                if schema_path and schema_path.exists():
                    # If file on disk is newer than our L1 entry creation time
                    if schema_path.stat().st_mtime > (expiry - self.l1_ttl):
                        self.metrics["invalidations"] += 1
                        debug_print(f"L1 cache invalidated for '{key}' (disk file changed)", level=3)
                        del self.l1_cache[key]
                    else:
                        self.metrics["l1_hits"] += 1
                        debug_print(f"L1 cache hit for '{key}'", level=3)
                        return data
                else:
                    self.metrics["l1_hits"] += 1
                    debug_print(f"L1 cache hit for '{key}' (no disk validation)", level=3)
                    return data
            else:
                debug_print(f"L1 cache expired for '{key}'", level=3)
                del self.l1_cache[key]
                
        # Breadcrumb: Check L2 Cache (Disk)
        l2_data = self._check_l2_cache(key, schema_path)
        if l2_data:
            self.metrics["l2_hits"] += 1
            # Promote to L1
            self.set_l1(key, l2_data)
            return l2_data
            
        self.metrics["misses"] += 1
        return None
        
    def _check_l2_cache(self, key: str, schema_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """Internal helper to check L2 disk cache."""
        safe_key = self._generate_key(key)
        cache_file = self.cache_dir / f"{safe_key}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            # Check L2 TTL
            mtime = cache_file.stat().st_mtime
            if (time.time() - mtime) > self.l2_ttl:
                debug_print(f"L2 cache expired for '{key}'", level=3)
                return None
                
            # Check against original schema file mtime
            if schema_path and schema_path.exists():
                if schema_path.stat().st_mtime > mtime:
                    debug_print(f"L2 cache stale for '{key}' (original file updated)", level=3)
                    return None
            
            with cache_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                debug_print(f"L2 cache hit for '{key}'", level=3)
                return data
                
        except (IOError, json.JSONDecodeError) as e:
            debug_print(f"Error reading L2 cache for '{key}': {e}", level=1)
            return None
            
    def set(self, key: str, data: Dict[str, Any], schema_path: Optional[Path] = None) -> None:
        """
        Set schema in both L1 and L2 cache.
        
        Breadcrumb: key → set_l1 → set_l2
        """
        self.set_l1(key, data)
        self.set_l2(key, data)
        
    def set_l1(self, key: str, data: Dict[str, Any]) -> None:
        """Set L1 in-memory cache."""
        expiry = time.time() + self.l1_ttl
        content_hash = self._get_content_hash(data)
        self.l1_cache[key] = (data, expiry, content_hash)
        
    def set_l2(self, key: str, data: Dict[str, Any]) -> None:
        """Set L2 disk cache."""
        safe_key = self._generate_key(key)
        cache_file = self.cache_dir / f"{safe_key}.json"
        
        try:
            with cache_file.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            debug_print(f"L2 cache write for '{key}' successful", level=3)
        except IOError as e:
            debug_print(f"Error writing L2 cache for '{key}': {e}", level=1)
            
    def clear(self, level: int = 0) -> None:
        """
        Clear cache levels.
        
        Args:
            level: 0 for all, 1 for L1, 2 for L2, 3 for L3
        """
        if level in (0, 1):
            self.l1_cache.clear()
            debug_print("L1 cache cleared", level=2)
        if level in (0, 2):
            for f in self.cache_dir.glob("*.json"):
                try:
                    f.unlink()
                except IOError:
                    pass
            debug_print("L2 cache cleared", level=2)
        if level in (0, 3):
            self.l3_cache.clear()
            debug_print("L3 cache cleared", level=2)
            
    def get_l3(self, key: str) -> Any:
        """Get from L3 session cache."""
        return self.l3_cache.get(key)
        
    def set_l3(self, key: str, data: Any) -> None:
        """Set L3 session cache."""
        self.l3_cache[key] = data

    def get_metrics(self) -> Dict[str, int]:
        """Return cache performance metrics."""
        return self.metrics.copy()
