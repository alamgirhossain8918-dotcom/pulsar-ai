from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.signals.lifecycle import SignalLifecycleManager, SignalUpdateEvent
from backend.app.data.data_models import Candle


class SignalTracker:
    """In-memory active signal manager with cooldown and lifecycle tracking"""

    def __init__(self):
        # Map: symbol -> datetime of last signal generated
        self._last_signal_times: Dict[str, datetime] = {}
        # In-memory store of active signals: id -> dict
        self._active_signals: Dict[str, Dict] = {}

    def is_in_cooldown(self, symbol: str) -> bool:
        last_time = self._last_signal_times.get(symbol)
        if not last_time:
            return False
        elapsed = datetime.now(timezone.utc) - last_time
        return elapsed < timedelta(minutes=settings.SIGNAL_COOLDOWN_MINUTES)

    def record_new_signal(self, signal_dict: Dict) -> None:
        sym = signal_data = signal_dict["symbol"]
        self._last_signal_times[sym] = datetime.now(timezone.utc)
        self._active_signals[signal_dict["id"]] = signal_dict
        logger.info(f"Recorded new signal {signal_dict['id']} for {sym} {signal_dict['direction']}")

    def get_active_signals(self) -> List[Dict]:
        return list(self._active_signals.values())

    def update_with_candle(self, symbol: str, candle: Candle) -> List[SignalUpdateEvent]:
        events: List[SignalUpdateEvent] = []
        to_remove = []

        for sig_id, sig in self._active_signals.items():
            if sig.get("symbol") != symbol:
                continue

            event = SignalLifecycleManager.evaluate_candle(sig, candle)
            if event:
                events.append(event)
                sig["status"] = event.new_status
                if event.realized_pnl != 0.0:
                    sig["realized_pnl"] = event.realized_pnl

                # If terminal state, schedule removal from active tracking
                if event.new_status in ["SL Hit", "TP3 Hit", "Expired", "Invalidated"]:
                    to_remove.append(sig_id)

        for sig_id in to_remove:
            self._active_signals.pop(sig_id, None)

        return events


signal_tracker = SignalTracker()
