from datetime import datetime, timezone
import unittest

from brainchain.intelligence import Direction, ExternalSignal, SignalFusion
from brainchain.providers.doto import DotoSignalAdapter
from brainchain.risk import RiskGate


class ExternalIntelligenceTests(unittest.TestCase):
    def test_doto_signal_normalization(self) -> None:
        signal = DotoSignalAdapter().normalize(
            {
                "direction": "BUY",
                "confidence": 75,
                "entry": 100,
                "stop_loss": 95,
                "take_profit": 110,
            },
            instrument="BTC/USD",
        )
        self.assertEqual(signal.direction, Direction.LONG)
        self.assertAlmostEqual(signal.confidence or 0, 0.75)
        self.assertEqual(signal.source, "doto_ai")

    def test_conflicting_signals_do_not_create_high_confidence_trade(self) -> None:
        now = datetime.now(timezone.utc)
        signals = [
            ExternalSignal("BTC/USD", now, Direction.LONG, 0.8, source="brainchain"),
            ExternalSignal("BTC/USD", now, Direction.SHORT, 0.8, source="doto_ai"),
        ]
        fused = SignalFusion(min_confidence=0.60).fuse(signals)
        decision = RiskGate().evaluate(fused, dry_run=True)
        self.assertFalse(decision.allowed)

    def test_single_strong_signal_is_blocked_by_missing_independent_evidence(self) -> None:
        now = datetime.now(timezone.utc)
        fused = SignalFusion(min_confidence=0.60).fuse([
            ExternalSignal("BTC/USD", now, Direction.LONG, 0.95, source="doto_ai")
        ])
        self.assertEqual(fused.direction, Direction.LONG)
        decision = RiskGate().evaluate(fused, dry_run=True)
        self.assertFalse(decision.allowed)
        self.assertIn("independent evidence threshold not met", decision.reasons)


if __name__ == "__main__":
    unittest.main()
