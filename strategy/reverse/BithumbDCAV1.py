import backtrader as bt
import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal

'''
백테스팅할 데이터 목록 초기화
'''
pairs = {
    "KRW-PEPE": DataUtils.CANDLE_TICK_30M
}

class BithumbDcaV1(bt.Strategy):
    params=dict(
        risks=[Decimal('2'), Decimal('2'), Decimal('2'), Decimal('2'), Decimal('2')],
        add_risks=[Decimal('3'), Decimal('3'), Decimal('3'), Decimal('3'), Decimal('3')],
        bb_length=80,
        bb_mult=1.0,
        atr_length=50,
        atr_avg_length=200,
        rsi_length=2,
        rsi_low=50,
        exit_percent=Decimal('0.7'),
        add_exit_percent=Decimal('1.3'),
        bull_consts=[Decimal('0.5'), Decimal('0.7'), Decimal('0.9'), Decimal('1'), Decimal('1.5')],
        def_consts=[Decimal('1.5'), Decimal('2'), Decimal('3'), Decimal('4'), Decimal('5')],
        bear_consts=[Decimal('1'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2')],
    )

    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.rsis = []
        self.tr = []

        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.datas)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            self.tr.append(tr)

    def next(self):
        for i in range(0, len(self.pairs)):
            self.log(f'{self.dates[i].datetime(0)} => {self.tr[i][0]}')


if __name__ == '__main__':
    data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(BithumbDcaV1)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002, leverage=5)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BITHUMB, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    results = cerebro.run()