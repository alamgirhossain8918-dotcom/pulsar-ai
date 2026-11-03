from typing import Optional
from backend.app.engine.confluence import ConfluenceScorer
from backend.app.engine.mtf_analyzer import MTFAnalysisResult
from backend.app.market_structure.structure import MarketTrend, StructureType
from backend.app.strategies.base import BaseStrategy, StrategySignalOutput


class ICTSniperStrategy(BaseStrategy):
    """
    ICT Sniper Strategy
    Precision setup: Liquidity Raid -> CHoCH with Displacement -> Retracement to OTE/FVG -> Entry
    """

    def __init__(self, min_confluence: float = 70.0, min_rr: float = 2.0):
        super().__init__(name="Sniper", min_confluence=min_confluence, min_rr=min_rr)

    def evaluate(self, mtf: MTFAnalysisResult) -> Optional[StrategySignalOutput]:
        ltf_key = "15m" if "15m" in mtf.tf_analyses else ("5m" if "5m" in mtf.tf_analyses else list(mtf.tf_analyses.keys())[0])
        ltf = mtf.tf_analyses.get(ltf_key)
        if not ltf:
            return None

        current_price = ltf.dealing_range.current_price
        htf_bias_str = mtf.htf_bias.value

        # Check for recent sweeps (in last 5 candles)
        recent_sweeps = ltf.sweeps
        has_ssl_sweep = any(s.pool_type == "SSL" for s in recent_sweeps)
        has_bsl_sweep = any(s.pool_type == "BSL" for s in recent_sweeps)

        # Check recent structure breaks
        recent_breaks = ltf.breaks
        bullish_choch = any(b.break_type == StructureType.BULLISH_CHOCH for b in recent_breaks)
        bearish_choch = any(b.break_type == StructureType.BEARISH_CHOCH for b in recent_breaks)
        bullish_bos = any(b.break_type == StructureType.BULLISH_BOS for b in recent_breaks)
        bearish_bos = any(b.break_type == StructureType.BEARISH_BOS for b in recent_breaks)

        # Check unmitigated FVGs or active OBs
        unmitigated_bullish_fvgs = [f for f in ltf.fvgs if f.kind == "BULLISH" and not f.is_mitigated]
        unmitigated_bearish_fvgs = [f for f in ltf.fvgs if f.kind == "BEARISH" and not f.is_mitigated]
        active_bullish_obs = [o for o in ltf.order_blocks if o.kind == "BULLISH" and not o.is_invalidated]
        active_bearish_obs = [o for o in ltf.order_blocks if o.kind == "BEARISH" and not o.is_invalidated]

        # Check displacement
        has_displacement = any(b.displacement for b in recent_breaks)

        # -------------------
        # 1. EVALUATE BUY SETUP
        # -------------------
        if (has_ssl_sweep or bullish_choch or bullish_bos) and (unmitigated_bullish_fvgs or active_bullish_obs):
            # Prefer entry when resting in discount or OTE
            zone = ltf.dealing_range.zone
            sl_level = ltf.recent_low if ltf.recent_low and ltf.recent_low < current_price else (current_price * 0.985)
            sl_distance = current_price - sl_level

            if sl_distance > 0:
                tp1 = round(current_price + (sl_distance * 2.0), 2)
                tp2 = round(current_price + (sl_distance * 3.5), 2)
                tp3 = round(current_price + (sl_distance * 5.0), 2)
                rr = round(2.0, 2)

                confluence = ConfluenceScorer.calculate_score(
                    direction="BUY",
                    htf_bias=htf_bias_str,
                    structure_break_type="BULLISH_CHOCH" if bullish_choch else "BULLISH_BOS",
                    has_liquidity_sweep=has_ssl_sweep,
                    sweep_type="SSL",
                    has_fvg_or_ob=bool(unmitigated_bullish_fvgs or active_bullish_obs),
                    dealing_zone=zone,
                    has_displacement=has_displacement,
                    rsi_value=50.0
                )

                if confluence.total_score >= self.min_confluence and rr >= self.min_rr:
                    return StrategySignalOutput(
                        direction="BUY",
                        entry_price=round(current_price, 2),
                        stop_loss=round(sl_level, 2),
                        take_profit_1=tp1,
                        take_profit_2=tp2,
                        take_profit_3=tp3,
                        rr_ratio=rr,
                        confluence_score=confluence.total_score,
                        htf_bias=htf_bias_str,
                        ltf_confirmation="SSL Sweep + LTF Structure Shift + Retest",
                        liquidity_event="Sell-side liquidity sweep below key swing low",
                        bos_choch_confirmation="Bullish CHoCH confirmed on closed candle",
                        fvg_ob_info="Entry confluence at unmitigated Bullish FVG / OB zone",
                        entry_explanation=f"Sniper Buy trigger: {' | '.join(confluence.reasons[:3])}",
                        strategy_profile=self.name,
                        invalidation_conditions="Signal invalidates if 15m candle closes below Stop Loss or if opposite CHoCH prints."
                    )

        # -------------------
        # 2. EVALUATE SELL SETUP
        # -------------------
        if (has_bsl_sweep or bearish_choch or bearish_bos) and (unmitigated_bearish_fvgs or active_bearish_obs):
            zone = ltf.dealing_range.zone
            sl_level = ltf.recent_high if ltf.recent_high and ltf.recent_high > current_price else (current_price * 1.015)
            sl_distance = sl_level - current_price

            if sl_distance > 0:
                tp1 = round(current_price - (sl_distance * 2.0), 2)
                tp2 = round(current_price - (sl_distance * 3.5), 2)
                tp3 = round(current_price - (sl_distance * 5.0), 2)
                rr = round(2.0, 2)

                confluence = ConfluenceScorer.calculate_score(
                    direction="SELL",
                    htf_bias=htf_bias_str,
                    structure_break_type="BEARISH_CHOCH" if bearish_choch else "BEARISH_BOS",
                    has_liquidity_sweep=has_bsl_sweep,
                    sweep_type="BSL",
                    has_fvg_or_ob=bool(unmitigated_bearish_fvgs or active_bearish_obs),
                    dealing_zone=zone,
                    has_displacement=has_displacement,
                    rsi_value=50.0
                )

                if confluence.total_score >= self.min_confluence and rr >= self.min_rr:
                    return StrategySignalOutput(
                        direction="SELL",
                        entry_price=round(current_price, 2),
                        stop_loss=round(sl_level, 2),
                        take_profit_1=tp1,
                        take_profit_2=tp2,
                        take_profit_3=tp3,
                        rr_ratio=rr,
                        confluence_score=confluence.total_score,
                        htf_bias=htf_bias_str,
                        ltf_confirmation="BSL Sweep + LTF Structure Shift + Retest",
                        liquidity_event="Buy-side liquidity sweep above key swing high",
                        bos_choch_confirmation="Bearish CHoCH confirmed on closed candle",
                        fvg_ob_info="Entry confluence at unmitigated Bearish FVG / OB zone",
                        entry_explanation=f"Sniper Sell trigger: {' | '.join(confluence.reasons[:3])}",
                        strategy_profile=self.name,
                        invalidation_conditions="Signal invalidates if 15m candle closes above Stop Loss or if opposite CHoCH prints."
                    )

        return None
