import backtrader as bt
from util.Util import DataUtil

pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
    '1000BONKUSDT': DataUtil.CANDLE_TICK_30M,
}


class AtrRsiWithBBV1(bt.Strategy):
    params = dict(
        atr_length=10,
        rsi_length=2,
        rsi_high=90,
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.pairs = []
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])

        self.pairs_open = []
        for i in range(0, len(self.pairs)):
            self.pairs_open.append(self.pairs[i].open)

        self.pairs_high = []
        for i in range(0, len(self.pairs)):
            self.pairs_high.append(self.pairs[i].high)

        self.pairs_low = []
        for i in range(0, len(self.pairs)):
            self.pairs_low.append(self.pairs[i].low)

        self.pairs_close = []
        for i in range(0, len(self.pairs)):
            self.pairs_close.append(self.pairs[i].close)

        self.pairs_date = []
        for i in range(0, len(self.pairs)):
            self.pairs_date.append(self.pairs[i].datetime)

        # 내장 ATR의 경우, 계산 방식이 옳지 못한 것으로 보여, TR 계산 후 직접 ATR을 계산한다.
        # 계산방식은 Simple Moving Avrage 방식이다.
        self.pairs_atr = []
        for i in range(0, len(self.pairs)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            self.pairs_atr.append(bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length))

        self.pair_rsi = []
        for i in range(0, len(self.pairs)):
            rsi = bt.ind.RSI_Safe(self.pair_close[i], period=self.p.rsi_length)
            self.pair_rsi.append(rsi)

        self.order_balance_list = []

    def next(self):
        try:
            position_value = 0.0
            bough_value = 0.0
            account_value = self.broker.get_cash()
            broker_leverage = self.broker.comminfo[None].p.leverage
            for pair in self.pairs:
                position_value += self.getposition(pair).size * pair.low[0]
                bough_value += self.getposition(pair).size * self.getposition(pair).price

            account_value += position_value - bough_value * (broker_leverage-1) / broker_leverage
            self.order_balance_list.append([self.pairs_date[1].datetime(0), account_value])

            self.cancel_all()
            # for i in range(1, len(self.pairs)):
            #     currency = self.pairs[i]._name
            #     position_size = self.getposition(self.pairs[i]).size
            #     if position_size > 0:
            #         if self.pair_rsi[i][0] > self.p.rsi_high:

        except:
            raise

    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=4)
    cerebro.addstrategy(AtrRsiWithBBV1)

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    cerebro.run()