import math
from datetime import datetime
from indicator.Indicators import Indicator
import backtrader as bt
import backtrader.indicators as btind
import pandas as pd
import quantstats as qs
import pyfolio as pf
from util.Util import DataUtil

class TestStrategy(bt.Strategy):
    params = dict(
        short_ma_length=60,
        long_ma_length=120,
        leverage=5,
        tick_size=3,
        risk_per_trade=10
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
        self.date_value = []
        self.my_assets = []

        # 승률 계산을 위함
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

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
                self.log(str(self.date.datetime(0)) + 'SELL EXECUTED, %.3f , QTY = %.3f' % (order.executed.price, order.executed.size))
                self.log("")
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        self.date_value.append(self.date.datetime(0))
        self.my_assets.append(self.broker.getvalue() + self.getposition(self.datas[0]).size * self.low[0])

        if self.order:
            return

        if not self.position:
            if self.short_ma[-1] < self.long_ma[-1] and self.short_ma[0] > self.long_ma[0]:
                qty = self.broker.getvalue() * self.p.risk_per_trade / 100 / self.close[0]
                qty = math.floor(qty / 0.1) * 0.1
                self.order = self.buy(size=qty)
        else:
            if self.short_ma[-1] > self.long_ma[-1] and self.short_ma[0] < self.long_ma[0]:
                self.order = self.sell(size=self.getposition(self.datas[0]).size)

    def stop(self):
        self.winning_rate = self.winning_trading_count * 100 / self.total_trading_count
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getvalue())

        self.log("total trading count %.2f" % self.total_trading_count)
        self.log("winning percent : [%.2f]" % self.winning_rate)
        self.log(f"수익률 : {self.return_rate}%")
        # self.log("수익률 : [%.2f]" % self.return_rate)


if __name__ == '__main__':
    start_date = '2022-12-30 00:00:00'
    end_date = '2023-12-01 08:00:00'

    df = DataUtil.load_candle_data_as_df(DataUtil.CANDLE_DATA_DIR_PATH,
                                         DataUtil.COMPANY_BYBIT,
                                         "LINKUSDT",
                                         DataUtil.CANDLE_TICK_30M)

    filtered_df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    data = bt.feeds.PandasData(dataname=filtered_df, datetime='datetime')

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002) # pinescript는 0.02%이면 0.02를 넣으면 되지만 backtrader는 0.0002를 넣어줘야함.

    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    asset_list = pd.DataFrame({'asset':strat.my_assets}, index=pd.to_datetime(strat.date_value))
    mdd = qs.stats.max_drawdown(asset_list).iloc[0]
    print(f" quanstats's my variable MDD : {mdd * 100:.2f} %")
    mdd = Indicator.calculate_max_draw_down(asset_list)
    print(f" quanstats's my function MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")
    # print(f'\n')
    # print("Result:")
    # return_rate = strat.return_rate
    # cagr = qs.stats.cagr(returns)
    mdd = qs.stats.max_drawdown(returns)
    # sharpe = qs.stats.sharpe(returns)
    # print(f"SHARPE: {sharpe:.2f}")
    # print(f"CAGR: {cagr * 100:.2f} %")
    # print(f"MDD : {mdd * 100:.2f} %")
    # print(f"수익률 : {return_rate:.2f} %")

    # 자세한 결과 html 파일로 저장
    # qs.reports.html(returns, output=f'SMA_MSFT.html', title='result')


