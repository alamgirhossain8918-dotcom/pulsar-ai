"use client";

import { useState, useEffect } from "react";
import { Activity, Wifi, AlertTriangle } from "lucide-react";
import { api } from "../lib/api";
import { useWebSocket } from "../hooks/useWebSocket";
import { formatDate } from "../lib/utils";

export function Header() {
  const { isConnected } = useWebSocket();
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    api.getOverview().then(setOverview).catch(() => {});
    const interval = setInterval(() => {
      api.getOverview().then(setOverview).catch(() => {});
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const provider = overview?.active_provider || "binance";
  const isDemo = overview?.is_demo_mode;
  const lastScan = overview?.last_scanner_run;

  return (
    <header className="h-14 border-b border-border bg-surface/50 backdrop-blur px-6 flex items-center justify-between shrink-0">
      {/* Left: Active Provider & Demo Badge */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs">
          <span className="text-neutral">Data Provider:</span>
          <span className="font-semibold text-white uppercase px-2 py-0.5 rounded bg-card border border-border">
            {provider} USDⓈ-M
          </span>
        </div>

        {isDemo && (
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-bearish/10 border border-bearish/30 text-bearish text-xs font-semibold animate-pulse">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>DEMO MODE (DATA UNAVAILABLE)</span>
          </div>
        )}
      </div>

      {/* Right: Last Update & Connection status */}
      <div className="flex items-center gap-4 text-xs">
        {lastScan && (
          <div className="text-neutral hidden md:block">
            Last Scanner Update:{" "}
            <span className="text-white font-mono">{formatDate(lastScan)}</span>
          </div>
        )}

        {/* WebSocket Ping */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-card border border-border">
          <Wifi className={`w-3.5 h-3.5 ${isConnected ? "text-bullish" : "text-bearish"}`} />
          <span className="text-neutral text-[11px]">
            {isConnected ? "Live Stream Active" : "Connecting..."}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-bullish animate-ping" />
          <span className="text-white font-medium text-xs">Cloud Operational</span>
        </div>
      </div>
    </header>
  );
}
