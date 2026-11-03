from typing import List, Optional
import pandas as pd
from pydantic import BaseModel


class FairValueGap(BaseModel):
    kind: str  # 'BULLISH' or 'BEARISH'
    top: float
    bottom: float
    midpoint: float  # Consequent Encroachment (50% level)
    created_candle_index: int
    created_timestamp: str
    is_mitigated: bool = False
    is_invalidated: bool = False
    is_inverse: bool = False  # True if violated and flipped to Inverse FVG
    fill_percent: float = 0.0
    mitigation_timestamp: Optional[str] = None


class FVGEngine:
    """Detects and tracks ICT Fair Value Gaps (FVG) and Inverse FVGs (IFVG)"""

    @staticmethod
    def detect_fvgs(df: pd.DataFrame, min_gap_percent: float = 0.0005) -> List[FairValueGap]:
        """
        Scans OHLCV DataFrame for 3-bar Fair Value Gaps.
        Uses closed candles only.
        """
        n = len(df)
        if n < 3:
            return []

        fvgs: List[FairValueGap] = []
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        timestamps = [str(t) for t in df.index.values]

        for i in range(2, n):
            c0_h, c0_l = highs[i - 2], lows[i - 2]
            c1_h, c1_l = highs[i - 1], lows[i - 1]
            c2_h, c2_l = highs[i], lows[i]

            # 1. Bullish FVG: Low of candle 2 is strictly greater than High of candle 0
            if c2_l > c0_h:
                gap = c2_l - c0_h
                if gap / max(c0_h, 1e-6) >= min_gap_percent:
                    top = float(c2_l)
                    bottom = float(c0_h)
                    fvg = FairValueGap(
                        kind="BULLISH",
                        top=top,
                        bottom=bottom,
                        midpoint=round((top + bottom) / 2.0, 2),
                        created_candle_index=i,
                        created_timestamp=timestamps[i]
                    )
                    # Check subsequent candles for mitigation / fill / invalidation
                    for j in range(i + 1, n):
                        sub_l = lows[j]
                        sub_c = closes[j]
                        if sub_l <= fvg.top:
                            fvg.is_mitigated = True
                            fvg.mitigation_timestamp = timestamps[j]
                            penetration = max(0.0, fvg.top - sub_l)
                            fvg.fill_percent = min(100.0, round((penetration / (top - bottom)) * 100.0, 1))
                        # Invalidation: Candle body closes completely below bottom of bullish FVG
                        if sub_c < fvg.bottom:
                            fvg.is_invalidated = True
                            fvg.is_inverse = True  # Flips into Inverse Bearish FVG
                            break

                    fvgs.append(fvg)

            # 2. Bearish FVG: High of candle 2 is strictly less than Low of candle 0
            elif c2_h < c0_l:
                gap = c0_l - c2_h
                if gap / max(c2_h, 1e-6) >= min_gap_percent:
                    top = float(c0_l)
                    bottom = float(c2_h)
                    fvg = FairValueGap(
                        kind="BEARISH",
                        top=top,
                        bottom=bottom,
                        midpoint=round((top + bottom) / 2.0, 2),
                        created_candle_index=i,
                        created_timestamp=timestamps[i]
                    )
                    # Check subsequent candles
                    for j in range(i + 1, n):
                        sub_h = highs[j]
                        sub_c = closes[j]
                        if sub_h >= fvg.bottom:
                            fvg.is_mitigated = True
                            fvg.mitigation_timestamp = timestamps[j]
                            penetration = max(0.0, sub_h - fvg.bottom)
                            fvg.fill_percent = min(100.0, round((penetration / (top - bottom)) * 100.0, 1))
                        # Invalidation: Candle body closes completely above top of bearish FVG
                        if sub_c > fvg.top:
                            fvg.is_invalidated = True
                            fvg.is_inverse = True  # Flips into Inverse Bullish FVG
                            break

                    fvgs.append(fvg)

        return fvgs

    @staticmethod
    def get_unmitigated_fvgs(fvgs: List[FairValueGap]) -> List[FairValueGap]:
        return [f for f in fvgs if not f.is_mitigated and not f.is_invalidated]
