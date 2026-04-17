# Architecture: Multi-Level Caching Strategy

The Schema Engine employs a three-tier caching strategy to balance performance, persistence, and data integrity. This document explains the technical implementation and design decisions behind the `SchemaCache`.

---

## 1. Multi-Level Architecture

The cache is designed as a hierarchy, where each level serves a specific purpose:

### L1: In-Memory (Fastest)
- **Implementation**: Python Dictionary.
- **Key**: Schema name or URI.
- **Entry**: `(parsed_json, expiry_timestamp, content_hash)`.
- **Purpose**: Eliminate redundant JSON parsing during a single recursive resolution walk.
- **Default TTL**: 5 Minutes.

### L2: Disk Cache (Persistent)
- **Implementation**: JSON files in `.cache/schemas/`.
- **Key**: MD5 hash of the schema URI.
- **Purpose**: Persist parsed schemas across different process runs (e.g., between multiple notebook executions).
- **Default TTL**: 1 Hour.

### L3: Session Cache (Global)
- **Implementation**: Global Python Dictionary.
- **Purpose**: Stores heavy objects that are expensive to compute but stable for a session, specifically the `SchemaDependencyGraph`.

---

## 2. Smart Invalidation

The most critical feature of the cache is its ability to stay in sync with the file system.

### The `mtime` Check
Before serving any schema from L1 or L2, the engine performs a **Modification Time (mtime) check**:
1.  It gets the current `st_mtime` of the physical schema file.
2.  It compares it to the timestamp when the cache entry was created.
3.  If the file on disk is newer, the cache is instantly **purged**.

This ensures that developers can modify JSON schemas and see the results immediately without manually clearing caches.

---

## 3. Data Integrity: Content Hashing

For L1 entries, the engine computes a **SHA256 Content Hash**.
- This hash is used to verify that the JSON data hasn't been corrupted in memory.
- In future versions, this will be used for cross-project schema versioning.

---

## 4. Performance Metrics

The `SchemaCache` tracks hits and misses to allow for optimization:

- **Hit Rate**: (L1 Hits + L2 Hits) / Total Requests.
- **Misses**: Occur when a schema is loaded for the very first time.
- **Invalidations**: Occur when a file change is detected. High invalidation counts usually indicate an active development session.

---

## 5. Security & Safety

- **Atomic Writes**: L2 cache writes use standard Python file I/O which is generally atomic on modern Linux systems for small files.
- **Safe Keys**: Using MD5 for filenames prevents path injection and handles long URIs that might exceed OS filename limits.
- **Isolation**: The cache is stored in a hidden `.cache` directory at the project root, excluded from git via `.gitignore`.
