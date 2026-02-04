import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime

class HybridTrendMeanReversion(bt.Strategy):

    params = dict(
        fast_ma=20,
        slow_ma=50,
        trend_ma=100,
        rsi_period=14,
        atr_period=14,
        risk_per_trade=0.01,
        stop_atr=1.5,
        target_atr=3.0,
        max_bars_in_trade=48
    )

    def __init__(self):
        self.fast = bt.indicators.EMA(self.data.close, period=self.p.fast_ma)
        self.slow = bt.indicators.EMA(self.data.close, period=self.p.slow_ma)
        self.trend = bt.indicators.EMA(self.data.close, period=self.p.trend_ma)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.bar_entry = None

    def next(self):

        if self.position and self.bar_entry is not None:
            if len(self) - self.bar_entry >= self.p.max_bars_in_trade:
                self.close()
                return

        if self.position:
            return

        if (
            self.data.close[0] > self.trend[0] and
            self.fast[0] > self.slow[0] and
            40 < self.rsi[0] < 55
        ):
            portfolio_value = self.broker.getvalue()
            risk_cash = portfolio_value * self.p.risk_per_trade

            stop_dist = self.atr[0] * self.p.stop_atr
            if stop_dist <= 0:
                return

            size = risk_cash / stop_dist
            max_size = (portfolio_value * 0.2) / self.data.close[0]
            size = min(size, max_size)

            entry_price = self.data.close[0]
            stop_price = entry_price - stop_dist
            target_price = entry_price + self.atr[0] * self.p.target_atr

            self.buy(size=size)
            self.sell(exectype=bt.Order.Stop, price=stop_price, size=size)
            self.sell(exectype=bt.Order.Limit, price=target_price, size=size)

            self.bar_entry = len(self)

    def notify_trade(self, trade):
        if trade.isclosed:
            print(
                f"Trade Closed | PnL Gross: {trade.pnl:.2f}, "
                f"PnL Net: {trade.pnlcomm:.2f}"
            )


def run_backtest():

    cerebro = bt.Cerebro(stdstats=False)

    df = yf.download(
        "SPY",
        period="730d",
        interval="1h",
        progress=False
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    df.dropna(inplace=True)

    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    cerebro.addstrategy(HybridTrendMeanReversion)

    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addanalyzer(
        bt.analyzers.SharpeRatio,
        _name='sharpe',
        timeframe=bt.TimeFrame.Minutes,
        compression=60
    )
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    print(f"Starting Portfolio: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    strat = results[0]
    final_value = cerebro.broker.getvalue()

    print("\n===== PERFORMANCE =====")
    print(f"Final Portfolio Value: {final_value:.2f}")

    sharpe = strat.analyzers.sharpe.get_analysis()
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 0):.2f}")

    dd = strat.analyzers.drawdown.get_analysis()
    print(f"Max Drawdown: {dd['max']['drawdown']:.2f}%")

    trades = strat.analyzers.trades.get_analysis()
    total = trades.get('total', {}).get('total', 0)

    if total > 0:
        win_rate = trades['won']['total'] / total
        profit_factor = abs(
            trades['won']['pnl']['total'] /
            trades['lost']['pnl']['total']
        ) if trades['lost']['pnl']['total'] != 0 else 0

        print(f"Total Trades: {total}")
        print(f"Win Rate: {win_rate:.2%}")
        print(f"Profit Factor: {profit_factor:.2f}")
    else:
        print("No trades executed.")

    cerebro.plot(style='candlestick', volume=False)


if __name__ == "__main__":
    run_backtest()
