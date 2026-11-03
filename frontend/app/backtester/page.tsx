"use client";

import { useState } from "react";
import { History, Play, CheckCircle2, TrendingUp, TrendingDown, AlertCircle } from "lucide-react";
import { api } from "../../lib/api";
import { BacktestResult } from "../../types";
import { formatCurrency, formatPercent } from "../../lib/utils";

export default function BacktesterPage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [timeframe, setTimeframe] = useState("15m");
  const [strategy, setStrategy] = useState("sniper");
  const [initialBalance, setInitialBalance] = useState(10000);
  const [riskPercent, setRiskPercent] = useState(1.0);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  async function handleRunBacktest(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.runBacktest({
        symbol,
        timeframe,
        strategy_profile: strategy,
        initial_balance: initialBalance,
        risk_percentage: riskPercent,
      });
      setResult(res);
    } catch (err: any) {
      alert("Backtest error: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-surface border border-border">
        <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
          <History className="w-5 h-5 text-accent" />
          <span>EVENT-DRIVEN QUANTITATIVE BACKTESTER</span>
        </h2>
        <p className="text-xs text-neutral mt-1">
          Simulate institutional ICT/SMC strategies across historical closed candles. Zero look-ahead bias, 0.05% fee modeling, 0.02% slippage, and conservative same-candle tie-break assumption.
        </p>
      </div>

      {/* Control Panel Form */}
      <form onSubmit={handleRunBacktest} className="p-5 rounded-xl bg-surface border border-border grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-4 text-xs">
        <div>
          <label className="text-neutral font-semibold block mb-1.5">Asset Pair</label>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="w-full p-2 rounded-lg bg-card border border-border text-white focus:outline-none focus:border-accent"
          >
            {["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"].map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-neutral font-semibold block mb-1.5">Timeframe</label>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="w-full p-2 rounded-lg bg-card border border-border text-white focus:outline-none focus:border-accent"
          >
            {["5m", "15m", "1h", "4h"].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-neutral font-semibold block mb-1.5">Strategy Profile</label>
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            className="w-full p-2 rounded-lg bg-card border border-border text-white focus:outline-none focus:border-accent"
          >
            <option value="sniper">ICT Sniper (Sweep + CHoCH + OTE)</option>
            <option value="swing">ICT Trend Swing (Order Blocks)</option>
            <option value="scalp">ICT Scalp (Session Extremes)</option>
          </select>
        </div>

        <div>
          <label className="text-neutral font-semibold block mb-1.5">Initial Capital ($)</label>
          <input
            type="number"
            value={initialBalance}
            onChange={(e) => setInitialBalance(Number(e.target.value))}
            className="w-full p-2 rounded-lg bg-card border border-border text-white font-mono focus:outline-none focus:border-accent"
          />
        </div>

        <div>
          <label className="text-neutral font-semibold block mb-1.5">Risk per Trade (%)</label>
          <input
            type="number"
            step="0.1"
            value={riskPercent}
            onChange={(e) => setRiskPercent(Number(e.target.value))}
            className="w-full p-2 rounded-lg bg-card border border-border text-white font-mono focus:outline-none focus:border-accent"
          />
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white font-bold transition flex items-center justify-center gap-1.5 shadow-lg shadow-accent/20"
          >
            <Play className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>{loading ? "Running..." : "Run Backtest"}</span>
          </button>
        </div>
      </form>

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          {/* Key Metrics Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold">Net Realized PnL</span>
              <h3 className={`text-xl font-mono font-bold mt-1 ${result.net_pnl >= 0 ? "text-bullish" : "text-bearish"}`}>
                {formatCurrency(result.net_pnl)}
              </h3>
              <span className="text-[11px] text-neutral">
                ROI: {formatPercent((result.net_pnl / result.initial_balance) * 100)}
              </span>
            </div>

            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold">Win Rate</span>
              <h3 className="text-xl font-mono font-bold mt-1 text-white">
                {result.win_rate}%
              </h3>
              <span className="text-[11px] text-neutral">
                {result.wins} Wins / {result.losses} Losses ({result.total_trades} Total)
              </span>
            </div>

            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold">Profit Factor</span>
              <h3 className="text-xl font-mono font-bold mt-1 text-accent">
                {result.profit_factor}
              </h3>
              <span className="text-[11px] text-neutral">Gross Profit / Gross Loss</span>
            </div>

            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="text-[11px] text-neutral uppercase font-bold">Max Drawdown</span>
              <h3 className="text-xl font-mono font-bold mt-1 text-bearish">
                -{result.max_drawdown_percent}%
              </h3>
              <span className="text-[11px] text-neutral">Peak-to-valley loss: {formatCurrency(result.max_drawdown)}</span>
            </div>
          </div>

          {/* Trade History Table */}
          <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Simulated Trade Execution Log ({result.trades.length} Trades)
            </h3>

            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-left text-xs">
                <thead className="bg-card text-neutral uppercase text-[10px] tracking-wider sticky top-0">
                  <tr>
                    <th className="p-2.5 rounded-l">#</th>
                    <th className="p-2.5">Type</th>
                    <th className="p-2.5">Entry Price</th>
                    <th className="p-2.5">Exit Price</th>
                    <th className="p-2.5">Net PnL</th>
                    <th className="p-2.5">Exit Reason</th>
                    <th className="p-2.5 rounded-r">Exit Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50 font-mono">
                  {result.trades.map((t) => {
                    const isWin = t.pnl > 0;
                    return (
                      <tr key={t.trade_id} className="hover:bg-card/50 transition">
                        <td className="p-2.5 text-neutral">{t.trade_id}</td>
                        <td className={`p-2.5 font-bold ${t.direction === "BUY" ? "text-bullish" : "text-bearish"}`}>
                          {t.direction}
                        </td>
                        <td className="p-2.5 text-white">{formatCurrency(t.entry_price)}</td>
                        <td className="p-2.5 text-white">{formatCurrency(t.exit_price)}</td>
                        <td className={`p-2.5 font-bold ${isWin ? "text-bullish" : "text-bearish"}`}>
                          {isWin ? "+" : ""}{formatCurrency(t.pnl)}
                        </td>
                        <td className="p-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${isWin ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"}`}>
                            {t.exit_reason}
                          </span>
                        </td>
                        <td className="p-2.5 text-neutral text-[11px]">{t.exit_time}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
