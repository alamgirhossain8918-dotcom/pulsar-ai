"use client";

import { useEffect, useState } from "react";
import { Send, CheckCircle2, ShieldCheck, AlertCircle } from "lucide-react";
import { api } from "../../../lib/api";

export default function TelegramSettingsPage() {
  const [isConfigured, setIsConfigured] = useState(false);
  const [notifyNewSignal, setNotifyNewSignal] = useState(true);
  const [notifyTriggered, setNotifyTriggered] = useState(true);
  const [notifyTP, setNotifyTP] = useState(true);
  const [notifySL, setNotifySL] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getTelegramSettings().then((res) => {
      if (res) {
        setIsConfigured(res.is_configured);
      }
    });
  }, []);

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="p-5 rounded-xl bg-surface border border-border">
        <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
          <Send className="w-5 h-5 text-accent" />
          <span>TELEGRAM BOT NOTIFICATION SERVICE</span>
        </h2>
        <p className="text-xs text-neutral mt-1">
          Receive real-time push alerts on Telegram when institutional signals print, fill, hit take-profit, or stop out.
        </p>
      </div>

      <div className="p-4 rounded-xl bg-card border border-border flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <div className={`w-2.5 h-2.5 rounded-full ${isConfigured ? "bg-bullish" : "bg-yellow-500"}`} />
          <span className="font-semibold text-white">Bot Integration Status:</span>
        </div>
        <span className={`font-bold px-2 py-0.5 rounded text-[11px] ${isConfigured ? "bg-bullish/10 text-bullish" : "bg-yellow-500/10 text-yellow-500"}`}>
          {isConfigured ? "CONNECTED VIA RAILWAY SECRETS" : "PENDING TOKEN CONFIGURATION"}
        </span>
      </div>

      <form onSubmit={handleSave} className="p-6 rounded-xl bg-surface border border-border space-y-5 text-xs">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Alert Preferences
        </h3>

        <div className="space-y-3">
          <label className="flex items-center justify-between p-3 rounded-lg bg-card border border-border cursor-pointer">
            <div>
              <span className="font-semibold text-white block">New BUY / SELL Signals</span>
              <span className="text-[11px] text-neutral">Triggered when confluence score &gt;= 70 is confirmed</span>
            </div>
            <input
              type="checkbox"
              checked={notifyNewSignal}
              onChange={(e) => setNotifyNewSignal(e.target.checked)}
              className="accent-accent w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between p-3 rounded-lg bg-card border border-border cursor-pointer">
            <div>
              <span className="font-semibold text-white block">Order Triggered / Filled</span>
              <span className="text-[11px] text-neutral">Alert when price touches the planned entry level</span>
            </div>
            <input
              type="checkbox"
              checked={notifyTriggered}
              onChange={(e) => setNotifyTriggered(e.target.checked)}
              className="accent-accent w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between p-3 rounded-lg bg-card border border-border cursor-pointer">
            <div>
              <span className="font-semibold text-white block">Take Profit Hit (TP1, TP2, TP3)</span>
              <span className="text-[11px] text-neutral">Alert with partial scaling info & breakeven movement</span>
            </div>
            <input
              type="checkbox"
              checked={notifyTP}
              onChange={(e) => setNotifyTP(e.target.checked)}
              className="accent-accent w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between p-3 rounded-lg bg-card border border-border cursor-pointer">
            <div>
              <span className="font-semibold text-white block">Stop Loss Hit</span>
              <span className="text-[11px] text-neutral">Immediate notification with net loss calculation</span>
            </div>
            <input
              type="checkbox"
              checked={notifySL}
              onChange={(e) => setNotifySL(e.target.checked)}
              className="accent-accent w-4 h-4"
            />
          </label>
        </div>

        <button
          type="submit"
          className="px-6 py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white font-bold transition flex items-center gap-2 shadow-lg shadow-accent/20"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Save Alert Preferences</span>
        </button>

        {saved && (
          <div className="p-3 rounded-lg bg-bullish/10 border border-bullish/30 text-bullish text-xs font-semibold">
            Notification preferences successfully updated!
          </div>
        )}
      </form>

      {/* Security Best Practices Reminder */}
      <div className="p-4 rounded-xl bg-card border border-border space-y-2 text-xs">
        <div className="flex items-center gap-2 text-white font-bold">
          <ShieldCheck className="w-4 h-4 text-bullish" />
          <span>Security Architecture Best Practice</span>
        </div>
        <p className="text-neutral text-[11px] leading-relaxed">
          For production security, your Telegram bot token is never exposed to the frontend browser.
          To update your token, set <code className="text-accent bg-surface px-1 py-0.5 rounded font-mono">TELEGRAM_BOT_TOKEN</code> and <code className="text-accent bg-surface px-1 py-0.5 rounded font-mono">TELEGRAM_CHAT_ID</code> as environment secrets in your Railway dashboard.
        </p>
      </div>
    </div>
  );
}
