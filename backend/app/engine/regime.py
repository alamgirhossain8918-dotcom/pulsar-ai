from enum import Enum
from typing import Dict, Any
import numpy as np
import pandas as pd
from pydantic import BaseModel
from backend.app.market_structure.structure import MarketTrend


class RegimeType(str, Enum):
    STRONG_BULLISH = "Strong Bullish"
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"
    STRONG_BEARISH = "Strong Bearish"
    RANGING = "Ranging"
    HIGH_VOLATILITY = "High Volatility"
    LOW_VOLATILITY = "Low Volatility"


class MarketRegimeResult(BaseModel):
    regime: RegimeType
    trend: MarketTrend
    volatility_ratio: float  # ATR / Price
    volatility_state: str    # "HIGH", "NORMAL", "LOW"
    description: str
    metrics: Dict[str, Any]


class MarketRegimeDetector:
    """Detects current macro and micro market regimes using trend and volatility"""

    @classmethod
    def detect_regime(cls, df: pd.DataFrame, trend: MarketTrend) -> MarketRegimeResult:
        if len(df) < 20:
            return MarketRegimeResult(
                regime=RegimeType.NEUTRAL,
                trend=trend,
                volatility_ratio=0.0,
                volatility_state="NORMAL",
                description="Insufficient candle history to establish robust regime.",
                metrics={}
            )

        latest = df.iloc[-1]
        c = latest['close']
        atr = latest.get('atr_14', c * 0.01)
        vol_ratio = (atr / c) * 100.0  # ATR as % of price

        # Calculate historical volatility baseline (rolling 50-bar ATR mean)
        historical_atr = df['atr_14'].rolling(50, min_periods=10).mean().iloc[-1]
        atr_ratio_to_history = atr / max(historical_atr, 1e-6)

        if atr_ratio_to_history > 1.45:
            vol_state = "HIGH"
        elif atr_ratio_to_history < 0.65:
            vol_state = "LOW"
        else:
            vol_state = "NORMAL"

        # Synthesize Regime
        regime = RegimeType.NEUTRAL
        desc = ""

        if vol_state == "HIGH" and trend in [MarketTrend.RANGING, MarketTrend.NEUTRAL]:
            regime = RegimeType.HIGH_VOLATILITY
            desc = "Market experiencing elevated volatility without directional trend. Caution on false breakouts."
        elif vol_state == "LOW" and trend in [MarketTrend.RANGING, MarketTrend.NEUTRAL]:
            regime = RegimeType.LOW_VOLATILITY
            desc = "Market is consolidating in a low volatility compression cycle. Potential expansion imminent."
        elif trend == MarketTrend.STRONG_BULLISH:
            regime = RegimeType.STRONG_BULLISH
            desc = "Aggressive institutional accumulation and upward displacement. Favor pullbacks to discount zones."
        elif trend == MarketTrend.BULLISH:
            regime = RegimeType.BULLISH
            desc = "Bullish structure intact with higher highs and higher lows. Long bias active."
        elif trend == MarketTrend.STRONG_BEARISH:
            regime = RegimeType.STRONG_BEARISH
            desc = "Heavy institutional distribution and downward displacement. Favor rallies into premium zones."
        elif trend == MarketTrend.BEARISH:
            regime = RegimeType.BEARISH
            desc = "Bearish structure intact with lower highs and lower lows. Short bias active."
        elif trend == MarketTrend.RANGING:
            regime = RegimeType.RANGING
            desc = "Price oscillating between established dealing range boundaries. Look for liquidity sweeps at extremes."
        else:
            regime = RegimeType.NEUTRAL
            desc = "Market in transitional state with balanced order flow."

        return MarketRegimeResult(
            regime=regime,
            trend=trend,
            volatility_ratio=round(vol_ratio, 3),
            volatility_state=vol_state,
            description=desc,
            metrics={
                "atr": round(float(atr), 2),
                "atr_ratio_to_history": round(float(atr_ratio_to_history), 2),
                "close_price": round(float(c), 2)
            }
        )
