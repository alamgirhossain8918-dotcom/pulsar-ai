"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Radar, Filter, RefreshCw, LineChart, Search } from "lucide-react";
import { api } from "../../lib/api";
import { ScannerItem } from "../../types";
import { formatCurrency } from "../../lib/utils";
import { RegimeBadge } from "../../components/RegimeBadge";

export default function ScannerPage() {
  const [items, setItems] = useState<ScannerItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSignal, setFilterSignal] = useState<string>("ALL");
  const [search, setSearch] = useState("");

  async function loadScanner() {
    setLoading(true);
    try {
      const res = await api.getScannerResults();
      setItems(res.results || []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadScanner();
    const interval = setInterval(loadScanner, 30000);
    return () => clearInterval(interval);
  }, []);

  const filtered = items.filter((item) => {
    const matchSearch = item.symbol.toLowerCase().includes(search.toLowerCase());
    const matchSignal =
      filterSignal === "ALL"
        ? true
        : filterSignal === "SIGNALS_ONLY"
        ? item.signal !== "NO TRADE"
        : item.signal === filterSignal;
    return matchSearch && matchSignal;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-surface border border-border">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <Radar className="w-5 h-5 text-accent" />
            <span>LIVE INSTITUTIONAL SCANNER</span>
          </h2>
          <p className="text-xs text-neutral mt-1">
            Real-time scanning across active USDT perpetual futures pairs using closed candle ICT/SMC algorithms.
          </p>
        </div>

        <button
          onClick={loadScanner}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-card hover:bg-card/80 border border-border text-xs font-semibold text-white transition flex items-center gap-1.5 self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Scan</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-neutral absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search symbol (e.g. BTC)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-card border border-border text-xs text-white placeholder-neutral focus:outline-none focus:border-accent"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-neutral" />
          <div className="flex bg-card border border-border rounded-lg p-0.5 text-xs">
            {["ALL", "SIGNALS_ONLY", "BUY", "SELL"].map((f) => (
              <button
                key={f}
                onClick={() => setFilterSignal(f)}
                className={`px-3 py-1 rounded font-medium transition ${
                  filterSignal === f ? "bg-accent text-white" : "text-neutral hover:text-white"
                }`}
              >
                {f.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Scanner Table */}
      <div className="p-4 rounded-xl bg-surface border border-border overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-card text-neutral uppercase text-[10px] tracking-wider">
            <tr>
              <th className="p-3 rounded-l">Pair</th>
              <th className="p-3">Price</th>
              <th className="p-3">HTF Bias</th>
              <th className="p-3">LTF Trend</th>
              <th className="p-3">Regime</th>
              <th className="p-3">Dealing Zone</th>
              <th className="p-3 text-center">Sweeps</th>
              <th className="p-3 text-center">FVGs / OBs</th>
              <th className="p-3 text-center">Signal Status</th>
              <th className="p-3 rounded-r text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {filtered.map((item) => (
              <tr key={item.symbol} className="hover:bg-card/50 transition">
                <td className="p-3 font-bold text-white text-sm">{item.symbol}</td>
                <td className="p-3 font-mono text-neutral">{formatCurrency(item.price)}</td>
                <td className="p-3 text-neutral">{item.htf_bias}</td>
                <td className="p-3 text-neutral">{item.trend}</td>
                <td className="p-3">
                  <RegimeBadge regime={item.regime} />
                </td>
                <td className="p-3 font-mono text-neutral">{item.dealing_zone}</td>
                <td className="p-3 text-center font-mono text-neutral">{item.liquidity_sweeps_count}</td>
                <td className="p-3 text-center font-mono text-neutral">
                  {item.unmitigated_fvgs_count} / {item.active_obs_count}
                </td>
                <td className="p-3 text-center">
                  <span
                    className={`font-bold px-2 py-0.5 rounded text-[11px] ${
                      item.signal === "BUY"
                        ? "bg-bullish/10 text-bullish border border-bullish/30"
                        : item.signal === "SELL"
                        ? "bg-bearish/10 text-bearish border border-bearish/30"
                        : "text-neutral"
                    }`}
                  >
                    {item.signal}
                  </span>
                </td>
                <td className="p-3 text-right">
                  <Link
                    href={`/analysis?symbol=${item.symbol}`}
                    className="p-1.5 rounded hover:bg-card border border-border inline-flex items-center text-accent"
                    title="Open Chart"
                  >
                    <LineChart className="w-4 h-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
