from datetime import datetime

import backtrader as bt
import pandas as pd
import quantstats as qs
from util.FileUtil import FileUtil
from config.StrategyConfiguration import TurtleATR
from indicator.Indicators import Indicator


class TestStrategy(bt.Strategy):
    def log(self, txt):
        print(txt)

    def __init__(self):
        # 지표 설정에 필요한 수치 획득
        json = FileUtil.load_strategy_config("sample/strategy.json")
        self.turtle_atr = TurtleATR(json)
        self.min = 100
        self.min_date = None
        # 각종 지표 설정
        self.data_date = self.datas[0].datetime
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_close = self.datas[0].close
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.turtle_atr.rsi_length)
        self.data_percent = (self.data_close - self.data_open) * 100 / self.data_open

    def next(self):
        if self.data_percent[0] < self.min and self.data_date.datetime(0) > datetime(2023, 1, 1, 9):
            self.min_date = self.data_date.datetime(0)
            self.min = self.data_percent[0]

    def stop(self):
        self.log("최대 마이너스 폭 : " + str(self.min) + " <-> 시간 :[" + str(self.min_date) + "]")

if __name__ == '__main__':
    # 백테스팅할 데이터 설정
    df = pd.read_csv('sample/linkusdt_30m.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')

    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)

    results = cerebro.run()
    print(results[0].number)