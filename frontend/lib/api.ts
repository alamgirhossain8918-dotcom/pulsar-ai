import {
  MarketOverview,
  ScannerItem,
  Signal,
  PaperAccount,
  VirtualPosition,
  VirtualTrade,
  BacktestResult,
  RiskCalculation
} from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetcher<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || errorBody.message || `HTTP ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Market
  getOverview: () => fetcher<MarketOverview>("/market/overview"),
  getCandles: (symbol: string, timeframe: string = "15m", limit: number = 150) =>
    fetcher<{ symbol: string; timeframe: string; provider: string; is_demo: boolean; candles: any[]; markers: any[]; analysis: any }>(
      `/market/candles/${symbol}?timeframe=${timeframe}&limit=${limit}`
    ),
  getScannerResults: () => fetcher<{ timestamp: string; provider: string; is_demo: boolean; results: ScannerItem[] }>("/market/scanner"),

  // Signals
  getSignals: (filters?: { status?: string; direction?: string; symbol?: string }) => {
    const query = new URLSearchParams(filters as any).toString();
    return fetcher<Signal[]>(`/signals${query ? `?${query}` : ""}`);
  },
  getSignalById: (id: string) => fetcher<Signal>(`/signals/${id}`),

  // Backtest
  runBacktest: (params: { symbol: string; timeframe: string; strategy_profile: string; initial_balance: number; risk_percentage: number }) =>
    fetcher<BacktestResult>("/backtest/run", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  // Paper Trading
  getPaperAccount: () => fetcher<PaperAccount>("/paper-trading/account"),
  getPaperPositions: () => fetcher<VirtualPosition[]>("/paper-trading/positions"),
  getPaperTrades: () => fetcher<VirtualTrade[]>("/paper-trading/trades"),
  openPaperOrder: (order: {
    symbol: string;
    direction: string;
    entry_price: number;
    stop_loss: number;
    take_profit_1: number;
    quantity: number;
    leverage: number;
  }) =>
    fetcher<VirtualPosition>("/paper-trading/order", {
      method: "POST",
      body: JSON.stringify(order),
    }),
  closePaperPosition: (posId: string, exitPrice: number) =>
    fetcher<VirtualTrade>(`/paper-trading/close/${posId}?exit_price=${exitPrice}`, {
      method: "POST",
    }),

  // Risk Calculator
  calculateRisk: (params: {
    account_balance: number;
    risk_percentage: number;
    entry_price: number;
    stop_loss: number;
    take_profit_1?: number;
    leverage: number;
  }) =>
    fetcher<RiskCalculation>("/risk/calculate", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  // Performance Analytics
  getPerformanceAnalytics: () => fetcher<any>("/analytics/performance"),

  // Settings
  getStrategySettings: () => fetcher<any>("/settings/strategy"),
  getRiskSettings: () => fetcher<any>("/settings/risk"),
  getTelegramSettings: () => fetcher<any>("/settings/telegram"),

  // Health
  getHealth: () => fetcher<any>("/health"),
};
