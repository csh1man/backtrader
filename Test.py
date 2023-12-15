from datetime import datetime
from indicator.Indicators import Indicator
import backtrader as bt
import backtrader.indicators as btind
import pandas as pd
import quantstats as qs
import pyfolio as pf


class TestStrategy(bt.Strategy):
    params = dict(
        short_ma_length=60,
        long_ma_length=120
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.date = self.datas[0].datetime
        self.percent = Indicator.get_percent(self.open, self.low)
        self.short_ma = btind.SimpleMovingAverage(self.close, period=self.p.short_ma_length)
        self.long_ma = btind.SimpleMovingAverage(self.close, period=self.p.long_ma_length)

        # monitoring variable
        self.order = None
        self.trading_count = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(str(self.date.datetime(0)) + 'BUY EXECUTED, %.3f' % order.executed.price)
            elif order.issell():
                self.log(str(self.date.datetime(0)) + 'SELL EXECUTED, %.3f' % order.executed.price)
                self.log("")

                self.trading_count = self.trading_count + 1

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        if self.order:
            return

        if self.date.datetime(0) < datetime(2023, 1, 1):
            return

        if self.date.datetime(0) > datetime(2023, 11, 29):
            return

        if not self.position:
            if self.short_ma[-1] < self.long_ma[-1] and self.short_ma[0] > self.long_ma[0]:
                self.order = self.buy(size=3)
        else:
            if self.short_ma[-1] > self.long_ma[-1] and self.short_ma[0] < self.long_ma[0]:
                self.order = self.sell(size=3)

    def stop(self):
        self.log("total trading count : [" + str(self.trading_count) + "]")


if __name__ == '__main__':
    start_date = '2023-01-01'
    end_date = '2023-11-30'

    df = pd.read_csv('sample/linkusdt_30m.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    # filtered_df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]

    data = bt.feeds.PandasData(dataname=df, datetime='datetime')

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002) # pinescript는 0.02%이면 0.02를 넣으면 되지만 backtrader는 0.0002를 넣어줘야함.

    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print(f'\n')
    print("Result:")
    cagr = qs.stats.cagr(returns)
    mdd = qs.stats.max_drawdown(returns)
    sharpe = qs.stats.sharpe(returns)
    print(f"SHARPE: {sharpe:.2f}")
    print(f"CAGR: {cagr * 100:.2f} %")
    print(f"MDD : {mdd * 100:.2f} %")

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    benchmark_data = pd.Series(data=cerebro.datas[0].close.plot())
    qs.reports.html(returns, benchmark=benchmark_data, output=f'SMA_MSFT.html', title='result')