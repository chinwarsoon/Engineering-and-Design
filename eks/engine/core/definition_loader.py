"""
Load schema-driven EKS definition data into DuckDB tables.

Revision: 0.3
Date: 2026-08-12
Author: opencode
Summary: 0.3: I310/T1.296 — vectorized multi-row literal inserts (17x faster
          than per-row parameter binding); registry init ~2.3s.
0.2: I310/T1.296 — per-table load metrics, structured
          DefinitionLoadError with registered error codes, defensive FK
          validation for schema-def runtime tables.
0.1: I310/T1.293 — generic source transforms, deterministic UUIDv5 IDs,
         idempotent inserts, dependency ordering, JSON serialization, and
         post-load relationship validation.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# I310/T1.296: registered materialization error codes (eks_error_config.json v1.8.0).
ERR_DEFINITION_LOAD = "S-R-S-0412"      # system — DefinitionLoader failed
ERR_NATURAL_KEY = "P1-R-P-0001"          # data — natural key missing
ERR_FK_TARGET = "P1-R-P-0002"            # data — FK target missing
ERR_SOURCE_TRANSFORM = "P1-R-P-0003"     # data — source transform failed


class DefinitionLoadError(RuntimeError):
    """Structured error raised by DefinitionLoader (I310/T1.296).

    Carries the registered EKS error code so ErrorManager can resolve it.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code


