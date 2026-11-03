import pytest
from backend.app.paper_trading.paper_engine import PaperTradingEngine, PaperOrderRequest


def test_paper_trading_lifecycle():
    engine = PaperTradingEngine(initial_balance=10000.0)
    summary = engine.get_account_summary()
    assert summary["balance"] == 10000.0

    # 1. Open virtual position
    req = PaperOrderRequest(
        symbol="BTCUSDT",
        direction="BUY",
        entry_price=60000.0,
        stop_loss=58000.0,
        take_profit_1=64000.0,
        quantity=0.1,  # Notional: $6,000, 10x margin: $600
        leverage=10
    )
    pos = engine.open_position(req)
    assert pos.status == "OPEN"
    assert pos.margin == 600.0
    assert engine.margin_used == 600.0

    # 2. Close position with profit
    trade = engine.close_position(pos.id, exit_price=64000.0, exit_reason="TAKE_PROFIT")
    assert trade.pnl > 390.0  # (64000 - 60000) * 0.1 - fees
    assert engine.margin_used == 0.0
    assert engine.balance > 10390.0


def test_paper_trading_margin_protection():
    engine = PaperTradingEngine(initial_balance=1000.0)
    # Attempt position requiring $5,000 margin on a $1,000 balance
    req = PaperOrderRequest(
        symbol="BTCUSDT",
        direction="BUY",
        entry_price=50000.0,
        stop_loss=48000.0,
        take_profit_1=55000.0,
        quantity=1.0,  # Notional: $50,000, 10x margin: $5,000
        leverage=10
    )
    with pytest.raises(ValueError, match="Insufficient virtual free margin"):
        engine.open_position(req)
