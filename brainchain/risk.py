from __future__ import annotations

from dataclasses import dataclass

from brainchain.intelligence import FusedSignal


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reasons: tuple[str, ...]


class RiskGate:
    """Execution authorization boundary.

    Provider signals can contribute evidence but can never bypass this gate.
    """

    def __init__(
        self,
        *,
        min_confidence: float = 0.60,
        min_sources: int = 2,
        max_signal_age_seconds: int = 900,
    ) -> None:
        self.min_confidence = min_confidence
        self.min_sources = min_sources
        self.max_signal_age_seconds = max_signal_age_seconds

    def evaluate(
        self,
        fused: FusedSignal,
        *,
        signal_age_seconds: float | None = None,
        dry_run: bool = True,
    ) -> RiskDecision:
        reasons = list(fused.reasons)
        if fused.blocked:
            reasons.append("signal fusion blocked execution")
        if fused.direction.value in {"NEUTRAL", "UNKNOWN"}:
            reasons.append("no actionable direction")
        if fused.confidence < self.min_confidence:
            reasons.append("risk confidence threshold not met")
        if len(fused.sources) < self.min_sources:
            reasons.append("independent evidence threshold not met")
        if signal_age_seconds is not None and signal_age_seconds > self.max_signal_age_seconds:
            reasons.append("signal is stale")
        if not dry_run:
            reasons.append("live execution is disabled in Phase 1")

        return RiskDecision(allowed=not reasons, reasons=tuple(dict.fromkeys(reasons)))
