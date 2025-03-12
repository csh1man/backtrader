import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal

pairs = {
    'KRW-BTC' : DataUtils.CANDLE_TICK_4HOUR,
    'KRW-PEPE': DataUtils.CANDLE_TICK_30M,
}

class BithumbGridV1(bt.Strategy):
    params = dict(
        risks=[Decimal('2.0'), Decimal('2.0'), Decimal('2.0'), Decimal('2.0'), Decimal('2.0')],
        addRisks=[Decimal('3.0'), Decimal('3.0'), Decimal('3.0'), Decimal('3.0'), Decimal('3.0')],
        bb_length=80,
        bb_mult=1.0,
        atr_length=50,
        atr_avg_length=200,
        rsi_length=2,
        rsi_low=50,
        exit_percent=Decimal('0.7'),
        add_exit_percent=Decimal('1.3'),
        bull_constants=[Decimal('0.5'), Decimal('0.7'), Decimal('0.9'), Decimal('1.0'), Decimal('1.5')],
        def_constants=[Decimal('1.5'), Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0')],
        bear_constants=[Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')]
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
        self.atrs = []
        '''
        자산 추정용 변수 추가
        '''
        self.order = None
        self.date_value = []
        self.my_assets = []
        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

            # RSI 지표 초기화
            rsi = bt.ind.RSI_Safe(self.datas[i].close, period=self.p.rsi_length)
            self.rsis.append(rsi)
            
            # ATR 지표 초기화
            atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length)
            # tr = bt.indicators.TrueRange(self.pairs[i])
            # atr = bt.indicators.SmoothedMovingAverage(tr, period=self.p.atr_length)
            # atr = bt.indicators.MovingAverageSimple(atr, period=self.p.atr_avg_length)
            self.atrs.append(atr)

        self.bb = []
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []

        bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_length, devfactor=self.p.bb_mult)
        self.bb_top.append(bb.lines.top)
        self.bb_mid.append(bb.lines.mid)
        self.bb_bot.append(bb.lines.bot)

    def next(self):
        for i in range(1, len(self.pairs)):
            self.log(f'{self.dates[i].datetime(0)} => {self.atrs[i][0]}')


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(BithumbGridV1)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002, leverage=5)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BITHUMB, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    cerebro.run()