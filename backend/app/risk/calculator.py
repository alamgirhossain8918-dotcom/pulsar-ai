from typing import List, Optional
from pydantic import BaseModel, Field


class RiskCalculationInput(BaseModel):
    account_balance: float = Field(..., gt=0, description="Account balance in USDT")
    risk_percentage: float = Field(default=1.0, gt=0, le=100, description="Percentage of balance to risk (default 1%)")
    entry_price: float = Field(..., gt=0, description="Planned entry price")
    stop_loss: float = Field(..., gt=0, description="Planned stop loss price")
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    leverage: int = Field(default=10, ge=1, le=125, description="Position leverage")
    trading_fee_rate: float = Field(default=0.0005, ge=0, description="Fee rate per transaction (default 0.05% taker)")
    slippage_rate: float = Field(default=0.0002, ge=0, description="Estimated slippage (default 0.02%)")


class RiskCalculationResult(BaseModel):
    direction: str  # BUY or SELL
    risk_amount_usd: float
    position_size_tokens: float
    notional_value_usd: float
    estimated_margin_usd: float
    total_estimated_fees_usd: float
    potential_loss_usd: float
    potential_profit_tp1_usd: Optional[float] = None
    potential_profit_tp2_usd: Optional[float] = None
    potential_profit_tp3_usd: Optional[float] = None
    risk_reward_ratio_tp1: Optional[float] = None
    risk_reward_ratio_tp2: Optional[float] = None
    risk_reward_ratio_tp3: Optional[float] = None
    approx_liquidation_price: float
    liquidation_distance_pct: float
    warnings: List[str]


class RiskCalculator:
    """Institutional Crypto Futures Risk and Position Sizing Calculator"""

    @staticmethod
    def calculate(params: RiskCalculationInput) -> RiskCalculationResult:
        warnings: List[str] = []

        # 1. Determine direction
        if params.entry_price > params.stop_loss:
            direction = "BUY"
            sl_distance = params.entry_price - params.stop_loss
        elif params.entry_price < params.stop_loss:
            direction = "SELL"
            sl_distance = params.stop_loss - params.entry_price
        else:
            raise ValueError("Entry price and Stop Loss cannot be identical.")

        sl_distance_pct = (sl_distance / params.entry_price) * 100.0
        if sl_distance_pct < 0.25:
            warnings.append("WARNING: Stop-Loss distance is under 0.25%. High risk of premature hunt on crypto volatility.")

        if params.leverage > 25:
            warnings.append("HIGH LEVERAGE WARNING: Leverage exceeds 25x. Liquidation risk significantly elevated.")

        # 2. Maximum capital to risk on this trade
        risk_amount_usd = params.account_balance * (params.risk_percentage / 100.0)

        # 3. Position size calculation based on stop loss distance
        # Loss per token = sl_distance + (entry_price * (fee_rate + slippage)) + (stop_loss * fee_rate)
        loss_per_token = sl_distance + (params.entry_price * (params.trading_fee_rate + params.slippage_rate)) + (params.stop_loss * params.trading_fee_rate)
        position_size_tokens = risk_amount_usd / max(loss_per_token, 1e-6)

        notional_value_usd = position_size_tokens * params.entry_price
        estimated_margin_usd = notional_value_usd / params.leverage

        if estimated_margin_usd > params.account_balance:
            warnings.append("MARGIN DEFICIT: Required margin exceeds current account balance. Increase leverage or decrease risk percentage.")

        # 4. Total fees
        entry_fee = notional_value_usd * params.trading_fee_rate
        exit_fee = (position_size_tokens * params.stop_loss) * params.trading_fee_rate
        total_fees = entry_fee + exit_fee
        potential_loss = (position_size_tokens * sl_distance) + total_fees

        # 5. Take Profit Calculations
        p_profit_tp1, rr_tp1 = None, None
        p_profit_tp2, rr_tp2 = None, None
        p_profit_tp3, rr_tp3 = None, None

        if params.take_profit_1:
            tp_dist = abs(params.take_profit_1 - params.entry_price)
            tp_exit_fee = (position_size_tokens * params.take_profit_1) * params.trading_fee_rate
            p_profit_tp1 = round((position_size_tokens * tp_dist) - (entry_fee + tp_exit_fee), 2)
            rr_tp1 = round(tp_dist / max(sl_distance, 1e-6), 2)

        if params.take_profit_2:
            tp_dist = abs(params.take_profit_2 - params.entry_price)
            tp_exit_fee = (position_size_tokens * params.take_profit_2) * params.trading_fee_rate
            p_profit_tp2 = round((position_size_tokens * tp_dist) - (entry_fee + tp_exit_fee), 2)
            rr_tp2 = round(tp_dist / max(sl_distance, 1e-6), 2)

        if params.take_profit_3:
            tp_dist = abs(params.take_profit_3 - params.entry_price)
            tp_exit_fee = (position_size_tokens * params.take_profit_3) * params.trading_fee_rate
            p_profit_tp3 = round((position_size_tokens * tp_dist) - (entry_fee + tp_exit_fee), 2)
            rr_tp3 = round(tp_dist / max(sl_distance, 1e-6), 2)

        # 6. Approximate Liquidation Price (Heuristic estimation; not exchange guarantee)
        # Maintenance margin approx ~ 0.5% for major crypto futures
        maint_margin_rate = 0.005
        if direction == "BUY":
            approx_liq = params.entry_price * (1.0 - (1.0 / params.leverage) + maint_margin_rate)
            liq_dist_pct = ((params.entry_price - approx_liq) / params.entry_price) * 100.0
            if approx_liq >= params.stop_loss:
                warnings.append("CRITICAL: Approximate liquidation is higher than your Stop Loss! You will be liquidated before SL triggers.")
        else:
            approx_liq = params.entry_price * (1.0 + (1.0 / params.leverage) - maint_margin_rate)
            liq_dist_pct = ((approx_liq - params.entry_price) / params.entry_price) * 100.0
            if approx_liq <= params.stop_loss:
                warnings.append("CRITICAL: Approximate liquidation is lower than your Stop Loss! You will be liquidated before SL triggers.")

        warnings.append("DISCLAIMER: Liquidation price is an approximate calculation. Exact exchange liquidation depends on maintenance margin tier.")

        return RiskCalculationResult(
            direction=direction,
            risk_amount_usd=round(risk_amount_usd, 2),
            position_size_tokens=round(position_size_tokens, 4),
            notional_value_usd=round(notional_value_usd, 2),
            estimated_margin_usd=round(estimated_margin_usd, 2),
            total_estimated_fees_usd=round(total_fees, 2),
            potential_loss_usd=round(potential_loss, 2),
            potential_profit_tp1_usd=p_profit_tp1,
            potential_profit_tp2_usd=p_profit_tp2,
            potential_profit_tp3_usd=p_profit_tp3,
            risk_reward_ratio_tp1=rr_tp1,
            risk_reward_ratio_tp2=rr_tp2,
            risk_reward_ratio_tp3=rr_tp3,
            approx_liquidation_price=round(approx_liq, 2),
            liquidation_distance_pct=round(liq_dist_pct, 2),
            warnings=warnings
        )
