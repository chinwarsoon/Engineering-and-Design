"""
AI Ops Engine — Ollama Provider

Local LLM adapter for Ollama. Calls the Ollama chat API and parses
the structured JSON response into an AiInsight.
Breadcrumb: ctx → format_context_for_prompt() → POST /api/chat → parse → AiInsight
"""

from __future__ import annotations
import json
import logging
import re
import urllib.request
import urllib.error
from typing import Optional

from ..core.contracts import AiContext, AiInsight, RiskItem, TrendItem
from ..core.context_builder import format_context_for_prompt
from .base import BaseProvider, RuleBasedProvider

try:
    from utility_engine.errors import system_error_print
except ImportError:
    def system_error_print(*args, **kwargs): pass

try:
    from utility_engine.console import milestone_print
except ImportError:
    def milestone_print(*args, **kwargs): pass

logger = logging.getLogger(__name__)

_OLLAMA_URL = "http://localhost:11434/api/chat"
_TIMEOUT = 120  # seconds


class OllamaProvider(BaseProvider):
    """
    Ollama local LLM provider.

    Sends the formatted context prompt to Ollama and parses the
    structured JSON response. Falls back to RuleBasedProvider on
    any connection or parse error.

    Phase 5.6: This provider is metadata-free — no model names, sizes,
    or families are hardcoded. The model name is supplied by the caller
    (which in turn resolves it from the schema-driven model_pool in
    AiOpsEngine._resolve_model_selection). Optional `model_metadata` is
    used only for logging/explainability, never for selection logic.

    Args:
        model: Ollama model name (must be supplied by caller; no default)
        base_url: Ollama API base URL
        timeout: Request timeout in seconds
        model_metadata: Optional schema-driven model_entry dict for
            logging context (family, capability, size_gb). Never used
            for control flow.
    """

    def __init__(
        self,
        model: str,
        base_url: str = _OLLAMA_URL,
        timeout: int = _TIMEOUT,
        model_metadata: Optional[dict] = None,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.model_metadata = model_metadata
        self._fallback = RuleBasedProvider()

    def generate(self, ctx: AiContext) -> AiInsight:
        """
        Generate AI insight via Ollama chat API.

        Args:
            ctx: Populated AiContext

        Returns:
            AiInsight from LLM or fallback if unavailable
        """
        prompt = format_context_for_prompt(ctx)
        try:
            raw = self._call_ollama(prompt)
            insight = self._parse_response(raw, ctx)
            insight.model_used = self.model
            insight.provider = "ollama"
            insight.fallback_used = False
            logger.info(f"[ollama] Generated insight: risk={insight.risk_level}")
            milestone_print("MILESTONE_AI_INSIGHT", f"Ollama insight generated — risk={insight.risk_level}", ok=True)
            return insight
        except Exception as exc:
            logger.warning(f"[ollama] Provider failed ({exc}), using rule-based fallback")
            system_error_print("S-A-S-0504", detail=str(exc), fatal=False)
            return self._fallback.generate(ctx)

    def _call_ollama(self, prompt: str) -> str:
        """
        POST to Ollama /api/chat and return the full response text.

        Args:
            prompt: Formatted prompt string

        Returns:
            Concatenated response content string
        """
        payload = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "options": {"temperature": 0.1, "num_predict": 2048},
        }).encode("utf-8")

        req = urllib.request.Request(
            self.base_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        content_parts = []
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            for line in resp:
                line = line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    part = chunk.get("message", {}).get("content", "")
                    if part:
                        content_parts.append(part)
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

        return "".join(content_parts)

    def _parse_response(self, raw: str, ctx: AiContext) -> AiInsight:
        """
        Parse LLM response into AiInsight.

        Extracts JSON block from response text. Falls back to
        rule-based insight if JSON is malformed.

        Args:
            raw: Raw LLM response string
            ctx: Original context (for run_id)

        Returns:
            Parsed AiInsight
        """
        # Extract JSON block from response
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            logger.warning("[ollama] No JSON block found in response, using fallback")
            system_error_print("S-A-S-0505", detail="No JSON block in response", fatal=False)
            return self._fallback.generate(ctx)

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as exc:
            logger.warning(f"[ollama] JSON parse error: {exc}, using fallback")
            system_error_print("S-A-S-0505", detail=str(exc), fatal=False)
            return self._fallback.generate(ctx)

        # Build RiskItems
        risks = []
        for r in data.get("top_risks", []):
            risks.append(RiskItem(
                title=r.get("title", ""),
                description=r.get("description", ""),
                severity=r.get("severity", "MEDIUM"),
                affected_rows=int(r.get("affected_rows", 0)),
                error_codes=r.get("error_codes", []),
                columns=r.get("columns", []),
                recommendation=r.get("recommendation", ""),
            ))

        # Build TrendItems
        trends = []
        for t in data.get("trends", []):
            trends.append(TrendItem(
                pattern=t.get("pattern", ""),
                frequency=int(t.get("frequency", 0)),
                error_code=t.get("error_code", ""),
                phases=t.get("phases", []),
            ))

        return AiInsight(
            run_id=ctx.run_id,
            risk_level=data.get("risk_level", "MEDIUM"),
            executive_summary=data.get("executive_summary", ""),
            top_risks=risks,
            trends=trends,
            recommendations=data.get("recommendations", []),
        )

    def is_available(self) -> bool:
        """
        Check if Ollama is running and the model is available.

        Phase 5.6: Adds defense-in-depth memory check using
        model_metadata (if provided) — if the model's required RAM
        exceeds available RAM + headroom, returns False even if Ollama
        is running. This complements the engine-level selector and
        prevents loading a model that would OOM the host.

        Returns:
            True if Ollama responds to a health check AND the model
            passes the memory check.
        """
        if not self.model:
            logger.warning("[ollama] No model name supplied to provider")
            return False

        # Defense-in-depth memory check (uses schema-provided metadata)
        if isinstance(self.model_metadata, dict):
            try:
                import psutil
                size_gb = float(self.model_metadata.get("size_gb", 0))
                mult = float(self.model_metadata.get("ram_multiplier", 1.5))
                headroom_gb = float(
                    self.model_metadata.get("model_memory_headroom_gb", 2.0)
                )
                required_gb = size_gb * mult
                available_gb = psutil.virtual_memory().available / (1024 ** 3)
                if required_gb + headroom_gb > available_gb:
                    logger.warning(
                        f"[ollama] Memory check failed: model={self.model} "
                        f"requires {required_gb:.2f}GB + {headroom_gb:.2f}GB "
                        f"headroom, only {available_gb:.2f}GB available"
                    )
                    return False
            except Exception:
                # If psutil missing or metadata malformed, fall through
                # to standard health check rather than fail closed.
                pass

        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                models = [m.get("name", "") for m in data.get("models", [])]
                available = any(self.model in m for m in models)
                logger.info(f"[ollama] Available={available}, model={self.model}")
                return available
        except Exception as exc:
            logger.warning(f"[ollama] Ollama server not available: {exc}")
            system_error_print("S-A-S-0503", detail=str(exc), fatal=False)
            return False
