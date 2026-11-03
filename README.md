# PULSAR AI V2.0 — Quantitative Crypto Futures Platform

**PULSAR AI V2.0** is an enterprise-grade, cloud-native quantitative crypto futures analysis, signal generation, backtesting, and virtual paper trading platform based on **Inner Circle Trader (ICT)** and **Smart Money Concepts (SMC)**.

---

## ⚡ Core Capabilities

- **Institutional Market Data**: Continuous multi-timeframe feeds from **Binance USDⓈ-M Futures** (Primary) with automated failover to **Bybit Linear Perpetuals** (Fallback). Strict data isolation ensures feeds are never mixed.
- **ICT / SMC Core Engine**:
  - Fractal Swing Highs & Lows, Displacement Impulse detection.
  - Break of Structure (Bullish/Bearish BOS) & Change of Character (Bullish/Bearish CHoCH).
  - Buy-Side (BSL) & Sell-Side (SSL) Liquidity Sweeps, Equal Highs/Lows (EQH/EQL), and Session Levels (Asia, London, New York, PDH/PDL, PWH/PWL).
  - Fair Value Gaps (Bullish, Bearish, Inverse IFVG, Mitigations, and Invalidation).
  - Institutional Order Blocks & Breaker Blocks with 50% Mean Threshold checks.
  - Dealing Ranges, 50% Equilibrium, Premium & Discount Zones, and OTE (0.62–0.79).
- **Market Regime Detection**: Classifies Strong Bullish, Bullish, Neutral, Bearish, Strong Bearish, Ranging, High Volatility, and Low Volatility.
- **Strict Quality Gates**: Algorithmic confluence score (0–100, min 70/100 threshold) and minimum Risk/Reward ratio (min 1:2.0). Closed-candle confirmation only; no repainting; NO TRADE on unclear markets.
- **Risk Calculator**: Position sizing, notional value, margin, fee deductions (0.05%), slippage (0.02%), and approximate liquidation distance warnings.
- **Event-Driven Backtester**: Zero look-ahead bias, closed candles only, conservative same-candle tie-breaker resolution.
- **Virtual Paper Trading Desk**: Zero real capital risk. Never stores or requires private exchange API trading keys.
- **Telegram Bot Notifications**: Real-time push alerts for new signals, triggers, TP1/TP2/TP3 hits, and SL hits.
- **Modern Responsive Dashboard**: 13 full pages built with Next.js 14, React, TypeScript, Tailwind CSS, and TradingView Lightweight Charts.

---

## 🚀 Cloud Deployment Architecture

- **Source Control**: GitHub (`alamgirhossain8918-dotcom/pulsar-ai`)
- **Database**: Supabase Managed PostgreSQL with Row Level Security (RLS)
- **Backend & Background Scanner Worker**: Railway Container Platform
- **Frontend CDN**: Vercel Edge Network
- **Push Alerts**: Telegram Bot API

---

## 📁 Project Structure

```
pulsar-ai/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST routes and WebSocket streaming
│   │   ├── core/            # Configuration, security, logging, exceptions
│   │   ├── data/            # Binance & Bybit market data feeds and failover
│   │   ├── engine/          # MTF analyzer, confluence scoring, regime detection
│   │   ├── indicators/      # EMA, RSI, ATR, Volume SMA, fractal swings
│   │   ├── market_structure/# BOS, CHoCH, displacement, trend classification
│   │   ├── liquidity/       # Sweeps, sessions, FVGs, Order Blocks, OTE
│   │   ├── strategies/      # ICT Sniper, Trend Swing, Micro Scalp
│   │   ├── signals/         # Quality gates, lifecycle state machine, tracker
│   │   ├── risk/            # Position sizing & approximate liquidation calculator
│   │   ├── backtesting/     # Event-driven backtesting engine
│   │   ├── paper_trading/   # Virtual paper trading desk
│   │   ├── notifications/   # Telegram bot alerts
│   │   ├── database/        # SQLAlchemy models (all 18 tables) & async session
│   │   ├── workers/         # Background continuous cloud scanner worker
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Comprehensive automated test suite
│   ├── requirements.txt     # Pinned Python 3.12 dependencies
│   ├── Dockerfile           # Railway container build specification
│   ├── railway.json         # Railway deployment config
│   └── Procfile             # Process entrypoint
├── frontend/
│   ├── app/                 # 13 Next.js pages (App router)
│   ├── components/          # Navigation, Header, LightweightChart, Badges
│   ├── hooks/               # WebSocket & market data hooks
│   ├── lib/                 # API client, formatting utils, Supabase helper
│   ├── types/               # TypeScript definitions
│   ├── package.json         # Pinned frontend dependencies
│   └── vercel.json          # Vercel deployment config
├── supabase/
│   ├── migrations/          # Complete schema migration (18 tables, RLS)
│   └── seed.sql             # Priority pairs, strategy profiles, and seed data
├── docs/                    # Complete architecture, API, deployment, security guides
├── .github/workflows/       # GitHub Actions CI/CD pipeline
├── .gitignore               # Clean repository exclusions
├── .env.example             # Environment variable template
├── README.md                # English documentation
└── README_BN.md             # Bengali documentation
```

---

## 📖 Documentation Index

- [Cloud Deployment Guide](docs/DEPLOYMENT.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [REST & WebSocket API Reference](docs/API.md)
- [Security & Risk Policy](docs/SECURITY.md)
- [User Operational Guide](docs/USER_GUIDE.md)
- [বাংলা নির্দেশিকা (Bengali Guide)](README_BN.md)
