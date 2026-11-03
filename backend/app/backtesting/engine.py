from typing import Dict, List, Optional
import pandas as pd
from backend.app.backtesting.metrics import BacktestSummary, BacktestTradeRecord
from backend.app.engine.mtf_analyzer import MultiTimeframeAnalyzer
from backend.app.strategies.sniper_strategy import ICTSniperStrategy
from backend.app.strategies.swing_strategy import ICTSwingStrategy
from backend.app.strategies.scalp_strategy import ICTScalpStrategy


class BacktestEngine:
    """
    Event-Driven Backtesting Engine
    - Uses exact same ICT/SMC strategies as live execution
    - Bar-by-bar chronological iteration (No look-ahead bias)
    - Closed candle signals only (Zero repainting)
    - Conservative same-candle resolution: If TP & SL both breached in same bar, assumes SL hit
    - Models fee (0.05%) and slippage (0.02%)
    """

    def __init__(
        self,
        initial_balance: float = 10000.0,
        risk_percent: float = 1.0,
        fee_rate: float = 0.0005,
        slippage_rate: float = 0.0002
    ):
        self.initial_balance = initial_balance
        self.risk_percent = risk_percent
        self.fee_rate = fee_rate
        self.slippage_rate = slippage_rate

        self.strategy_map = {
            "sniper": ICTSniperStrategy(),
            "swing": ICTSwingStrategy(),
            "scalp": ICTScalpStrategy()
        }

    def run_backtest(
        self,
        symbol: str,
        timeframe: str,
        df: pd.DataFrame,
        strategy_name: str = "sniper"
    ) -> BacktestSummary:
        strategy = self.strategy_map.get(strategy_name.lower(), self.strategy_map["sniper"])
        balance = self.initial_balance
        equity_curve = [{"time": str(df.index[0]), "equity": round(balance, 2)}]
        trades: List[BacktestTradeRecord] = []
        peak_balance = balance
        max_dd = 0.0
        max_dd_pct = 0.0

        n = len(df)
        warmup = 30
        if n < warmup + 10:
            return BacktestSummary(
                symbol=symbol,
                timeframe=timeframe,
                strategy_profile=strategy.name,
                initial_balance=self.initial_balance,
                final_balance=balance,
                net_pnl=0.0,
                total_trades=0,
                wins=0,
                losses=0,
                win_rate=0.0,
                profit_factor=0.0,
                max_drawdown=0.0,
                max_drawdown_percent=0.0,
                average_rr=0.0,
                equity_curve=equity_curve,
                trades=[]
            )

        active_trade: Optional[Dict] = None
        trade_counter = 0

        # Bar-by-bar forward stepping
        for i in range(warmup, n):
            current_bar = df.iloc[i]
            bar_time = str(df.index[i])
            c_high = current_bar['high']
            c_low = current_bar['low']
            c_close = current_bar['close']
            c_open = current_bar['open']

            # 1. Manage Active Trade if any
            if active_trade:
                direction = active_trade["direction"]
                entry = active_trade["entry_price"]
                sl = active_trade["stop_loss"]
                tp1 = active_trade["take_profit_1"]
                tp2 = active_trade["take_profit_2"]
                size = active_trade["size"]

                sl_hit = False
                tp_hit = False

                if direction == "BUY":
                    if c_low <= sl:
                        sl_hit = True
                    if c_high >= tp1:
                        tp_hit = True

                    # Same-candle ambiguity: Conservative rule assumes SL hit
                    if sl_hit and tp_hit:
                        sl_hit = True
                        tp_hit = False

                    if sl_hit:
                        exit_price = sl * (1.0 - self.slippage_rate)
                        fee = (entry * size * self.fee_rate) + (exit_price * size * self.fee_rate)
                        pnl = ((exit_price - entry) * size) - fee
                        balance += pnl
                        trade_counter += 1
                        trades.append(BacktestTradeRecord(
                            trade_id=trade_counter,
                            symbol=symbol,
                            direction=direction,
                            entry_time=active_trade["entry_time"],
                            exit_time=bar_time,
                            entry_price=round(entry, 2),
                            exit_price=round(exit_price, 2),
                            stop_loss=round(sl, 2),
                            take_profit=round(tp1, 2),
                            size=round(size, 4),
                            fees=round(fee, 2),
                            slippage=round(sl * self.slippage_rate * size, 2),
                            pnl=round(pnl, 2),
                            pnl_percent=round((pnl / balance) * 100.0, 2),
                            exit_reason="SL"
                        ))
                        active_trade = None

                    elif tp_hit:
                        exit_price = tp1 * (1.0 - self.slippage_rate)
                        fee = (entry * size * self.fee_rate) + (exit_price * size * self.fee_rate)
                        pnl = ((exit_price - entry) * size) - fee
                        balance += pnl
                        trade_counter += 1
                        trades.append(BacktestTradeRecord(
                            trade_id=trade_counter,
                            symbol=symbol,
                            direction=direction,
                            entry_time=active_trade["entry_time"],
                            exit_time=bar_time,
                            entry_price=round(entry, 2),
                            exit_price=round(exit_price, 2),
                            stop_loss=round(sl, 2),
                            take_profit=round(tp1, 2),
                            size=round(size, 4),
                            fees=round(fee, 2),
                            slippage=round(tp1 * self.slippage_rate * size, 2),
                            pnl=round(pnl, 2),
                            pnl_percent=round((pnl / balance) * 100.0, 2),
                            exit_reason="TP1"
                        ))
                        active_trade = None

                elif direction == "SELL":
                    if c_high >= sl:
                        sl_hit = True
                    if c_low <= tp1:
                        tp_hit = True

                    # Conservative same-candle resolution
                    if sl_hit and tp_hit:
                        sl_hit = True
                        tp_hit = False

                    if sl_hit:
                        exit_price = sl * (1.0 + self.slippage_rate)
                        fee = (entry * size * self.fee_rate) + (exit_price * size * self.fee_rate)
                        pnl = ((entry - exit_price) * size) - fee
                        balance += pnl
                        trade_counter += 1
                        trades.append(BacktestTradeRecord(
                            trade_id=trade_counter,
                            symbol=symbol,
                            direction=direction,
                            entry_time=active_trade["entry_time"],
                            exit_time=bar_time,
                            entry_price=round(entry, 2),
                            exit_price=round(exit_price, 2),
                            stop_loss=round(sl, 2),
                            take_profit=round(tp1, 2),
                            size=round(size, 4),
                            fees=round(fee, 2),
                            slippage=round(sl * self.slippage_rate * size, 2),
                            pnl=round(pnl, 2),
                            pnl_percent=round((pnl / balance) * 100.0, 2),
                            exit_reason="SL"
                        ))
                        active_trade = None

                    elif tp_hit:
                        exit_price = tp1 * (1.0 + self.slippage_rate)
                        fee = (entry * size * self.fee_rate) + (exit_price * size * self.fee_rate)
                        pnl = ((entry - exit_price) * size) - fee
                        balance += pnl
                        trade_counter += 1
                        trades.append(BacktestTradeRecord(
                            trade_id=trade_counter,
                            symbol=symbol,
                            direction=direction,
                            entry_time=active_trade["entry_time"],
                            exit_time=bar_time,
                            entry_price=round(entry, 2),
                            exit_price=round(exit_price, 2),
                            stop_loss=round(sl, 2),
                            take_profit=round(tp1, 2),
                            size=round(size, 4),
                            fees=round(fee, 2),
                            slippage=round(tp1 * self.slippage_rate * size, 2),
                            pnl=round(pnl, 2),
                            pnl_percent=round((pnl / balance) * 100.0, 2),
                            exit_reason="TP1"
                        ))
                        active_trade = None

            # 2. Check for New Signal on CLOSED bar if no active trade
            if not active_trade:
                sub_df = df.iloc[: i + 1]  # Strictly slice up to current closed candle
                # Single-timeframe surrogate MTF for backtest
                tf_analysis = MultiTimeframeAnalyzer.analyze_single_timeframe(sub_df, timeframe)
                mtf_surrogate = MultiTimeframeAnalyzer.analyze_symbol(
                    symbol=symbol,
                    timeframe_dfs={timeframe: sub_df}
                )

                signal_out = strategy.evaluate(mtf_surrogate)
                if signal_out and signal_out.confluence_score >= 70.0:
                    entry = signal_out.entry_price * (1.0 + (self.slippage_rate if signal_out.direction == "BUY" else -self.slippage_rate))
                    sl = signal_out.stop_loss
                    dist = abs(entry - sl)
                    if dist > 0:
                        risk_capital = balance * (self.risk_percent / 100.0)
                        size = risk_capital / dist
                        active_trade = {
                            "direction": signal_out.direction,
                            "entry_price": entry,
                            "stop_loss": sl,
                            "take_profit_1": signal_out.take_profit_1,
                            "take_profit_2": signal_out.take_profit_2,
                            "size": size,
                            "entry_time": bar_time
                        }

            # Update Equity & Drawdown tracking
            if balance > peak_balance:
                peak_balance = balance
            dd = peak_balance - balance
            dd_pct = (dd / peak_balance) * 100.0 if peak_balance > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

            if i % 5 == 0 or i == n - 1:
                equity_curve.append({"time": bar_time, "equity": round(balance, 2)})

        # Compute Summary Statistics
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]
        total_trades = len(trades)
        win_rate = round((len(wins) / total_trades * 100.0), 2) if total_trades > 0 else 0.0

        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        profit_factor = round(gross_profit / max(gross_loss, 1e-6), 2) if gross_loss > 0 else (round(gross_profit, 2) if gross_profit > 0 else 0.0)

        return BacktestSummary(
            symbol=symbol,
            timeframe=timeframe,
            strategy_profile=strategy.name,
            initial_balance=self.initial_balance,
            final_balance=round(balance, 2),
            net_pnl=round(balance - self.initial_balance, 2),
            total_trades=total_trades,
            wins=len(wins),
            losses=len(losses),
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=round(max_dd, 2),
            max_drawdown_percent=round(max_dd_pct, 2),
            average_rr=round(strategy.min_rr, 2),
            equity_curve=equity_curve,
            trades=trades
        )
