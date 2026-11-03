"use client";

import { useEffect, useState, useTransition } from "react";
import { useSearchParams } from "next/navigation";
import { LineChart, Layers, Sliders, ChevronDown } from "lucide-react";
import { api } from "../../lib/api";
import { LightweightChart } from "../../components/LightweightChart";
import { Candle, ChartMarker } from "../../types";
import { formatCurrency } from "../../lib/utils";

const PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT"];
const TIMEFRAMES = ["5m", "15m", "1h", "4h", "1d"];

export default function AnalysisPage() {
  const searchParams = useSearchParams();
  const initialSymbol = searchParams.get("symbol") || "BTCUSDT";

  const [symbol, setSymbol] = useState(initialSymbol);
  const [timeframe, setTimeframe] = useState("15m");
  const [candles, setCandles] = useState<Candle[]>([]);
  const [markers, setMarkers] = useState<ChartMarker[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchChartData() {
      setLoading(true);
      try {
        const res = await api.getCandles(symbol, timeframe, 150);
        setCandles(res.candles || []);
        setMarkers(res.markers || []);
        setAnalysis(res.analysis || null);
      } finally {
        setLoading(false);
      }
    }
    fetchChartData();
  }, [symbol, timeframe]);

  return (
    <div className="space-y-6">
      {/* Top Controls: Symbol, Timeframe, Overlays */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
        {/* Symbol Selector */}
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
          {PAIRS.map((p) => (
            <button
              key={p}
              onClick={() => setSymbol(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                symbol === p ? "bg-accent text-white" : "bg-card text-neutral hover:text-white"
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Timeframe Selector */}
        <div className="flex bg-card border border-border rounded-lg p-0.5 text-xs">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1 rounded font-medium transition ${
                timeframe === tf ? "bg-accent text-white" : "text-neutral hover:text-white"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="p-4 rounded-xl bg-surface border border-border space-y-4">
        <div className="flex justify-between items-center text-xs">
          <div className="flex items-center gap-3">
            <span className="font-bold text-white text-base">{symbol}</span>
            <span className="text-neutral font-mono">{timeframe} Timeframe</span>
            <span className="px-2 py-0.5 rounded bg-card text-neutral border border-border">
              Closed Candles
            </span>
          </div>

          <div className="flex items-center gap-3 text-neutral">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-bullish" />
              <span>Bullish BOS/CHoCH</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-bearish" />
              <span>Bearish BOS/CHoCH</span>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="h-[450px] w-full rounded-lg bg-card border border-border animate-pulse flex items-center justify-center text-neutral text-xs">
            Loading TradingView Chart...
          </div>
        ) : (
          <LightweightChart candles={candles} markers={markers} height={450} />
        )}
      </div>

      {/* ICT / SMC Level Inspection Cards */}
      {analysis && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-card border border-border">
            <span className="text-[11px] text-neutral uppercase font-bold">Dealing Range</span>
            <div className="mt-2 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-neutral">High:</span>
                <span className="font-mono text-white">{formatCurrency(analysis.dealing_range?.range_high)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral">Equilibrium:</span>
                <span className="font-mono text-accent">{formatCurrency(analysis.dealing_range?.equilibrium)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral">Low:</span>
                <span className="font-mono text-white">{formatCurrency(analysis.dealing_range?.range_low)}</span>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-card border border-border">
            <span className="text-[11px] text-neutral uppercase font-bold">OTE Zone (0.62 - 0.79)</span>
            <div className="mt-2 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-neutral">OTE 62%:</span>
                <span className="font-mono text-white">{formatCurrency(analysis.dealing_range?.ote_62)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral">Sweet Spot (70.5%):</span>
                <span className="font-mono text-bullish">{formatCurrency(analysis.dealing_range?.ote_705)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral">OTE 79%:</span>
                <span className="font-mono text-white">{formatCurrency(analysis.dealing_range?.ote_79)}</span>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-card border border-border">
            <span className="text-[11px] text-neutral uppercase font-bold">FVG & Order Blocks</span>
            <div className="mt-2 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-neutral">Active FVGs:</span>
                <span className="font-mono text-white">{analysis.fvgs?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral">Order Blocks:</span>
                <span className="font-mono text-white">{analysis.order_blocks?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral">Current Zone:</span>
                <span className="font-bold text-accent">{analysis.dealing_range?.zone}</span>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-card border border-border">
            <span className="text-[11px] text-neutral uppercase font-bold">Macro Session Levels</span>
            <div className="mt-2 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-neutral">PDH / PDL:</span>
                <span className="font-mono text-white">
                  {formatCurrency(analysis.session_levels?.pdh || 0)} / {formatCurrency(analysis.session_levels?.pdl || 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral">Asia High/Low:</span>
                <span className="font-mono text-neutral">
                  {analysis.session_levels?.asia_high ? formatCurrency(analysis.session_levels?.asia_high) : "-"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
