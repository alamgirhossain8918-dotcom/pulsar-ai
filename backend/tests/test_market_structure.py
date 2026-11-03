import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone
from backend.app.indicators.technical import enrich_technical_indicators
from backend.app.market_structure.structure import (
    MarketStructureAnalysis, MarketTrend, StructureType
)


def test_displacement_detection():
    # Construct DataFrame with an explosive institutional candle
    dates = [datetime.now(timezone.utc) + timedelta(minutes=15 * i) for i in range(25)]
    df = pd.DataFrame({
        "open": [100.0] * 24 + [100.0],
        "high": [101.0] * 24 + [115.0],
        "low": [99.0] * 24 + [99.8],
        "close": [100.5] * 24 + [114.5],
        "volume": [500.0] * 24 + [3500.0]
    }, index=dates)

    enriched = enrich_technical_indicators(df)
    is_disp = MarketStructureAnalysis.detect_displacement(enriched, 24)
    assert is_disp is True


def test_structure_evaluation():
    # Construct wave structure: Low -> High -> Higher Low -> Break above High (Bullish BOS)
    dates = [datetime.now(timezone.utc) + timedelta(minutes=15 * i) for i in range(30)]
    prices = [
        100, 102, 105, 110, 108, 106, 104, 102, 105, 107,
        110, 112, 115, 118, 120, 116, 114, 112, 115, 118,
        122, 125, 128, 130, 126, 124, 128, 132, 135, 140
    ]
    df = pd.DataFrame({
        "open": prices,
        "high": [p + 1.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [1000.0] * 30
    }, index=dates)

    enriched = enrich_technical_indicators(df)
    breaks, trend, r_high, r_low = MarketStructureAnalysis.evaluate_structure(enriched)

    assert isinstance(breaks, list)
    assert trend in [MarketTrend.BULLISH, MarketTrend.STRONG_BULLISH]
    assert r_high is not None
    assert r_low is not None
