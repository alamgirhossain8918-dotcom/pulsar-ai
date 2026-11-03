import asyncio
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from backend.app.core.logger import logger
from backend.app.data.data_models import Candle, Ticker

TF_MAP = {
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "1w": "1w"
}


class BinanceFuturesClient:
    """Binance USD-M Futures Public Market Data Client"""
    BASE_URL = "https://fapi.binance.com"

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.provider_name = "binance"
        self._rate_limit_backoff = 1.0

    async def ping(self) -> float:
        start = asyncio.get_event_loop().time()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.BASE_URL}/fapi/v1/ping")
            resp.raise_for_status()
        latency = (asyncio.get_event_loop().time() - start) * 1000.0
        return round(latency, 2)

    async def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 250,
        end_time: Optional[int] = None
    ) -> List[Candle]:
        interval = TF_MAP.get(timeframe, timeframe)
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        if end_time:
            params["endTime"] = end_time

        url = f"{self.BASE_URL}/fapi/v1/klines"
        candles: List[Candle] = []

        retries = 3
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 429:
                        wait = self._rate_limit_backoff * (2 ** attempt)
                        logger.warning(f"Binance rate limited (429). Backing off {wait}s...")
                        await asyncio.sleep(wait)
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                    break
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Binance klines failed for {symbol} {timeframe}: {e}")
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))
        else:
            return []

        # Format:
        # [0: open_time, 1: open, 2: high, 3: low, 4: close, 5: volume, 6: close_time, ...]
        now_ms = datetime.now(timezone.utc).timestamp() * 1000.0

        for row in data:
            open_ms = row[0]
            close_ms = row[6]
            is_closed = now_ms >= close_ms

            candle = Candle(
                timestamp=datetime.fromtimestamp(open_ms / 1000.0, tz=timezone.utc),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                is_closed=is_closed,
                provider=self.provider_name
            )
            candles.append(candle)

        return candles

    async def get_ticker_24h(self, symbol: str) -> Ticker:
        url = f"{self.BASE_URL}/fapi/v1/ticker/24hr"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params={"symbol": symbol.upper()})
            resp.raise_for_status()
            data = resp.json()

        return Ticker(
            symbol=symbol.upper(),
            last_price=float(data.get("lastPrice", 0.0)),
            high_24h=float(data.get("highPrice", 0.0)),
            low_24h=float(data.get("lowPrice", 0.0)),
            volume_24h=float(data.get("volume", 0.0)),
            price_change_percent=float(data.get("priceChangePercent", 0.0)),
            provider=self.provider_name,
            timestamp=datetime.now(timezone.utc)
        )