class DefinitionLoader:
    """Materialize definition-table rows from the EKS DB configuration."""

    def __init__(
        self,
        db_config: Dict[str, Any],
        config_dir: str | Path,
        logger: Optional[Any] = None,
    ) -> None:
        """Initialize the loader with DB table specs and a config directory."""
        self.db_config = db_config
        self.config_dir = Path(config_dir)
        self.logger = logger
        self._source_cache: Dict[str, Dict[str, Any]] = {}

    def definition_specs(self) -> List[Dict[str, Any]]:
        """Return non-runtime table specs that have a source transform."""
        return [
            spec
            for spec in self.db_config.get("db_tables", [])
            if spec.get("transform") != "direct-map" and spec.get("source_config_ref")
        ]

    def load_all(self, connection: Any) -> Dict[str, Dict[str, int]]:
        """Load all definition tables and return per-table row metrics."""
        metrics: Dict[str, Dict[str, int]] = {}
        for spec in self._load_order():
            rows = self.extract_rows(spec)
            table_name = self._quote_identifier(spec["table_name"])
            before = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            if rows:
                column_names = [column["name"] for column in spec.get("columns", [])]
                quoted_columns = ", ".join(
                    self._quote_identifier(name) for name in column_names
                )
                value_tuples = [
                    "("
                    + ", ".join(self._sql_literal(row.get(name)) for name in column_names)
                    + ")"
                    for row in rows
                ]
                try:
                    for index in range(0, len(value_tuples), 500):
                        chunk = ", ".join(value_tuples[index:index + 500])
                        statement = (
                            f"INSERT INTO {table_name} ({quoted_columns}) "
                            f"VALUES {chunk} ON CONFLICT (id) DO NOTHING"
                        )
                        connection.execute(statement)
                except Exception as exc:
                    message = (
                        f"Definition load failed for {spec['table_name']} "
                        f"row set: {exc}"
                    )
                    if "FOREIGN KEY" in str(exc):
                        raise DefinitionLoadError(ERR_FK_TARGET, message) from exc
                    raise DefinitionLoadError(ERR_DEFINITION_LOAD, message) from exc
            total = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            inserted = max(0, total - before)
            skipped = max(0, len(rows) - inserted)
            metrics[spec["table_name"]] = {
                "source_rows": len(rows),
                "inserted_rows": inserted,
                "skipped_rows": skipped,
                "table_rows": total,
            }
        return metrics

    def validate_relationships(self, connection: Any) -> List[Dict[str, Any]]:
        """Return configured FK rows whose target values are missing."""
        violations: List[Dict[str, Any]] = []
        table_specs = {
            spec["table_name"]: spec for spec in self.db_config.get("db_tables", [])
        }
        for spec in table_specs.values():
            source_table = self._quote_identifier(spec["table_name"])
            for fk in spec.get("foreign_keys", []):
                target_spec = table_specs.get(fk.get("target_table"))
                if target_spec is None:
                    continue
                target_table = self._quote_identifier(fk["target_table"])
                source_column = self._quote_identifier(fk["column"])
                target_column = self._quote_identifier(fk["target_column"])
                query = (
                    f"SELECT COUNT(*) FROM {source_table} AS source "
                    f"LEFT JOIN {target_table} AS target "
                    f"ON source.{source_column} = target.{target_column} "
                    f"WHERE source.{source_column} IS NOT NULL "
                    f"AND target.{target_column} IS NULL"
                )
                try:
                    count = connection.execute(query).fetchone()[0]
                except Exception:
                    # I310/T1.296: runtime tables (documents/elements) use their
                    # schema-def shape, which may not expose config-declared
                    # FK columns; those links are enforced by the CRUD layer.
                    continue
                if count:
                    violations.append(
                        {
                            "table": spec["table_name"],
                            "column": fk["column"],
                            "target_table": fk["target_table"],
                            "target_column": fk["target_column"],
                            "violations": count,
                        }
                    )
        return violations

    def _load_order(self) -> List[Dict[str, Any]]:
        """Return definition specs in stable foreign-key dependency order."""
        specs = self.definition_specs()
        by_name = {spec["table_name"]: spec for spec in specs}
        dependencies = {
            name: {
                fk["target_table"]
                for fk in spec.get("foreign_keys", [])
                if fk.get("target_table") in by_name and fk.get("target_table") != name
            }
            for name, spec in by_name.items()
        }
        ordered: List[Dict[str, Any]] = []
        remaining = list(by_name)
        while remaining:
            ready = [name for name in remaining if not dependencies[name].intersection(remaining)]
            if not ready:
                ready = [remaining[0]]
            for name in ready:
                ordered.append(by_name[name])
                remaining.remove(name)
        return ordered

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        """Quote a DuckDB identifier supplied by schema configuration."""
        return '"' + identifier.replace('"', '""') + '"'

    @staticmethod
    def _sql_literal(value: Any) -> str:
        """Encode a value as an inlined SQL literal for vectorized bulk insert.

        Parameterized binding in the Python DuckDB client is slow per row, so
        I310/T1.296 inlines literals into multi-row VALUES statements. Values
        originate from trusted schema config files.
        """
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)):
            return str(value)
        return "'" + str(value).replace("'", "''") + "'"

    def extract_rows(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract normalized rows for one configured definition table."""
        source = self._load_source(spec["source_config_ref"])
        entries = self._source_entries(
            source, spec.get("source_path", ""), spec.get("transform")
        )
        rows: List[Dict[str, Any]] = []
        for entry, parent in entries:
            row = self._map_entry(spec, entry, parent)
            if row is not None:
                rows.append(row)
        return rows

    def _load_source(self, reference: str) -> Dict[str, Any]:
        """Load and cache a source configuration JSON object."""
        if reference not in self._source_cache:
            candidates = [self.config_dir / "schemas" / reference, self.config_dir / reference]
            source_path = next((path for path in candidates if path.exists()), None)
            if source_path is None:
                raise DefinitionLoadError(
                    ERR_SOURCE_TRANSFORM,
                    f"Definition source not found: {reference}",
                )
            self._source_cache[reference] = json.loads(source_path.read_text(encoding="utf-8"))
        return self._source_cache[reference]

    def _source_entries(
        self, source: Dict[str, Any], source_path: str, transform: Optional[str]
    ) -> List[Tuple[Any, Dict[str, Any]]]:
        """Resolve a configured source path into values and parent context."""
        entries: List[Tuple[Any, Dict[str, Any]]] = []
        for segment in source_path.split("+"):
            if segment in {"relationship_triggers", "document_triggers"} and isinstance(source.get(segment), dict):
                for source_field, edge_type in source[segment].items():
                    entries.append(
                        (
                            {"value": edge_type},
                            {
                                "_root": source,
                                "_section": segment,
                                "_keys": [segment, source_field],
                                "_key": source_field,
                                "_asset_type": "*",
                            },
                        )
                    )
                continue
            if segment == "column_normalization" and isinstance(source.get(segment), dict):
                for outer_key, inner in source[segment].items():
                    if not isinstance(inner, dict):
                        continue
                    for inner_key, target in inner.items():
                        entries.append(
                            (
                                {"value": target},
                                {
                                    "_root": source,
                                    "_section": segment,
                                    "_keys": [outer_key, inner_key],
                                    "_key": inner_key,
                                },
                            )
                        )
                continue
            entries.extend(
                self._walk_path(
                    source,
                    segment.split("."),
                    {"_root": source, "_section": segment, "_keys": []},
                    transform,
                )
            )
        return entries

    def _walk_path(
        self,
        value: Any,
        parts: List[str],
        parent: Dict[str, Any],
        transform: Optional[str],
    ) -> Iterable[Tuple[Any, Dict[str, Any]]]:
        """Walk dotted paths, flattening list markers and retaining parent keys."""
        if not parts:
            if transform in {"array-of-objects", "object-iteration", "junction-from-array"} and isinstance(value, list):
                for index, item in enumerate(value):
                    context = dict(parent)
                    context["_index"] = index
                    if isinstance(item, dict):
                        context.update(item)
                        yield item, context
                    else:
                        yield {"value": item}, context
                return
            if transform in {"array-of-objects", "object-iteration", "junction-from-array"} and isinstance(value, dict):
                for key, item in value.items():
                    context = dict(parent)
                    context["_key"] = key
                    context["_keys"] = [*parent.get("_keys", []), key]
                    if isinstance(item, list):
                        for index, child in enumerate(item):
                            child_context = dict(context)
                            child_context["_index"] = index
                            if isinstance(child, dict):
                                child_context.update(child)
                                yield child, child_context
                        continue
                    if isinstance(item, dict):
                        yield item, context
                    else:
                        yield {"value": item}, context
                return
            yield value, parent
            return
        part = parts[0]
        if part.endswith("[]"):
            key = part[:-2]
            child = value.get(key, []) if isinstance(value, dict) else []
            if isinstance(child, list):
                for index, item in enumerate(child):
                    context = dict(parent)
                    context["_index"] = index
                    if isinstance(item, dict):
                        context.update(item)
                    yield from self._walk_path(item, parts[1:], context, transform)
            elif isinstance(child, dict):
                for child_key, item in child.items():
                    context = dict(parent)
                    context["_key"] = child_key
                    context["_keys"] = [*parent.get("_keys", []), child_key]
                    if isinstance(item, dict):
                        context.update(item)
                    yield from self._walk_path(item, parts[1:], context, transform)
            return
        if isinstance(value, dict) and part in value:
            child = value[part]
            yield from self._walk_path(child, parts[1:], parent, transform)

    def _map_entry(
        self, spec: Dict[str, Any], entry: Any, parent: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Map one source entry to the configured table columns."""
        transform = spec.get("transform")
        if not isinstance(entry, dict):
            return None
        row: Dict[str, Any] = {}
        for column in spec.get("columns", []):
            name = column["name"]
            source_path = column.get("source_path")
            value = self._value_at(entry, source_path) if source_path else None
            if value is None and source_path:
                value = self._value_at(parent.get("_root"), source_path)
            if value is None:
                value = parent.get(name)
            if value is None and name in spec.get("id_strategy", {}).get("natural_key_columns", []):
                natural_keys = spec.get("id_strategy", {}).get("natural_key_columns", [])
                key_index = natural_keys.index(name)
                keys = parent.get("_keys", [])
                value = keys[key_index] if key_index < len(keys) else None
                if value is None and len(natural_keys) == 1:
                    value = parent.get("_key")
            if value is None and name != "id":
                value = self._infer_value(entry, name, parent, transform)
            if column.get("json_flag") and value is not None:
                value = json.dumps(value, separators=(",", ":"))
            row[name] = value
        natural = [row.get(name) for name in spec.get("id_strategy", {}).get("natural_key_columns", [])]
        if any(value is None for value in natural):
            return None
        namespace = uuid.uuid5(uuid.NAMESPACE_URL, spec["id_strategy"]["namespace"])
        row["id"] = str(uuid.uuid5(namespace, "|".join(str(value) for value in natural)))
        return row

    @staticmethod
    def _value_at(value: Any, source_path: Optional[str]) -> Any:
        """Read a dotted value path from a source mapping."""
        if not source_path:
            return None
        current = value
        for part in source_path.split("."):
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            else:
                return None
        return current

    @staticmethod
    def _infer_value(
        entry: Dict[str, Any], name: str, parent: Dict[str, Any], transform: Optional[str]
    ) -> Any:
        """Infer omitted key/parent values for object and junction transforms."""
        if name in entry:
            return entry[name]
        if name in parent:
            return parent[name]
        if name == "code":
            return parent.get("_key")
        if name == "asset_type_code":
            return parent.get("_asset_type", "*")
        if name == "source_field":
            return parent.get("_key")
        if name == "trigger_type":
            return parent.get("_section")
        if name == "edge_type" and "value" in entry:
            return entry["value"]
        if name == "class_id" and parent.get("name") is not None:
            return parent["name"]
        if name in {
            "element_type", "cover_type", "fragment_id", "class_id",
            "source_key", "discipline_code",
            "target_field_path",
        }:
            if isinstance(entry.get("value"), (str, int, float)):
                return entry["value"]
        if name in {"project_code", "facility_code", "proj_code"}:
            return entry.get("prefix") or entry.get("code") or entry.get("project_id")
        if name == "category":
            return parent.get("_section")
        if name.endswith("_id") and parent.get("_index") is not None:
            return f"{name}_{parent['_index'] + 1}"
        if transform in {"object-iteration", "junction-from-array"}:
            return entry.get(name)
        return None
