from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from backend.app.data.data_models import Candle


class SwingPoint:
    def __init__(self, index: int, timestamp, price: float, kind: str):
        self.index = index
        self.timestamp = timestamp
        self.price = price
        self.kind = kind  # 'HIGH' or 'LOW'


def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    """Calculates Exponential Moving Average"""
    return series.ewm(span=span, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculates Relative Strength Index (RSI) using Wilder's smoothing"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculates Average True Range (ATR)"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=period).mean()
    # Backfill ATR for initial bars using TR
    return atr.bfill()


def calculate_volume_sma(series: pd.Series, period: int = 20) -> pd.Series:
    """Calculates Volume Simple Moving Average"""
    return series.rolling(window=period, min_periods=1).mean()


def find_swing_points(df: pd.DataFrame, left_bars: int = 3, right_bars: int = 3) -> Tuple[List[SwingPoint], List[SwingPoint]]:
    """
    Identifies fractal Swing Highs and Swing Lows.
    Uses closed candles only (strictly no look-ahead on current forming candle).
    """
    swing_highs: List[SwingPoint] = []
    swing_lows: List[SwingPoint] = []
    
    n = len(df)
    if n < left_bars + right_bars + 1:
        return swing_highs, swing_lows

    highs = df['high'].values
    lows = df['low'].values
    timestamps = df.index.values

    # We evaluate swings strictly up to n - right_bars - 1
    for i in range(left_bars, n - right_bars):
        # Swing High Check
        current_h = highs[i]
        is_swing_h = True
        for l in range(1, left_bars + 1):
            if highs[i - l] >= current_h:
                is_swing_h = False
                break
        if is_swing_h:
            for r in range(1, right_bars + 1):
                if highs[i + r] > current_h:
                    is_swing_h = False
                    break
        if is_swing_h:
            swing_highs.append(SwingPoint(i, timestamps[i], float(current_h), 'HIGH'))

        # Swing Low Check
        current_l = lows[i]
        is_swing_l = True
        for l in range(1, left_bars + 1):
            if lows[i - l] <= current_l:
                is_swing_l = False
                break
        if is_swing_l:
            for r in range(1, right_bars + 1):
                if lows[i + r] < current_l:
                    is_swing_l = False
                    break
        if is_swing_l:
            swing_lows.append(SwingPoint(i, timestamps[i], float(current_l), 'LOW'))

    return swing_highs, swing_lows


def enrich_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Enriches OHLCV DataFrame with all standard indicators"""
    res = df.copy()
    res['ema_20'] = calculate_ema(res['close'], 20)
    res['ema_50'] = calculate_ema(res['close'], 50)
    res['ema_200'] = calculate_ema(res['close'], 200)
    res['rsi_14'] = calculate_rsi(res['close'], 14)
    res['atr_14'] = calculate_atr(res, 14)
    res['vol_sma_20'] = calculate_volume_sma(res['volume'], 20)
    return res
