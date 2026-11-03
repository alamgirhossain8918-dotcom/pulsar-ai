"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  ShieldCheck,
  Target,
  AlertTriangle,
  Zap,
  TrendingUp,
  TrendingDown,
  Layers
} from "lucide-react";
import { api } from "../../../lib/api";
import { Signal } from "../../../types";
import { formatCurrency, formatDate } from "../../../lib/utils";

export default function SignalDetailPage() {
  const params = useParams();
  const signalId = params.id as string;

  const [signal, setSignal] = useState<Signal | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (signalId) {
      api.getSignalById(signalId).then(setSignal).catch(() => null).finally(() => setLoading(false));
    }
  }, [signalId]);

  if (loading) {
    return <div className="p-8 text-center text-neutral text-xs">Loading signal details...</div>;
  }

  if (!signal) {
    return (
      <div className="p-8 text-center text-neutral text-xs space-y-3">
        <p>Signal not found or expired.</p>
        <Link href="/signals" className="text-accent underline">Return to Signals</Link>
      </div>
    );
  }

  const isBuy = signal.direction === "BUY";

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button & Header */}
      <div className="flex items-center gap-3">
        <Link
          href="/signals"
          className="p-2 rounded-lg bg-surface hover:bg-card border border-border text-neutral hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>#{signal.symbol}</span>
            <span
              className={`text-xs px-2.5 py-0.5 rounded font-bold ${
                isBuy ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"
              }`}
            >
              {signal.direction}
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-card text-neutral font-mono">
              {signal.strategy_profile}
            </span>
          </h2>
          <p className="text-xs text-neutral mt-0.5">
            Created at {formatDate(signal.created_at)} | Data Provider: {signal.data_provider}
          </p>
        </div>
      </div>

      {/* Main Grid: Parameters & Confluence Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Execution Levels */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Target className="w-4 h-4 text-accent" />
            <span>Execution Price Levels</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-lg bg-card border border-border flex justify-between items-center">
              <span className="text-neutral">Planned Entry</span>
              <span className="font-mono text-base font-bold text-white">{formatCurrency(signal.entry_price)}</span>
            </div>

            <div className="p-3 rounded-lg bg-bearish/10 border border-bearish/20 flex justify-between items-center">
              <span className="text-bearish font-medium">Stop Loss</span>
              <span className="font-mono text-base font-bold text-bearish">{formatCurrency(signal.stop_loss)}</span>
            </div>

            <div className="p-3 rounded-lg bg-bullish/10 border border-bullish/20 flex justify-between items-center">
              <span className="text-bullish font-medium">Take Profit 1 (50% Scale)</span>
              <span className="font-mono text-base font-bold text-bullish">{formatCurrency(signal.take_profit_1)}</span>
            </div>

            <div className="p-3 rounded-lg bg-bullish/10 border border-bullish/20 flex justify-between items-center">
              <span className="text-bullish font-medium">Take Profit 2 (30% Scale)</span>
              <span className="font-mono text-base font-bold text-bullish">{formatCurrency(signal.take_profit_2)}</span>
            </div>

            <div className="p-3 rounded-lg bg-bullish/10 border border-bullish/20 flex justify-between items-center">
              <span className="text-bullish font-medium">Take Profit 3 (Runner Target)</span>
              <span className="font-mono text-base font-bold text-bullish">{formatCurrency(signal.take_profit_3)}</span>
            </div>

            <div className="flex justify-between items-center text-xs pt-2">
              <span className="text-neutral">Confluence Quality:</span>
              <span className="font-bold text-accent font-mono text-sm">{signal.confluence_score} / 100</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-neutral">Minimum Risk/Reward:</span>
              <span className="font-bold text-white font-mono">1 : {signal.rr_ratio}</span>
            </div>
          </div>
        </div>

        {/* Right: ICT/SMC Institutional Confluences */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-bullish" />
            <span>ICT / SMC Confluence Audit</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-lg bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold block">Higher Timeframe Bias</span>
              <p className="text-white mt-1 font-semibold">{signal.htf_bias}</p>
            </div>

            <div className="p-3 rounded-lg bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold block">Liquidity Event</span>
              <p className="text-white mt-1">{signal.liquidity_event}</p>
            </div>

            <div className="p-3 rounded-lg bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold block">Market Structure Shift</span>
              <p className="text-white mt-1">{signal.bos_choch_confirmation}</p>
            </div>

            <div className="p-3 rounded-lg bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold block">FVG / Order Block Zone</span>
              <p className="text-white mt-1">{signal.fvg_ob_info}</p>
            </div>

            <div className="p-3 rounded-lg bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold block">Entry Explanation</span>
              <p className="text-white mt-1 leading-relaxed">{signal.entry_explanation}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Invalidation Rules */}
      {signal.invalidation_conditions && (
        <div className="p-4 rounded-xl bg-surface border border-border flex items-start gap-3 text-xs">
          <AlertTriangle className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-white uppercase text-[11px] block">Invalidation Condition:</span>
            <p className="text-neutral mt-0.5">{signal.invalidation_conditions}</p>
          </div>
        </div>
      )}
    </div>
  );
}
