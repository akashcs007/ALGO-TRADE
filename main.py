import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime
import math

# --- PART 1: STRATEGY IMPLEMENTATION [cite: 2] ---

class HybridTrendMeanReversion(bt.Strategy):
    """
    Strategy: Hybrid Trend Following + Mean Reversion
    
    Logic:
    1. Trend Filter: Price must be above SMA 200 (Long-term trend).
    2. Entry Signal: SMA 10 crosses over SMA 30 AND RSI is not overbought (< 70).
    3. Exit Signal: SMA 10 crosses under SMA 30 OR Trailing Stop hit.
    4. Risk Management: ATR-based position sizing and stops.
    """
    
    # Parameters for optimization [cite: 12]
    params = (
        ('fast_ma', 10),
        ('slow_ma', 30),
        ('trend_ma', 200),
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('atr_period', 14),
        ('risk_per_trade', 0.02),  # Risk 2% of account per trade 
        ('stop_loss_atr', 2.0),    # Stop loss at 2x ATR
    )

    def __init__(self):
        # Indicators [cite: 4, 40]
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_ma)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_ma)
        self.trend_ma = bt.indicators.SMA(self.data.close, period=self.params.trend_ma)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        
        # CrossOver Signal
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        # Skip if orders are pending
        if self.position:
            # Check for Exit Signal 
            if self.crossover < 0: # Fast MA crosses under Slow MA
                self.close() 
            return

        # Entry Logic 
        # 1. Trend Filter (Price > 200 SMA)
        # 2. Bullish Crossover (10 > 30)
        # 3. RSI is healthy (not > 70)
        if (self.data.close[0] > self.trend_ma[0] and 
            self.crossover > 0 and 
            self.rsi[0] < self.params.rsi_upper):
            
            # Position Sizing (Dynamic Risk Management) 
            # Calculate size based on risking % of equity
            risk_amt = self.broker.get_cash() * self.params.risk_per_trade
            stop_dist = self.atr[0] * self.params.stop_loss_atr
            
            if stop_dist == 0: return # Avoid division by zero
            
            size = risk_amt / stop_dist
            
            # Send Buy Order with Bracket (Stop Loss + Take Profit) 
            self.buy(size=size)
            
            # Set Stop Loss (ATR Based)
            self.sell(exectype=bt.Order.Stop, price=self.data.close[0] - stop_dist, size=size)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        # Logging trade results [cite: 27]
        print(f'Trade PnL: Gross {trade.pnl:.2f}, Net {trade.pnlcomm:.2f}')

# --- PART 2: PERFORMANCE ANALYSIS SETUP [cite: 13] ---

def run_backtest():
    cerebro = bt.Cerebro()

    # 1. Data Loading (Using yfinance for <1 hour timeframe) 
    # We download hourly data for SPY (S&P 500 ETF) for the last 730 days (~2 years)
    print("Downloading Data...")
    data_df = yf.download("SPY", period="730d", interval="1h", progress=False)
    
    # Clean data (Multi-index handling for new yfinance versions)
    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = data_df.columns.droplevel(1)
    data_df.dropna(inplace=True)

    # Feed data to Cerebro
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    # 2. Add Strategy
    cerebro.addstrategy(HybridTrendMeanReversion)

    # 3. Broker Setup
    cerebro.broker.setcash(100000.0) # $100k Capital
    cerebro.broker.setcommission(commission=0.001) # 0.1% commission

    # 4. Add Analyzers for Part 2 Requirements [cite: 15]
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Minutes, compression=60)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # Run
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    results = cerebro.run()
    strat = results[0]
    
    # --- OUTPUT METRICS [cite: 14, 15] ---
    print("\n--- PERFORMANCE METRICS ---")
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    
    # Sharpe
    sharpe = strat.analyzers.sharpe.get_analysis()
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 0):.4f}")
    
    # Drawdown
    dd = strat.analyzers.drawdown.get_analysis()
    print(f"Max Drawdown: {dd['max']['drawdown']:.2f}%")
    print(f"Max Drawdown Duration: {dd['max']['len']} periods")
    
    # Trade Stats [cite: 17]
    trades = strat.analyzers.trades.get_analysis()
    total_trades = trades.get('total', {}).get('total', 0)
    if total_trades > 0:
        win_rate = trades['won']['total'] / total_trades
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.2%}")
        print(f"Profit Factor: {abs(trades['won']['pnl']['total'] / trades['lost']['pnl']['total'] if trades['lost']['pnl']['total'] != 0 else 0):.2f}")
    else:
        print("No trades generated.")

    # --- VISUALIZATION [cite: 16] ---
    print("\nPlotting results...")
    cerebro.plot(style='candlestick', volume=False)

if __name__ == '__main__':
    run_backtest()