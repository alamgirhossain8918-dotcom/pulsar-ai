# PULSAR AI V2.0 — SYSTEM ARCHITECTURE

## 1. High-Level Architecture

PULSAR AI V2.0 is designed as a cloud-native, event-driven quantitative crypto futures analysis and signal platform built around Inner Circle Trader (ICT) and Smart Money Concepts (SMC).

```
                      +---------------------------------------+
                      |          MARKET DATA FEEDS           |
                      |  Primary: Binance USD-M Futures (REST)|
                      |  Fallback: Bybit Linear Perpetuals    |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |         MARKET FEED MANAGER          |
                      |  - Failover orchestration             |
                      |  - Closed-candle isolation            |
                      |  - Stale/missing data guard           |
                      |  - Labeled DEMO fallback              |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |         ICT / SMC ENGINE              |
                      |  - Swing Fractals & Displacement      |
                      |  - Market Structure (BOS / CHoCH)     |
                      |  - Liquidity Sweeps (BSL, SSL, Sess)  |
                      |  - FVGs & Order Blocks / Breakers     |
                      |  - Dealing Range / Equilibrium / OTE  |
                      |  - Market Regime Classification       |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |     CONFLUENCE SCORER & GATES        |
                      |  - Weighted 0-100 confluence score    |
                      |  - Min score: 70/100                  |
                      |  - Min RR: 1:2.0                      |
                      |  - Rejection on unclear market        |
                      +-------------------+-------------------+
                                          |
                         +----------------+----------------+
                         |                                 |
                         v                                 v
        +---------------------------------+  +-------------------------------+
        |    SIGNAL LIFECYCLE & RISK      |  |    EVENT-DRIVEN BACKTESTER    |
        |  - Pending -> Triggered -> TP/SL|  |  - No look-ahead bias         |
        |  - Partial TP (50%/30%/20%)     |  |  - Closed candles only        |
        |  - Trailing Stop to Breakeven   |  |  - Conservative same-candle   |
        |  - Position Sizing & Liquidation|  |  - Realistic fees & slippage  |
        +----------------+----------------+  +-------------------------------+
                         |
                         v
        +---------------------------------+
        |     NOTIFICATIONS & STREAM      |
        |  - Telegram Bot Push Alerts     |
        |  - WebSocket Client Broadcast   |
        +----------------+----------------+
                         |
         +---------------+---------------+
         |                               |
         v                               v
+------------------+           +------------------+
|   RAILWAY HOST   |           |   VERCEL EDGE    |
|  - FastAPI (REST)|           |  - Next.js 14    |
|  - Cloud Worker  |           |  - TradingView   |
+--------+---------+           |    Lightweight   |
         |                     |    Charts        |
         |                     +------------------+
         v
+------------------+
|   SUPABASE PG    |
|  - 18 DB Tables  |
|  - RLS Policies  |
+------------------+
```

## 2. Core Modules

1. **Market Data Layer (`backend/app/data/`)**:
   - `BinanceFuturesClient`: Connects to `https://fapi.binance.com` for public klines and tickers.
   - `BybitFuturesClient`: Secondary fallback connecting to `https://api.bybit.com/v5`.
   - `MarketFeedManager`: Strict isolation rule — never mixes Binance and Bybit candles within a single analysis run.

2. **ICT/SMC Engine (`backend/app/indicators/`, `backend/app/market_structure/`, `backend/app/liquidity/`, `backend/app/engine/`)**:
   - **Market Structure**: Detects displacement candles (> 1.4x ATR with high volume and solid body), fractal swing highs/lows, Bullish/Bearish BOS, and CHoCH character changes.
   - **Liquidity**: Tracks BSL/SSL pools, equal highs/lows (EQH/EQL within 0.1% tolerance), wick sweeps followed by closing rejection, and Session Highs/Lows (Asia, London, New York).
   - **Fair Value Gaps**: 3-candle imbalance zones (Bullish & Bearish), mitigation retests, invalidation, and Inverse FVGs.
   - **Order Blocks**: Last opposite candle preceding displacement structure breaks, 50% mean threshold validation, and Breaker Block conversion.
   - **Premium / Discount / OTE**: 50% equilibrium level and 0.62–0.79 Fibonacci retracement zones.

3. **Risk Management & Position Sizing (`backend/app/risk/calculator.py`)**:
   - Computes required margin, position size in tokens, fees (0.05% taker), slippage (0.02%), and approximate liquidation distance.
   - Warns on excessive leverage (> 25x) and tight stops (< 0.25%).

4. **Signal Lifecycle State Machine (`backend/app/signals/lifecycle.py`)**:
   - State flow: `Pending` -> `Triggered` -> `TP1 Hit` (scales 50%, moves SL to breakeven) -> `TP2 Hit` (scales 30%) -> `TP3 Hit` (scales 20%, closes trade).
   - Downside flow: `Triggered` -> `SL Hit` (exits trade, records net PnL).
   - Cooldown: 30-minute block per symbol to prevent repetitive churn.

5. **Backtesting Engine (`backend/app/backtesting/engine.py`)**:
   - Chronological bar-by-bar iteration.
   - Conservative same-candle resolution: if both TP and SL are touched within the same candle, assumes the Stop Loss was hit first.

6. **Virtual Paper Trading Desk (`backend/app/paper_trading/paper_engine.py`)**:
   - Virtual account with 10,000 USDT initial balance.
   - Pure simulated execution requiring zero exchange trading keys.
