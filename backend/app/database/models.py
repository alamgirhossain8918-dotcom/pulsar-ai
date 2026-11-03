from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Integer, JSON, ForeignKey, Text, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    paper_accounts = relationship("PaperAccount", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = Column(String(50), default="dark")
    default_leverage = Column(Integer, default=10)
    risk_percentage = Column(Float, default=1.0)
    telegram_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User", back_populates="settings")


class MarketSymbol(Base):
    __tablename__ = "market_symbols"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(50), unique=True, index=True, nullable=False)  # e.g., BTCUSDT
    base_asset = Column(String(20), nullable=False)  # BTC
    quote_asset = Column(String(20), nullable=False)  # USDT
    is_active = Column(Boolean, default=True, index=True)
    price_precision = Column(Integer, default=2)
    quantity_precision = Column(Integer, default=3)
    min_quantity = Column(Float, default=0.001)
    priority = Column(Integer, default=10)  # Lower is higher priority (e.g. 1 for BTCUSDT)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class MarketCandle(Base):
    __tablename__ = "market_candles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(50), index=True, nullable=False)
    timeframe = Column(String(10), index=True, nullable=False)
    open_time = Column(DateTime(timezone=True), index=True, nullable=False)
    close_time = Column(DateTime(timezone=True), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    is_closed = Column(Boolean, default=True, nullable=False)
    provider = Column(String(50), default="binance", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", "open_time", "provider", name="uq_candle_key"),
        Index("idx_candles_sym_tf_time", "symbol", "timeframe", "open_time"),
    )


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(50), index=True, nullable=False)
    timeframe = Column(String(10), nullable=False)
    last_price = Column(Float, nullable=False)
    trend = Column(String(50), nullable=False)
    regime = Column(String(50), nullable=False)
    htf_bias = Column(String(50), nullable=False)
    ltf_structure = Column(String(50), nullable=False)
    swing_high = Column(Float, nullable=True)
    swing_low = Column(Float, nullable=True)
    bos_choch = Column(String(50), nullable=True)
    fvg_status = Column(String(50), nullable=True)
    ob_status = Column(String(50), nullable=True)
    liquidity_sweep = Column(String(100), nullable=True)
    confluence_score = Column(Float, default=0.0)
    provider = Column(String(50), default="binance")
    is_demo = Column(Boolean, default=False)
    snapshot_time = Column(DateTime(timezone=True), default=utcnow, index=True)
    details = Column(JSON, nullable=True)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(50), index=True, nullable=False)
    direction = Column(String(10), index=True, nullable=False)  # BUY or SELL
    timeframe = Column(String(10), default="15m", nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit_1 = Column(Float, nullable=False)
    take_profit_2 = Column(Float, nullable=False)
    take_profit_3 = Column(Float, nullable=False)
    rr_ratio = Column(Float, nullable=False)
    confluence_score = Column(Float, nullable=False)
    htf_bias = Column(String(50), nullable=False)
    ltf_confirmation = Column(String(100), nullable=False)
    liquidity_event = Column(String(100), nullable=False)
    bos_choch_confirmation = Column(String(100), nullable=False)
    fvg_ob_info = Column(String(200), nullable=False)
    entry_explanation = Column(Text, nullable=False)
    status = Column(String(50), default="Pending", index=True, nullable=False)
    # Pending, Triggered, TP1 Hit, TP2 Hit, TP3 Hit, SL Hit, Expired, Invalidated
    strategy_profile = Column(String(100), default="Sniper", nullable=False)
    data_provider = Column(String(50), default="binance", nullable=False)
    is_demo = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    expiry_time = Column(DateTime(timezone=True), nullable=False)
    invalidation_conditions = Column(Text, nullable=True)
    realized_pnl = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)

    events = relationship("SignalEvent", back_populates="signal", cascade="all, delete-orphan")


