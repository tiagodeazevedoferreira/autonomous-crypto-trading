# BrAInChain — Architecture Baseline

## Objective

Evolve Freqtrade into an autonomous crypto-trading intelligence platform while preserving Freqtrade as the trading, strategy, backtesting and execution foundation wherever practical.

## Initial boundary

```text
Market data
    ↓
Freqtrade / CCXT
    ↓
Strategy + FreqAI
    ↓
Signal / Decision layer
    ↓
Risk layer
    ↓
Execution
```

BrAInChain modules will be added around this core rather than rewriting Freqtrade prematurely.

## Planned intelligence layers

```text
                    BrAInChain
                        │
        ┌───────────────┼────────────────┐
        ↓               ↓                ↓
 Market Intelligence  On-chain        Social/News
        │              Intelligence    Intelligence
        └───────────────┼────────────────┘
                        ↓
                 Feature Engineering
                        ↓
                  ML Ensemble
                        ↓
                Regime Detection
                        ↓
                Decision Engine
                        ↓
                   Risk Engine
                        ↓
                Portfolio Engine
                        ↓
                 Execution Layer
```

## New-token path

```text
Token discovery
    ↓
Contract/security screening
    ↓
Liquidity + volume analysis
    ↓
Holder/wallet/smart-money analysis
    ↓
Social/community velocity
    ↓
Feature construction
    ↓
Opportunity scoring
    ↓
Risk gate
    ↓
Execution eligibility
```

A high predicted return must never override a failed security or liquidity gate.

## Exchange decision

The first venue is OKX Spot. For the initial phase, Freqtrade will use **dry-run** against OKX market data. The OKX Demo API credentials already created by the operator are retained for a later controlled integration test.

Important compatibility constraint: current Freqtrade's generic `demo_trading` mechanism is not equivalent to saying every exchange's demo environment is supported. The current Freqtrade release notes explicitly document Demo mode for Bybit, while the current exchange code gates demo support through an exchange capability flag. Therefore, we will not set `exchange.demo_trading=true` for OKX until the repository's pinned Freqtrade/CCXT versions are verified and a dedicated compatibility test passes.

If authenticated OKX Demo order execution is required, BrAInChain will implement a project-owned OKX Demo adapter with a single order-writer boundary and explicit safety gates rather than silently routing Demo credentials through an unsupported Freqtrade path.

## Safety principles

- No production API credentials in Git.
- No withdrawal permission for trading keys.
- Dry-run before any authenticated order-writing test.
- No automatic Demo → Live fallback.
- One authoritative order writer at a time.
- Every live/demo execution path must have an explicit risk gate.
- Backtests must account for fees, slippage and realistic execution assumptions.
- ML evaluation must guard against look-ahead bias and data leakage.
