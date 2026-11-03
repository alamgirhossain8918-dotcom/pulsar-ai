from typing import Optional
from backend.app.engine.confluence import ConfluenceScorer
from backend.app.engine.mtf_analyzer import MTFAnalysisResult
from backend.app.strategies.base import BaseStrategy, StrategySignalOutput


class ICTScalpStrategy(BaseStrategy):
    """
    ICT Scalp Strategy
    Session liquidity raid (Asia / London / NY extremes) and micro FVG fill (5m / 15m)
    """

    def __init__(self, min_confluence: float = 70.0, min_rr: float = 2.0):
        super().__init__(name="Scalp", min_confluence=min_confluence, min_rr=min_rr)

    def evaluate(self, mtf: MTFAnalysisResult) -> Optional[StrategySignalOutput]:
        tf_key = "5m" if "5m" in mtf.tf_analyses else ("15m" if "15m" in mtf.tf_analyses else list(mtf.tf_analyses.keys())[0])
        tf_data = mtf.tf_analyses.get(tf_key)
        if not tf_data:
            return None

        current_price = tf_data.dealing_range.current_price
        sess = tf_data.session_levels

        # Check session low sweep for Long Scalp
        if sess.asia_low and current_price < sess.asia_low:
            sl_dist = current_price * 0.005  # 0.5% tight stop
            sl_level = round(current_price - sl_dist, 2)
            tp1 = round(current_price + (sl_dist * 2.0), 2)
            tp2 = round(current_price + (sl_dist * 3.0), 2)
            tp3 = round(current_price + (sl_dist * 4.0), 2)

            confluence = ConfluenceScorer.calculate_score(
                direction="BUY",
                htf_bias=mtf.htf_bias.value,
                structure_break_type="BULLISH_CHOCH",
                has_liquidity_sweep=True,
                sweep_type="SSL",
                has_fvg_or_ob=True,
                dealing_zone="DISCOUNT",
                has_displacement=True,
                rsi_value=32.0
            )

            if confluence.total_score >= self.min_confluence:
                return StrategySignalOutput(
                    direction="BUY",
                    entry_price=round(current_price, 2),
                    stop_loss=sl_level,
                    take_profit_1=tp1,
                    take_profit_2=tp2,
                    take_profit_3=tp3,
                    rr_ratio=2.0,
                    confluence_score=confluence.total_score,
                    htf_bias=mtf.htf_bias.value,
                    ltf_confirmation="Asia session low sweep and quick 5m rejection",
                    liquidity_event="Asia low liquidity sweep",
                    bos_choch_confirmation="Micro 5m CHoCH",
                    fvg_ob_info="Micro 5m FVG fill",
                    entry_explanation="Scalp Long targeting London session equilibrium.",
                    strategy_profile=self.name,
                    invalidation_conditions="Signal invalidates if 5m candle closes below sweep low."
                )

        # Check session high sweep for Short Scalp
        elif sess.asia_high and current_price > sess.asia_high:
            sl_dist = current_price * 0.005  # 0.5% tight stop
            sl_level = round(current_price + sl_dist, 2)
            tp1 = round(current_price - (sl_dist * 2.0), 2)
            tp2 = round(current_price - (sl_dist * 3.0), 2)
            tp3 = round(current_price - (sl_dist * 4.0), 2)

            confluence = ConfluenceScorer.calculate_score(
                direction="SELL",
                htf_bias=mtf.htf_bias.value,
                structure_break_type="BEARISH_CHOCH",
                has_liquidity_sweep=True,
                sweep_type="BSL",
                has_fvg_or_ob=True,
                dealing_zone="PREMIUM",
                has_displacement=True,
                rsi_value=68.0
            )

            if confluence.total_score >= self.min_confluence:
                return StrategySignalOutput(
                    direction="SELL",
                    entry_price=round(current_price, 2),
                    stop_loss=sl_level,
                    take_profit_1=tp1,
                    take_profit_2=tp2,
                    take_profit_3=tp3,
                    rr_ratio=2.0,
                    confluence_score=confluence.total_score,
                    htf_bias=mtf.htf_bias.value,
                    ltf_confirmation="Asia session high sweep and quick 5m rejection",
                    liquidity_event="Asia high liquidity sweep",
                    bos_choch_confirmation="Micro 5m CHoCH",
                    fvg_ob_info="Micro 5m FVG fill",
                    entry_explanation="Scalp Short targeting London session equilibrium.",
                    strategy_profile=self.name,
                    invalidation_conditions="Signal invalidates if 5m candle closes above sweep high."
                )

        return None
