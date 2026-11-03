# PULSAR AI V2.0 — TRADING OPERATIONAL USER GUIDE

## 1. Overview

PULSAR AI V2.0 assists quantitative crypto traders by automating Inner Circle Trader (ICT) and Smart Money Concepts (SMC) market structure and liquidity analysis.

## 2. Navigating the 13 Dashboard Sections

1. **Dashboard**: High-level command center showing active market regimes, priority assets (BTC, ETH, SOL), top signals, and live scanner previews.
2. **Live Scanner**: Comprehensive real-time table of all active USDT perpetual futures pairs. Displays displacement events, liquidity sweeps, unmitigated FVGs, active Order Blocks, and current dealing zones.
3. **Market Analysis**: Interactive TradingView Lightweight Charts with candlestick data, multi-timeframe indicators, swing highs/lows, and institutional BOS/CHoCH markers.
4. **Signals**: Filterable repository of algorithmic BUY and SELL signals with quality scores (0–100) and risk/reward ratios.
5. **Signal Details**: Granular breakdown of a signal's confluence checklist, higher timeframe bias, lower timeframe confirmation, and invalidation criteria.
6. **Backtester**: Event-driven historical simulation engine with zero look-ahead bias, closed-candle confirmation, realistic fee/slippage modeling, and conservative same-candle tie-breaker assumptions.
7. **Paper Trading**: Virtual trading desk with real-time mark-to-market valuations, position scaling, and historical trade logs without risking real capital.
8. **Performance**: Real-time statistical dashboard showing win rate, profit factor, maximum drawdown, and directional (Long vs Short) asymmetries.
9. **Strategy Settings**: Configurable confluence thresholds (default 70/100), minimum RR gates (default 1:2.0), and asset cooldown windows.
10. **Risk Management**: Precision position sizing calculator computing margin requirements, fee deductions, and approximate liquidation warnings.
11. **Telegram Bot**: Configure notification preferences for instant push alerts on your phone.
12. **System Health**: Infrastructure telemetry monitoring exchange latencies, cloud worker lease status, and WebSocket client connections.
13. **Owner Login**: Secure session login protecting settings and administrative actions.

## 3. How Signals are Generated

Every signal passes through strict institutional quality gates:
1. **Higher Timeframe Bias**: 4H/1D trend alignment.
2. **Liquidity Sweep**: Wick piercing Buy-Side (BSL) or Sell-Side (SSL) retail stop clusters.
3. **Market Structure Shift**: Closed-candle Change of Character (CHoCH) with displacement.
4. **Point of Interest Retest**: Price returning into an unmitigated Fair Value Gap (FVG) or Order Block inside the Optimal Trade Entry (OTE 0.62–0.79) zone.
5. **Quality Gates**: Confluence score must be $\ge 70/100$ and Risk/Reward must be $\ge 1:2.0$. If conditions are ambiguous, the engine outputs **NO TRADE**.
