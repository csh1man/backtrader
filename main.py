import backtrader as bt
import yfinance as yf
import pandas as pd
from repository.Repository import DB


# create strategy
class TestStrategy(bt.Strategy):

    def log(self, txt):
        print(txt)
        # dt = dt or self.datas[0].datetime.datetime(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_volume = self.datas[0].volume
        self.data_date = self.datas[0].datetime

    def next(self):
        self.log("===============" + str(self.data_date.datetime(0)) + "=================")
        self.log("시가 : " + str(self.data_open[0]))
        self.log("고가 : " + str(self.data_high[0]))
        self.log("저가 : " + str(self.data_low[0]))
        self.log("종가 : " + str(self.data_close[0]))
        self.log("==============================================")

if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    DB.init_connection_pool(config_path)

    db = DB()
    candle_infos = db.get_candle_info('BYBIT', 'LINKUSDT', '30m')
    df = pd.DataFrame([vars(info) for info in candle_infos])

    df['datetime'] = pd.to_datetime(df['date'])
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])

    # cerebro 인스턴스 초기화
    cerebro = bt.Cerebro()

    # cerebro에 전략 셋팅
    cerebro.addstrategy(TestStrategy)

    # 백테스팅할 데이터 설정
    # data = bt.feeds.PandasData(dataname=yf.download('036570.KS', '2018-01-01', '2021-12-01'))
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')
    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value : %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value : %.2f' % cerebro.broker.getvalue())
