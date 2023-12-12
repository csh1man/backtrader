from datetime import datetime

import backtrader as bt
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from repository.Repository import DB
from util.FileUtil import FileUtil
from config.StrategyConfiguration import TurtleATR


# create strategy
class TestStrategy(bt.Strategy):

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 전략에 필요한 각종 상수 값 획득
        json = FileUtil.load_strategy_config("sample/strategy.json")
        self.turtle_atr = TurtleATR(json)

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

    def next(self):
        position_divider = 0
        target_price1 = 0.0
        target_price1 = 0.0
        target_price1 = 0.0
        target_price1 = 0.0
        target_price5 = 0.0
        self.log("===============" + str(self.data_date.datetime(0)) + "=================")
        if self.rsi[0] < self.turtle_atr.rsi_low or self.rsi[0] > self.turtle_atr.rsi_high:
            position_divider = self.bearish_position_divider
            target_price1 = self.data_close - self.turtle_atr.bearish_constant[0]
            target_price2 = self.data_close - self.turtle_atr.bearish_constant[1]
            target_price3 = self.data_close - self.turtle_atr.bearish_constant[2]
            target_price4 = self.data_close - self.turtle_atr.bearish_constant[3]
            target_price5 = self.data_close - self.turtle_atr.bearish_constant[4]
        self.log("==============================================")


if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    # DB.init_connection_pool(config_path)

    # cerebro 인스턴스 초기화
    cerebro = bt.Cerebro()

    # cerebro에 전략 셋팅
    cerebro.addstrategy(TestStrategy)

    # 백테스팅할 데이터 설정
    df = pd.read_csv('sample/linkusdt_30m.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])

    data = bt.feeds.PandasData(dataname=df, datetime='datetime')
    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value : %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value : %.2f' % cerebro.broker.getvalue())
