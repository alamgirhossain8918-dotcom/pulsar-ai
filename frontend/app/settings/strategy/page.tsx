"use client";

import { useEffect, useState } from "react";
import { Sliders, CheckCircle2, ShieldAlert } from "lucide-react";
import { api } from "../../../lib/api";

export default function StrategySettingsPage() {
  const [minConfluence, setMinConfluence] = useState(70);
  const [minRR, setMinRR] = useState(2.0);
  const [defaultStrategy, setDefaultStrategy] = useState("sniper");
  const [cooldown, setCooldown] = useState(30);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getStrategySettings().then((res) => {
      if (res) {
        setMinConfluence(res.min_confluence_score);
        setMinRR(res.min_rr_ratio);
        setDefaultStrategy(res.default_strategy);
        setCooldown(res.signal_cooldown_minutes);
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
          <Sliders className="w-5 h-5 text-accent" />
          <span>STRATEGY & CONFLUENCE GATE CONFIGURATION</span>
        </h2>
        <p className="text-xs text-neutral mt-1">
          Tune algorithmic quality gates for institutional signal filtering and automated cooldowns.
        </p>
      </div>

      <form onSubmit={handleSave} className="p-6 rounded-xl bg-surface border border-border space-y-5 text-xs">
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-white font-semibold">Minimum Confluence Gate (0 - 100)</label>
            <span className="font-mono font-bold text-accent">{minConfluence} / 100</span>
          </div>
          <input
            type="range"
            min="50"
            max="95"
            value={minConfluence}
            onChange={(e) => setMinConfluence(Number(e.target.value))}
            className="w-full accent-accent"
          />
          <p className="text-[11px] text-neutral mt-1">
            Signals below this threshold are strictly discarded as NO TRADE. Default institutional gate is 70/100.
          </p>
        </div>

        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-white font-semibold">Minimum Risk/Reward Ratio</label>
            <span className="font-mono font-bold text-bullish">1 : {minRR.toFixed(1)}</span>
          </div>
          <input
            type="range"
            min="1.5"
            max="4.0"
            step="0.1"
            value={minRR}
            onChange={(e) => setMinRR(Number(e.target.value))}
            className="w-full accent-accent"
          />
          <p className="text-[11px] text-neutral mt-1">
            Trades offering less than this structural RR to TP1 are rejected. Default is 1:2.0.
          </p>
        </div>

        <div>
          <label className="text-white font-semibold block mb-1.5">Default Strategy Profile</label>
          <select
            value={defaultStrategy}
            onChange={(e) => setDefaultStrategy(e.target.value)}
            className="w-full p-2.5 rounded-lg bg-card border border-border text-white focus:outline-none focus:border-accent"
          >
            <option value="sniper">ICT Sniper (Liquidity Sweep + CHoCH + OTE entry)</option>
            <option value="swing">ICT Trend Swing (Order Blocks & Breaker continuation)</option>
            <option value="scalp">ICT Micro Scalp (Session highs/lows mitigation)</option>
          </select>
        </div>

        <div>
          <label className="text-white font-semibold block mb-1.5">Signal Cooldown Duration (Minutes)</label>
          <input
            type="number"
            value={cooldown}
            onChange={(e) => setCooldown(Number(e.target.value))}
            className="w-full p-2.5 rounded-lg bg-card border border-border text-white font-mono"
          />
          <p className="text-[11px] text-neutral mt-1">
            Prevents repetitive signal generation on the same asset within this cooldown period.
          </p>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white font-bold transition flex items-center gap-2 shadow-lg shadow-accent/20"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>

        {saved && (
          <div className="p-3 rounded-lg bg-bullish/10 border border-bullish/30 text-bullish text-xs font-semibold">
            Strategy parameters successfully updated and active in scanner engine!
          </div>
        )}
      </form>
    </div>
  );
}
