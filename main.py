from datetime import datetime

import backtrader as bt
import pandas as pd
from util.FileUtil import FileUtil
from config.StrategyConfiguration import TurtleATR
from indicator.Indicators import Indicator


# create strategy
class TestStrategy(bt.Strategy):

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 전략에 필요한 각종 상수 값 획득
        json = FileUtil.load_strategy_config("sample/strategy.json")
        self.turtle_atr = TurtleATR(json)
        self.trade_count = 0
        # 캔들 데이터 파싱
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_volume = self.datas[0].volume
        self.data_date = self.datas[0].datetime
        self.data_percent = (self.data_close - self.data_open) * 100 / self.data_open

        # 각종 지표 설정
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.turtle_atr.rsi_length)
        self.higher_band = bt.ind.Highest(self.data.high(-1), period=self.turtle_atr.higher_band_length)
        self.atr = bt.indicators.AverageTrueRange(period=self.turtle_atr.atr_length)
        self.atr_avg = bt.indicators.SimpleMovingAverage(self.atr, period=self.turtle_atr.atr_avg_length)
        self.bearish_position_divider = self.turtle_atr.dividers[0]
        self.basic_position_divider = self.turtle_atr.dividers[1]
        self.bullish_position_divider = self.turtle_atr.dividers[2]
        self.risk_per_trade = self.turtle_atr.risk_per_trade
        self.ma1 = bt.indicators.SimpleMovingAverage(self.data_close, period=self.turtle_atr.maLengths[0])
        self.ma2 = bt.indicators.SimpleMovingAverage(self.data_close, period=self.turtle_atr.maLengths[1])

        #주문을 저장해놓을 변수를 생성한다
        self.orders = []

    def notify_order(self, order):
        if order.status in [bt.Order.Completed]:
            self.log(self.data_date.datetime(0))
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}')
            elif order.issell():
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}')

    def next(self):
        # 지정가 주문 들어가지 않은 것들에 대한 모든 주문 취소
        for order in self.orders:
            self.cancel(order)
        self.orders = []

        # 종료 조건에 만족하는 상황이면 종료시킴.
        if self.ma1[0] < self.ma2[0]:
            size = self.getposition(self.datas[0]).size
            if size > 0:
                self.sell(data=self.datas[0], size=size)
                self.trade_count = self.trade_count + 1

        target_price1 = None
        target_price2 = None
        target_price3 = None
        target_price4 = None
        target_price5 = None
        position_divider = None
        if self.rsi[0] < self.turtle_atr.rsi_low or self.rsi[0] > self.turtle_atr.rsi_high:
            position_divider = self.bearish_position_divider
            target_price1 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[0], 3)
            target_price2 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[1], 3)
            target_price3 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[2], 3)
            target_price4 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[3], 3)
            target_price5 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[4], 3)

        elif Indicator.get_body_length(self.data_low[0], self.data_close[0]) > \
                Indicator.get_body_length(self.data_low[-1], self.data_close[-1]) * self.turtle_atr.body_length_constant:
            position_divider = self.bearish_position_divider
            target_price1 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[0], 3)
            target_price2 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[1], 3)
            target_price3 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[2], 3)
            target_price4 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[3], 3)
            target_price5 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.bearish_constant[4], 3)

        elif self.higher_band[0] < self.data_close[0]:
            position_divider = self.bullish_position_divider
            target_price1 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[0] / 2, 3)
            target_price2 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[1] / 2, 3)
            target_price3 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[2] / 2, 3)
            target_price4 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[3] / 2, 3)
            target_price5 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[4] / 2, 3)

        else:
            position_divider = self.basic_position_divider
            target_price1 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[0], 3)
            target_price2 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[1], 3)
            target_price3 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[2], 3)
            target_price4 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[3], 3)
            target_price5 = round(self.data_close[0] - self.atr_avg[0] * self.turtle_atr.basic_constant[4], 3)

        # 현재 자산 획득
        equity = self.broker.getvalue()

        # 진입하고자 하는 포지션 사이즈 획득
        position_size1 = equity * self.turtle_atr.risk_per_trade[0] / 100 / target_price1 / position_divider
        position_size2 = equity * self.turtle_atr.risk_per_trade[1] / 100 / target_price2 / position_divider
        position_size3 = equity * self.turtle_atr.risk_per_trade[2] / 100 / target_price3 / position_divider
        position_size4 = equity * self.turtle_atr.risk_per_trade[3] / 100 / target_price4 / position_divider
        position_size5 = equity * self.turtle_atr.risk_per_trade[4] / 100 / target_price5 / position_divider

        if position_size1 > 0 and position_size2 > 0 and position_size3 > 0 \
                and position_size4 > 0 and position_size5 > 0 and self.data_date.datetime(0) >= datetime(2023, 1, 1, 9):
            order1 = self.buy(exectype=bt.Order.Limit, price=target_price1, size=position_size1)
            order2 = self.buy(exectype=bt.Order.Limit, price=target_price2, size=position_size2)
            order3 = self.buy(exectype=bt.Order.Limit, price=target_price3, size=position_size3)
            order4 = self.buy(exectype=bt.Order.Limit, price=target_price4, size=position_size4)
            order5 = self.buy(exectype=bt.Order.Limit, price=target_price5, size=position_size5)

            self.orders.append(order1)
            self.orders.append(order2)
            self.orders.append(order3)
            self.orders.append(order4)
            self.orders.append(order5)

    def start(self):
        self.start_val = self.broker.getvalue()

    def stop(self):
        end_val = self.broker.getvalue()
        pnl = end_val - self.start_val
        returns = (end_val / self.start_val - 1.0) * 100
        self.log("승률 : [" + str(returns) + " %]")
        self.log("청산된 트레이드 전체 : " + str(self.trade_count))


if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    # DB.init_connection_pool(config_path)

    # cerebro 인스턴스 초기화
    cerebro = bt.Cerebro()
    cerebro.broker.setcommission(commission=0.02)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')

    # cerebro에 전략 셋팅
    cerebro.addstrategy(TestStrategy)

    # 백테스팅할 데이터 설정
    df = pd.read_csv('sample/linkusdt_30m.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])

    data = bt.feeds.PandasData(dataname=df, datetime='datetime')
    cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석 추가

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')

    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    # cerebro.broker.setcash(100000.0)
    #
    # print('Starting Portfolio Value : %.2f' % cerebro.broker.getvalue())
    #
    # results = cerebro.run()
    # strat = results[0]
    # drawdown = strat.analyzers.dd.get_analysis()
    #
    # print("MDD : " + str(drawdown))
    # print('Final Portfolio Value : %.2f' % cerebro.broker.getvalue())
