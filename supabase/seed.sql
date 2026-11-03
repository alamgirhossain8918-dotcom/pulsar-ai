-- ========================================================================
-- PULSAR AI V2.0 — INITIAL SEED DATA
-- ========================================================================

-- Insert Initial Priority Market Symbols
INSERT INTO market_symbols (symbol, base_asset, quote_asset, is_active, priority)
VALUES
    ('BTCUSDT', 'BTC', 'USDT', true, 1),
    ('ETHUSDT', 'ETH', 'USDT', true, 2),
    ('SOLUSDT', 'SOL', 'USDT', true, 3),
    ('BNBUSDT', 'BNB', 'USDT', true, 4),
    ('XRPUSDT', 'XRP', 'USDT', true, 5),
    ('DOGEUSDT', 'DOGE', 'USDT', true, 6),
    ('ADAUSDT', 'ADA', 'USDT', true, 7),
    ('AVAXUSDT', 'AVAX', 'USDT', true, 8)
ON CONFLICT (symbol) DO NOTHING;

-- Insert Strategy Profiles
INSERT INTO strategy_profiles (name, description, is_active, min_confluence, min_rr, risk_percentage, allowed_timeframes)
VALUES
    ('Sniper', 'ICT Sniper Strategy: Liquidity raid, CHoCH with displacement, and entry at OTE / unmitigated FVG.', true, 70.0, 2.0, 1.0, '["15m", "1h", "4h"]'::jsonb),
    ('Swing', 'ICT Trend Swing: 4H/1D macro continuation off unmitigated institutional Order Blocks & Breakers.', true, 70.0, 2.5, 1.0, '["1h", "4h", "1d"]'::jsonb),
    ('Scalp', 'ICT Micro Scalp: Session high/low liquidity harvest with rapid 5m/15m mitigation target.', true, 70.0, 2.0, 0.5, '["5m", "15m"]'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- Insert Default Strategy Config Version
INSERT INTO strategy_config_versions (profile_id, version, config_snapshot, change_reason)
SELECT id, 1, '{"version": 1, "active": true}'::jsonb, 'Initial system release'
FROM strategy_profiles
LIMIT 1;

-- Insert Initial System Health Record
INSERT INTO system_health (service_name, status, primary_provider, active_provider, latency_ms)
VALUES ('Pulsar API Engine', 'HEALTHY', 'binance', 'binance', 42.5);

-- Insert Default Virtual Paper Account
INSERT INTO paper_accounts (name, initial_balance, balance, currency, is_active)
VALUES ('Main Virtual Account', 10000.0, 10000.0, 'USDT', true);
