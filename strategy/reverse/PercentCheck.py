import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal

company = DataUtils.COMPANY_BINANCE
leverage = 3

pairs = {
    'ZECUSDT': DataUtils.CANDLE_TICK_1HOUR,
}
class PercentCheck(bt.Strategy):
    params=dict(
        log=True,
        bb_length={
            'STXUSDT': 30,
            'ZECUSDT': 30,
        },
        bb_mult={
            'STXUSDT': 0.5,
            'ZECUSDT': 0.5,
        }
    )

    def log(self, txt):
        if self.p.log:
            print(f'{txt}')

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.r = []
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []

        self.top_percents = []
        self.mid_percents = []
        self.bot_percents = []

        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_length[name], devfactor=self.p.bb_mult[name])
            self.bb_top.append(bb.lines.top)
            self.bb_mid.append(bb.lines.mid)
            self.bb_bot.append(bb.lines.bot)

    def next(self):
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            date = self.dates[i].datetime(0)
            candle_percent = (self.closes[i][0]-self.opens[i][0]) * 100  / self.opens[i][0]
            if self.closes[i][-1] >= self.bb_top[i][-1]:
                self.top_percents.append((date, candle_percent))
            elif self.bb_bot[i][-1] <= self.closes[i][-1] < self.bb_top[i][-1]:
                self.mid_percents.append((date, candle_percent))
            else:
                self.bot_percents.append((date, candle_percent))


    def stop(self):
        sorted_top_percents = sorted(self.top_percents, key=lambda x: x[1])
        sorted_mid_percents = sorted(self.mid_percents, key=lambda x: x[1])
        sorted_bot_percents = sorted(self.bot_percents, key=lambda x: x[1])
        self.log(f"top percents length : [{len(sorted_top_percents)}]")
        for key, value in sorted_top_percents[:51]:
            self.log(f'{key} -> {value}%')
        self.log("")

        self.log(f"mid percents length : [{len(sorted_mid_percents)}]")
        for key, value in sorted_mid_percents[:51]:
            self.log(f'{key} -> {value}%')
        self.log("")

        self.log(f"bot percents length : [{len(sorted_bot_percents)}]")
        for key, value in sorted_bot_percents[:51]:
            self.log(f'{key} -> {value}%')

if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(PercentCheck)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.001, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, company, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    before_balance = cerebro.broker.getvalue()
    print('Before Portfolio Value: %.2f' % before_balance)
    results = cerebro.run()
    strat = results[0]
    after_balance = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % after_balance)