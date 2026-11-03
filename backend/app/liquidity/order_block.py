from typing import List, Optional
import pandas as pd
from pydantic import BaseModel
from backend.app.market_structure.structure import StructureBreak, StructureType


class OrderBlock(BaseModel):
    kind: str  # 'BULLISH' or 'BEARISH'
    high: float
    low: float
    mean_threshold: float  # 50% midpoint
    open_price: float
    close_price: float
    candle_index: int
    timestamp: str
    is_mitigated: bool = False
    is_invalidated: bool = False
    is_breaker: bool = False  # True if invalidated and became a Breaker Block
    mitigated_timestamp: Optional[str] = None


class OrderBlockEngine:
    """Detects ICT Order Blocks (OB) and Breaker Blocks"""

    @staticmethod
    def detect_order_blocks(
        df: pd.DataFrame,
        structure_breaks: List[StructureBreak]
    ) -> List[OrderBlock]:
        """
        Correlates structure breaks with the preceding origin candle to find valid institutional OBs.
        """
        n = len(df)
        if n < 5 or not structure_breaks:
            return []

        order_blocks: List[OrderBlock] = []
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        closes = df['close'].values
        timestamps = [str(t) for t in df.index.values]

        for s_break in structure_breaks:
            break_idx = s_break.candle_index
            if break_idx < 1 or break_idx >= n:
                continue

            # 1. Bullish BOS / CHoCH: Look back for the last down-close candle before the run up
            if s_break.break_type in [StructureType.BULLISH_BOS, StructureType.BULLISH_CHOCH]:
                target_idx = None
                for k in range(break_idx - 1, max(0, break_idx - 6), -1):
                    if closes[k] < opens[k]:  # Bearish candle
                        target_idx = k
                        break

                if target_idx is not None:
                    ob_high = float(highs[target_idx])
                    ob_low = float(lows[target_idx])
                    ob = OrderBlock(
                        kind="BULLISH",
                        high=ob_high,
                        low=ob_low,
                        mean_threshold=round((ob_high + ob_low) / 2.0, 2),
                        open_price=float(opens[target_idx]),
                        close_price=float(closes[target_idx]),
                        candle_index=target_idx,
                        timestamp=timestamps[target_idx]
                    )

                    # Check forward candles after the break for retest/mitigation
                    for j in range(break_idx + 1, n):
                        sub_l = lows[j]
                        sub_c = closes[j]
                        if sub_l <= ob.high and not ob.is_mitigated:
                            ob.is_mitigated = True
                            ob.mitigated_timestamp = timestamps[j]
                        # Invalidation: candle closes below the low of the bullish OB
                        if sub_c < ob.low:
                            ob.is_invalidated = True
                            ob.is_breaker = True  # Converts into Bearish Breaker Block
                            break

                    order_blocks.append(ob)

            # 2. Bearish BOS / CHoCH: Look back for the last up-close candle before the drop
            elif s_break.break_type in [StructureType.BEARISH_BOS, StructureType.BEARISH_CHOCH]:
                target_idx = None
                for k in range(break_idx - 1, max(0, break_idx - 6), -1):
                    if closes[k] > opens[k]:  # Bullish candle
                        target_idx = k
                        break

                if target_idx is not None:
                    ob_high = float(highs[target_idx])
                    ob_low = float(lows[target_idx])
                    ob = OrderBlock(
                        kind="BEARISH",
                        high=ob_high,
                        low=ob_low,
                        mean_threshold=round((ob_high + ob_low) / 2.0, 2),
                        open_price=float(opens[target_idx]),
                        close_price=float(closes[target_idx]),
                        candle_index=target_idx,
                        timestamp=timestamps[target_idx]
                    )

                    # Check forward candles
                    for j in range(break_idx + 1, n):
                        sub_h = highs[j]
                        sub_c = closes[j]
                        if sub_h >= ob.low and not ob.is_mitigated:
                            ob.is_mitigated = True
                            ob.mitigated_timestamp = timestamps[j]
                        # Invalidation: candle closes above the high of the bearish OB
                        if sub_c > ob.high:
                            ob.is_invalidated = True
                            ob.is_breaker = True  # Converts into Bullish Breaker Block
                            break

                    order_blocks.append(ob)

        return order_blocks

    @staticmethod
    def get_active_order_blocks(obs: List[OrderBlock]) -> List[OrderBlock]:
        return [b for b in obs if not b.is_invalidated]
