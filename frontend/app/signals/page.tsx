"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BellRing, Filter, ArrowUpRight, ArrowDownRight, ChevronRight } from "lucide-react";
import { api } from "../../lib/api";
import { Signal } from "../../types";
import { formatCurrency, formatDate } from "../../lib/utils";

export default function SignalsPage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await api.getSignals(
          statusFilter !== "ALL" ? { status: statusFilter } : undefined
        );
        setSignals(data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [statusFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-surface border border-border">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <BellRing className="w-5 h-5 text-accent" />
            <span>ALGORITHMIC SIGNALS REPOSITORY</span>
          </h2>
          <p className="text-xs text-neutral mt-1">
            Institutional signals generated strictly on closed candles with multi-confluence gates (min score 70/100, min RR 1:2).
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex bg-card border border-border rounded-lg p-0.5 text-xs">
          {["ALL", "Pending", "Triggered", "TP1 Hit", "SL Hit", "Expired"].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1 rounded font-medium transition ${
                statusFilter === s ? "bg-accent text-white" : "text-neutral hover:text-white"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Signals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {signals.map((sig) => {
          const isBuy = sig.direction === "BUY";
          return (
            <div
              key={sig.id}
              className="p-5 rounded-xl bg-surface border border-border flex flex-col justify-between hover:border-accent/50 transition relative overflow-hidden"
            >
              {sig.is_demo && (
                <div className="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] bg-bearish/20 text-bearish border border-bearish/30 font-bold">
                  DEMO MODE
                </div>
              )}

              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded flex items-center gap-1 ${
                        isBuy ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"
                      }`}
                    >
                      {isBuy ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                      <span>{sig.direction}</span>
                    </span>
                    <span className="font-bold text-white text-base">{sig.symbol}</span>
                  </div>

                  <span className="text-xs font-mono font-bold text-accent">
                    {sig.confluence_score}/100
                  </span>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-neutral text-[11px] block">Entry Price</span>
                    <span className="font-mono text-white font-bold">{formatCurrency(sig.entry_price)}</span>
                  </div>
                  <div>
                    <span className="text-neutral text-[11px] block">Stop Loss</span>
                    <span className="font-mono text-bearish font-bold">{formatCurrency(sig.stop_loss)}</span>
                  </div>
                  <div>
                    <span className="text-neutral text-[11px] block">Take Profit 1</span>
                    <span className="font-mono text-bullish font-bold">{formatCurrency(sig.take_profit_1)}</span>
                  </div>
                  <div>
                    <span className="text-neutral text-[11px] block">Risk / Reward</span>
                    <span className="font-mono text-accent font-bold">1:{sig.rr_ratio}</span>
                  </div>
                </div>

                <div className="mt-3 p-2.5 rounded bg-card border border-border text-[11px] text-neutral line-clamp-2">
                  {sig.entry_explanation}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs">
                <span className="text-neutral font-mono text-[11px]">{formatDate(sig.created_at)}</span>
                <Link
                  href={`/signals/${sig.id}`}
                  className="text-accent hover:underline flex items-center gap-1 font-semibold"
                >
                  <span>Details</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
