import pytest
from backend.app.risk.calculator import RiskCalculator, RiskCalculationInput


def test_risk_calculation_buy():
    inp = RiskCalculationInput(
        account_balance=10000.0,
        risk_percentage=1.0,  # $100 risk
        entry_price=65000.0,
        stop_loss=64000.0,    # $1000 SL dist
        take_profit_1=67000.0,
        take_profit_2=68500.0,
        leverage=10
    )

    res = RiskCalculator.calculate(inp)
    assert res.direction == "BUY"
    assert res.risk_amount_usd == 100.0
    assert res.position_size_tokens > 0.09  # approx ~0.099
    assert res.estimated_margin_usd > 0
    assert res.potential_loss_usd >= 100.0
    assert res.potential_profit_tp1_usd > 180.0
    assert res.risk_reward_ratio_tp1 == 2.0
    assert res.approx_liquidation_price < 64000.0  # Safe with 10x leverage


def test_risk_calculation_excessive_leverage_warning():
    inp = RiskCalculationInput(
        account_balance=10000.0,
        risk_percentage=1.0,
        entry_price=65000.0,
        stop_loss=64500.0,
        leverage=50  # Over 25x threshold
    )

    res = RiskCalculator.calculate(inp)
    assert any("HIGH LEVERAGE WARNING" in w for w in res.warnings)


def test_risk_calculation_tight_stop_warning():
    inp = RiskCalculationInput(
        account_balance=10000.0,
        risk_percentage=1.0,
        entry_price=65000.0,
        stop_loss=64950.0,  # ~0.07% stop distance
        leverage=10
    )

    res = RiskCalculator.calculate(inp)
    assert any("Stop-Loss distance is under 0.25%" in w for w in res.warnings)
