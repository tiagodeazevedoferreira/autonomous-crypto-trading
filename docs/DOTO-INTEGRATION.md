# BrAInChain — Doto / Trading Central Integration

## Purpose

This document defines the integration boundary for Doto intelligence and execution. The project must treat Doto and Trading Central as **external intelligence/execution services**, not as the authoritative decision maker.

## Confirmed Doto capabilities

Doto documents AI Market Insights powered by AI and Trading Central. Its analysis includes support/resistance, technical indicators, recent news and Doto account safety level. Doto can use a generated signal to construct a trade with stop-loss and take-profit. Doto also documents MT5 support and automated Expert Advisors.

Sources:
- https://help.doto.com/en/articles/14328468-trading-with-ai-insights-smart-tools-for-smarter-trades
- https://help.doto.com/en/articles/10721605-metatrader-5
- https://help.doto.com/en/articles/10722628-trading-bots

## Confirmed Trading Central API surface

Trading Central publishes an API v3/v4/v5 documentation set with authentication plus technical summaries, support/resistance, stops, instrument events, article analytics/sentiment, latest articles, economic events, anticipated events and Storyteller endpoints.

Source: https://global.tradingcentral.com/api/doc.html

The implementation therefore uses an adapter boundary instead of embedding provider-specific logic in the Decision Engine.

## Architecture

```text
                         BrAInChain
                              |
             +----------------+----------------+
             |                |                |
          Internal         Doto AI       Trading Central
        Intelligence      Insights            API
             |                |                |
             +----------------+----------------+
                              |
                       Signal Fusion
                              |
                       Decision Engine
                              |
                         Risk Engine
                              |
                    Execution Eligibility
                              |
                    +---------+---------+
                    |                   |
                 Dry-run             MT5/EA
                    |                   |
                    +---------+---------+
                              |
                             Doto
```

## Safety boundary

1. Doto/Trading Central signals are evidence, never direct authorization.
2. A provider outage must degrade to `NO_TRADE` or internal-only operation; it must never bypass risk controls.
3. No Doto credentials, Trading Central secrets or MT5 credentials may be committed to Git.
4. No production order writer is enabled by this integration.
5. The first execution target is demo/dry-run validation.
6. There is no automatic Demo -> Live fallback.
7. Only one component may own order writing at a time.
8. Provider timestamps and source identifiers must be retained for auditability.

## Normalized signal contract

All providers must normalize to the same conceptual fields:

- `instrument`
- `timestamp`
- `direction`: `LONG`, `SHORT`, `NEUTRAL`, `UNKNOWN`
- `confidence`: 0..1 when available
- `entry`
- `stop_loss`
- `take_profit`
- `support`
- `resistance`
- `sentiment`
- `source`
- `source_version`
- `raw_reference`

Missing provider fields remain null. The adapter must never fabricate values.

## Phase 1 implemented in this repository

- Provider-neutral `ExternalSignal` model.
- Doto signal ingestion boundary for future observed/exported Doto signals.
- Trading Central REST client with explicit authentication boundary and configurable endpoint paths.
- Signal fusion engine that combines independent evidence without allowing any provider to force a trade.
- Risk gate that blocks execution when evidence is incomplete, confidence is insufficient, or a provider is stale.
- MT5/Doto execution remains a separate adapter and is not activated by the intelligence integration.

## Phase 2

- Obtain/validate Trading Central API credentials and instrument identifiers.
- Exercise the read-only endpoints in a controlled environment.
- Map Doto AI Market Insights observations from the user's account to the normalized contract.
- Compare Doto AI vs Trading Central vs BrAInChain predictions over the same timestamps.
- Add calibration/backtesting of provider signals before any order-writing test.

## Phase 3

- Implement the MT5 Expert Advisor bridge for Doto demo.
- Make the Risk Engine the sole authorization point.
- Run shadow trading, then demo execution, with complete event/audit logging.
