from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_closed: bool = True
    provider: str = "binance"

    @property
    def hl2(self) -> float:
        return (self.high + self.low) / 2.0

    @property
    def hlc3(self) -> float:
        return (self.high + self.low + self.close) / 3.0

    @property
    def ohlc4(self) -> float:
        return (self.open + self.high + self.low + self.close) / 4.0


class CandleSeries(BaseModel):
    symbol: str
    timeframe: str
    candles: List[Candle]
    provider: str
    is_demo: bool = False
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def to_dataframe(self):
        import pandas as pd
        if not self.candles:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume", "is_closed"])
        data = [
            {
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
                "is_closed": c.is_closed
            }
            for c in self.candles
        ]
        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)
        return df


class Ticker(BaseModel):
    symbol: str
    last_price: float
    high_24h: float
    low_24h: float
    volume_24h: float
    price_change_percent: float
    provider: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProviderStatus(BaseModel):
    name: str
    is_online: bool
    latency_ms: float
    last_checked: datetime
    error_message: Optional[str] = None
