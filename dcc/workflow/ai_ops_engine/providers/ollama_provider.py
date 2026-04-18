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

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "llama3.1:8b"
_OLLAMA_URL = "http://localhost:11434/api/chat"
_TIMEOUT = 120  # seconds


class OllamaProvider(BaseProvider):
    """
    Ollama local LLM provider.

    Sends the formatted context prompt to Ollama and parses the
    structured JSON response. Falls back to RuleBasedProvider on
    any connection or parse error.

    Args:
        model: Ollama model name (default: llama3.1:8b)
        base_url: Ollama API base URL
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        base_url: str = _OLLAMA_URL,
        timeout: int = _TIMEOUT,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
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
            return insight
        except Exception as exc:
            logger.warning(f"[ollama] Provider failed ({exc}), using rule-based fallback")
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
            return self._fallback.generate(ctx)

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as exc:
            logger.warning(f"[ollama] JSON parse error: {exc}, using fallback")
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

        Returns:
            True if Ollama responds to a health check
        """
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
        except Exception:
            return False
