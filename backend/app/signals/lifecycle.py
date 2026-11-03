from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.data.data_models import Candle


class SignalUpdateEvent(BaseModel):
    signal_id: str
    symbol: str
    previous_status: str
    new_status: str
    price: float
    message: str
    realized_pnl: float = 0.0
    timestamp: datetime


class SignalLifecycleManager:
    """Manages state transitions, partial TP scaling, trailing stops, and net PnL"""

    FEE_RATE = 0.0005      # 0.05% taker fee
    SLIPPAGE_RATE = 0.0002  # 0.02% execution slippage

    @classmethod
    def evaluate_candle(
        cls,
        signal_data: Dict,
        candle: Candle
    ) -> Optional[SignalUpdateEvent]:
        """
        Evaluates a closed candle against an active signal.
        State machine:
            PENDING -> TRIGGERED or EXPIRED or INVALIDATED
            TRIGGERED -> TP1 HIT -> TP2 HIT -> TP3 HIT (CLOSED)
            TRIGGERED -> SL HIT (CLOSED)
        """
        now = datetime.now(timezone.utc)
        sig_id = signal_data["id"]
        symbol = signal_data["symbol"]
        direction = signal_data["direction"]
        entry = float(signal_data["entry_price"])
        sl = float(signal_data["stop_loss"])
        tp1 = float(signal_data["take_profit_1"])
        tp2 = float(signal_data["take_profit_2"])
        tp3 = float(signal_data["take_profit_3"])
        status = signal_data.get("status", "Pending")
        expiry = signal_data.get("expiry_time")

        high = candle.high
        low = candle.low
        close = candle.close

        # 1. PENDING STATE
        if status == "Pending":
            # Check expiry
            if expiry:
                exp_dt = expiry if isinstance(expiry, datetime) else datetime.fromisoformat(str(expiry))
                if now > exp_dt:
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status="Pending",
                        new_status="Expired",
                        price=close,
                        message=f"Signal expired without triggering.",
                        timestamp=now
                    )

            # Check if entry is reached within candle range
            if direction == "BUY":
                if low <= entry <= high:
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status="Pending",
                        new_status="Triggered",
                        price=entry,
                        message=f"BUY order filled at entry {entry}.",
                        timestamp=now
                    )
            elif direction == "SELL":
                if low <= entry <= high:
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status="Pending",
                        new_status="Triggered",
                        price=entry,
                        message=f"SELL order filled at entry {entry}.",
                        timestamp=now
                    )

        # 2. TRIGGERED / IN-TRADE STATE
        elif status in ["Triggered", "TP1 Hit", "TP2 Hit"]:
            # Check SL
            if direction == "BUY":
                # If TP1 hit, stop-loss was trailed to breakeven (entry)
                effective_sl = entry if status in ["TP1 Hit", "TP2 Hit"] else sl
                if low <= effective_sl:
                    # SL Hit
                    loss_pct = ((effective_sl - entry) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="SL Hit",
                        price=effective_sl,
                        realized_pnl=round(loss_pct * 100.0, 2),
                        message=f"Stop Loss hit at {effective_sl} (Trailing SL: {status in ['TP1 Hit', 'TP2 Hit']}).",
                        timestamp=now
                    )

                # Check TP3
                if high >= tp3:
                    gain_pct = ((tp3 - entry) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="TP3 Hit",
                        price=tp3,
                        realized_pnl=round(gain_pct * 100.0, 2),
                        message=f"Full TP3 target reached at {tp3}!",
                        timestamp=now
                    )

                # Check TP2
                if status == "TP1 Hit" and high >= tp2:
                    gain_pct = ((tp2 - entry) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="TP2 Hit",
                        price=tp2,
                        realized_pnl=round(gain_pct * 100.0, 2),
                        message=f"TP2 target reached at {tp2}.",
                        timestamp=now
                    )

                # Check TP1
                if status == "Triggered" and high >= tp1:
                    gain_pct = ((tp1 - entry) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="TP1 Hit",
                        price=tp1,
                        realized_pnl=round(gain_pct * 100.0, 2),
                        message=f"TP1 hit at {tp1}. Scaled out 50%, moved SL to Breakeven.",
                        timestamp=now
                    )

            elif direction == "SELL":
                effective_sl = entry if status in ["TP1 Hit", "TP2 Hit"] else sl
                if high >= effective_sl:
                    loss_pct = ((entry - effective_sl) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="SL Hit",
                        price=effective_sl,
                        realized_pnl=round(loss_pct * 100.0, 2),
                        message=f"Stop Loss hit at {effective_sl} (Trailing SL: {status in ['TP1 Hit', 'TP2 Hit']}).",
                        timestamp=now
                    )

                # Check TP3
                if low <= tp3:
                    gain_pct = ((entry - tp3) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="TP3 Hit",
                        price=tp3,
                        realized_pnl=round(gain_pct * 100.0, 2),
                        message=f"Full TP3 target reached at {tp3}!",
                        timestamp=now
                    )

                # Check TP2
                if status == "TP1 Hit" and low <= tp2:
                    gain_pct = ((entry - tp2) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="TP2 Hit",
                        price=tp2,
                        realized_pnl=round(gain_pct * 100.0, 2),
                        message=f"TP2 target reached at {tp2}.",
                        timestamp=now
                    )

                # Check TP1
                if status == "Triggered" and low <= tp1:
                    gain_pct = ((entry - tp1) / entry) - (cls.FEE_RATE * 2 + cls.SLIPPAGE_RATE)
                    return SignalUpdateEvent(
                        signal_id=sig_id,
                        symbol=symbol,
                        previous_status=status,
                        new_status="TP1 Hit",
                        price=tp1,
                        realized_pnl=round(gain_pct * 100.0, 2),
                        message=f"TP1 hit at {tp1}. Scaled out 50%, moved SL to Breakeven.",
                        timestamp=now
                    )

        return None
