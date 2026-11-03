"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Radar,
  LineChart,
  BellRing,
  History,
  Coins,
  TrendingUp,
  Sliders,
  ShieldAlert,
  Send,
  Activity,
  LogIn
} from "lucide-react";
import { cn } from "../lib/utils";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Live Scanner", href: "/scanner", icon: Radar },
  { name: "Market Analysis", href: "/analysis", icon: LineChart },
  { name: "Signals", href: "/signals", icon: BellRing },
  { name: "Backtester", href: "/backtester", icon: History },
  { name: "Paper Trading", href: "/paper-trading", icon: Coins },
  { name: "Performance", href: "/performance", icon: TrendingUp },
  { name: "Strategy Settings", href: "/settings/strategy", icon: Sliders },
  { name: "Risk Management", href: "/settings/risk", icon: ShieldAlert },
  { name: "Telegram Bot", href: "/settings/telegram", icon: Send },
  { name: "System Health", href: "/health", icon: Activity },
  { name: "Owner Login", href: "/login", icon: LogIn },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="p-5 border-b border-border flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center font-bold text-accent">
          P
        </div>
        <div>
          <h1 className="font-bold text-base tracking-wider text-white">PULSAR AI</h1>
          <p className="text-[10px] text-neutral uppercase tracking-widest">V2.0 Quantitative</p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors",
                isActive
                  ? "bg-accent text-white shadow-lg shadow-accent/20"
                  : "text-neutral hover:text-white hover:bg-card"
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* System Footer Info */}
      <div className="p-4 border-t border-border text-[11px] text-neutral/70 space-y-1">
        <div className="flex justify-between">
          <span>Engine:</span>
          <span className="text-white font-mono">ICT + SMC V2</span>
        </div>
        <div className="flex justify-between">
          <span>Mode:</span>
          <span className="text-bullish font-mono">Real-time</span>
        </div>
      </div>
    </aside>
  );
}
