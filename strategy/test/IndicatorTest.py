import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from api.Api import Common, Download
from decimal import Decimal

config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
# config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"

download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
# download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
# download_dir_path = "/Users/tjgus/Desktop/project/krtrade/backData"

result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
# result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"

result_file_prefix = "TrendFollowWithATRScalingV1"

pairs = {
    'SOLUSDT': DataUtils.CANDLE_TICK_4HOUR,
    # 'BTCUSDT': DataUtils.CANDLE_TICK_4HOUR,
    # 'ETHUSDT': DataUtils.CANDLE_TICK_4HOUR,
    # 'AVAXUSDT': DataUtils.CANDLE_TICK_4HOUR,
    # '1000PEPEUSDT': DataUtils.CANDLE_TICK_4HOUR,
    # '1000BONKUSDT': DataUtils.CANDLE_TICK_4HOUR,
}

exchange = DataUtil.BYBIT
leverage = 4

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)

class TrendFollowWithATRScalingV1(bt.Strategy):
    params = dict(
        atr_length={
            'BTCUSDT': [14, 30],
            'ETHUSDT': [5, 50],
            'SOLUSDT': [5, 50],
            'AVAXUSDT': [14, 50],
            '1000PEPEUSDT': [14, 50],
            '1000BONKUSDT': [14, 50],
        },
        tick_size={
            'BTCUSDT': common.fetch_tick_size(exchange, 'BTCUSDT'),
            'ETHUSDT': common.fetch_tick_size(exchange, 'ETHUSDT'),
            'SOLUSDT': common.fetch_tick_size(exchange, 'SOLUSDT'),
            'AVAXUSDT': common.fetch_tick_size(exchange, 'AVAXUSDT'),
            '1000PEPEUSDT': common.fetch_tick_size(exchange, '1000PEPEUSDT'),
            '1000BONKUSDT': common.fetch_tick_size(exchange, '1000BONKUSDT'),
        },
        step_size={
            'BTCUSDT': common.fetch_step_size(exchange, "BTCUSDT"),
            'ETHUSDT': common.fetch_step_size(exchange, "ETHUSDT"),
            'SOLUSDT': common.fetch_step_size(exchange, "SOLUSDT"),
            'AVAXUSDT': common.fetch_step_size(exchange, "AVAXUSDT"),
            '1000PEPEUSDT': common.fetch_step_size(exchange, "1000PEPEUSDT"),
            '1000BONKUSDT': common.fetch_step_size(exchange, "1000BONKUSDT"),
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

        self.atr1 = []
        self.atr2 = []

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

            atr1 = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name][0])
            self.atr1.append(atr1)

            atr2 = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name][1])
            self.atr2.append(atr2)

    def next(self):
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            tick_size = self.p.tick_size[name]
            atr1 = int(DataUtils.convert_to_decimal(self.atr1[i][0]) / tick_size) * tick_size
            atr2 = int(DataUtils.convert_to_decimal(self.atr2[i][0]) / tick_size) * tick_size
            vol_factor = int((atr1 / atr2) / tick_size) * tick_size
            self.log(f'{self.dates[i].datetime(0)} => atr : {atr1} / avg atr : {atr2}, vol factor : {vol_factor}')

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendFollowWithATRScalingV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.002, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        download.download_candles(exchange, pair, tick_kind)
        df = DataUtils.load_candle_data_as_df(download_dir_path, DataUtils.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    before_balance = cerebro.broker.getvalue()
    print('Before Portfolio Value: %.2f' % before_balance)
    results = cerebro.run()