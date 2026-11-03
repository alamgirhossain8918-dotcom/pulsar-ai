# PULSAR AI V2.0 — API DOCUMENTATION

Base URL (Railway Cloud): `https://<YOUR-RAILWAY-APP>.up.railway.app/api/v1`
WebSocket Stream: `wss://<YOUR-RAILWAY-APP>.up.railway.app/api/v1/ws`

---

## 1. Authentication
### `POST /auth/login`
Authenticates the single-owner trading session.
- **Request Body**:
  ```json
  { "email": "owner@pulsarai.io", "password": "your-password" }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbG...",
    "token_type": "bearer",
    "user": { "id": "owner-admin-1", "email": "owner@pulsarai.io" }
  }
  ```

---

## 2. Market Data
### `GET /market/overview`
Returns high-level status of prioritized crypto assets (BTC, ETH, SOL), provider health, and active signal counts.

### `GET /market/candles/{symbol}?timeframe=15m&limit=150`
Returns historical closed candles formatted for TradingView Lightweight Charts with ICT overlay markers (BOS, CHoCH).
- **Query Parameters**:
  - `timeframe`: `5m`, `15m`, `1h`, `4h`, `1d`, `1w` (default: `15m`)
  - `limit`: `20` to `500` (default: `150`)

### `GET /market/scanner`
Returns the latest multi-pair scanning results with trend, regime, dealing zone, sweeps count, and signal status.

---

## 3. Signals Repository
### `GET /signals`
Lists active and past signals.
- **Query Parameters**:
  - `status_filter`: `Pending`, `Triggered`, `TP1 Hit`, `SL Hit`, `Expired`
  - `direction`: `BUY`, `SELL`
  - `symbol`: e.g. `BTCUSDT`

### `GET /signals/{id}`
Returns granular confluence audit, structural explanations, execution targets, and event timeline for a specific signal.

---

## 4. Backtesting
### `POST /backtest/run`
Executes an event-driven backtest across historical candles.
- **Request Body**:
  ```json
  {
    "symbol": "BTCUSDT",
    "timeframe": "15m",
    "strategy_profile": "sniper",
    "initial_balance": 10000.0,
    "risk_percentage": 1.0
  }
  ```

---

## 5. Paper Trading
### `GET /paper-trading/account`
Returns virtual balance, equity, margin used, free margin, and open position counts.

### `POST /paper-trading/order`
Opens a virtual simulated futures position.
- **Request Body**:
  ```json
  {
    "symbol": "BTCUSDT",
    "direction": "BUY",
    "entry_price": 65000.0,
    "stop_loss": 64000.0,
    "take_profit_1": 67000.0,
    "quantity": 0.1,
    "leverage": 10
  }
  ```

### `POST /paper-trading/close/{pos_id}?exit_price=66500.0`
Closes an open virtual position and records realized PnL in virtual history.

---

## 6. Risk Calculator
### `POST /risk/calculate`
Calculates mathematical position size, fees, margin, and approximate liquidation warnings.

---

## 7. System Health
### `GET /health`
Returns provider ping latencies, background worker lease status, and connected WebSocket clients.