class SignalEvent(Base):
    __tablename__ = "signal_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_id = Column(String(36), ForeignKey("signals.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type = Column(String(50), nullable=False)  # CREATED, TRIGGERED, TP1, TP2, TP3, SL, EXPIRED, INVALIDATED
    price = Column(Float, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    signal = relationship("Signal", back_populates="events")


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    symbol = Column(String(50), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    strategy_profile = Column(String(100), default="Sniper")
    initial_balance = Column(Float, default=10000.0)
    final_balance = Column(Float, default=10000.0)
    net_pnl = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    average_rr = Column(Float, default=0.0)
    equity_curve = Column(JSON, nullable=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    trades = relationship("BacktestTrade", back_populates="run", cascade="all, delete-orphan")


class BacktestTrade(Base):
    __tablename__ = "backtest_trades"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("backtest_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    symbol = Column(String(50), nullable=False)
    direction = Column(String(10), nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    position_size = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    pnl = Column(Float, nullable=False)
    return_percentage = Column(Float, nullable=False)
    exit_reason = Column(String(50), nullable=False)  # TP1, TP2, TP3, SL, TIMEOUT

    run = relationship("BacktestRun", back_populates="trades")


class PaperAccount(Base):
    __tablename__ = "paper_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), default="Main Virtual Account")
    initial_balance = Column(Float, default=10000.0)
    balance = Column(Float, default=10000.0)
    margin_used = Column(Float, default=0.0)
    currency = Column(String(10), default="USDT")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User", back_populates="paper_accounts")
    positions = relationship("PaperPosition", back_populates="account", cascade="all, delete-orphan")
    trades = relationship("PaperTrade", back_populates="account", cascade="all, delete-orphan")


class PaperPosition(Base):
    __tablename__ = "paper_positions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("paper_accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    symbol = Column(String(50), index=True, nullable=False)
    direction = Column(String(10), nullable=False)  # BUY / SELL
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    leverage = Column(Integer, default=10)
    margin = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit_1 = Column(Float, nullable=False)
    take_profit_2 = Column(Float, nullable=False)
    take_profit_3 = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    status = Column(String(50), default="OPEN")  # OPEN, CLOSED
    opened_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    account = relationship("PaperAccount", back_populates="positions")


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("paper_accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    symbol = Column(String(50), nullable=False)
    direction = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    leverage = Column(Integer, default=10)
    fee = Column(Float, default=0.0)
    pnl = Column(Float, nullable=False)
    exit_reason = Column(String(50), nullable=False)
    opened_at = Column(DateTime(timezone=True), nullable=False)
    closed_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    account = relationship("PaperAccount", back_populates="trades")


class PerformanceSnapshot(Base):
    __tablename__ = "performance_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_date = Column(DateTime(timezone=True), default=utcnow, index=True)
    total_signals = Column(Integer, default=0)
    winning_signals = Column(Integer, default=0)
    losing_signals = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    net_pnl = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    average_rr = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    metrics_by_symbol = Column(JSON, nullable=True)
    metrics_by_timeframe = Column(JSON, nullable=True)
    metrics_by_strategy = Column(JSON, nullable=True)
    data_type = Column(String(50), default="live")  # live, backtest, demo


class StrategyProfile(Base):
    __tablename__ = "strategy_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    min_confluence = Column(Float, default=70.0)
    min_rr = Column(Float, default=2.0)
    risk_percentage = Column(Float, default=1.0)
    allowed_timeframes = Column(JSON, default=lambda: ["15m", "1h", "4h"])
    parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class StrategyConfigVersion(Base):
    __tablename__ = "strategy_config_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("strategy_profiles.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    config_snapshot = Column(JSON, nullable=False)
    change_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel = Column(String(50), default="telegram")
    target = Column(String(255), nullable=False)  # Chat ID or Channel ID
    notify_on_new_signal = Column(Boolean, default=True)
    notify_on_triggered = Column(Boolean, default=True)
    notify_on_tp_hit = Column(Boolean, default=True)
    notify_on_sl_hit = Column(Boolean, default=True)
    notify_on_expired = Column(Boolean, default=False)
    notify_on_provider_down = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class SystemHealth(Base):
    __tablename__ = "system_health"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # HEALTHY, DEGRADED, DOWN
    primary_provider = Column(String(50), default="binance")
    active_provider = Column(String(50), default="binance")
    last_heartbeat = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_scan_time = Column(DateTime(timezone=True), nullable=True)
    latency_ms = Column(Float, default=0.0)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(100), nullable=False)
    actor = Column(String(100), default="system")
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
