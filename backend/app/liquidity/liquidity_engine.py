from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd
from pydantic import BaseModel
from backend.app.indicators.technical import find_swing_points


class LiquidityPool(BaseModel):
    kind: str  # 'BSL' (Buy-side) or 'SSL' (Sell-side)
    price: float
    timestamp: str
    is_swept: bool = False
    sweep_time: Optional[str] = None
    sweep_candle_index: Optional[int] = None


class LiquiditySweepEvent(BaseModel):
    pool_type: str  # BSL or SSL
    swept_level: float
    sweep_high_or_low: float
    reversal_close: float
    candle_index: int
    timestamp: str


class SessionLevels(BaseModel):
    asia_high: Optional[float] = None
    asia_low: Optional[float] = None
    london_high: Optional[float] = None
    london_low: Optional[float] = None
    ny_high: Optional[float] = None
    ny_low: Optional[float] = None
    pdh: Optional[float] = None  # Previous Day High
    pdl: Optional[float] = None  # Previous Day Low
    pwh: Optional[float] = None  # Previous Week High
    pwl: Optional[float] = None  # Previous Week Low


class LiquidityEngine:
    """Detects institutional liquidity pools, equal highs/lows, sweeps, and session levels"""

    @staticmethod
    def detect_equal_highs_lows(df: pd.DataFrame, tolerance_pct: float = 0.001) -> Tuple[List[float], List[float]]:
        """
        Finds Equal Highs (EQH) and Equal Lows (EQL) within small tolerance (default 0.1%).
        EQH and EQL represent retail stop clusters (prime liquidity).
        """
        swing_highs, swing_lows = find_swing_points(df, left_bars=2, right_bars=2)
        eqh_levels: List[float] = []
        eql_levels: List[float] = []

        # Find EQH
        for i in range(len(swing_highs)):
            for j in range(i + 1, len(swing_highs)):
                p1, p2 = swing_highs[i].price, swing_highs[j].price
                if abs(p1 - p2) / max(p1, 1e-6) <= tolerance_pct:
                    eqh_levels.append(round((p1 + p2) / 2.0, 2))

        # Find EQL
        for i in range(len(swing_lows)):
            for j in range(i + 1, len(swing_lows)):
                p1, p2 = swing_lows[i].price, swing_lows[j].price
                if abs(p1 - p2) / max(p1, 1e-6) <= tolerance_pct:
                    eql_levels.append(round((p1 + p2) / 2.0, 2))

        return list(set(eqh_levels)), list(set(eql_levels))

    @staticmethod
    def detect_liquidity_sweeps(df: pd.DataFrame) -> Tuple[List[LiquidityPool], List[LiquiditySweepEvent]]:
        """
        Identifies BSL/SSL pools and checks if a wick pierced the level while the candle body
        closed back inside the range (classic ICT liquidity raid / stop run).
        """
        swing_highs, swing_lows = find_swing_points(df, left_bars=3, right_bars=3)
        pools: List[LiquidityPool] = []
        sweeps: List[LiquiditySweepEvent] = []

        # Populate initial pools
        for sh in swing_highs:
            pools.append(LiquidityPool(kind="BSL", price=sh.price, timestamp=str(sh.timestamp)))
        for sl in swing_lows:
            pools.append(LiquidityPool(kind="SSL", price=sl.price, timestamp=str(sl.timestamp)))

        # Evaluate sweeps in historical sequence
        for pool in pools:
            for i in range(len(df)):
                row = df.iloc[i]
                c_high = row['high']
                c_low = row['low']
                c_close = row['close']
                c_open = row['open']
                c_time = str(df.index[i])

                if pool.kind == "BSL" and not pool.is_swept:
                    # BSL Sweep: High pierces pool price, but close is strictly below pool price
                    if c_high > pool.price and c_close < pool.price:
                        pool.is_swept = True
                        pool.sweep_time = c_time
                        pool.sweep_candle_index = i
                        sweeps.append(LiquiditySweepEvent(
                            pool_type="BSL",
                            swept_level=pool.price,
                            sweep_high_or_low=c_high,
                            reversal_close=c_close,
                            candle_index=i,
                            timestamp=c_time
                        ))
                        break

                elif pool.kind == "SSL" and not pool.is_swept:
                    # SSL Sweep: Low pierces pool price, but close is strictly above pool price
                    if c_low < pool.price and c_close > pool.price:
                        pool.is_swept = True
                        pool.sweep_time = c_time
                        pool.sweep_candle_index = i
                        sweeps.append(LiquiditySweepEvent(
                            pool_type="SSL",
                            swept_level=pool.price,
                            sweep_high_or_low=c_low,
                            reversal_close=c_close,
                            candle_index=i,
                            timestamp=c_time
                        ))
                        break

        return pools, sweeps

    @staticmethod
    def calculate_session_and_macro_levels(df: pd.DataFrame) -> SessionLevels:
        """
        Extracts PDH, PDL, PWH, PWL, and session boundaries (Asia, London, NY)
        Timings:
            Asia: 00:00 - 08:00 UTC
            London: 08:00 - 14:00 UTC
            New York: 13:00 - 21:00 UTC
        """
        levels = SessionLevels()
        if len(df) < 5:
            return levels

        # Check if index is DatetimeIndex
        idx = df.index
        if not isinstance(idx, pd.DatetimeIndex):
            try:
                df = df.copy()
                df.index = pd.to_datetime(df.index, utc=True)
                idx = df.index
            except Exception:
                return levels

        # Previous Day High / Low
        last_dt = idx[-1]
        prev_day = (last_dt - pd.Timedelta(days=1)).date()
        prev_day_bars = df[df.index.date == prev_day]
        if not prev_day_bars.empty:
            levels.pdh = float(prev_day_bars['high'].max())
            levels.pdl = float(prev_day_bars['low'].min())

        # Previous Week High / Low
        prev_week = last_dt.isocalendar().week - 1
        prev_week_bars = df[[dt.isocalendar().week == prev_week for dt in df.index]]
        if not prev_week_bars.empty:
            levels.pwh = float(prev_week_bars['high'].max())
            levels.pwl = float(prev_week_bars['low'].min())

        # Today's sessions
        today = last_dt.date()
        today_bars = df[df.index.date == today]

        if not today_bars.empty:
            # Asia: 00 to 08 UTC
            asia = today_bars[(today_bars.index.hour >= 0) & (today_bars.index.hour < 8)]
            if not asia.empty:
                levels.asia_high = float(asia['high'].max())
                levels.asia_low = float(asia['low'].min())

            # London: 08 to 14 UTC
            london = today_bars[(today_bars.index.hour >= 8) & (today_bars.index.hour < 14)]
            if not london.empty:
                levels.london_high = float(london['high'].max())
                levels.london_low = float(london['low'].min())

            # New York: 13 to 21 UTC
            ny = today_bars[(today_bars.index.hour >= 13) & (today_bars.index.hour < 21)]
            if not ny.empty:
                levels.ny_high = float(ny['high'].max())
                levels.ny_low = float(ny['low'].min())

        return levels
