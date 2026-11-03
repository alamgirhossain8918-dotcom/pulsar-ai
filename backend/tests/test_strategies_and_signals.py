import pytest
from datetime import datetime, timezone
from backend.app.data.data_models import Candle
from backend.app.signals.lifecycle import SignalLifecycleManager
from backend.app.signals.tracker import SignalTracker


def test_signal_lifecycle_tp_and_sl():
    sig_data = {
        "id": "sig-test-1",
        "symbol": "BTCUSDT",
        "direction": "BUY",
        "entry_price": 60000.0,
        "stop_loss": 59000.0,
        "take_profit_1": 62000.0,
        "take_profit_2": 63500.0,
        "take_profit_3": 65000.0,
        "status": "Pending",
        "expiry_time": None
    }

    # 1. Candle triggers entry
    c_trigger = Candle(
        timestamp=datetime.now(timezone.utc),
        open=60100.0,
        high=60500.0,
        low=59900.0,
        close=60300.0,
        volume=100.0
    )
    ev1 = SignalLifecycleManager.evaluate_candle(sig_data, c_trigger)
    assert ev1 is not None
    assert ev1.new_status == "Triggered"
    sig_data["status"] = "Triggered"

    # 2. Candle hits TP1
    c_tp1 = Candle(
        timestamp=datetime.now(timezone.utc),
        open=60300.0,
        high=62200.0,
        low=60200.0,
        close=62100.0,
        volume=150.0
    )
    ev2 = SignalLifecycleManager.evaluate_candle(sig_data, c_tp1)
    assert ev2 is not None
    assert ev2.new_status == "TP1 Hit"
    assert ev2.realized_pnl > 0


def test_signal_tracker_cooldown():
    tracker = SignalTracker()
    assert tracker.is_in_cooldown("BTCUSDT") is False

    tracker.record_new_signal({
        "id": "sig-test-cooldown",
        "symbol": "BTCUSDT",
        "direction": "BUY",
        "entry_price": 60000.0,
        "stop_loss": 59000.0,
        "take_profit_1": 62000.0,
        "take_profit_2": 63000.0,
        "take_profit_3": 64000.0
    })

    assert tracker.is_in_cooldown("BTCUSDT") is True
