"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Clock,
  ChevronRight
} from "lucide-react";
import { api } from "../lib/api";
import { MarketOverview, Signal, ScannerItem } from "../types";
import { formatCurrency, formatPercent } from "../lib/utils";
import { RegimeBadge } from "../components/RegimeBadge";

export default function DashboardPage() {
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [scannerItems, setScannerItems] = useState<ScannerItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [ov, sigs, sc] = await Promise.all([
          api.getOverview().catch(() => null),
          api.getSignals().catch(() => []),
          api.getScannerResults().catch(() => ({ results: [] })),
        ]);
        if (ov) setOverview(ov);
        setSignals(sigs);
        setScannerItems(sc.results || []);
      } finally {
        setLoading(false);
      }
    }
    loadData();
    const interval = setInterval(loadData, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner: Market Status */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-surface border border-border">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <span>PULSAR AI QUANTITATIVE DESK</span>
            <span className="text-xs px-2 py-0.5 rounded bg-accent/20 text-accent font-mono font-semibold border border-accent/40">
              V2.0 PRO
            </span>
          </h2>
          <p className="text-xs text-neutral mt-1">
            Real-time ICT/SMC Institutional Market Structure, Liquidity Sweeps, and Automated Confluence Gates.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/scanner"
            className="px-4 py-2 rounded-lg bg-card hover:bg-card/80 border border-border text-xs font-semibold text-white transition flex items-center gap-1.5"
          >
            <Activity className="w-3.5 h-3.5 text-accent" />
            <span>Open Scanner</span>
          </Link>
          <Link
            href="/paper-trading"
            className="px-4 py-2 rounded-lg bg-accent hover:bg-accent/90 text-xs font-semibold text-white transition flex items-center gap-1.5 shadow-lg shadow-accent/20"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Virtual Paper Desk</span>
          </Link>
        </div>
      </div>

      {/* Priority Assets Overview (BTC, ETH, SOL) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {overview?.priority_assets && overview.priority_assets.length > 0 ? (
          overview.priority_assets.map((asset) => {
            const isPos = asset.price_change_percent >= 0;
            return (
              <div key={asset.symbol} className="p-4 rounded-xl bg-card border border-border relative overflow-hidden">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-bold text-neutral tracking-wider">{asset.symbol}</span>
                    <h3 className="text-xl font-bold font-mono text-white mt-1">
                      {formatCurrency(asset.last_price)}
                    </h3>
                  </div>
                  <div className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded ${isPos ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"}`}>
                    {isPos ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                    <span>{formatPercent(asset.price_change_percent)}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-border/50 text-[11px] text-neutral">
                  <div>
                    24h High: <span className="text-white font-mono">{formatCurrency(asset.high_24h)}</span>
                  </div>
                  <div className="text-right">
                    24h Low: <span className="text-white font-mono">{formatCurrency(asset.low_24h)}</span>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          [1, 2, 3].map((i) => (
            <div key={i} className="p-4 rounded-xl bg-card border border-border animate-pulse h-28" />
          ))
        )}
      </div>

      {/* Dual Section: Best Signal Opportunities & Live Market Scanner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Signals Column (1 Col) */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-accent" />
              <span>Active Signals ({signals.length})</span>
            </h3>
            <Link href="/signals" className="text-xs text-accent hover:underline flex items-center gap-1">
              <span>View All</span>
              <ChevronRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-3">
            {signals.slice(0, 3).map((sig) => {
              const isBuy = sig.direction === "BUY";
              return (
                <Link
                  key={sig.id}
                  href={`/signals/${sig.id}`}
                  className="block p-3.5 rounded-lg bg-card hover:bg-card/80 border border-border transition group"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${isBuy ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"}`}>
                        {sig.direction}
                      </span>
                      <span className="font-bold text-sm text-white">{sig.symbol}</span>
                      <span className="text-[11px] text-neutral font-mono">{sig.timeframe}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-mono font-bold text-accent">
                        Score: {sig.confluence_score}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-1 mt-3 pt-2 border-t border-border/50 text-[11px]">
                    <div>
                      <span className="text-neutral block">Entry</span>
                      <span className="font-mono text-white">{formatCurrency(sig.entry_price)}</span>
                    </div>
                    <div>
                      <span className="text-neutral block">Stop Loss</span>
                      <span className="font-mono text-bearish">{formatCurrency(sig.stop_loss)}</span>
                    </div>
                    <div>
                      <span className="text-neutral block">TP 1</span>
                      <span className="font-mono text-bullish">{formatCurrency(sig.take_profit_1)}</span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Live Scanner Mini-Table (2 Cols) */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-bullish" />
              <span>Multi-Timeframe Market Scanner</span>
            </h3>
            <Link href="/scanner" className="text-xs text-accent hover:underline flex items-center gap-1">
              <span>Full Scanner</span>
              <ChevronRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-card text-neutral uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l">Pair</th>
                  <th className="p-2.5">Price</th>
                  <th className="p-2.5">HTF Bias</th>
                  <th className="p-2.5">Regime</th>
                  <th className="p-2.5">Zone</th>
                  <th className="p-2.5 rounded-r text-right">Signal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {scannerItems.slice(0, 6).map((item) => (
                  <tr key={item.symbol} className="hover:bg-card/50 transition">
                    <td className="p-2.5 font-bold text-white">{item.symbol}</td>
                    <td className="p-2.5 font-mono text-neutral">{formatCurrency(item.price)}</td>
                    <td className="p-2.5 text-neutral">{item.htf_bias}</td>
                    <td className="p-2.5">
                      <RegimeBadge regime={item.regime} />
                    </td>
                    <td className="p-2.5 font-mono text-neutral">{item.dealing_zone}</td>
                    <td className="p-2.5 text-right font-bold">
                      <span
                        className={
                          item.signal === "BUY"
                            ? "text-bullish"
                            : item.signal === "SELL"
                            ? "text-bearish"
                            : "text-neutral"
                        }
                      >
                        {item.signal}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
