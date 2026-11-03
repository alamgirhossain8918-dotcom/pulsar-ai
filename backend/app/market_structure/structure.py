from enum import Enum
from typing import List, Optional, Tuple
import pandas as pd
from pydantic import BaseModel
from backend.app.indicators.technical import find_swing_points, SwingPoint


class MarketTrend(str, Enum):
    STRONG_BULLISH = "Strong Bullish"
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"
    STRONG_BEARISH = "Strong Bearish"
    RANGING = "Ranging"


class StructureType(str, Enum):
    BULLISH_BOS = "BULLISH_BOS"
    BEARISH_BOS = "BEARISH_BOS"
    BULLISH_CHOCH = "BULLISH_CHOCH"
    BEARISH_CHOCH = "BEARISH_CHOCH"
    MSS = "MARKET_STRUCTURE_SHIFT"
    NONE = "NONE"


class StructureBreak(BaseModel):
    break_type: StructureType
    broken_level: float
    break_price: float
    candle_index: int
    timestamp: str
    is_confirmed: bool = True
    displacement: bool = False


class MarketStructureAnalysis:
    """Analyzes Price Action Market Structure using ICT / SMC principles"""

    @staticmethod
    def detect_displacement(df: pd.DataFrame, candle_idx: int) -> bool:
        """
        Displacement is an aggressive institutional candle:
        - Body is large (> 1.6x ATR)
        - Wicks are relatively small (< 30% of total candle size)
        - Volume is above volume SMA
        """
        if candle_idx < 0 or candle_idx >= len(df):
            return False
            
        row = df.iloc[candle_idx]
        body = abs(row['close'] - row['open'])
        full_range = row['high'] - row['low']
        atr = row.get('atr_14', body)
        vol = row.get('volume', 0)
        vol_sma = row.get('vol_sma_20', vol)

        if full_range <= 0 or atr <= 0:
            return False

        body_ratio = body / full_range
        is_large_body = body >= 1.4 * atr
        is_solid_candle = body_ratio >= 0.65
        is_above_avg_vol = vol >= 1.15 * vol_sma

        return bool(is_large_body and is_solid_candle and is_above_avg_vol)

    @classmethod
    def evaluate_structure(cls, df: pd.DataFrame) -> Tuple[List[StructureBreak], MarketTrend, Optional[float], Optional[float]]:
        """
        Evaluates historical and current structure breaks (BOS / CHoCH / MSS).
        Returns:
            - List of StructureBreak events
            - Overall current Trend
            - Most recent active Swing High price
            - Most recent active Swing Low price
        """
        if len(df) < 20:
            return [], MarketTrend.NEUTRAL, None, None

        swing_highs, swing_lows = find_swing_points(df, left_bars=3, right_bars=3)
        if not swing_highs or not swing_lows:
            return [], MarketTrend.NEUTRAL, None, None

        breaks: List[StructureBreak] = []
        current_trend = MarketTrend.NEUTRAL

        # Track active swing points
        active_high = swing_highs[0].price
        active_low = swing_lows[0].price

        # Sort all swings chronologically
        all_swings = sorted(swing_highs + swing_lows, key=lambda s: s.index)
        
        # Step through candles after first few swings to detect breaks
        first_eval_idx = max(all_swings[0].index, 5)
        last_break_type = StructureType.NONE

        for i in range(first_eval_idx, len(df)):
            row = df.iloc[i]
            c_close = row['close']
            c_time = str(df.index[i])

            # Update latest known swings before this candle
            known_highs = [s for s in swing_highs if s.index < i]
            known_lows = [s for s in swing_lows if s.index < i]

            if not known_highs or not known_lows:
                continue

            latest_high = known_highs[-1].price
            latest_low = known_lows[-1].price
            is_disp = cls.detect_displacement(df, i)

            # Bullish Break: Candle closes above the latest known swing high
            if c_close > latest_high:
                if current_trend in [MarketTrend.BEARISH, MarketTrend.STRONG_BEARISH]:
                    # Change of Character from Bearish to Bullish
                    b_type = StructureType.BULLISH_CHOCH
                    current_trend = MarketTrend.BULLISH
                else:
                    b_type = StructureType.BULLISH_BOS
                    current_trend = MarketTrend.STRONG_BULLISH if is_disp else MarketTrend.BULLISH

                breaks.append(StructureBreak(
                    break_type=b_type,
                    broken_level=latest_high,
                    break_price=c_close,
                    candle_index=i,
                    timestamp=c_time,
                    is_confirmed=True,
                    displacement=is_disp
                ))
                last_break_type = b_type

            # Bearish Break: Candle closes below the latest known swing low
            elif c_close < latest_low:
                if current_trend in [MarketTrend.BULLISH, MarketTrend.STRONG_BULLISH]:
                    # Change of Character from Bullish to Bearish
                    b_type = StructureType.BEARISH_CHOCH
                    current_trend = MarketTrend.BEARISH
                else:
                    b_type = StructureType.BEARISH_BOS
                    current_trend = MarketTrend.STRONG_BEARISH if is_disp else MarketTrend.BEARISH

                breaks.append(StructureBreak(
                    break_type=b_type,
                    broken_level=latest_low,
                    break_price=c_close,
                    candle_index=i,
                    timestamp=c_time,
                    is_confirmed=True,
                    displacement=is_disp
                ))
                last_break_type = b_type

        # Assess moving average alignment for final trend confirmation
        latest = df.iloc[-1]
        c = latest['close']
        ema20 = latest.get('ema_20', c)
        ema50 = latest.get('ema_50', c)
        ema200 = latest.get('ema_200', c)

        if c > ema20 > ema50 > ema200 and current_trend in [MarketTrend.BULLISH, MarketTrend.STRONG_BULLISH]:
            current_trend = MarketTrend.STRONG_BULLISH
        elif c < ema20 < ema50 < ema200 and current_trend in [MarketTrend.BEARISH, MarketTrend.STRONG_BEARISH]:
            current_trend = MarketTrend.STRONG_BEARISH
        elif abs(ema20 - ema50) / max(ema50, 1e-6) < 0.002:
            current_trend = MarketTrend.RANGING

        recent_high = swing_highs[-1].price if swing_highs else None
        recent_low = swing_lows[-1].price if swing_lows else None

        return breaks, current_trend, recent_high, recent_low
