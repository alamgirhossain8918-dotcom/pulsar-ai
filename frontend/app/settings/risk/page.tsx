"use client";

import { useState } from "react";
import { ShieldAlert, Calculator, AlertTriangle, CheckCircle2 } from "lucide-react";
import { api } from "../../../lib/api";
import { RiskCalculation } from "../../../types";
import { formatCurrency } from "../../../lib/utils";

export default function RiskManagementPage() {
  const [balance, setBalance] = useState(10000);
  const [riskPercent, setRiskPercent] = useState(1.0);
  const [entryPrice, setEntryPrice] = useState(65000);
  const [stopLoss, setStopLoss] = useState(64000);
  const [tp1, setTp1] = useState(67000);
  const [leverage, setLeverage] = useState(10);

  const [result, setResult] = useState<RiskCalculation | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleCalculate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.calculateRisk({
        account_balance: balance,
        risk_percentage: riskPercent,
        entry_price: entryPrice,
        stop_loss: stopLoss,
        take_profit_1: tp1,
        leverage: leverage,
      });
      setResult(res);
    } catch (err: any) {
      alert("Calculation error: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="p-5 rounded-xl bg-surface border border-border">
        <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-accent" />
          <span>INSTITUTIONAL RISK CALCULATOR & SIZING ENGINE</span>
        </h2>
        <p className="text-xs text-neutral mt-1">
          Compute accurate mathematical position size, fees, margin requirements, and liquidation proximity warnings.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Form Input */}
        <form onSubmit={handleCalculate} className="p-5 rounded-xl bg-surface border border-border space-y-4 text-xs">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Calculator className="w-4 h-4 text-accent" />
            <span>Position Parameters</span>
          </h3>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-neutral font-medium block mb-1">Account Balance ($)</label>
              <input
                type="number"
                value={balance}
                onChange={(e) => setBalance(Number(e.target.value))}
                className="w-full p-2.5 rounded-lg bg-card border border-border text-white font-mono"
                required
              />
            </div>

            <div>
              <label className="text-neutral font-medium block mb-1">Risk Percentage (%)</label>
              <input
                type="number"
                step="0.1"
                value={riskPercent}
                onChange={(e) => setRiskPercent(Number(e.target.value))}
                className="w-full p-2.5 rounded-lg bg-card border border-border text-white font-mono"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-neutral font-medium block mb-1">Planned Entry ($)</label>
              <input
                type="number"
                value={entryPrice}
                onChange={(e) => setEntryPrice(Number(e.target.value))}
                className="w-full p-2.5 rounded-lg bg-card border border-border text-white font-mono"
                required
              />
            </div>

            <div>
              <label className="text-neutral font-medium block mb-1">Stop Loss ($)</label>
              <input
                type="number"
                value={stopLoss}
                onChange={(e) => setStopLoss(Number(e.target.value))}
                className="w-full p-2.5 rounded-lg bg-card border border-border text-white font-mono text-bearish"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-neutral font-medium block mb-1">Take Profit 1 ($)</label>
              <input
                type="number"
                value={tp1}
                onChange={(e) => setTp1(Number(e.target.value))}
                className="w-full p-2.5 rounded-lg bg-card border border-border text-white font-mono text-bullish"
                required
              />
            </div>

            <div>
              <label className="text-neutral font-medium block mb-1">Leverage ({leverage}x)</label>
              <input
                type="number"
                min="1"
                max="100"
                value={leverage}
                onChange={(e) => setLeverage(Number(e.target.value))}
                className="w-full p-2.5 rounded-lg bg-card border border-border text-white font-mono"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-accent hover:bg-accent/90 text-white font-bold transition flex items-center justify-center gap-1.5 shadow-lg shadow-accent/20 mt-2"
          >
            <span>{loading ? "Calculating..." : "Compute Exact Risk Sizing"}</span>
          </button>
        </form>

        {/* Calculation Output Card */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Risk & Margin Breakdown
          </h3>

          {result ? (
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-card border border-border">
                  <span className="text-neutral text-[11px] block">Max Risk Amount</span>
                  <span className="font-mono text-base font-bold text-bearish">
                    {formatCurrency(result.risk_amount_usd)}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-card border border-border">
                  <span className="text-neutral text-[11px] block">Position Size</span>
                  <span className="font-mono text-base font-bold text-white">
                    {result.position_size_tokens} Tokens
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-card border border-border">
                  <span className="text-neutral text-[11px] block">Notional Value</span>
                  <span className="font-mono text-sm font-bold text-white">
                    {formatCurrency(result.notional_value_usd)}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-card border border-border">
                  <span className="text-neutral text-[11px] block">Estimated Margin</span>
                  <span className="font-mono text-sm font-bold text-accent">
                    {formatCurrency(result.estimated_margin_usd)}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-card border border-border">
                  <span className="text-neutral text-[11px] block">Estimated Fees</span>
                  <span className="font-mono text-sm font-bold text-neutral">
                    {formatCurrency(result.total_estimated_fees_usd)}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-card border border-border">
                  <span className="text-neutral text-[11px] block">Potential Profit (TP1)</span>
                  <span className="font-mono text-sm font-bold text-bullish">
                    {formatCurrency(result.potential_profit_tp1_usd || 0)}
                  </span>
                </div>
              </div>

              {/* Liquidation estimation */}
              <div className="p-3 rounded-lg bg-card border border-border flex justify-between items-center">
                <div>
                  <span className="text-neutral text-[11px] block">Approx Liquidation Price</span>
                  <span className="font-mono font-bold text-white">
                    {formatCurrency(result.approx_liquidation_price)}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-neutral text-[11px] block">Distance to Liq</span>
                  <span className="font-mono font-bold text-bullish">
                    {result.liquidation_distance_pct}%
                  </span>
                </div>
              </div>

              {/* Warnings List */}
              {result.warnings.length > 0 && (
                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 space-y-1 text-[11px]">
                  {result.warnings.map((w, i) => (
                    <div key={i} className="flex items-start gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center text-neutral text-xs">
              Enter trade values and submit to compute position size.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
