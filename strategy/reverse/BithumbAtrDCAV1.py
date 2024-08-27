import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'KRW-BTC' : DataUtil.CANDLE_TICK_30M,
    'KRW-PEPE': DataUtil.CANDLE_TICK_30M,
}


class BithumbAtrDCAV1(bt.Strategy):
    params=dict(
        bb_length=20,
        bb_mult=1.0,
        atr_length={
            'KRW-BTC': 50,
            'KRW-PEPE':50
        },
        atr_avg_length={
            'KRW-BTC': 200,
            'KRW-PEPE':200
        },
        bull_constants={
            'KRW-PEPE': [Decimal('0.5'), Decimal('0.7'), Decimal('0.9'), Decimal('1.2'), Decimal('1.5')]
        },
        def_constants={
            'KRW-PEPE': [Decimal('1.5'), Decimal('2'), Decimal('3'), Decimal('4'), Decimal('5')]
        },
        bear_constants={
            'KRW-PEPE': [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')]
        }
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
        self.atrs = []
        self.bb = []
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []

        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.SmoothedMovingAverage(tr, period=self.p.atr_length[name])
            atr = bt.indicators.MovingAverageSimple(atr, period=self.p.atr_avg_length[name])
            self.atrs.append(atr)

        self.bb = bt.indicators.BollingerBands(self.closes[0], period=self.p.bb_length, devfactor=self.p.bb_mult)
        self.bb_top = self.bb.lines.top
        self.bb_mid = self.bb.lines.mid
        self.bb_bot = self.bb.lines.bot

    def next(self):
        constants = None
        for i in range(1, len(self.pairs)):
            name = self.names[i]
            if self.bb_bot[0] <= self.closes[0][0] and self.bb_top[0]:
                constants = self.p.def_constants[name]
            elif self.closes[0][0] < self.bb_bot[0]:
                constants = self.p.bear_constants[name]
            prices = []
            for j in range(0, len(constants)):
                price = DataUtil.convert_to_decimal(self.closes[i][0]) - constants[j] * DataUtil.convert_to_decimal(self.atrs[i][0])
                price = int(price / DataUtil.get_bithumb_tick_size(price)) * DataUtil.get_bithumb_tick_size(price)
                prices.append(price)
            for j in range(0, len(prices)):
                self.log(f'{self.dates[i].datetime(0)} => {prices[j]}')

if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(BithumbAtrDCAV1)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002, leverage=5)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BITHUMB, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    results = cerebro.run()
