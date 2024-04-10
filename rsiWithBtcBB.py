import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal
from indicator.Indicators import Indicator

class RsiWithBtcBB(bt.Strategy):

    # 환경설정 파라미터값 선언
    params = dict(
        leverage=5,
        risks=[1, 1, 2, 4, 8],
        bb_span=80,
        bb_mult=1,
        rsi_length=2,
        rsi_high=90,
        bull_percents=[0.5, 1.0, 1.5, 2.0, 2.5],
        bear_percents=[2.0, 4.0, 6.0, 8.0, 10.0],
        default_percents=[1.0, 2.0, 3.0, 4.0, 5.0],
        tick_size=0.0001,
        step_size=1,
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        # data feeds 초기화
        self.btc = self.datas[0]
        self.pair = self.datas[1]
        
        # 테스팅용 종목 ohlc 초기화
        self.pair_open = self.pair.open
        self.pair_high = self.pair.high
        self.pair_low = self.pair.low
        self.pair_close = self.pair.close
        self.pair_date = self.pair.datetime
        self.pair_rsi = bt.ind.RSI(self.pair_close, period=self.p.rsi_length)

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

        self.order = None
        self.date_value = []
        self.my_assets = []

        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

    # def notify_order(self, order):
    #     if order.status in [order.Submitted, order.Accepted]:
    #         # Buy/Sell order submitted/accepted to/by broker - Nothing to do
    #         return
    #
    #     # Check if an order has been completed
    #     # Attention: broker could reject order if not enough cash
    #     if order.status in [order.Completed]:
    #         if order.isbuy():
    #             self.log(str(self.pair_date.datetime(0)) + 'BUY EXECUTED, %.3f' % order.executed.price)
    #         elif order.issell():
    #             self.log(str(self.pair_date.datetime(0)) + 'SELL EXECUTED, %.3f , QTY = %.3f' % (order.executed.price, order.executed.size))
    #             self.log("")
    #             # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
    #             self.total_trading_count += 1
    #             # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
    #             if order.executed.pnl > 0:
    #                 self.winning_trading_count += 1
    #     elif order.status in [order.Canceled]:
    #         self.log(f'{self.pair_date.datetime(0)} => Order Canceled')
    #     elif order.status in [order.Margin]:
    #         self.log(f'{self.pair_date.datetime(0)} => Order Margin')
    #     elif order.status in [order.Rejected]:
    #         self.log(f'{self.pair_date.datetime(0)} => Order Rejected')
    #
    #     # Write down: no pending order
    #     self.order = None

    def next(self):

        self.cancel_all()
        current_date = self.pair_date.datetime(0)
        if self.position:
            if self.pair_rsi[0] > self.p.rsi_high:
                self.order = self.sell(size=self.getposition(self.datas[1].size))

        prices = []
        if self.btc_close[0] > self.bb_top[0]:
            for i in range(0, 5):
                price = Decimal(self.pair_close[0]) * (Decimal(1) - Decimal(self.p.bull_percents[i]) / Decimal(100))
                price = int(price / Decimal(self.p.tick_size)) * Decimal(self.p.tick_size)
                prices.append(float(price))

        elif self.bb_bot[0] < self.btc_close[0] < self.bb_top[0]:
            for i in range(0, 5):
                price = Decimal(self.pair_close[0]) * (Decimal(1) - Decimal(self.p.default_percents[i]) / Decimal(100))
                price = int(price / Decimal(self.p.tick_size)) * Decimal(self.p.tick_size)
                prices.append(float(price))

        elif self.btc_close[0] < self.bb_bot[0]:
            for i in range(0, 5):
                price = Decimal(self.pair_close[0]) * (Decimal(1) - Decimal(self.p.bear_percents[i]) / Decimal(100))
                price = int(price / Decimal(self.p.tick_size)) * Decimal(self.p.tick_size)
                prices.append(float(price))

        current_equity = self.broker.getvalue()
        for i in range(0, 5):
            qty = self.p.leverage * current_equity * self.p.risks[i] / 100 / prices[i]
            qty = int(qty / self.p.step_size) * self.p.step_size
            if qty > 0:
                self.order = self.buy(exectype=bt.Order.Limit, price=prices[i], size=qty)

    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.log(f'{self.pair_date.datetime(0)} => opened')
            self.broker.cancel(order)
            self.log(f'{self.pair_date.datetime(0)} => canceled')


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"

    start_date = '2020-01-01 00:00:00'
    end_date = '2021-10-01 00:00:00'

    pairs = {
        'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
        'XRPUSDT': DataUtil.CANDLE_TICK_30M
    }

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(0.0002, leverage=10)
    cerebro.addstrategy(RsiWithBtcBB)


    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        # df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')

        cerebro.adddata(data, name=pair)


    print('시작 포트폴리오 가격: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('끝 포트폴리오 가격: %.2f' % cerebro.broker.getvalue())