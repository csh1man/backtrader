import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal, ROUND_HALF_UP
from indicator.Indicators import Indicator
import quantstats as qs
import pandas as pd
import matplotlib.pyplot as plt
import pyfolio as pf
from indicator.Indicators import Indicator

pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
    '1000BONKUSDT': DataUtil.CANDLE_TICK_30M,
    # '1000PEPEUSDT': DataUtil.CANDLE_TICK_30M,
    # 'TIAUSDT': DataUtil.CANDLE_TICK_30M,
    # 'SEIUSDT': DataUtil.CANDLE_TICK_30M,
}

class MultiRsiWithBtcBB(bt.Strategy):
    # 환경설정 파라미터값 선언
    params = dict(
        leverage=Decimal('5'),
        risks=[
            Decimal('1'),  # 1차 진입%
            Decimal('1'),  # 2차 진입%
            Decimal('2'),  # 3차 진입%
            Decimal('4'),  # 4차 진입%
            Decimal('4')  # 5차 진입%
        ],
        bb_span=80,
        bb_mult=1,
        rsi_length=2,
        rsi_high=90,

        bull_percents = {
            '1000BONKUSDT': [Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
            '1000PEPEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0')],
            'SEIUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0')],
            'TIAUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0')],
        },

        bear_percents = {
            '1000BONKUSDT': [Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
            '1000PEPEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0')],
            'SEIUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0')],
            'TIAUSDT': [Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
        },

        default_percents = {
            '1000BONKUSDT': [Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
            '1000PEPEUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('9.0'), Decimal('11.0')],
            'SEIUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('9.0'), Decimal('11.0')],
            'TIAUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
        },

        tick_size = {
            '1000BONKUSDT': Decimal('0.0000010'),
            '1000PEPEUSDT': Decimal('0.0000001'),
            'SEIUSDT': Decimal('0.00010'),
            'TIAUSDT': Decimal('0.001'),
        },
        step_size={
            '1000BONKUSDT': Decimal('100'),
            '1000PEPEUSDT': Decimal('100'),
            'SEIUSDT': Decimal('1'),
            'TIAUSDT': Decimal('0.1'),
        },
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        try:
            # data feeds 초기화
            self.btc = self.datas[0]

            # 비트코인 정보초기화
            self.btc_open = self.btc.open
            self.btc_high = self.btc.high
            self.btc_low = self.btc.low
            self.btc_close = self.btc.close
            self.btc_date = self.btc.datetime

            self.bb = bt.indicators.BollingerBands(self.btc.close, period=self.p.bb_span, devfactor=self.p.bb_mult)
            self.bb_top = self.bb.lines.top
            self.bb_mid = self.bb.lines.mid
            self.bb_bot = self.bb.lines.bot

            # 멀티페어 페어 초기화
            self.pairs = []
            for i in range(0, len(self.datas)):
                self.pairs.append(self.datas[i])

            self.pair_open = []
            for i in range(0, len(self.pairs)):
                self.pair_open.append(self.pairs[i].open)

            self.pair_high = []
            for i in range(0, len(self.pairs)):
                self.pair_high.append(self.pairs[i].high)

            self.pair_low = []
            for i in range(0, len(self.pairs)):
                self.pair_low.append(self.pairs[i].low)

            self.pair_close = []
            for i in range(0, len(self.pairs)):
                self.pair_close.append(self.pairs[i].close)

            self.pair_date = []
            for i in range(0, len(self.pairs)):
                self.pair_date.append(self.pairs[i].datetime)

            self.pair_rsi = []
            for i in range(0, len(self.pairs)):
                rsi = bt.ind.RSI_Safe(self.pair_close[i], period=self.p.rsi_length)
                self.pair_rsi.append(rsi)

            self.price_list = []

        except Exception as e:
            raise (e)

    def next(self):
        try:
            for i in range(1, len(self.pairs)):
                open_close_percent = (self.pair_close[i][0] - self.pair_open[i][0])  * 100 / self.pair_open[i][0]
                if open_close_percent < 0:
                    open_low_percent = (self.pair_low[i][0] - self.pair_open[i][0]) * 100 / self.pair_open[i][0]
                    self.price_list.append([self.pair_date[i].datetime(0), open_close_percent, open_low_percent])
        except:
            raise


if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    start_date = '2022-04-01 00:00:00'
    end_date = '2024-04-17 00:00:00'

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=5)
    cerebro.addstrategy(MultiRsiWithBtcBB)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        df = DataUtil.get_candle_data_in_scape(df, start_date, end_date)
        # df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')

        cerebro.adddata(data, name=pair)

    results = cerebro.run()
    strat = results[0]
    pair_data = strat.price_list
    pair_dat = sorted(pair_data, key=lambda x: x[1], reverse=True)
    for date, price1, price2 in pair_dat:
        print(f'{date} -> {price1}% <-> {price2}%')
