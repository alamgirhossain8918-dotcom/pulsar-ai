import asyncio
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from backend.app.core.logger import logger
from backend.app.data.data_models import Candle, Ticker

BYBIT_TF_MAP = {
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D",
    "1w": "W"
}


class BybitFuturesClient:
    """Bybit Linear Perpetuals Public Market Data Client (Fallback Provider)"""
    BASE_URL = "https://api.bybit.com"

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.provider_name = "bybit"
        self._rate_limit_backoff = 1.0

    async def ping(self) -> float:
        start = asyncio.get_event_loop().time()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.BASE_URL}/v5/market/time")
            resp.raise_for_status()
        latency = (asyncio.get_event_loop().time() - start) * 1000.0
        return round(latency, 2)

    async def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
        end_time: Optional[int] = None
    ) -> List[Candle]:
        interval = BYBIT_TF_MAP.get(timeframe, "15")
        params = {
            "category": "linear",
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        if end_time:
            params["end"] = end_time

        url = f"{self.BASE_URL}/v5/market/kline"
        retries = 3
        data = None

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 429:
                        wait = self._rate_limit_backoff * (2 ** attempt)
                        logger.warning(f"Bybit rate limited (429). Backing off {wait}s...")
                        await asyncio.sleep(wait)
                        continue
                    resp.raise_for_status()
                    payload = resp.json()
                    if payload.get("retCode") == 0:
                        data = payload.get("result", {}).get("list", [])
                        break
                    else:
                        raise ValueError(f"Bybit API error: {payload.get('retMsg')}")
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"Bybit klines failed for {symbol} {timeframe}: {e}")
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))
        
        if not data:
            return []

        candles: List[Candle] = []
        now_ms = datetime.now(timezone.utc).timestamp() * 1000.0

        # Bybit returns reverse chronological order: [0: startTime, 1: openPrice, 2: highPrice, 3: lowPrice, 4: closePrice, 5: volume, 6: turnover]
        for row in reversed(data):
            open_ms = int(row[0])
            open_dt = datetime.fromtimestamp(open_ms / 1000.0, tz=timezone.utc)
            
            # Estimate close time based on timeframe
            tf_delta_seconds = 60 * 15
            if timeframe == "5m": tf_delta_seconds = 300
            elif timeframe == "15m": tf_delta_seconds = 900
            elif timeframe == "1h": tf_delta_seconds = 3600
            elif timeframe == "4h": tf_delta_seconds = 14400
            elif timeframe == "1d": tf_delta_seconds = 86400
            elif timeframe == "1w": tf_delta_seconds = 604800

            close_ms = open_ms + (tf_delta_seconds * 1000)
            is_closed = now_ms >= close_ms

            candles.append(Candle(
                timestamp=open_dt,
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                is_closed=is_closed,
                provider=self.provider_name
            ))

        return candles

    async def get_ticker_24h(self, symbol: str) -> Ticker:
        url = f"{self.BASE_URL}/v5/market/tickers"
        params = {"category": "linear", "symbol": symbol.upper()}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            list_res = payload.get("result", {}).get("list", [])
            if not list_res:
                raise ValueError(f"No ticker found on Bybit for {symbol}")
            t = list_res[0]

        last_p = float(t.get("lastPrice", 0.0))
        high_24h = float(t.get("highPrice24h", last_p))
        low_24h = float(t.get("lowPrice24h", last_p))
        vol_24h = float(t.get("volume24h", 0.0))
        pct_change = float(t.get("price24hPcnt", 0.0)) * 100.0

        return Ticker(
            symbol=symbol.upper(),
            last_price=last_p,
            high_24h=high_24h,
            low_24h=low_24h,
            volume_24h=vol_24h,
            price_change_percent=pct_change,
            provider=self.provider_name,
            timestamp=datetime.now(timezone.utc)
        )
