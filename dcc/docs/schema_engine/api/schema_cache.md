# SchemaCache API

The `SchemaCache` is a multi-level caching system designed to minimize disk I/O and JSON parsing overhead. It ensures that schemas are loaded once and shared across all components of the pipeline.

---

## Class: `SchemaCache`

```python
class SchemaCache:
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        l1_ttl: int = 300,
        l2_ttl: int = 3600
    )
```

---

## Cache Levels

| Level | Name | Storage | Persistence | Scope | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L1** | **Memory** | Python Dict | Volatile | Thread/Process | Sub-millisecond retrieval of parsed JSON. |
| **L2** | **Disk** | `.cache/` | Persistent | Project-wide | Avoids re-parsing large files across runs. |
| **L3** | **Session** | Python Dict | Volatile | Global Session | Stores complex objects like the Dependency Graph. |

---

## Key Methods

### `get(key: str, schema_path: Optional[Path] = None) -> Optional[Dict[str, Any]]`
Retrieves a schema from the cache.
- **Args**:
  - `key`: Typically the schema stem name or URI.
  - `schema_path`: Path to the physical file for **stale-check validation**.
- **Returns**: The parsed JSON data or `None` if miss/expired.

### `set(key: str, data: Dict[str, Any], schema_path: Optional[Path] = None)`
Stores a schema in both L1 and L2 cache levels.

### `get_metrics() -> Dict[str, int]`
Returns a dictionary of performance metrics:
- `l1_hits`: Count of successful memory retrievals.
- `l2_hits`: Count of successful disk cache retrievals.
- `misses`: Count of total cache misses.
- `invalidations`: Count of entries purged due to file changes on disk.

### `clear(level: int = 0)`
Clears specific cache levels.
- `0`: All levels.
- `1`: L1 only.
- `2`: L2 only (deletes files).
- `3`: L3 only.

---

## Smart Invalidation (mtime Check)

The `SchemaCache` automatically detects if a schema file on disk has been updated. When calling `get()` with a `schema_path`, the cache compares the file's `st_mtime` against the timestamp of the cached entry.
- If the file is newer, the cache entry is **purged**.
- The method returns `None`, forcing a re-load from the fresh source file.

---

## Key Generation
- **L1 Keys**: Exact strings (URI or filename).
- **L2 Filenames**: MD5 hashes of the key to ensure safe file names and collision avoidance.

---

## Example Usage

```python
from dcc.workflow.schema_engine.loader.schema_cache import SchemaCache

# Initialize cache with 10-minute memory TTL
cache = SchemaCache(l1_ttl=600)

# Store data
cache.set("my_schema", {"v": 1})

# Retrieve (fast hit)
data = cache.get("my_schema")

# Check performance
print(cache.get_metrics())
```
