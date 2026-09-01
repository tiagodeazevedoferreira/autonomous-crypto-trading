from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from brainchain.intelligence import Direction, ExternalSignal


class DotoSignalAdapter:
    """Normalize an observed/exported Doto AI Market Insight.

    This adapter deliberately does not scrape or automate the Doto web UI.
    It accepts provider data supplied by an approved integration/export path.
    """

    SOURCE = "doto_ai"

    @staticmethod
    def _direction(value: Any) -> Direction:
        if value is None:
            return Direction.UNKNOWN
        normalized = str(value).strip().upper()
        mapping = {
            "BUY": Direction.LONG,
            "BULLISH": Direction.LONG,
            "LONG": Direction.LONG,
            "SELL": Direction.SHORT,
            "BEARISH": Direction.SHORT,
            "SHORT": Direction.SHORT,
            "NEUTRAL": Direction.NEUTRAL,
        }
        return mapping.get(normalized, Direction.UNKNOWN)

    @staticmethod
    def _number(payload: dict[str, Any], *keys: str) -> float | None:
        for key in keys:
            value = payload.get(key)
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    continue
        return None

    def normalize(self, payload: dict[str, Any], *, instrument: str, timestamp: datetime | None = None) -> ExternalSignal:
        confidence = self._number(payload, "confidence", "confidence_score")
        if confidence is not None and confidence > 1:
            confidence /= 100.0

        return ExternalSignal(
            instrument=instrument,
            timestamp=timestamp or datetime.now(timezone.utc),
            direction=self._direction(payload.get("direction") or payload.get("signal") or payload.get("recommendation")),
            confidence=confidence,
            entry=self._number(payload, "entry", "entry_price"),
            stop_loss=self._number(payload, "stop_loss", "stopLoss", "sl"),
            take_profit=self._number(payload, "take_profit", "takeProfit", "tp", "target"),
            support=self._number(payload, "support", "support_level"),
            resistance=self._number(payload, "resistance", "resistance_level"),
            sentiment=self._number(payload, "sentiment", "sentiment_score"),
            source=self.SOURCE,
            source_version=str(payload.get("version")) if payload.get("version") is not None else None,
            raw_reference=str(payload.get("id")) if payload.get("id") is not None else None,
            metadata={"provider_payload_keys": sorted(payload.keys())},
        )
