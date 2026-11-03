from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.engine.mtf_analyzer import MTFAnalysisResult
from backend.app.strategies.base import BaseStrategy
from backend.app.strategies.sniper_strategy import ICTSniperStrategy
from backend.app.strategies.swing_strategy import ICTSwingStrategy
from backend.app.strategies.scalp_strategy import ICTScalpStrategy


class SignalPayload(BaseModel):
    symbol: str
    direction: str  # BUY or SELL
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    rr_ratio: float
    confluence_score: float
    htf_bias: str
    ltf_confirmation: str
    liquidity_event: str
    bos_choch_confirmation: str
    fvg_ob_info: str
    entry_explanation: str
    status: str = "Pending"
    strategy_profile: str
    data_provider: str
    is_demo: bool = False
    created_at: datetime
    expiry_time: datetime
    invalidation_conditions: str


class SignalGenerator:
    """Orchestrates strategy execution with strict institutional quality gates"""

    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {
            "sniper": ICTSniperStrategy(
                min_confluence=settings.MIN_CONFLUENCE_SCORE,
                min_rr=settings.MIN_RR_RATIO
            ),
            "swing": ICTSwingStrategy(
                min_confluence=settings.MIN_CONFLUENCE_SCORE,
                min_rr=settings.MIN_RR_RATIO
            ),
            "scalp": ICTScalpStrategy(
                min_confluence=settings.MIN_CONFLUENCE_SCORE,
                min_rr=settings.MIN_RR_RATIO
            )
        }

    def generate_signal(
        self,
        mtf_result: MTFAnalysisResult,
        strategy_name: Optional[str] = None
    ) -> Optional[SignalPayload]:
        """
        Executes selected or all strategies.
        Returns a qualified SignalPayload only if all quality gates pass.
        Returns None (NO TRADE) if market is unclear.
        """
        target_strategies = []
        if strategy_name and strategy_name.lower() in self.strategies:
            target_strategies.append(self.strategies[strategy_name.lower()])
        else:
            # Default to sniper first, then swing, then scalp
            target_strategies = [
                self.strategies["sniper"],
                self.strategies["swing"],
                self.strategies["scalp"]
            ]

        for strat in target_strategies:
            signal_output = strat.evaluate(mtf_result)
            if not signal_output:
                continue

            # Strict Quality Gates Verification:
            # Gate 1: Confluence Score
            if signal_output.confluence_score < settings.MIN_CONFLUENCE_SCORE:
                logger.info(f"Signal rejected for {mtf_result.symbol}: confluence {signal_output.confluence_score} < {settings.MIN_CONFLUENCE_SCORE}")
                continue

            # Gate 2: Risk / Reward
            if signal_output.rr_ratio < settings.MIN_RR_RATIO:
                logger.info(f"Signal rejected for {mtf_result.symbol}: RR {signal_output.rr_ratio} < {settings.MIN_RR_RATIO}")
                continue

            # Gate 3: Validity of Entry and Stop
            if signal_output.direction == "BUY" and signal_output.entry_price <= signal_output.stop_loss:
                continue
            if signal_output.direction == "SELL" and signal_output.entry_price >= signal_output.stop_loss:
                continue

            now = datetime.now(timezone.utc)
            expiry = now + timedelta(hours=24)

            return SignalPayload(
                symbol=mtf_result.symbol,
                direction=signal_output.direction,
                entry_price=signal_output.entry_price,
                stop_loss=signal_output.stop_loss,
                take_profit_1=signal_output.take_profit_1,
                take_profit_2=signal_output.take_profit_2,
                take_profit_3=signal_output.take_profit_3,
                rr_ratio=signal_output.rr_ratio,
                confluence_score=signal_output.confluence_score,
                htf_bias=signal_output.htf_bias,
                ltf_confirmation=signal_output.ltf_confirmation,
                liquidity_event=signal_output.liquidity_event,
                bos_choch_confirmation=signal_output.bos_choch_confirmation,
                fvg_ob_info=signal_output.fvg_ob_info,
                entry_explanation=signal_output.entry_explanation,
                status="Pending",
                strategy_profile=signal_output.strategy_profile,
                data_provider=mtf_result.provider,
                is_demo=mtf_result.is_demo,
                created_at=now,
                expiry_time=expiry,
                invalidation_conditions=signal_output.invalidation_conditions
            )

        return None


signal_generator = SignalGenerator()
