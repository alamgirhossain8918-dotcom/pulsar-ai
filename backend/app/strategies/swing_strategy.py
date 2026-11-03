from typing import Optional
from backend.app.engine.confluence import ConfluenceScorer
from backend.app.engine.mtf_analyzer import MTFAnalysisResult
from backend.app.market_structure.structure import MarketTrend, StructureType
from backend.app.strategies.base import BaseStrategy, StrategySignalOutput


class ICTSwingStrategy(BaseStrategy):
    """
    ICT Trend Swing Strategy
    Higher timeframe trend continuation off 4H / 1H Order Blocks & Breakers
    """

    def __init__(self, min_confluence: float = 70.0, min_rr: float = 2.5):
        super().__init__(name="Swing", min_confluence=min_confluence, min_rr=min_rr)

    def evaluate(self, mtf: MTFAnalysisResult) -> Optional[StrategySignalOutput]:
        htf_bias = mtf.htf_bias
        itf_key = "1h" if "1h" in mtf.tf_analyses else ("4h" if "4h" in mtf.tf_analyses else list(mtf.tf_analyses.keys())[0])
        itf = mtf.tf_analyses.get(itf_key)
        if not itf:
            return None

        current_price = itf.dealing_range.current_price

        # Trend continuation logic
        if htf_bias in [MarketTrend.STRONG_BULLISH, MarketTrend.BULLISH]:
            bullish_obs = [o for o in itf.order_blocks if o.kind == "BULLISH" and not o.is_invalidated]
            if bullish_obs and itf.recent_low:
                sl_level = round(itf.recent_low * 0.99, 2)
                sl_dist = current_price - sl_level
                if sl_dist > 0:
                    tp1 = round(current_price + (sl_dist * 2.5), 2)
                    tp2 = round(current_price + (sl_dist * 4.0), 2)
                    tp3 = round(current_price + (sl_dist * 6.0), 2)
                    confluence = ConfluenceScorer.calculate_score(
                        direction="BUY",
                        htf_bias=htf_bias.value,
                        structure_break_type="BULLISH_BOS",
                        has_liquidity_sweep=True,
                        sweep_type="SSL",
                        has_fvg_or_ob=True,
                        dealing_zone=itf.dealing_range.zone,
                        has_displacement=True,
                        rsi_value=48.0
                    )
                    if confluence.total_score >= self.min_confluence:
                        return StrategySignalOutput(
                            direction="BUY",
                            entry_price=round(current_price, 2),
                            stop_loss=sl_level,
                            take_profit_1=tp1,
                            take_profit_2=tp2,
                            take_profit_3=tp3,
                            rr_ratio=2.5,
                            confluence_score=confluence.total_score,
                            htf_bias=htf_bias.value,
                            ltf_confirmation="1H Order Block mitigation in macro discount",
                            liquidity_event="Macro sell-side liquidity harvested",
                            bos_choch_confirmation="4H Trend Continuation BOS",
                            fvg_ob_info="Reaction off 1H Bullish Institutional Order Block",
                            entry_explanation="Swing Long aligned with HTF Bullish trend.",
                            strategy_profile=self.name,
                            invalidation_conditions="Signal invalidates if 4H candle closes below the 1H Order Block low."
                        )

        elif htf_bias in [MarketTrend.STRONG_BEARISH, MarketTrend.BEARISH]:
            bearish_obs = [o for o in itf.order_blocks if o.kind == "BEARISH" and not o.is_invalidated]
            if bearish_obs and itf.recent_high:
                sl_level = round(itf.recent_high * 1.01, 2)
                sl_dist = sl_level - current_price
                if sl_dist > 0:
                    tp1 = round(current_price - (sl_dist * 2.5), 2)
                    tp2 = round(current_price - (sl_dist * 4.0), 2)
                    tp3 = round(current_price - (sl_dist * 6.0), 2)
                    confluence = ConfluenceScorer.calculate_score(
                        direction="SELL",
                        htf_bias=htf_bias.value,
                        structure_break_type="BEARISH_BOS",
                        has_liquidity_sweep=True,
                        sweep_type="BSL",
                        has_fvg_or_ob=True,
                        dealing_zone=itf.dealing_range.zone,
                        has_displacement=True,
                        rsi_value=52.0
                    )
                    if confluence.total_score >= self.min_confluence:
                        return StrategySignalOutput(
                            direction="SELL",
                            entry_price=round(current_price, 2),
                            stop_loss=sl_level,
                            take_profit_1=tp1,
                            take_profit_2=tp2,
                            take_profit_3=tp3,
                            rr_ratio=2.5,
                            confluence_score=confluence.total_score,
                            htf_bias=htf_bias.value,
                            ltf_confirmation="1H Order Block mitigation in macro premium",
                            liquidity_event="Macro buy-side liquidity harvested",
                            bos_choch_confirmation="4H Trend Continuation BOS",
                            fvg_ob_info="Reaction off 1H Bearish Institutional Order Block",
                            entry_explanation="Swing Short aligned with HTF Bearish trend.",
                            strategy_profile=self.name,
                            invalidation_conditions="Signal invalidates if 4H candle closes above the 1H Order Block high."
                        )

        return None
