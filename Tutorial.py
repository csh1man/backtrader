import datetime
import math

import pandas as pd
import quantstats as qs
import backtrader as bt
from util.Util import DataUtil
from repository.Repository import DB
from indicator.Indicators import Indicator


class TutorialStrategy(bt.Strategy):
    params = (
        ("ma_length", 60),
        ("atr_length", 2),
        ("atr_constant", 1.5),
        ("risk_per_trade", 10),
        ("leverage", 3)
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.db = DB()
        self.size_info = self.db.get_currency_info(DataUtil.COMPANY_BYBIT, "BTCUSDT")
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.date = self.datas[0].datetime
        self.atr = bt.indicators.AverageTrueRange(period=self.p.atr_length)
        self.ma = bt.ind.SimpleMovingAverage(self.close, period=self.p.ma_length)

        # 데이터 추적용
        self.order = None
        self.stop_price = None

        # 자산 추적용
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0
        self.date_value = []
        self.my_assets = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY ! "
                         f"date : {self.date.datetime(0)}, price : {order.executed.price},"
                         f"size : {order.executed.size}"
                         f"comm : {order.executed.comm}")
            elif order.issell():
                self.log(f"SELL ! "
                         f"date : {self.date.datetime(0)}, price : {order.executed.price}"
                         f" size : {order.executed.size}"
                         f" comm : {order.executed.comm}"
                         f" my asset : {self.broker.getvalue() + self.getposition(self.datas[0]).size * self.low[0]}")
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

        self.order = None

    def next(self):
        self.date_value.append(self.date.datetime(0))
        self.my_assets.append(self.broker.getvalue() + self.getposition(self.datas[0]).size * self.low[0])

        # 제출은 되었지만 미체결인 상태면 넘어감.
        if self.order:
            return

        if not self.position:
            if self.close[-1] < self.ma[-1] and self.close[0] > self.ma[0]:
                self.stop_price = self.close[0] - self.atr[0] * self.p.atr_constant
                diff_percent = Indicator.get_percent(self.close[0], self.stop_price)
                leverage = Indicator.get_leverage(self.p.risk_per_trade, diff_percent)
                position_size = leverage * self.broker.getvalue() * self.p.risk_per_trade / 100 / self.close[0]
                position_size = math.floor(position_size / self.size_info.step_size) * self.size_info.step_size
                self.buy(size=position_size)

        else:
            if self.close[-1] > self.ma[-1] and self.close[0] < self.ma[0]:
                self.sell(size=self.getposition().size)
            elif self.close[0] < self.stop_price:
                self.sell(size=self.getposition().size)
                self.stop_price = None

    def stop(self):
        self.winning_rate = self.winning_trading_count * 100 / self.total_trading_count
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getvalue())

        self.log(f"전체 트레이딩 수 : {self.total_trading_count}번")
        self.log(f"승률 : {self.winning_rate :.2f}%")
        self.log(f"수익률 : {self.return_rate:.2f}%")


if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    DB.init_connection_pool(config_path)

    # backtesting할 데이터 추출
    df = DataUtil.load_candle_data_as_df(DataUtil.CANDLE_DATA_DIR_PATH, DataUtil.COMPANY_BYBIT,
                                         "BTCUSDT", DataUtil.CANDLE_TICK_1DAY)

    df = DataUtil.get_candle_data_in_scape(df, "2020-05-01", "2023-09-30")
    # 특정 날짜 만큼만 추출
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.0002, leverage=1)
    cerebro.adddata(data)
    cerebro.addstrategy(TutorialStrategy)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    mdd = Indicator.calculate_max_draw_down(asset_list)
    print(f"my function MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f"quanstats's returns MDD : {mdd * 100:.2f} %")
    # qs.reports.html(returns, output=f'SMA_MSFT.html', title='result')

