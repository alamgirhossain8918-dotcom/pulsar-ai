from typing import Dict, List
from pydantic import BaseModel


class ConfluenceBreakdown(BaseModel):
    htf_bias_score: float
    structure_score: float
    liquidity_score: float
    poi_mitigation_score: float  # FVG / OB
    premium_discount_score: float
    momentum_score: float
    total_score: float
    reasons: List[str]


class ConfluenceScorer:
    """Calculates algorithmic confluence score (0 - 100) for trading setups"""

    @staticmethod
    def calculate_score(
        direction: str,  # "BUY" or "SELL"
        htf_bias: str,
        structure_break_type: str,
        has_liquidity_sweep: bool,
        sweep_type: str,
        has_fvg_or_ob: bool,
        dealing_zone: str,
        has_displacement: bool,
        rsi_value: float
    ) -> ConfluenceBreakdown:
        score = 0.0
        reasons: List[str] = []
        is_buy = direction.upper() == "BUY"

        # 1. HTF Bias Alignment (Max 20 pts)
        htf_score = 0.0
        if is_buy and "Bullish" in htf_bias:
            htf_score = 20.0
            reasons.append(f"Higher Timeframe is bullish (+20)")
        elif not is_buy and "Bearish" in htf_bias:
            htf_score = 20.0
            reasons.append(f"Higher Timeframe is bearish (+20)")
        elif "Neutral" in htf_bias or "Ranging" in htf_bias:
            htf_score = 8.0
            reasons.append(f"Higher Timeframe is neutral/ranging (+8)")
        else:
            reasons.append(f"Counter-trend to Higher Timeframe bias (+0)")

        # 2. Market Structure (BOS / CHoCH) (Max 20 pts)
        struct_score = 0.0
        if is_buy:
            if "BULLISH_CHOCH" in structure_break_type:
                struct_score = 20.0
                reasons.append("Bullish Change of Character (CHoCH) confirmed (+20)")
            elif "BULLISH_BOS" in structure_break_type:
                struct_score = 17.0
                reasons.append("Bullish Break of Structure (BOS) confirmed (+17)")
        else:
            if "BEARISH_CHOCH" in structure_break_type:
                struct_score = 20.0
                reasons.append("Bearish Change of Character (CHoCH) confirmed (+20)")
            elif "BEARISH_BOS" in structure_break_type:
                struct_score = 17.0
                reasons.append("Bearish Break of Structure (BOS) confirmed (+17)")

        # 3. Liquidity Sweep (Max 20 pts)
        liq_score = 0.0
        if has_liquidity_sweep:
            if is_buy and "SSL" in sweep_type:
                liq_score = 20.0
                reasons.append("Sell-Side Liquidity (SSL) swept before reversal (+20)")
            elif not is_buy and "BSL" in sweep_type:
                liq_score = 20.0
                reasons.append("Buy-Side Liquidity (BSL) swept before reversal (+20)")
            else:
                liq_score = 10.0
                reasons.append("Minor liquidity raid detected (+10)")
        else:
            reasons.append("No clear institutional liquidity sweep (+0)")

        # 4. Point of Interest (FVG / OB Mitigation) (Max 15 pts)
        poi_score = 0.0
        if has_fvg_or_ob:
            poi_score = 15.0
            reasons.append("Price reacting inside unmitigated Order Block / FVG (+15)")
        else:
            reasons.append("No active unmitigated Order Block / FVG confluence (+0)")

        # 5. Premium / Discount / OTE Alignment (Max 15 pts)
        pd_score = 0.0
        if is_buy:
            if dealing_zone == "OTE_BUY":
                pd_score = 15.0
                reasons.append("Entry resting in Optimal Trade Entry (OTE 0.62 - 0.79) (+15)")
            elif dealing_zone == "DISCOUNT":
                pd_score = 12.0
                reasons.append("Entry resting in Discount Zone (< 0.50) (+12)")
            else:
                reasons.append(f"Entry is in {dealing_zone} (Unfavorable for Long) (+0)")
        else:
            if dealing_zone == "OTE_SELL":
                pd_score = 15.0
                reasons.append("Entry resting in Optimal Trade Entry (OTE 0.62 - 0.79) (+15)")
            elif dealing_zone == "PREMIUM":
                pd_score = 12.0
                reasons.append("Entry resting in Premium Zone (> 0.50) (+12)")
            else:
                reasons.append(f"Entry is in {dealing_zone} (Unfavorable for Short) (+0)")

        # 6. Momentum & Displacement (Max 10 pts)
        mom_score = 0.0
        if has_displacement:
            mom_score += 6.0
            reasons.append("Institutional displacement impulse candle present (+6)")
        if is_buy and 35.0 <= rsi_value <= 60.0:
            mom_score += 4.0
            reasons.append(f"RSI ({round(rsi_value, 1)}) indicates healthy momentum pullback (+4)")
        elif not is_buy and 40.0 <= rsi_value <= 65.0:
            mom_score += 4.0
            reasons.append(f"RSI ({round(rsi_value, 1)}) indicates healthy momentum pullback (+4)")

        total = htf_score + struct_score + liq_score + poi_score + pd_score + mom_score

        return ConfluenceBreakdown(
            htf_bias_score=htf_score,
            structure_score=struct_score,
            liquidity_score=liq_score,
            poi_mitigation_score=poi_score,
            premium_discount_score=pd_score,
            momentum_score=mom_score,
            total_score=round(total, 1),
            reasons=reasons
        )
