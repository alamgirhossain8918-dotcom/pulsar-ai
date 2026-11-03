# PULSAR AI V2.0 — SECURITY POLICY & AUDIT

## 1. Zero Real-Fund Risk Architecture

PULSAR AI V2.0 is strictly an **analysis, signal generation, backtesting, and paper trading** platform.
- **NEVER** stores real Binance or Bybit private trading API keys or secrets.
- **NEVER** executes actual exchange order placements.
- All paper trading executions are strictly virtual and simulated on synthetic balances.

## 2. Secrets Management

- **Zero Hardcoded Secrets**: All sensitive secrets (JWT `SECRET_KEY`, database credentials, Telegram bot tokens) are loaded exclusively via environment variables.
- **Client-Side Isolation**: The Next.js frontend only receives public configuration keys prefixed with `NEXT_PUBLIC_`. Private tokens are never bundled in frontend JavaScript.

## 3. Database Security (Supabase PostgreSQL)

- **Row Level Security (RLS)** is enabled across all database tables.
- Sensitive user records, settings, and paper trading accounts are protected by strict RLS policies.
- Database connections utilize SSL encrypted transport (`sslmode=require`).

## 4. Input Sanitization & Rate Limiting

- FastAPI route schemas are validated strictly with Pydantic V2 models.
- Market feeds feature exponential backoff retry algorithms to prevent 429 rate limit bans from Binance and Bybit.
