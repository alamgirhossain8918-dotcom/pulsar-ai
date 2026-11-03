export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ChartMarker {
  time: number;
  position: 'aboveBar' | 'belowBar';
  color: string;
  shape: 'arrowUp' | 'arrowDown';
  text: string;
}

export interface Signal {
  id: string;
  symbol: string;
  direction: 'BUY' | 'SELL';
  timeframe: string;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  take_profit_3: number;
  rr_ratio: number;
  confluence_score: number;
  htf_bias: string;
  ltf_confirmation: string;
  liquidity_event: string;
  bos_choch_confirmation: string;
  fvg_ob_info: string;
  entry_explanation: string;
  status: string;
  strategy_profile: string;
  data_provider: string;
  is_demo: boolean;
  created_at: string;
  expiry_time: string;
  invalidation_conditions?: string;
  realized_pnl?: number;
}

export interface ScannerItem {
  symbol: string;
  price: number;
  trend: string;
  regime: string;
  htf_bias: string;
  dealing_zone: string;
  liquidity_sweeps_count: number;
  unmitigated_fvgs_count: number;
  active_obs_count: number;
  provider: string;
  is_demo: boolean;
  signal: string;
  updated_at: string;
}

export interface Ticker {
  symbol: string;
  last_price: number;
  high_24h: number;
  low_24h: number;
  volume_24h: number;
  price_change_percent: number;
  provider: string;
}

export interface MarketOverview {
  active_provider: string;
  is_demo_mode: boolean;
  priority_assets: Ticker[];
  active_pairs: string[];
  last_scanner_run: string | null;
  total_active_signals: number;
}

export interface RiskCalculation {
  direction: 'BUY' | 'SELL';
  risk_amount_usd: number;
  position_size_tokens: number;
  notional_value_usd: number;
  estimated_margin_usd: number;
  total_estimated_fees_usd: number;
  potential_loss_usd: number;
  potential_profit_tp1_usd?: number;
  potential_profit_tp2_usd?: number;
  potential_profit_tp3_usd?: number;
  risk_reward_ratio_tp1?: number;
  risk_reward_ratio_tp2?: number;
  risk_reward_ratio_tp3?: number;
  approx_liquidation_price: number;
  liquidation_distance_pct: number;
  warnings: string[];
}

export interface PaperAccount {
  balance: number;
  equity: number;
  margin_used: number;
  free_margin: number;
  unrealized_pnl: number;
  open_positions_count: number;
  total_trades_count: number;
}

export interface VirtualPosition {
  id: string;
  symbol: string;
  direction: 'BUY' | 'SELL';
  entry_price: number;
  current_price: number;
  quantity: number;
  leverage: number;
  margin: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2?: number;
  take_profit_3?: number;
  unrealized_pnl: number;
  status: string;
  opened_at: string;
}

export interface VirtualTrade {
  id: string;
  symbol: string;
  direction: 'BUY' | 'SELL';
  entry_price: number;
  exit_price: number;
  quantity: number;
  leverage: number;
  fee: number;
  pnl: number;
  exit_reason: string;
  opened_at: string;
  closed_at: string;
}

export interface BacktestResult {
  symbol: string;
  timeframe: string;
  strategy_profile: string;
  initial_balance: number;
  final_balance: number;
  net_pnl: number;
  total_trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  profit_factor: number;
  max_drawdown: number;
  max_drawdown_percent: number;
  average_rr: number;
  equity_curve: { time: string; equity: number }[];
  trades: {
    trade_id: number;
    symbol: string;
    direction: string;
    entry_time: string;
    exit_time: string;
    entry_price: number;
    exit_price: number;
    stop_loss: number;
    take_profit: number;
    size: number;
    fees: number;
    pnl: number;
    exit_reason: string;
  }[];
}
