import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.core.logger import logger
from backend.app.data.data_models import Candle


class PaperOrderRequest(BaseModel):
    symbol: str
    direction: str  # BUY or SELL
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    quantity: float
    leverage: int = 10


class VirtualPosition(BaseModel):
    id: str
    symbol: str
    direction: str
    entry_price: float
    current_price: float
    quantity: float
    leverage: int
    margin: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float]
    take_profit_3: Optional[float]
    unrealized_pnl: float = 0.0
    status: str = "OPEN"
    opened_at: datetime
    closed_at: Optional[datetime] = None


class VirtualTrade(BaseModel):
    id: str
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    quantity: float
    leverage: int
    fee: float
    pnl: float
    exit_reason: str
    opened_at: datetime
    closed_at: datetime


class PaperTradingEngine:
    """
    Virtual Paper Trading Simulation Engine.
    STRICT SECURITY RULE: Never executes real exchange orders.
    Requires ZERO exchange API keys.
    """

    FEE_RATE = 0.0005  # 0.05% taker

    def __init__(self, initial_balance: float = 10000.0):
        self.balance: float = initial_balance
        self.initial_balance: float = initial_balance
        self.margin_used: float = 0.0
        self.positions: Dict[str, VirtualPosition] = {}
        self.trade_history: List[VirtualTrade] = []

    def get_account_summary(self) -> Dict:
        unrealized_total = sum(p.unrealized_pnl for p in self.positions.values())
        equity = self.balance + unrealized_total
        return {
            "balance": round(self.balance, 2),
            "equity": round(equity, 2),
            "margin_used": round(self.margin_used, 2),
            "free_margin": round(max(0.0, self.balance - self.margin_used), 2),
            "unrealized_pnl": round(unrealized_total, 2),
            "open_positions_count": len(self.positions),
            "total_trades_count": len(self.trade_history)
        }

    def open_position(self, req: PaperOrderRequest) -> VirtualPosition:
        notional = req.entry_price * req.quantity
        required_margin = notional / req.leverage

        if required_margin > (self.balance - self.margin_used):
            raise ValueError(f"Insufficient virtual free margin. Required: ${round(required_margin, 2)}, Available: ${round(self.balance - self.margin_used, 2)}")

        # Deduct entry fee from virtual balance
        entry_fee = notional * self.FEE_RATE
        self.balance -= entry_fee
        self.margin_used += required_margin

        pos_id = str(uuid.uuid4())
        pos = VirtualPosition(
            id=pos_id,
            symbol=req.symbol.upper(),
            direction=req.direction.upper(),
            entry_price=req.entry_price,
            current_price=req.entry_price,
            quantity=req.quantity,
            leverage=req.leverage,
            margin=round(required_margin, 2),
            stop_loss=req.stop_loss,
            take_profit_1=req.take_profit_1,
            take_profit_2=req.take_profit_2,
            take_profit_3=req.take_profit_3,
            unrealized_pnl=0.0,
            status="OPEN",
            opened_at=datetime.now(timezone.utc)
        )
        self.positions[pos_id] = pos
        logger.info(f"Paper trade opened: {pos.direction} {pos.quantity} {pos.symbol} @ {pos.entry_price}")
        return pos

    def close_position(self, pos_id: str, exit_price: float, exit_reason: str = "MANUAL") -> VirtualTrade:
        pos = self.positions.get(pos_id)
        if not pos:
            raise ValueError(f"Position {pos_id} not found.")

        notional_exit = exit_price * pos.quantity
        exit_fee = notional_exit * self.FEE_RATE

        if pos.direction == "BUY":
            raw_pnl = (exit_price - pos.entry_price) * pos.quantity
        else:
            raw_pnl = (pos.entry_price - exit_price) * pos.quantity

        net_pnl = raw_pnl - exit_fee
        self.balance += (pos.margin + net_pnl)
        self.margin_used = max(0.0, self.margin_used - pos.margin)

        now = datetime.now(timezone.utc)
        trade = VirtualTrade(
            id=pos.id,
            symbol=pos.symbol,
            direction=pos.direction,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            quantity=pos.quantity,
            leverage=pos.leverage,
            fee=round(exit_fee, 2),
            pnl=round(net_pnl, 2),
            exit_reason=exit_reason,
            opened_at=pos.opened_at,
            closed_at=now
        )
        self.trade_history.append(trade)
        del self.positions[pos_id]
        logger.info(f"Paper trade closed: {trade.symbol} PnL=${trade.pnl} Reason={trade.exit_reason}")
        return trade

    def update_positions_with_candle(self, symbol: str, candle: Candle) -> List[VirtualTrade]:
        """Checks SL / TP triggers across virtual positions"""
        closed_trades: List[VirtualTrade] = []
        to_close = []

        for pos_id, pos in list(self.positions.items()):
            if pos.symbol != symbol.upper():
                continue

            # Update current mark price
            pos.current_price = candle.close
            if pos.direction == "BUY":
                pos.unrealized_pnl = round((candle.close - pos.entry_price) * pos.quantity, 2)
                # Check SL
                if candle.low <= pos.stop_loss:
                    to_close.append((pos_id, pos.stop_loss, "STOP_LOSS"))
                # Check TP1
                elif candle.high >= pos.take_profit_1:
                    to_close.append((pos_id, pos.take_profit_1, "TAKE_PROFIT_1"))
            else:
                pos.unrealized_pnl = round((pos.entry_price - candle.close) * pos.quantity, 2)
                # Check SL
                if candle.high >= pos.stop_loss:
                    to_close.append((pos_id, pos.stop_loss, "STOP_LOSS"))
                # Check TP1
                elif candle.low <= pos.take_profit_1:
                    to_close.append((pos_id, pos.take_profit_1, "TAKE_PROFIT_1"))

        for p_id, exit_p, reason in to_close:
            if p_id in self.positions:
                t = self.close_position(p_id, exit_p, reason)
                closed_trades.append(t)

        return closed_trades


paper_engine = PaperTradingEngine()
