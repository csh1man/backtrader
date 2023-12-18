from indicator.Indicators import Indicator
from util.FileUtil import FileUtil
from config.StrategyConfiguration import TurtleATR
import backtrader as bt
import backtrader.indicators as btind
import pandas as pd
import quantstats as qs
import math
import datetime


class ATRTurtleGridStrategy(bt.Strategy):
    def log(self, txt):
        print(txt)

    def __init__(self):
        # 지표관련 데이터 획득
        config_json = FileUtil.load_strategy_config("sample/strategy.json")
        self.indicator_value = TurtleATR(config_json)
        
        # 캔들 데이터 초기화
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.volume = self.datas[0].volume
        self.date = self.datas[0].datetime
        self.orders = []

        # 트레이딩 기본 데이터 초기화
        self.risk_per_trade = self.indicator_value.risk_per_trade
        self.bearish_constant = self.indicator_value.bearish_constant
        self.basic_constant = self.indicator_value.basic_constant

        # 지표 데이터 초기화
        self.atr = bt.indicators.AverageTrueRange(period=self.indicator_value.atr_length)
        self.atr = bt.indicators.MovingAverageSimple(self.atr, period=self.indicator_value.atr_avg_length)
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.indicator_value.rsi_length)
        self.ma1 = bt.indicators.MovingAverageSimple(self.close, period=self.indicator_value.maLengths[0])
        self.ma2 = bt.indicators.MovingAverageSimple(self.close, period=self.indicator_value.maLengths[1])

    def notify_order(self, order):
        if order.status in [bt.Order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, date : {self.date.datetime(0)}, Price: {order.executed.price}, size : {order.executed.size}')
            elif order.issell():
                self.log(
                    f'SELL EXECUTED, date : {self.date.datetime(0)}, Price: {order.executed.price}, size : {order.executed.size}')

    def next(self):
        # 미체결 지정가 주문 전체 취소
        for order in self.orders:
            self.cancel(order)
        self.orders = []

        # 체결된 지정가 주문이 있을 경우 이평선 조건에 맞을 시 전체 종료.
        if self.ma1[0] < self.ma2[0]:
            size = self.getposition(self.datas[0]).size
            if size > 0:
                self.sell(data=self.datas[0], size=size)

        # ATR을 이용해서 지정가격 5개를 생성하고 지정가 주문 생성
        target_prices = []
        if self.indicator_value.rsi_low < self.rsi[0] and self.rsi[0] > self.indicator_value.rsi_high:
            for constant in self.bearish_constant:
                price = self.close[0] - self.atr[0] * constant
                price = round(price / 0.001) * 0.001
                target_prices.append(price)

        elif Indicator.get_body_length(self.open[0], self.close[0]) > Indicator.get_body_length(self.open[0], self.close[0]) * self.indicator_value.body_length_constant:
            for constant in self.bearish_constant:
                price = self.close[0] - self.atr[0] * constant
                price = round(price / 0.001) * 0.001
                target_prices.append(price)
        else:
            for constant in self.basic_constant:
                price = self.close[0] - self.atr[0] * constant
                price = round(price / 0.001) * 0.001
                target_prices.append(price)

        position_sizes = []
        for i in range(0, len(target_prices)):
            price = target_prices[i]
            risk_per_trade = self.risk_per_trade[i]
            position_size = self.broker.getvalue() * risk_per_trade / 100 / price
            position_size = math.floor(position_size / 0.1) * 0.1
            position_sizes.append(position_size)

        for i in range(0, len(target_prices)):
            price = target_prices[i]
            size = position_sizes[i]
            if size > 0:
                order = self.buy(exectype=bt.Order.Limit, price=price, size=size)
                self.orders.append(order)


if __name__ == '__main__':

    start_date = '2022-12-31 04:30:00'
    end_date = '2023-12-01 08:00:00'

    df = pd.read_csv('sample/linkusdt_30m.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    filtered_df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    data = bt.feeds.PandasData(dataname=filtered_df, datetime='datetime')

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002)

    cerebro.adddata(data)
    cerebro.addstrategy(ATRTurtleGridStrategy)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())