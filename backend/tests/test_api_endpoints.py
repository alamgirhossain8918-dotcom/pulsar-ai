import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project"] == "PULSAR AI V2.0"
    assert data["status"] == "ONLINE"


def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "providers" in data


def test_market_overview():
    resp = client.get("/api/v1/market/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_provider" in data
    assert "priority_assets" in data


def test_risk_calculator_endpoint():
    payload = {
        "account_balance": 10000.0,
        "risk_percentage": 1.0,
        "entry_price": 60000.0,
        "stop_loss": 59000.0,
        "take_profit_1": 62000.0,
        "leverage": 10
    }
    resp = client.post("/api/v1/risk/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["direction"] == "BUY"
    assert data["risk_amount_usd"] == 100.0
    assert data["risk_reward_ratio_tp1"] == 2.0


def test_signals_list_endpoint():
    resp = client.get("/api/v1/signals")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_paper_trading_account_endpoint():
    resp = client.get("/api/v1/paper-trading/account")
    assert resp.status_code == 200
    data = resp.json()
    assert "balance" in data
    assert "equity" in data
