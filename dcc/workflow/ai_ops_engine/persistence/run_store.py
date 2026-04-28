"""
AI Ops Engine — Run Store

Persists pipeline run metadata and AI insight payloads to DuckDB.
Breadcrumb: PipelineRunRecord + AiInsight → DuckDB pipeline_runs table
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import List, Optional

from ..core.contracts import AiInsight, PipelineRunRecord

logger = logging.getLogger(__name__)

_DEFAULT_DB = "dcc_runs.duckdb"


class RunStore:
    """
    DuckDB-backed store for pipeline run history and AI insights.

    Args:
        db_path: Path to DuckDB file (created if not exists)
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None
        self._init_db()

    def _get_conn(self):
        """Lazy-load DuckDB connection."""
        if self._conn is None:
            try:
                import duckdb
                self._conn = duckdb.connect(str(self.db_path))
            except ImportError:
                logger.warning("[run_store] duckdb not installed — persistence disabled")
                
                # Record error in context if available (non-blocking)
                # Note: This is a utility function, so context may not be available
                # We'll handle this gracefully without breaking the functionality
                
                # Also print to stderr for user visibility (preserved behavior)
                try:
                    from utility_engine.errors import system_error_print
                    system_error_print("S-A-S-0502", detail="duckdb not installed", fatal=False)
                except Exception:
                    pass
        return self._conn

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_conn()
        if conn is None:
            return
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id        VARCHAR PRIMARY KEY,
                timestamp     VARCHAR,
                input_file    VARCHAR,
                total_rows    INTEGER,
                health_score  DOUBLE,
                health_grade  VARCHAR,
                error_count   INTEGER,
                ai_risk_level VARCHAR,
                output_csv    VARCHAR,
                output_excel  VARCHAR,
                schema_version VARCHAR
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_insights (
                run_id           VARCHAR PRIMARY KEY,
                timestamp        VARCHAR,
                risk_level       VARCHAR,
                executive_summary VARCHAR,
                insight_json     VARCHAR,
                model_used       VARCHAR,
                provider         VARCHAR,
                fallback_used    BOOLEAN
            )
        """)
        logger.debug("[run_store] DuckDB tables initialised")

    def save_run(self, record: PipelineRunRecord) -> None:
        """
        Persist a pipeline run record.

        Args:
            record: PipelineRunRecord to save
        """
        conn = self._get_conn()
        if conn is None:
            return
        try:
            conn.execute("""
                INSERT OR REPLACE INTO pipeline_runs VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, [
                record.run_id, record.timestamp, record.input_file,
                record.total_rows, record.health_score, record.health_grade,
                record.error_count, record.ai_risk_level,
                record.output_csv, record.output_excel, record.schema_version,
            ])
            logger.info(f"[run_store] Saved run {record.run_id}")
        except Exception as exc:
            logger.warning(f"[run_store] Failed to save run: {exc}")

    def save_insight(self, insight: AiInsight) -> None:
        """
        Persist an AI insight payload.

        Args:
            insight: AiInsight to save
        """
        conn = self._get_conn()
        if conn is None:
            return
        try:
            conn.execute("""
                INSERT OR REPLACE INTO ai_insights VALUES (?,?,?,?,?,?,?,?)
            """, [
                insight.run_id, insight.timestamp, insight.risk_level,
                insight.executive_summary, json.dumps(insight.to_dict()),
                insight.model_used, insight.provider, insight.fallback_used,
            ])
            logger.info(f"[run_store] Saved insight {insight.run_id}")
        except Exception as exc:
            logger.warning(f"[run_store] Failed to save insight: {exc}")

    def load_run_history(self, limit: int = 20) -> List[dict]:
        """
        Load recent pipeline run records.

        Args:
            limit: Max number of records to return

        Returns:
            List of run record dicts ordered by timestamp desc
        """
        conn = self._get_conn()
        if conn is None:
            return []
        try:
            rows = conn.execute(
                "SELECT * FROM pipeline_runs ORDER BY timestamp DESC LIMIT ?", [limit]
            ).fetchall()
            cols = [d[0] for d in conn.description]
            return [dict(zip(cols, row)) for row in rows]
        except Exception as exc:
            logger.warning(f"[run_store] Failed to load history: {exc}")
            return []

    def load_insight(self, run_id: str) -> Optional[dict]:
        """
        Load a specific AI insight by run_id.

        Args:
            run_id: Run UUID

        Returns:
            Insight dict or None
        """
        conn = self._get_conn()
        if conn is None:
            return None
        try:
            row = conn.execute(
                "SELECT insight_json FROM ai_insights WHERE run_id = ?", [run_id]
            ).fetchone()
            if row:
                return json.loads(row[0])
        except Exception as exc:
            logger.warning(f"[run_store] Failed to load insight: {exc}")
        return None

    def close(self) -> None:
        """Close DuckDB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
