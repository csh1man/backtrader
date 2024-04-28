import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_2HOUR,
    # 'ETHUSDT': DataUtil.CANDLE_TICK_2HOUR,
    # 'SOLUSDT': DataUtil.CANDLE_TICK_2HOUR,
    # 'BCHUSDT': DataUtil.CANDLE_TICK_2HOUR
}

tick_size = {
    'BTCUSDT': Decimal('0.1'),
    'ETHUSDT': Decimal('0.01'),
    'SOLUSDT': Decimal('0.01'),
    'BCHUSDT': Decimal('0.05')

}

step_size = {
    'BTCUSDT': Decimal('0.001'),
    'ETHUSDT': Decimal('0.01'),
    'SOLUSDT': Decimal('0.1'),
    'BCHUSDT': Decimal('0.01')
}


class MultiBBV1Strategy(bt.Strategy):
    params = dict(
        bb_span={
            'BTCUSDT': 150,
            'ETHUSDT': 100,
            'SOLUSDT': 100,
            'BCHUSDT': 100
        },
        bb_mult={
            'BTCUSDT': 1.5,
            'ETHUSDT': 1.5,
            'SOLUSDT': 1.5,
            'BCHUSDT': 1.5
        },
        atr_length=10,
        atr_constant=Decimal('1.5'),
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.pairs = []
        self.pairs_open = []
        self.pairs_high = []
        self.pairs_low = []
        self.pairs_close = []
        self.pairs_date = []
        self.pairs_bb_top = []
        self.pairs_bb_mid = []
        self.pairs_bb_bot = []
        self.pairs_atr = []

        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.pairs_open.append(self.datas[i].open)
            self.pairs_high.append(self.datas[i].high)
            self.pairs_low.append(self.datas[i].low)
            self.pairs_close.append(self.datas[i].close)
            self.pairs_date.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            bb = bt.indicators.BollingerBands(self.pairs_close[i], period=self.p.bb_span[self.pairs[i]._name], devfactor=self.p.bb_mult[self.pairs[i]._name])
            self.pairs_bb_top.append(bb.lines.top)
            self.pairs_bb_mid.append(bb.lines.mid)
            self.pairs_bb_bot.append(bb.lines.bot)

        for i in range(0, len(self.pairs)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.ExponentialMovingAverage(tr, period=self.p.atr_length)
            self.pairs_atr.append(atr)


    def next(self):
        for i in range(0, len(self.pairs)):
            name = self.pairs[i]._name
            self.log(f'[{name}] {self.pairs_date[i].datetime(0)} atr : {self.pairs_atr[i][0]}')


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=30)
    cerebro.addstrategy(MultiBBV1Strategy)

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    cerebro.run()