import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal, ROUND_HALF_UP
import quantstats as qs
import pyfolio as pf
import pandas as pd
from indicator.Indicators import Indicator


class MultiRsiWithBtcBB(bt.Strategy):
    params = dict(
        leverage=Decimal('5'),
        risks=[Decimal('2'), Decimal('2'), Decimal('2'), Decimal('4'), Decimal('8')],
        bb_span=80,
        bb_mult=1,
        rsi_length=2,
        rsi_high=90,
        bull_percents=[
            [Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')], # solusdt
            [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')], # 1000bonkusdt
        ],
        bear_percents=[Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
        default_percents=[Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
        tick_size=[
            Decimal('0.10'),
            Decimal('0.01'),
            Decimal('0.00001'),
            Decimal('0.0001')
        ],
        step_size=[Decimal('0.01'), Decimal('0.1'), Decimal('1'), Decimal('1')]
    )

    def log(self,txt=None):
        print(txt)

    def __init__(self):
        for data in self.p.bull_percents:
            self.log(f'{data}')


if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    start_date = '2023-01-01 00:00:00'
    end_date = '2024-04-16 00:00:00'

    pairs = {
        'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
        '1000BONKUSDT': DataUtil.CANDLE_TICK_30M,
    }

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=5)
    cerebro.addstrategy(MultiRsiWithBtcBB)

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')

        cerebro.adddata(data, name=pair)


    results = cerebro.run()