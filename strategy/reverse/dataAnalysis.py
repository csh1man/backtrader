from util.Util import DataUtil
import backtrader as bt
from collections import OrderedDict
import pandas as pd
pairs = {
    'BTCUSDT' : DataUtil.CANDLE_TICK_30M,
    'XRPUSDT' : DataUtil.CANDLE_TICK_30M
}


class DataAnalysis(bt.Strategy):
    params = dict(
        btc_bb_span=100,
        btc_bb_mult=1.0
    )

    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        self.percents = {}
        self.ol_percents=  {}
        self.pairs = []
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])

        self.pair_open = []
        self.pair_high = []
        self.pair_low = []
        self.pair_close = []
        self.pair_date = []

        for i in range(0, len(self.pairs)):
            self.pair_open.append(self.pairs[i].open)
            self.pair_high.append(self.pairs[i].high)
            self.pair_low.append(self.pairs[i].low)
            self.pair_close.append(self.pairs[i].close)
            self.pair_date.append(self.pairs[i].datetime)

        self.bb = bt.indicators.BollingerBands(self.pair_close[0], period=self.p.btc_bb_span, devfactor=self.p.btc_bb_mult)
        self.bb_top = self.bb.lines.top
        self.bb_mid = self.bb.lines.mid
        self.bb_bot = self.bb.lines.bot

    def next(self):
        if self.pair_close[0][0] > self.bb_top[0]:
            percent = (self.pair_close[1][0] - self.pair_open[1][0]) * 100 / self.pair_close[1][0]
            ol_percent = (self.pair_low[1][0] - self.pair_open[1][0]) * 100 / self.pair_low[1][0]
            self.percents[self.pair_date[1].datetime(0)] = percent
            self.ol_percents[self.pair_date[1].datetime(0)] = ol_percent

    def stop(self):
        self.percents = OrderedDict(sorted(self.percents.items(), key=lambda item: item[1]))
        self.ol_percents = OrderedDict(sorted(self.ol_percents.items(), key=lambda item: item[1]))
        for key, value in self.ol_percents.items():
            self.log(f'{key} => {value}% , {self.percents[key]}%')


if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)  # 초기 시드 설정
    cerebro.broker.setcommission(0.0002, leverage=10)  # 수수료 설정
    cerebro.addstrategy(DataAnalysis)

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    cerebro.run()