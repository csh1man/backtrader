import backtrader as bt
from util.Util import DataUtils

pairs = {
    'BTCUSDT' : DataUtils.CANDLE_TICK_30M,
    "1000BONKUSDT" : DataUtils.CANDLE_TICK_30M,
}


class DataAnalysis(bt.Strategy):
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
        self.plus = 0
        self.minus = 0
        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

    def next(self):
        for i in range(1, len(self.pairs)):
            # 비트코인이 연속으로 두개의 음봉이 나타났을 때, 다음 캔들은 몇퍼센트 하락할까 ?
            if (self.closes[0][-1] - self.opens[0][-1]) * 100 / self.opens[0][-1] <= -0.5:
                percent = (self.closes[i][0] - self.opens[i][0]) * 100 / self.opens[i][0]
                if percent < 0:
                    self.minus += 1
                elif percent > 0:
                    self.plus += 1
                # self.log(f'{self.dates[i].datetime(0)} => {percent}%')

    def stop(self):
        total_count = self.plus + self.minus
        plus_percent = self.plus * 100 / total_count
        minus_percent = self.minus * 100 / total_count
        self.log(f'plus count : {self.plus}({plus_percent})% , minus count : {self.minus}({minus_percent}%)')

if __name__ == '__main__':
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(DataAnalysis)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002, leverage=10)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    cerebro.run()