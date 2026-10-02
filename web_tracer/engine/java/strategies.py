"""engine/java/strategies.py — method-level instrumentation strategy selection (T31, §8.4).

The OTel Java agent only instruments the *framework* layer by default (one ``POST /api/...``
handler span, no business methods — workplan §7.4). To get nested Controller/Service/Repository
spans we pick one of four strategies. The workplan's decision (Q1) is ``spring_aop`` for a
non-dcc Java target; for ``dcc`` (Python) the analogous registry is the OTel Python SDK + a
``@traced`` decorator. ``select_strategy("auto")`` probes the project and returns the best fit.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AgentConfig:
    name: str
    agent_args: str
    env: dict
    snippets: list[dict]  # [{language, file, content}]
    nested_ok: bool
    probe_hint: str


@dataclass
class ProbeResult:
    applicable: bool
    reason: str


# Java resource templates live next to this module.
RESOURCES = Path(__file__).parent / "java_resources"


class JavaMethodInstrumentation(ABC):
    name: str = "base"
    nested_ok: bool = False
    probe_hint: str = ""

    @abstractmethod
    def probe(self, project_path: Optional[Path]) -> ProbeResult: ...

    @abstractmethod
    def emit_config(self, project_path: Optional[Path]) -> AgentConfig: ...

    def _read(self, name: str) -> str:
        p = RESOURCES / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def _snippet(self, name: str, language: str) -> dict:
        return {"language": language, "file": name, "content": self._read(name)}


class FrameworkOnlyStrategy(JavaMethodInstrumentation):
    name = "framework_only"
    nested_ok = False
    probe_hint = (
        "No business-code change; the agent instruments the framework layer only "
        "(handler + storage). UI shows 'no method-level spans'."
    )

    def probe(self, project_path: Optional[Path]) -> ProbeResult:
        return ProbeResult(True, "always applicable as the fallback")

    def emit_config(self, project_path: Optional[Path]) -> AgentConfig:
        return AgentConfig(
            name=self.name,
            agent_args="-javaagent:opentelemetry-javaagent.jar",
            env={},
            snippets=[],
            nested_ok=self.nested_ok,
            probe_hint=self.probe_hint,
        )


class SpringAopStrategy(JavaMethodInstrumentation):
    name = "spring_aop"
    nested_ok = True
    probe_hint = (
        "Requires Spring + an AOP dependency; adds one @Around aspect (no business-code edits). "
        "Correct nesting."
    )

    def probe(self, project_path: Optional[Path]) -> ProbeResult:
        if project_path and (project_path / "pom.xml").exists():
            txt = (project_path / "pom.xml").read_text(encoding="utf-8", errors="ignore")
            if "spring-boot" in txt or "spring-aop" in txt or "springframework" in txt:
                return ProbeResult(True, "Spring Boot / AOP detected in pom.xml")
        if project_path and (project_path / "build.gradle").exists():
            txt = (project_path / "build.gradle").read_text(encoding="utf-8", errors="ignore")
            if "spring" in txt:
                return ProbeResult(True, "Spring detected in build.gradle")
        return ProbeResult(False, "no Spring dependency detected")

    def emit_config(self, project_path: Optional[Path]) -> AgentConfig:
        return AgentConfig(
            name=self.name,
            agent_args="-javaagent:opentelemetry-javaagent.jar -Dotel.instrumentation.spring-webmvc.enabled=true",
            env={"OTEL_RESOURCE_ATTRIBUTES": "service.name=web-tracer-target"},
            snippets=[self._snippet("TracedAspect.java", "java"), self._snippet("pom-snippet.xml", "xml")],
            nested_ok=self.nested_ok,
            probe_hint=self.probe_hint,
        )


class WithSpanStrategy(JavaMethodInstrumentation):
    name = "with_span"
    nested_ok = True
    probe_hint = "Edit source: add @WithSpan to each method. Precise but coverage depends on humans."

    def probe(self, project_path: Optional[Path]) -> ProbeResult:
        return ProbeResult(True, "applicable wherever source is editable")

    def emit_config(self, project_path: Optional[Path]) -> AgentConfig:
        return AgentConfig(
            name=self.name,
            agent_args="-javaagent:opentelemetry-javaagent.jar",
            env={},
            snippets=[self._snippet("TracedAspect.java", "java")],
            nested_ok=self.nested_ok,
            probe_hint=self.probe_hint,
        )


class ByteBuddyStrategy(JavaMethodInstrumentation):
    name = "bytebuddy"
    nested_ok = True
    probe_hint = "Zero intrusion; custom Byte Buddy agent (P8). High cost."

    def probe(self, project_path: Optional[Path]) -> ProbeResult:
        return ProbeResult(False, "deferred to P8; not in the main delivery path")

    def emit_config(self, project_path: Optional[Path]) -> AgentConfig:
        return AgentConfig(
            name=self.name,
            agent_args="-javaagent:bytebuddy-agent.jar",
            env={},
            snippets=[],
            nested_ok=self.nested_ok,
            probe_hint=self.probe_hint,
        )


# framework_only | spring_aop | with_span | bytebuddy  (workplan §8.4 REGISTRY)
REGISTRY = {
    "framework_only": FrameworkOnlyStrategy,
    "spring_aop": SpringAopStrategy,
    "with_span": WithSpanStrategy,
    "bytebuddy": ByteBuddyStrategy,
}


def strategy_names() -> list[str]:
    return list(REGISTRY.keys())


def describe_strategies() -> list[dict]:
    """``GET /java/instrumentation/strategies`` payload."""
    out: list[dict] = []
    for name, cls in REGISTRY.items():
        inst = cls()
        out.append({"name": inst.name, "nested_ok": inst.nested_ok, "probe_hint": inst.probe_hint})
    return out


def select_strategy(preference: str = "auto", project_path: Optional[Path] = None) -> JavaMethodInstrumentation:
    """Return the chosen strategy instance.

    An explicit ``preference`` (framework_only | spring_aop | with_span | bytebuddy) is always
    honoured. ``auto`` is non-intrusive: it uses ``spring_aop`` when a Spring project is detected,
    otherwise the zero-code-change ``framework_only`` fallback. ``with_span`` / ``bytebuddy``
    require active code changes or a custom agent, so they are reachable only by explicit
    preference, never silently auto-applied to an arbitrary project.
    """
    if preference != "auto":
        return REGISTRY.get(preference, FrameworkOnlyStrategy)()
    order = ["spring_aop", "framework_only"]
    for name in order:
        inst = REGISTRY[name]()
        if inst.probe(project_path).applicable:
            return inst
    return FrameworkOnlyStrategy()
