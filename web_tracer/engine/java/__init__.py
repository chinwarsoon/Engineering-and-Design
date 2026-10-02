"""engine/java — Java (and OTel) runtime capture (workplan Phase 3, T29-T33, §8.4)."""
from engine.java.otlp_receiver import OtlpReceiver
from engine.java.otlp_decode import ProtobufUnavailable, decode
from engine.java.strategies import (
    AgentConfig,
    FrameworkOnlyStrategy,
    JavaMethodInstrumentation,
    SpringAopStrategy,
    WithSpanStrategy,
    ByteBuddyStrategy,
    describe_strategies,
    select_strategy,
    strategy_names,
)
from engine.java.source_mapper import SourceMapper, SourceLocation

__all__ = [
    "OtlpReceiver",
    "ProtobufUnavailable",
    "decode",
    "AgentConfig",
    "FrameworkOnlyStrategy",
    "JavaMethodInstrumentation",
    "SpringAopStrategy",
    "WithSpanStrategy",
    "ByteBuddyStrategy",
    "describe_strategies",
    "select_strategy",
    "strategy_names",
    "SourceMapper",
    "SourceLocation",
]
