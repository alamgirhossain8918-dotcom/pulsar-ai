from typing import List, Dict, Any
from pydantic import BaseModel


class BacktestTradeRecord(BaseModel):
    trade_id: int
    symbol: str
    direction: str
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    size: float
    fees: float
    slippage: float
    pnl: float
    pnl_percent: float
    exit_reason: str  # TP1, TP2, TP3, SL, TIMEOUT


class BacktestSummary(BaseModel):
    symbol: str
    timeframe: str
    strategy_profile: str
    initial_balance: float
    final_balance: float
    net_pnl: float
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_percent: float
    average_rr: float
    equity_curve: List[Dict[str, Any]]
    trades: List[BacktestTradeRecord]
