import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone
from backend.app.liquidity.liquidity_engine import LiquidityEngine
from backend.app.liquidity.fvg import FVGEngine
from backend.app.liquidity.order_block import OrderBlockEngine
from backend.app.liquidity.premium_discount import PremiumDiscountEngine
from backend.app.market_structure.structure import StructureBreak, StructureType


def test_premium_discount_ote():
    # Range 100 to 200: Eq = 150. OTE 0.62-0.79 = 138 to 121
    dr = PremiumDiscountEngine.calculate_dealing_range(current_price=130.0, range_high=200.0, range_low=100.0)
    assert dr.equilibrium == 150.0
    assert dr.ote_62 == 138.2
    assert dr.ote_79 == 121.4
    assert dr.zone == "OTE_BUY"


def test_fvg_detection():
    # 3-bar Bullish FVG: Bar 0 High = 100, Bar 2 Low = 105 (Gap 100 to 105)
    dates = [datetime.now(timezone.utc) + timedelta(minutes=15 * i) for i in range(5)]
    df = pd.DataFrame({
        "open": [95, 99, 106, 107, 108],
        "high": [100, 104, 110, 111, 112],
        "low": [90, 98, 105, 106, 107],
        "close": [98, 103, 109, 110, 111],
        "volume": [1000] * 5
    }, index=dates)

    fvgs = FVGEngine.detect_fvgs(df)
    assert len(fvgs) >= 1
    bullish_fvg = next((f for f in fvgs if f.kind == "BULLISH"), None)
    assert bullish_fvg is not None
    assert bullish_fvg.bottom == 100.0
    assert bullish_fvg.top == 105.0


def test_order_block_detection():
    dates = [datetime.now(timezone.utc) + timedelta(minutes=15 * i) for i in range(10)]
    # Candle 2 is down-close candle, followed by upward break
    df = pd.DataFrame({
        "open": [100, 101, 102, 98, 105, 110, 115, 118, 120, 122],
        "high": [102, 103, 103, 106, 112, 116, 120, 122, 124, 125],
        "low": [99, 100, 97, 97, 104, 109, 114, 117, 119, 121],
        "close": [101, 102, 98, 105, 110, 115, 118, 120, 122, 124],
        "volume": [1000] * 10
    }, index=dates)

    s_breaks = [
        StructureBreak(
            break_type=StructureType.BULLISH_BOS,
            broken_level=103.0,
            break_price=105.0,
            candle_index=3,
            timestamp=str(dates[3]),
            is_confirmed=True,
            displacement=True
        )
    ]

    obs = OrderBlockEngine.detect_order_blocks(df, s_breaks)
    assert len(obs) >= 1
    assert obs[0].kind == "BULLISH"
