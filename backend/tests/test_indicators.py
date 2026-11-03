import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from backend.app.indicators.technical import (
    calculate_ema, calculate_rsi, calculate_atr, calculate_volume_sma,
    find_swing_points, enrich_technical_indicators
)


@pytest.fixture
def sample_df():
    """Generates synthetic OHLCV data for testing indicators"""
    dates = [datetime.now(timezone.utc) + timedelta(minutes=15 * i) for i in range(50)]
    prices = [100.0 + i + (5.0 if i % 2 == 0 else -3.0) for i in range(50)]
    
    df = pd.DataFrame({
        "open": prices,
        "high": [p + 2.0 for p in prices],
        "low": [p - 2.0 for p in prices],
        "close": [p + 1.0 for p in prices],
        "volume": [1000.0 + (i * 10) for i in range(50)]
    }, index=dates)
    return df


def test_calculate_ema(sample_df):
    ema20 = calculate_ema(sample_df['close'], 20)
    assert len(ema20) == len(sample_df)
    assert not ema20.isna().any()
    assert ema20.iloc[-1] > 0


def test_calculate_rsi(sample_df):
    rsi = calculate_rsi(sample_df['close'], 14)
    assert len(rsi) == len(sample_df)
    assert (rsi >= 0).all() and (rsi <= 100).all()


def test_calculate_atr(sample_df):
    atr = calculate_atr(sample_df, 14)
    assert len(atr) == len(sample_df)
    assert (atr > 0).all()


def test_find_swing_points(sample_df):
    highs, lows = find_swing_points(sample_df, left_bars=2, right_bars=2)
    assert isinstance(highs, list)
    assert isinstance(lows, list)
    for sh in highs:
        assert sh.kind == "HIGH"
        assert sh.price > 0
    for sl in lows:
        assert sl.kind == "LOW"
        assert sl.price > 0


def test_enrich_technical_indicators(sample_df):
    enriched = enrich_technical_indicators(sample_df)
    assert "ema_20" in enriched.columns
    assert "ema_50" in enriched.columns
    assert "ema_200" in enriched.columns
    assert "rsi_14" in enriched.columns
    assert "atr_14" in enriched.columns
    assert "vol_sma_20" in enriched.columns
