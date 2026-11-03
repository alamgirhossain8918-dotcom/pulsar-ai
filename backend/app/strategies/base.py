from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from backend.app.engine.mtf_analyzer import MTFAnalysisResult


class StrategySignalOutput(BaseModel):
    direction: str  # "BUY" or "SELL"
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
    strategy_profile: str
    invalidation_conditions: str


class BaseStrategy(ABC):
    """Abstract Base Class for all PULSAR AI ICT/SMC Trading Strategies"""

    def __init__(self, name: str, min_confluence: float = 70.0, min_rr: float = 2.0):
        self.name = name
        self.min_confluence = min_confluence
        self.min_rr = min_rr

    @abstractmethod
    def evaluate(self, mtf_result: MTFAnalysisResult) -> Optional[StrategySignalOutput]:
        """Analyzes multi-timeframe market state and produces a qualified signal or None"""
        pass
