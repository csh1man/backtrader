from decimal import Decimal, ROUND_HALF_UP
import backtrader as bt
from util.Util import DataUtil

class StaticStrategy(bt.Strategy):
    params = dict(
        bb_span=80,
        bb_mult=1,
        rsi_length=2,
        rsi_high=90,
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.log(f'data length :{len(self.datas)}')
        self.btc = self.datas[0]
        self.btc_close = self.btc.close
        self.bb = bt.indicators.BollingerBands(self.btc.close, period=self.p.bb_span, devfactor=self.p.bb_mult)
        self.bb_top = self.bb.lines.top
        self.bb_mid = self.bb.lines.mid
        self.bb_bot = self.bb.lines.bot

        self.pair = self.datas[1]
        self.pair_open = self.pair.open
        self.pair_high = self.pair.high
        self.pair_low = self.pair.low
        self.pair_close = self.pair.close
        self.pair_date = self.pair.datetime
        self.pair_rsi = bt.ind.RSI_Safe(self.pair_close, period=self.p.rsi_length)

        # 0 -> [0, 5)
        # 1 -> [5, 10)
        # 2 -> [10, 20)
        # 3 -> [20, 30)
        # 4 -> [30, 40)
        # 5 -> [40, 50)
        # 6 -> [50, 60)
        # 7 -> [60, 70)
        # 8 -> [70, 80)
        # 9 -> [80, 90)
        # 10 -> [90, 100)
        self.under = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def next(self):
        if self.bb_bot[0] < self.btc_close[0] < self.bb_top[0]:
            if 0 < self.pair_rsi[0] < 5:
                self.under[0] += 1
            elif 5 <= self.pair_rsi[0] < 10:
                self.under[1] += 1
            elif 10 <= self.pair_rsi[0] < 20:
                self.under[2] += 1
            elif 20 <= self.pair_rsi[0] < 30:
                self.under[3] += 1
            elif 30 <= self.pair_rsi[0] < 40:
                self.under[4] += 1
            elif 40 <= self.pair_rsi[0] < 50:
                self.under[5] += 1
            elif 50 <= self.pair_rsi[0] < 60:
                self.under[6] += 1
            elif 60 <= self.pair_rsi[0] < 70:
                self.under[7] += 1
            elif 70 <= self.pair_rsi[0] < 80:
                self.under[8] += 1
            elif 80 <= self.pair_rsi[0] < 90:
                self.under[9] += 1
            elif 90 <= self.pair_rsi[0] < 100:
                self.under[10] += 1

    def stop(self):
        self.log(f'0 ~ 5 : {self.under[0]}')
        self.log(f'5 ~ 10 : {self.under[1]}')
        self.log(f'10 ~ 20 : {self.under[2]}')
        self.log(f'20 ~ 30 : {self.under[3]}')
        self.log(f'30 ~ 40 : {self.under[4]}')
        self.log(f'40 ~ 50 : {self.under[5]}')
        self.log(f'50 ~ 60 : {self.under[6]}')
        self.log(f'60 ~ 70 : {self.under[7]}')
        self.log(f'70 ~ 80 : {self.under[8]}')
        self.log(f'80 ~ 90 : {self.under[9]}')
        self.log(f'90 ~ 100 : {self.under[10]}')


if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    start_date = '2020-01-01 00:00:00'
    end_date = '2024-04-11 00:00:00'

    pairs = {
        'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
        'XRPUSDT': DataUtil.CANDLE_TICK_30M
    }

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=100)
    cerebro.addstrategy(StaticStrategy)

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    results = cerebro.run()