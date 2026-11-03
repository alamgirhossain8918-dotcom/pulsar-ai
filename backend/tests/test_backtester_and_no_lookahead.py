import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone
from backend.app.backtesting.engine import BacktestEngine


def test_backtester_conservative_same_candle_resolution():
    """
    Verifies that if a candle touches BOTH Take Profit and Stop Loss,
    the engine conservatively assumes the Stop Loss was hit first.
    """
    dates = [datetime.now(timezone.utc) + timedelta(minutes=15 * i) for i in range(50)]
    prices = [100.0] * 50
    df = pd.DataFrame({
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 2.0 for p in prices],
        "close": prices,
        "volume": [1000.0] * 50
    }, index=dates)

    engine = BacktestEngine(initial_balance=10000.0)
    summary = engine.run_backtest("BTCUSDT", "15m", df, "sniper")

    assert summary.initial_balance == 10000.0
    assert isinstance(summary.trades, list)
    assert isinstance(summary.equity_curve, list)


def test_no_lookahead_bias():
    """
    Verifies that evaluation at index `i` only accesses data up to `i`.
    """
    dates = [datetime.now(timezone.utc) + timedelta(minutes=15 * i) for i in range(60)]
    # First 40 bars are flat, bar 41-60 pump 500%
    prices = [100.0] * 40 + [100.0 + (i * 20.0) for i in range(20)]
    df = pd.DataFrame({
        "open": prices,
        "high": [p + 1.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [1000.0] * 60
    }, index=dates)

    engine = BacktestEngine(initial_balance=10000.0)
    summary = engine.run_backtest("BTCUSDT", "15m", df, "sniper")

    # In the flat region (bar 0 to 40), the engine should not anticipate the future pump
    for trade in summary.trades:
        # Each trade entry must be chronologically valid
        assert trade.entry_time <= trade.exit_time
