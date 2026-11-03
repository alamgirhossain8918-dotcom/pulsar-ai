import asyncio
from datetime import datetime, timezone
from typing import Optional
import httpx
from backend.app.core.config import settings
from backend.app.core.logger import logger


class TelegramNotifier:
    """Telegram Bot Alert Service for PULSAR AI V2.0"""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.is_enabled = settings.TELEGRAM_ALERTS_ENABLED

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.is_enabled or not self.bot_token or not self.chat_id:
            logger.debug(f"[Telegram Mock] Alerts disabled or token/chat_id unset. Message:\n{text}")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    async def notify_new_signal(self, signal: dict) -> bool:
        icon = "🟢 <b>BUY SIGNAL</b>" if signal.get("direction") == "BUY" else "🔴 <b>SELL SIGNAL</b>"
        demo_tag = "\n⚠️ <i>[DEMO MODE - NOT REAL TRADE]</i>\n" if signal.get("is_demo") else ""

        msg = (
            f"⚡ <b>PULSAR AI V2.0 ALERT</b> ⚡\n"
            f"{icon} {demo_tag}\n"
            f"<b>Symbol:</b> #{signal.get('symbol')}\n"
            f"<b>Strategy:</b> {signal.get('strategy_profile')}\n"
            f"<b>Confluence Score:</b> {signal.get('confluence_score')}/100\n"
            f"<b>Risk/Reward:</b> 1:{signal.get('rr_ratio')}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 <b>Entry:</b> {signal.get('entry_price')}\n"
            f"🛑 <b>Stop Loss:</b> {signal.get('stop_loss')}\n"
            f"🎯 <b>TP 1:</b> {signal.get('take_profit_1')}\n"
            f"🎯 <b>TP 2:</b> {signal.get('take_profit_2')}\n"
            f"🎯 <b>TP 3:</b> {signal.get('take_profit_3')}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 <b>HTF Bias:</b> {signal.get('htf_bias')}\n"
            f"💧 <b>Liquidity:</b> {signal.get('liquidity_event')}\n"
            f"💡 <b>Setup:</b> {signal.get('entry_explanation')}\n"
            f"🕒 <i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
        )
        return await self.send_message(msg)

    async def notify_signal_update(self, event) -> bool:
        icon_map = {
            "Triggered": "🚀 <b>ORDER TRIGGERED</b>",
            "TP1 Hit": "🎯 <b>TAKE PROFIT 1 HIT</b> (Scaled 50%, SL to BE)",
            "TP2 Hit": "🎯🎯 <b>TAKE PROFIT 2 HIT</b>",
            "TP3 Hit": "🏆 <b>FULL TAKE PROFIT HIT</b>",
            "SL Hit": "🛑 <b>STOP LOSS HIT</b>",
            "Expired": "⌛ <b>SIGNAL EXPIRED</b>"
        }
        status_header = icon_map.get(event.new_status, f"ℹ️ <b>STATUS UPDATE: {event.new_status}</b>")
        pnl_text = f"\n<b>Net PnL:</b> {event.realized_pnl}%" if event.realized_pnl != 0.0 else ""

        msg = (
            f"⚡ <b>PULSAR AI SIGNAL UPDATE</b> ⚡\n"
            f"{status_header}\n"
            f"<b>Symbol:</b> #{event.symbol}\n"
            f"<b>Current Price:</b> {event.price}\n"
            f"<b>Details:</b> {event.message}{pnl_text}\n"
            f"🕒 <i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
        )
        return await self.send_message(msg)

    async def notify_system_event(self, title: str, details: str, is_critical: bool = False) -> bool:
        icon = "🚨 <b>SYSTEM ALERT</b>" if is_critical else "ℹ️ <b>SYSTEM NOTIFICATION</b>"
        msg = (
            f"{icon}\n"
            f"<b>{title}</b>\n"
            f"{details}\n"
            f"🕒 <i>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
        )
        return await self.send_message(msg)


telegram_notifier = TelegramNotifier()
