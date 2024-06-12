import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal, ROUND_HALF_UP
import quantstats as qs
import pandas as pd
import matplotlib.pyplot as plt
import pyfolio as pf
from indicator.Indicators import Indicator
pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_1DAY,
    '1000BONKUSDT': DataUtil.CANDLE_TICK_1HOUR,
}


class MultiAtrConstantStrategy(bt.Strategy):
    params = dict(
        leverage=Decimal('10'),
        risks=[
            Decimal('1'), Decimal('1'), Decimal('1'),
            Decimal('2'), Decimal('2'), Decimal('2'), Decimal('2'),
            Decimal('3'), Decimal('3'), Decimal('3')
        ],
        addRisks=[
            Decimal('2'), Decimal('2'), Decimal('2'),
            Decimal('3'), Decimal('3'), Decimal('3'), Decimal('3'),
            Decimal('4'), Decimal('4'), Decimal('4')
        ],
        atr_length=150,
        atr_avg_length=50,
        bearish_atr_constants={
            '1000BONKUSDT': [
                                Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0'),
                                Decimal('12.0'), Decimal('14.0'), Decimal('16.0'), Decimal('18.0'), Decimal('20.0')
                            ]
        },
        default_atr_constants={
            '1000BONKUSDT': [
                Decimal('1.5'), Decimal('2.0'), Decimal('2.5'), Decimal('3.0'), Decimal('3.5'),
                Decimal('4.0'), Decimal('4.5'), Decimal('5.0'), Decimal('5.5'), Decimal('6.0')
            ]
        },
        exitPercent={
            '1000BONKUSDT' : Decimal('0.5'),
        }
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.btc = self.datas[0]
        self.btc_open = self.btc.open
        self.btc_high = self.btc.high
        self.btc_low = self.btc.low
        self.btc_close = self.btc.close
        self.btc_date = self.btc.datetime

        self.pairs = []
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])

        self.pairs_open = []
        self.pairs_high = []
        self.pairs_low = []
        self.pairs_close = []
        self.pairs_date = []

        for i in range(0, len(self.pairs)):
            self.pairs_open.append(self.pairs[i].open)
            self.pairs_high.append(self.pairs[i].high)
            self.pairs_low.append(self.pairs[i].low)
            self.pairs_close.append(self.pairs[i].close)
            self.pairs_date.append(self.pairs[i].datetime)

    def next(self):
        self.log(f'{self.pairs[0]._name} date1 : {self.pairs_date[0].datetime(0)}, date2 : {self.pairs_date[0].datetime(-1)} <=> {self.pairs[1]._name} date : {self.pairs_date[1].datetime(0)}')


if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)  # 초기 시드 설정
    cerebro.broker.setcommission(0.0005, leverage=1)  # 수수료 설정
    cerebro.addstrategy(MultiAtrConstantStrategy)

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)


    cerebro.run()

