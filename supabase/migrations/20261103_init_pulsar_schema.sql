-- ========================================================================
-- PULSAR AI V2.0 — SUPABASE POSTGRESQL PRODUCTION DATABASE SCHEMA
-- Migration: 20261103_init_pulsar_schema.sql
-- ========================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. USER SETTINGS TABLE
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    theme VARCHAR(50) DEFAULT 'dark' NOT NULL,
    default_leverage INT DEFAULT 10 NOT NULL,
    risk_percentage DOUBLE PRECISION DEFAULT 1.0 NOT NULL,
    telegram_notifications BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 3. MARKET SYMBOLS TABLE
CREATE TABLE IF NOT EXISTS market_symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) UNIQUE NOT NULL,
    base_asset VARCHAR(20) NOT NULL,
    quote_asset VARCHAR(20) DEFAULT 'USDT' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    price_precision INT DEFAULT 2 NOT NULL,
    quantity_precision INT DEFAULT 3 NOT NULL,
    min_quantity DOUBLE PRECISION DEFAULT 0.001 NOT NULL,
    priority INT DEFAULT 10 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_market_symbols_active ON market_symbols(is_active);

-- 4. MARKET CANDLES TABLE
CREATE TABLE IF NOT EXISTS market_candles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open_time TIMESTAMPTZ NOT NULL,
    close_time TIMESTAMPTZ NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    is_closed BOOLEAN DEFAULT TRUE NOT NULL,
    provider VARCHAR(50) DEFAULT 'binance' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    CONSTRAINT uq_candle_record UNIQUE (symbol, timeframe, open_time, provider)
);
CREATE INDEX IF NOT EXISTS idx_candles_lookup ON market_candles(symbol, timeframe, open_time DESC);

-- 5. MARKET SNAPSHOTS TABLE
CREATE TABLE IF NOT EXISTS market_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    last_price DOUBLE PRECISION NOT NULL,
    trend VARCHAR(50) NOT NULL,
    regime VARCHAR(50) NOT NULL,
    htf_bias VARCHAR(50) NOT NULL,
    ltf_structure VARCHAR(50) NOT NULL,
    swing_high DOUBLE PRECISION,
    swing_low DOUBLE PRECISION,
    bos_choch VARCHAR(50),
    fvg_status VARCHAR(50),
    ob_status VARCHAR(50),
    liquidity_sweep VARCHAR(100),
    confluence_score DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    provider VARCHAR(50) DEFAULT 'binance' NOT NULL,
    is_demo BOOLEAN DEFAULT FALSE NOT NULL,
    snapshot_time TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    details JSONB
);
CREATE INDEX IF NOT EXISTS idx_snapshots_sym_time ON market_snapshots(symbol, snapshot_time DESC);

-- 6. SIGNALS TABLE
CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL, -- BUY or SELL
    timeframe VARCHAR(10) DEFAULT '15m' NOT NULL,
    entry_price DOUBLE PRECISION NOT NULL,
    stop_loss DOUBLE PRECISION NOT NULL,
    take_profit_1 DOUBLE PRECISION NOT NULL,
    take_profit_2 DOUBLE PRECISION NOT NULL,
    take_profit_3 DOUBLE PRECISION NOT NULL,
    rr_ratio DOUBLE PRECISION NOT NULL,
    confluence_score DOUBLE PRECISION NOT NULL,
    htf_bias VARCHAR(50) NOT NULL,
    ltf_confirmation VARCHAR(100) NOT NULL,
    liquidity_event VARCHAR(100) NOT NULL,
    bos_choch_confirmation VARCHAR(100) NOT NULL,
    fvg_ob_info VARCHAR(200) NOT NULL,
    entry_explanation TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending' NOT NULL,
    strategy_profile VARCHAR(100) DEFAULT 'Sniper' NOT NULL,
    data_provider VARCHAR(50) DEFAULT 'binance' NOT NULL,
    is_demo BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    triggered_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    expiry_time TIMESTAMPTZ NOT NULL,
    invalidation_conditions TEXT,
    realized_pnl DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_signals_sym_status ON signals(symbol, status);
CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at DESC);

-- 7. SIGNAL EVENTS TABLE (Audit Trail)
CREATE TABLE IF NOT EXISTS signal_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id UUID REFERENCES signals(id) ON DELETE CASCADE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    details JSONB,
    timestamp TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_signal_events_sig ON signal_events(signal_id, timestamp ASC);

-- 8. BACKTEST RUNS TABLE
CREATE TABLE IF NOT EXISTS backtest_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    strategy_profile VARCHAR(100) DEFAULT 'Sniper' NOT NULL,
    initial_balance DOUBLE PRECISION DEFAULT 10000.0 NOT NULL,
    final_balance DOUBLE PRECISION DEFAULT 10000.0 NOT NULL,
    net_pnl DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    total_trades INT DEFAULT 0 NOT NULL,
    wins INT DEFAULT 0 NOT NULL,
    losses INT DEFAULT 0 NOT NULL,
    win_rate DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    profit_factor DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    max_drawdown DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    average_rr DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    equity_curve JSONB,
    config JSONB,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 9. BACKTEST TRADES TABLE
