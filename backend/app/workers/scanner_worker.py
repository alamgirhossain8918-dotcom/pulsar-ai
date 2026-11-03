import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.data.feed_manager import feed_manager
from backend.app.engine.mtf_analyzer import MultiTimeframeAnalyzer, MTFAnalysisResult
from backend.app.signals.generator import signal_generator
from backend.app.signals.tracker import signal_tracker
from backend.app.notifications.telegram_bot import telegram_notifier
from backend.app.api.websocket import ws_manager


class MarketScannerWorker:
    """
    Continuous Cloud Market Scanner
    - Runs every minute
    - Distributed locking / in-memory lease to prevent concurrent replica conflicts
    - Prioritizes BTCUSDT, ETHUSDT, SOLUSDT
    - Evaluates multi-timeframe ICT/SMC structure
    - Generates signals and broadcasts live updates
    """

    def __init__(self):
        self._is_running: bool = False
        self._last_lock_time: float = 0.0
        self._lock_holder_id: str = str(uuid.uuid4())
        self.latest_scan_results: List[Dict] = []
        self.last_scan_timestamp: Optional[datetime] = None

    def acquire_lock(self) -> bool:
        """Simple lease-based lock for cloud worker replicas"""
        now = time.time()
        if now - self._last_lock_time > settings.WORKER_LOCK_TIMEOUT_SECONDS:
            self._last_lock_time = now
            return True
        return False

    def release_lock(self):
        self._last_lock_time = 0.0

    async def scan_symbol(self, symbol: str) -> Optional[Dict]:
        """Scans a single symbol across multiple timeframes"""
        try:
            # 1. Fetch candles for required timeframes
            tf_dfs = {}
            for tf in ["15m", "1h", "4h"]:
                series = await feed_manager.get_candles(symbol=symbol, timeframe=tf, limit=100)
                tf_dfs[tf] = series.to_dataframe()

            if not tf_dfs.get("15m") is not None or len(tf_dfs["15m"]) < 15:
                return None

            # 2. Perform Multi-Timeframe Analysis
            mtf: MTFAnalysisResult = MultiTimeframeAnalyzer.analyze_symbol(
                symbol=symbol,
                timeframe_dfs=tf_dfs,
                provider=feed_manager.active_provider_name,
                is_demo=feed_manager.is_demo_mode
            )

            # 3. Check for New Trading Signal if not in cooldown
            active_signal = None
            if not signal_tracker.is_in_cooldown(symbol):
                sig_payload = signal_generator.generate_signal(mtf)
                if sig_payload:
                    sig_dict = sig_payload.model_dump()
                    sig_dict["id"] = str(uuid.uuid4())
                    signal_tracker.record_new_signal(sig_dict)
                    active_signal = sig_dict
                    # Broadcast signal via Telegram and WebSocket
                    asyncio.create_task(telegram_notifier.notify_new_signal(sig_dict))
                    asyncio.create_task(ws_manager.broadcast("NEW_SIGNAL", sig_dict))

            # 4. Check active signals lifecycle with latest 15m candle
            latest_15m_candle = series.candles[-1]
            events = signal_tracker.update_with_candle(symbol, latest_15m_candle)
            for ev in events:
                asyncio.create_task(telegram_notifier.notify_signal_update(ev))
                asyncio.create_task(ws_manager.broadcast("SIGNAL_UPDATE", ev.model_dump()))

            # 5. Build summary snapshot for Scanner dashboard
            ltf_analysis = mtf.tf_analyses.get("15m")
            return {
                "symbol": symbol,
                "price": round(mtf.active_dealing_range.current_price, 2),
                "trend": ltf_analysis.trend.value if ltf_analysis else "Neutral",
                "regime": mtf.macro_regime.regime.value,
                "htf_bias": mtf.htf_bias.value,
                "dealing_zone": mtf.active_dealing_range.zone,
                "liquidity_sweeps_count": len(ltf_analysis.sweeps) if ltf_analysis else 0,
                "unmitigated_fvgs_count": len(ltf_analysis.fvgs) if ltf_analysis else 0,
                "active_obs_count": len(ltf_analysis.order_blocks) if ltf_analysis else 0,
                "provider": mtf.provider,
                "is_demo": mtf.is_demo,
                "signal": active_signal.get("direction") if active_signal else "NO TRADE",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
            return None

    async def run_scan_cycle(self):
        """Executes a full scanning pass across all symbols"""
        if not self.acquire_lock():
            logger.debug("Worker scan skipped: Another instance holds lease or cooldown active.")
            return

        try:
            logger.info("Starting market scan cycle...")
            # Prioritized order: BTC, ETH, SOL first
            pairs_to_scan = list(dict.fromkeys(settings.PRIORITY_PAIRS + settings.ACTIVE_PAIRS))
            snapshots = []

            for sym in pairs_to_scan:
                res = await self.scan_symbol(sym)
                if res:
                    snapshots.append(res)
                # Small yield to prevent event loop choking
                await asyncio.sleep(0.05)

            self.latest_scan_results = snapshots
            self.last_scan_timestamp = datetime.now(timezone.utc)
            logger.info(f"Scan cycle complete. Analyzed {len(snapshots)} pairs.")

            # Broadcast scanner results to connected clients
            await ws_manager.broadcast("SCANNER_UPDATE", {
                "timestamp": self.last_scan_timestamp.isoformat(),
                "provider": feed_manager.active_provider_name,
                "is_demo": feed_manager.is_demo_mode,
                "items": snapshots
            })

        except Exception as e:
            logger.error(f"Unexpected error in run_scan_cycle: {e}")
        finally:
            self.release_lock()

    async def start(self):
        """Main loop for the background worker"""
        self._is_running = True
        logger.info(f"Scanner worker loop started (Interval: {settings.SCAN_INTERVAL_SECONDS}s).")
        while self._is_running:
            start_t = time.time()
            try:
                await self.run_scan_cycle()
            except Exception as e:
                logger.error(f"Error in scanner loop iteration: {e}")

            elapsed = time.time() - start_t
            sleep_time = max(1.0, settings.SCAN_INTERVAL_SECONDS - elapsed)
            await asyncio.sleep(sleep_time)

    def stop(self):
        self._is_running = False
        logger.info("Scanner worker stopped.")


scanner_worker = MarketScannerWorker()
