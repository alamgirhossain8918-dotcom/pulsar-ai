import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.data.binance_client import BinanceFuturesClient
from backend.app.data.bybit_client import BybitFuturesClient
from backend.app.data.data_models import Candle, CandleSeries, ProviderStatus, Ticker


class MarketFeedManager:
    """
    Market Data Feed Manager
    - Primary: Binance USD-M Futures
    - Fallback: Bybit Linear Perpetuals
    - Strict isolation: NEVER mixes Binance and Bybit candles in a single analysis
    - Real-time provider health tracking and failover
    - Labeled DEMO MODE only when both providers fail or when requested
    """

    def __init__(self):
        self.binance = BinanceFuturesClient(timeout=settings.REQUEST_TIMEOUT_SECONDS)
        self.bybit = BybitFuturesClient(timeout=settings.REQUEST_TIMEOUT_SECONDS)
        self.active_provider_name: str = settings.PRIMARY_DATA_PROVIDER
        self.provider_statuses: Dict[str, ProviderStatus] = {
            "binance": ProviderStatus(
                name="binance",
                is_online=False,
                latency_ms=0.0,
                last_checked=datetime.now(timezone.utc)
            ),
            "bybit": ProviderStatus(
                name="bybit",
                is_online=False,
                latency_ms=0.0,
                last_checked=datetime.now(timezone.utc)
            )
        }
        self.is_demo_mode: bool = False

    async def check_health(self) -> Dict[str, ProviderStatus]:
        """Check latency and availability of both providers"""
        # Binance Check
        try:
            lat = await self.binance.ping()
            self.provider_statuses["binance"] = ProviderStatus(
                name="binance",
                is_online=True,
                latency_ms=lat,
                last_checked=datetime.now(timezone.utc)
            )
        except Exception as e:
            self.provider_statuses["binance"] = ProviderStatus(
                name="binance",
                is_online=False,
                latency_ms=0.0,
                last_checked=datetime.now(timezone.utc),
                error_message=str(e)
            )

        # Bybit Check
        try:
            lat = await self.bybit.ping()
            self.provider_statuses["bybit"] = ProviderStatus(
                name="bybit",
                is_online=True,
                latency_ms=lat,
                last_checked=datetime.now(timezone.utc)
            )
        except Exception as e:
            self.provider_statuses["bybit"] = ProviderStatus(
                name="bybit",
                is_online=False,
                latency_ms=0.0,
                last_checked=datetime.now(timezone.utc),
                error_message=str(e)
            )

        return self.provider_statuses

    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 250,
        force_demo: bool = False
    ) -> CandleSeries:
        """
        Fetch candles from primary provider.
        If primary fails, automatically fallback to secondary provider.
        If both fail, switch to labeled DEMO mode.
        NEVER combine data between providers.
        """
        if force_demo:
            return self._generate_labeled_demo_candles(symbol, timeframe, limit)

        # 1. Attempt Primary (Binance)
        try:
            candles = await self.binance.get_klines(symbol=symbol, timeframe=timeframe, limit=limit)
            if candles and len(candles) >= 10:
                self.active_provider_name = "binance"
                self.is_demo_mode = False
                return CandleSeries(
                    symbol=symbol,
                    timeframe=timeframe,
                    candles=candles,
                    provider="binance",
                    is_demo=False
                )
        except Exception as e:
            logger.warning(f"Primary provider Binance failed for {symbol} {timeframe}: {e}. Switching to Bybit fallback.")

        # 2. Attempt Fallback (Bybit)
        try:
            candles = await self.bybit.get_klines(symbol=symbol, timeframe=timeframe, limit=limit)
            if candles and len(candles) >= 10:
                self.active_provider_name = "bybit"
                self.is_demo_mode = False
                return CandleSeries(
                    symbol=symbol,
                    timeframe=timeframe,
                    candles=candles,
                    provider="bybit",
                    is_demo=False
                )
        except Exception as e:
            logger.error(f"Fallback provider Bybit also failed for {symbol} {timeframe}: {e}")

        # 3. Both Providers Failed: Switch to clearly labeled DEMO MODE
        logger.critical(f"Both market providers failed for {symbol}. Returning DATA UNAVAILABLE / LABELED DEMO MODE.")
        self.is_demo_mode = True
        return self._generate_labeled_demo_candles(symbol, timeframe, limit)

    async def get_ticker(self, symbol: str) -> Ticker:
        # Try primary
        try:
            ticker = await self.binance.get_ticker_24h(symbol)
            self.active_provider_name = "binance"
            return ticker
        except Exception:
            pass

        # Try fallback
        try:
            ticker = await self.bybit.get_ticker_24h(symbol)
            self.active_provider_name = "bybit"
            return ticker
        except Exception:
            pass

        # Demo fallback ticker
        return Ticker(
            symbol=symbol,
            last_price=65420.50 if "BTC" in symbol else (3450.25 if "ETH" in symbol else 145.75),
            high_24h=66500.0,
            low_24h=64200.0,
            volume_24h=15243.0,
            price_change_percent=1.85,
            provider="DEMO_DATA_UNAVAILABLE",
            timestamp=datetime.now(timezone.utc)
        )

    def _generate_labeled_demo_candles(self, symbol: str, timeframe: str, limit: int = 150) -> CandleSeries:
        """
        Creates synthetic realistic candles for demo/simulation when real exchanges are unreachable.
        Strictly tagged with provider='DEMO_MODE (DATA UNAVAILABLE)' and is_demo=True.
        """
        base_price = 68000.0 if "BTC" in symbol else (3500.0 if "ETH" in symbol else 160.0)
        candles: List[Candle] = []

        tf_mins = 15
        if timeframe == "5m": tf_mins = 5
        elif timeframe == "1h": tf_mins = 60
        elif timeframe == "4h": tf_mins = 240
        elif timeframe == "1d": tf_mins = 1440
        elif timeframe == "1w": tf_mins = 10080

        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=tf_mins * limit)

        current_price = base_price
        for i in range(limit):
            dt = start_time + timedelta(minutes=tf_mins * i)
            # deterministic wave + oscillation to simulate market structure
            cycle = math.sin(i * 0.15) * (base_price * 0.02)
            noise = (math.cos(i * 0.4) * 0.5) * (base_price * 0.005)
            open_p = current_price
            close_p = base_price + cycle + noise
            high_p = max(open_p, close_p) + (abs(cycle) * 0.15 + base_price * 0.003)
            low_p = min(open_p, close_p) - (abs(cycle) * 0.15 + base_price * 0.003)
            vol = 150.0 + abs(math.sin(i * 0.2)) * 300.0
            
            candles.append(Candle(
                timestamp=dt,
                open=round(open_p, 2),
                high=round(high_p, 2),
                low=round(low_p, 2),
                close=round(close_p, 2),
                volume=round(vol, 2),
                is_closed=True,
                provider="DEMO_MODE (DATA UNAVAILABLE)"
            ))
            current_price = close_p

        return CandleSeries(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
            provider="DEMO_MODE (DATA UNAVAILABLE)",
            is_demo=True
        )


feed_manager = MarketFeedManager()
