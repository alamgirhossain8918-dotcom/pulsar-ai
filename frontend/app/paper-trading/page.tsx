"use client";

import { useEffect, useState } from "react";
import { Coins, Plus, X, ArrowUpRight, ArrowDownRight, ShieldCheck } from "lucide-react";
import { api } from "../../lib/api";
import { PaperAccount, VirtualPosition, VirtualTrade } from "../../types";
import { formatCurrency, formatDate } from "../../lib/utils";

export default function PaperTradingPage() {
  const [account, setAccount] = useState<PaperAccount | null>(null);
  const [positions, setPositions] = useState<VirtualPosition[]>([]);
  const [trades, setTrades] = useState<VirtualTrade[]>([]);
  const [loading, setLoading] = useState(true);

  // New Position Form
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [direction, setDirection] = useState("BUY");
  const [entryPrice, setEntryPrice] = useState(65000);
  const [stopLoss, setStopLoss] = useState(64000);
  const [tp1, setTp1] = useState(67000);
  const [quantity, setQuantity] = useState(0.1);
  const [leverage, setLeverage] = useState(10);
  const [submitting, setSubmitting] = useState(false);

  async function loadData() {
    try {
      const [acc, pos, tr] = await Promise.all([
        api.getPaperAccount().catch(() => null),
        api.getPaperPositions().catch(() => []),
        api.getPaperTrades().catch(() => []),
      ]);
      if (acc) setAccount(acc);
      setPositions(pos);
      setTrades(tr);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function handleOpenOrder(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.openPaperOrder({
        symbol,
        direction,
        entry_price: entryPrice,
        stop_loss: stopLoss,
        take_profit_1: tp1,
        quantity,
        leverage,
      });
      await loadData();
    } catch (err: any) {
      alert("Error opening paper order: " + err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleClosePosition(posId: string, currentPrice: number) {
    if (!confirm(`Close paper position at ${formatCurrency(currentPrice)}?`)) return;
    try {
      await api.closePaperPosition(posId, currentPrice);
      await loadData();
    } catch (err: any) {
      alert("Error closing position: " + err.message);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-surface border border-border">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <Coins className="w-5 h-5 text-accent" />
            <span>VIRTUAL PAPER TRADING SIMULATOR</span>
          </h2>
          <p className="text-xs text-neutral mt-1">
            Safe simulation environment. Zero real exchange orders are executed. No Binance API keys requested.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-card border border-border text-xs text-bullish font-semibold">
          <ShieldCheck className="w-4 h-4" />
          <span>Simulation Active</span>
        </div>
      </div>

      {/* Account Balance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-card border border-border">
          <span className="text-[11px] text-neutral uppercase font-bold">Virtual Balance</span>
          <h3 className="text-xl font-mono font-bold mt-1 text-white">
            {formatCurrency(account?.balance || 10000)}
          </h3>
          <span className="text-[11px] text-neutral">Free Margin: {formatCurrency(account?.free_margin || 10000)}</span>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <span className="text-[11px] text-neutral uppercase font-bold">Total Equity</span>
          <h3 className="text-xl font-mono font-bold mt-1 text-accent">
            {formatCurrency(account?.equity || 10000)}
          </h3>
          <span className="text-[11px] text-neutral">Balance + Unrealized PnL</span>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <span className="text-[11px] text-neutral uppercase font-bold">Margin Used</span>
          <h3 className="text-xl font-mono font-bold mt-1 text-white">
            {formatCurrency(account?.margin_used || 0)}
          </h3>
          <span className="text-[11px] text-neutral">Open positions: {positions.length}</span>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <span className="text-[11px] text-neutral uppercase font-bold">Unrealized PnL</span>
          <h3
            className={`text-xl font-mono font-bold mt-1 ${
              (account?.unrealized_pnl || 0) >= 0 ? "text-bullish" : "text-bearish"
            }`}
          >
            {formatCurrency(account?.unrealized_pnl || 0)}
          </h3>
          <span className="text-[11px] text-neutral">Closed Trades: {trades.length}</span>
        </div>
      </div>

      {/* Grid: Open Order Form & Active Positions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Placement Form */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Plus className="w-4 h-4 text-accent" />
            <span>Place Paper Order</span>
          </h3>

          <form onSubmit={handleOpenOrder} className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-neutral font-medium block mb-1">Symbol</label>
                <select
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                  className="w-full p-2 rounded-lg bg-card border border-border text-white focus:outline-none focus:border-accent"
                >
                  {["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"].map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-neutral font-medium block mb-1">Direction</label>
                <div className="flex bg-card border border-border rounded-lg p-0.5">
                  <button
                    type="button"
                    onClick={() => setDirection("BUY")}
                    className={`flex-1 py-1.5 rounded font-bold transition ${
                      direction === "BUY" ? "bg-bullish text-white" : "text-neutral"
                    }`}
                  >
                    BUY
                  </button>
                  <button
                    type="button"
                    onClick={() => setDirection("SELL")}
                    className={`flex-1 py-1.5 rounded font-bold transition ${
                      direction === "SELL" ? "bg-bearish text-white" : "text-neutral"
                    }`}
                  >
                    SELL
                  </button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-neutral font-medium block mb-1">Entry Price ($)</label>
                <input
                  type="number"
                  value={entryPrice}
                  onChange={(e) => setEntryPrice(Number(e.target.value))}
                  className="w-full p-2 rounded-lg bg-card border border-border text-white font-mono"
                  required
                />
              </div>

              <div>
                <label className="text-neutral font-medium block mb-1">Quantity (Tokens)</label>
                <input
                  type="number"
                  step="0.001"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="w-full p-2 rounded-lg bg-card border border-border text-white font-mono"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-neutral font-medium block mb-1">Stop Loss ($)</label>
                <input
                  type="number"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(Number(e.target.value))}
                  className="w-full p-2 rounded-lg bg-card border border-border text-white font-mono text-bearish"
                  required
                />
              </div>

              <div>
                <label className="text-neutral font-medium block mb-1">Take Profit 1 ($)</label>
                <input
                  type="number"
                  value={tp1}
                  onChange={(e) => setTp1(Number(e.target.value))}
                  className="w-full p-2 rounded-lg bg-card border border-border text-white font-mono text-bullish"
                  required
                />
              </div>
            </div>

            <div>
              <label className="text-neutral font-medium block mb-1">Leverage ({leverage}x)</label>
              <input
                type="range"
                min="1"
                max="50"
                value={leverage}
                onChange={(e) => setLeverage(Number(e.target.value))}
                className="w-full accent-accent"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white font-bold transition mt-2 shadow-lg shadow-accent/20"
            >
              {submitting ? "Opening..." : "Execute Paper Order"}
            </button>
          </form>
        </div>

        {/* Active Open Positions Table */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-border space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Active Virtual Positions ({positions.length})
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-card text-neutral uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l">Symbol</th>
                  <th className="p-2.5">Side</th>
                  <th className="p-2.5">Entry</th>
                  <th className="p-2.5">Mark</th>
                  <th className="p-2.5">SL / TP1</th>
                  <th className="p-2.5">Unrealized PnL</th>
                  <th className="p-2.5 rounded-r text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50 font-mono">
                {positions.map((pos) => {
                  const isBuy = pos.direction === "BUY";
                  const isProfit = pos.unrealized_pnl >= 0;
                  return (
                    <tr key={pos.id} className="hover:bg-card/50 transition">
                      <td className="p-2.5 font-bold text-white font-sans">{pos.symbol}</td>
                      <td className={`p-2.5 font-bold ${isBuy ? "text-bullish" : "text-bearish"}`}>
                        {pos.direction} {pos.leverage}x
                      </td>
                      <td className="p-2.5 text-white">{formatCurrency(pos.entry_price)}</td>
                      <td className="p-2.5 text-neutral">{formatCurrency(pos.current_price)}</td>
                      <td className="p-2.5 text-[11px] text-neutral">
                        <span className="text-bearish">{formatCurrency(pos.stop_loss)}</span> /{" "}
                        <span className="text-bullish">{formatCurrency(pos.take_profit_1)}</span>
                      </td>
                      <td className={`p-2.5 font-bold ${isProfit ? "text-bullish" : "text-bearish"}`}>
                        {formatCurrency(pos.unrealized_pnl)}
                      </td>
                      <td className="p-2.5 text-right">
                        <button
                          onClick={() => handleClosePosition(pos.id, pos.current_price)}
                          className="px-2.5 py-1 rounded bg-bearish/10 hover:bg-bearish/20 border border-bearish/30 text-bearish text-[11px] font-sans font-semibold transition"
                        >
                          Close
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {positions.length === 0 && (
                  <tr>
                    <td colSpan={7} className="p-6 text-center text-neutral font-sans text-xs">
                      No active virtual positions. Open one using the form.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
