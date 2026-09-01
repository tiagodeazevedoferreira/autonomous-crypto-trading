from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ExternalSignal:
    """Provider-neutral market evidence.

    Providers must leave unavailable fields as None rather than inventing data.
    """

    instrument: str
    timestamp: datetime
    direction: Direction = Direction.UNKNOWN
    confidence: float | None = None
    entry: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    support: float | None = None
    resistance: float | None = None
    sentiment: float | None = None
    source: str = "unknown"
    source_version: str | None = None
    raw_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.instrument:
            raise ValueError("instrument is required")
        if not 0 <= (self.confidence if self.confidence is not None else 0.0) <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.sentiment is not None and not -1 <= self.sentiment <= 1:
            raise ValueError("sentiment must be between -1 and 1")

    @property
    def age_seconds(self) -> float:
        now = datetime.now(timezone.utc)
        timestamp = self.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return max(0.0, (now - timestamp).total_seconds())


@dataclass(frozen=True)
class FusedSignal:
    instrument: str
    direction: Direction
    score: float
    confidence: float
    sources: tuple[str, ...]
    blocked: bool = False
    reasons: tuple[str, ...] = ()


class SignalFusion:
    """Small, deterministic evidence combiner.

    This is intentionally not a predictive model. Its job is to combine
    independent provider evidence before the ML/Decision/Risk layers.
    """

    def __init__(self, weights: dict[str, float] | None = None, min_confidence: float = 0.60) -> None:
        self.weights = weights or {
            "brainchain": 1.0,
            "doto_ai": 1.0,
            "trading_central": 1.0,
        }
        self.min_confidence = min_confidence

    def fuse(self, signals: list[ExternalSignal]) -> FusedSignal:
        if not signals:
            raise ValueError("at least one signal is required")

        instrument = signals[0].instrument
        if any(s.instrument != instrument for s in signals):
            raise ValueError("all signals must reference the same instrument")

        weighted = 0.0
        total_weight = 0.0
        reasons: list[str] = []
        for signal in signals:
            weight = self.weights.get(signal.source, 1.0)
            confidence = signal.confidence or 0.0
            if signal.direction is Direction.LONG:
                value = confidence
            elif signal.direction is Direction.SHORT:
                value = -confidence
            else:
                value = 0.0
            weighted += value * weight
            total_weight += weight

        score = weighted / total_weight if total_weight else 0.0
        confidence = min(1.0, abs(score))
        direction = Direction.NEUTRAL
        if score > 0:
            direction = Direction.LONG
        elif score < 0:
            direction = Direction.SHORT

        if confidence < self.min_confidence:
            reasons.append("fused confidence below execution threshold")

        return FusedSignal(
            instrument=instrument,
            direction=direction,
            score=score,
            confidence=confidence,
            sources=tuple(sorted({s.source for s in signals})),
            blocked=bool(reasons),
            reasons=tuple(reasons),
        )
