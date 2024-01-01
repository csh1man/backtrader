import backtrader as bt
from util.Util import DataUtil
from repository.Repository import DB
from indicator.Indicators import Indicator

class MACDStrategy(bt.Strategy):
    params = (
        ("risk_per_trade", 10),
        ("short_ma", 10),
        ("long_ma", 15),
        ("signal_length", 10),
        ("atr_length", 2),
        ("atr_constant", 1.5)
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 디비 접속
        self.db = DB()
        self.currency_info = self.db.get_currency_info(DataUtil.COMPANY_BYBIT, "BTCUSDT")

        # 캔들 정보 초기화
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.date = self.datas[0].datetime

        # 지표 초기화
        self.short_ma = bt.indicators.ExponentialMovingAverage(self.close, period=self.p.short_ma)
        self.long_ma = bt.indicators.ExponentialMovingAverage(self.close, period=self.p.long_ma)
        self.macd = self.short_ma - self.long_ma
        self.signal = bt.indicators.ExponentialMovingAverage(self.macd, period=self.p.signal_length)
        self.atr = bt.indicators.AverageTrueRange(period=self.p.atr_length)

        # 주문 추적용
        self.order = None
        self.stop_price = None

        # 자산 추적용
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0
        self.date_value = []
        self.my_assets = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY ! "
                         f"date : {self.date.datetime(0)}, price : {order.executed.price},"
                         f"size : {order.executed.size}"
                         f"comm : {order.executed.comm}")
            elif order.issell():
                self.log(f"SELL ! "
                         f"date : {self.date.datetime(0)}, price : {order.executed.price}"
                         f" size : {order.executed.size}"
                         f" comm : {order.executed.comm}"
                         f" my asset : {self.broker.getvalue() + self.getposition(self.datas[0]).size * self.low[0]}")
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

        self.order = None

    def next(self):
        self.date_value.append(self.date.datetime(0))
        self.my_assets.append(self.broker.getvalue() + self.getposition(self.datas[0]).size * self.low[0])

        if self.order:
            return

        if not self.position:
            if self.macd[0] > 0 and self.macd[0] > self.signal[0]:
                if self.close[0] > self.open[0]:
                    self.stop_price = self.open[0] - self.atr[0] * self.p.atr_constant
                else:
                    self.stop_price = self.close[0] - self.atr[0] * self.p.atr_constant
                # 진입가(종가)랑 손절가 간의 퍼센트 획득
                diff_percent = (self.close[0] - self.stop_price) * 100 / self.close[0]

                # 진입가 손절가 퍼센트에 따른 레버리지 획득
                leverage = Indicator.get_leverage(self.p.risk_per_trade, diff_percent)
                position_size = leverage * self.broker.getvalue() * self.p.risk_per_trade / 100 / self.close[0]
                position_size = Indicator.adjust_quantity(position_size, self.currency_info.step_size)
                self.buy(size=position_size)
        else:
            if self.close[0] < self.stop_price:
                self.sell(size=self.getposition(self.datas[0]).size)
            elif self.macd[-1] > self.signal[-1] and self.macd[0] < self.signal[0]:
                self.sell(size=self.getposition(self.datas[0]).size)

    def stop(self):
        self.winning_rate = self.winning_trading_count * 100 / self.total_trading_count
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getvalue())

        self.log(f"전체 트레이딩 수 : {self.total_trading_count}번")
        self.log(f"승률 : {self.winning_rate :.2f}%")
        self.log(f"수익률 : {self.return_rate:.2f}%")


if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    DB.init_connection_pool(config_path)

    # backtesting할 데이터 추출
    df = DataUtil.load_candle_data_as_df(DataUtil.CANDLE_DATA_DIR_PATH, DataUtil.COMPANY_BYBIT,
                                         "BTCUSDT", DataUtil.CANDLE_TICK_2HOUR)

    df = DataUtil.get_candle_data_in_scape(df, "2020-03-01", "2023-12-27")
    # 특정 날짜 만큼만 추출
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.0002)

    cerebro.adddata(data)
    cerebro.addstrategy(MACDStrategy)

    cerebro.run()