CREATE TABLE IF NOT EXISTS backtest_trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES backtest_runs(id) ON DELETE CASCADE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ NOT NULL,
    entry_price DOUBLE PRECISION NOT NULL,
    exit_price DOUBLE PRECISION NOT NULL,
    stop_loss DOUBLE PRECISION NOT NULL,
    take_profit DOUBLE PRECISION NOT NULL,
    position_size DOUBLE PRECISION NOT NULL,
    fees DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    slippage DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    pnl DOUBLE PRECISION NOT NULL,
    return_percentage DOUBLE PRECISION NOT NULL,
    exit_reason VARCHAR(50) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_run ON backtest_trades(run_id);

-- 10. PAPER ACCOUNTS TABLE
CREATE TABLE IF NOT EXISTS paper_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) DEFAULT 'Main Virtual Account' NOT NULL,
    initial_balance DOUBLE PRECISION DEFAULT 10000.0 NOT NULL,
    balance DOUBLE PRECISION DEFAULT 10000.0 NOT NULL,
    margin_used DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    currency VARCHAR(10) DEFAULT 'USDT' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 11. PAPER POSITIONS TABLE
CREATE TABLE IF NOT EXISTS paper_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES paper_accounts(id) ON DELETE CASCADE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_price DOUBLE PRECISION NOT NULL,
    current_price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    leverage INT DEFAULT 10 NOT NULL,
    margin DOUBLE PRECISION NOT NULL,
    stop_loss DOUBLE PRECISION NOT NULL,
    take_profit_1 DOUBLE PRECISION NOT NULL,
    take_profit_2 DOUBLE PRECISION,
    take_profit_3 DOUBLE PRECISION,
    unrealized_pnl DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    status VARCHAR(50) DEFAULT 'OPEN' NOT NULL,
    opened_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    closed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_paper_positions_status ON paper_positions(account_id, status);

-- 12. PAPER TRADES TABLE
CREATE TABLE IF NOT EXISTS paper_trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES paper_accounts(id) ON DELETE CASCADE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_price DOUBLE PRECISION NOT NULL,
    exit_price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    leverage INT DEFAULT 10 NOT NULL,
    fee DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    pnl DOUBLE PRECISION NOT NULL,
    exit_reason VARCHAR(50) NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL,
    closed_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_paper_trades_acc ON paper_trades(account_id, closed_at DESC);

-- 13. PERFORMANCE SNAPSHOTS TABLE
CREATE TABLE IF NOT EXISTS performance_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_date TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    total_signals INT DEFAULT 0 NOT NULL,
    winning_signals INT DEFAULT 0 NOT NULL,
    losing_signals INT DEFAULT 0 NOT NULL,
    win_rate DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    net_pnl DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    profit_factor DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    average_rr DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    max_drawdown DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    metrics_by_symbol JSONB,
    metrics_by_timeframe JSONB,
    metrics_by_strategy JSONB,
    data_type VARCHAR(50) DEFAULT 'live' NOT NULL
);

-- 14. STRATEGY PROFILES TABLE
CREATE TABLE IF NOT EXISTS strategy_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    min_confluence DOUBLE PRECISION DEFAULT 70.0 NOT NULL,
    min_rr DOUBLE PRECISION DEFAULT 2.0 NOT NULL,
    risk_percentage DOUBLE PRECISION DEFAULT 1.0 NOT NULL,
    allowed_timeframes JSONB DEFAULT '["15m", "1h", "4h"]'::jsonb NOT NULL,
    parameters JSONB,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 15. STRATEGY CONFIG VERSIONS TABLE
CREATE TABLE IF NOT EXISTS strategy_config_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES strategy_profiles(id) ON DELETE CASCADE NOT NULL,
    version INT NOT NULL,
    config_snapshot JSONB NOT NULL,
    change_reason VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 16. NOTIFICATION SETTINGS TABLE
CREATE TABLE IF NOT EXISTS notification_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel VARCHAR(50) DEFAULT 'telegram' NOT NULL,
    target VARCHAR(255) NOT NULL,
    notify_on_new_signal BOOLEAN DEFAULT TRUE NOT NULL,
    notify_on_triggered BOOLEAN DEFAULT TRUE NOT NULL,
    notify_on_tp_hit BOOLEAN DEFAULT TRUE NOT NULL,
    notify_on_sl_hit BOOLEAN DEFAULT TRUE NOT NULL,
    notify_on_expired BOOLEAN DEFAULT FALSE NOT NULL,
    notify_on_provider_down BOOLEAN DEFAULT TRUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 17. SYSTEM HEALTH TABLE
CREATE TABLE IF NOT EXISTS system_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    primary_provider VARCHAR(50) DEFAULT 'binance' NOT NULL,
    active_provider VARCHAR(50) DEFAULT 'binance' NOT NULL,
    last_heartbeat TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    last_scan_time TIMESTAMPTZ,
    latency_ms DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- 18. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100) NOT NULL,
    actor VARCHAR(100) DEFAULT 'system' NOT NULL,
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- ========================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ========================================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE signal_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Allow public read of signals and system status for authenticated / app users
CREATE POLICY "Public read active signals" ON signals FOR SELECT USING (true);
CREATE POLICY "Public read market symbols" ON market_symbols FOR SELECT USING (true);
