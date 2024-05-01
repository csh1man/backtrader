import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal
from indicator.Indicators import Indicator

pairs = {
    # 'BTCUSDT': DataUtil.CANDLE_TICK_2HOUR,
    'ETHUSDT': DataUtil.CANDLE_TICK_2HOUR,
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

target_percent = {
    'BTCUSDT': Decimal('1.0'),
    'ETHUSDT': Decimal('1.0'),
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
        atr_length={
            'BTCUSDT': 10,
            'ETHUSDT': 10,
            'SOLUSDT': 10,
            'BCHUSDT': 10
        },
        atr_constant=Decimal('1.5'),
        pyramiding=1,
        initRiskSize=Decimal('10'),
        addRiskSize=Decimal('5'),
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.pairs = []
        self.names = []
        self.pairs_open = []
        self.pairs_high = []
        self.pairs_low = []
        self.pairs_close = []
        self.pairs_date = []
        self.pairs_bb_top = []
        self.pairs_bb_mid = []
        self.pairs_bb_bot = []
        self.pairs_atr = []
        self.pairs_pyramiding = []
        self.pairs_stop_price = []
        self.pairs_leverages = []

        self.order = None
        self.date_value = []
        self.my_assets = []

        # 승률 계산을 위함
        self.init_qty = []
        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.pairs_open.append(self.datas[i].open)
            self.pairs_high.append(self.datas[i].high)
            self.pairs_low.append(self.datas[i].low)
            self.pairs_close.append(self.datas[i].close)
            self.pairs_date.append(self.datas[i].datetime)
            self.pairs_leverages.append(-1)
            self.pairs_pyramiding.append(0)
            self.pairs_stop_price.append(-1)

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            bb = bt.indicators.BollingerBands(self.pairs_close[i], period=self.p.bb_span[name], devfactor=self.p.bb_mult[name])
            self.pairs_bb_top.append(bb.lines.top)
            self.pairs_bb_mid.append(bb.lines.mid)
            self.pairs_bb_bot.append(bb.lines.bot)

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.init_qty.append(Decimal('-1'))
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length[name])
            self.pairs_atr.append(atr)

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{order.ref:<3} {cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                self.total_trading_count += 1
            elif order.issell():
                self.log(f'{order.ref:<3} {cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def next(self):
        for i in range(0, len(self.pairs)):
            self.log(f'[{self.pairs_date[i].datetime(0)}]')
            name = self.names[i]
            current_equity = Decimal(str(self.broker.getcash()))

            do_add_entry = True
            if self.pairs_pyramiding[i] >= self.p.pyramiding:
                do_add_entry = False

            entry_position_size = self.getposition(self.pairs[i]).size
            if entry_position_size > 0:
                if self.pairs_close[i][-1] > self.pairs_stop_price[i] > self.pairs_close[i][0]:
                    self.order = self.sell(data=self.pairs[i], size=entry_position_size)
                    self.pairs_pyramiding[i] = 0
                    self.pairs_stop_price[i] = Decimal('-1')
                elif self.pairs_bb_mid[i][-1] < self.pairs_close[i][-1] and self.pairs_bb_mid[i][0] > self.pairs_close[i][0]:
                    self.order = self.sell(data=self.pairs[i], size=entry_position_size)
                    self.pairs_pyramiding[i] = 0
                    self.pairs_stop_price[i] = Decimal('-1')
                elif do_add_entry:
                    avg_price = self.getposition(self.pairs[i]).price
                    target_price = Decimal(str(avg_price)) * (Decimal('1') + target_percent[name] / Decimal('100'))
                    if Decimal(str(self.pairs_close[i][-1])) < target_price < Decimal(self.pairs_close[i][0]):
                        entry_qty = self.init_qty[i] / Decimal('2')
                        entry_qty = int(entry_qty / step_size[name]) * step_size[name]
                        if current_equity > entry_qty:
                            self.log(f'피라미딩 수 : {self.pairs_pyramiding[i] + 1}')
                            self.order = self.buy(data=self.pairs[i], size=float(entry_qty))
                            avg_price = self.getposition(self.pairs[i]).price
                            self.pairs_stop_price[i] = Decimal(str(avg_price)) - Decimal(str(round(self.pairs_atr[i][0], 2))) * self.p.atr_constant
                            self.pairs_pyramiding[i] += 1

            else:
                if self.pairs_close[i][-1] < self.pairs_bb_top[i][-1] and self.pairs_close[i][0] > self.pairs_bb_top[i][0]:
                    self.pairs_stop_price[i] = Decimal(str(self.pairs_close[i][0])) - Decimal(str(round(self.pairs_atr[i][0], 2))) * self.p.atr_constant
                    diff_percent = Indicator.get_diff_percent(self.pairs_close[i][0], self.pairs_stop_price[i])
                    self.pairs_leverages[i] = Indicator.get_leverage(self.p.initRiskSize, diff_percent)
                    qty = self.pairs_leverages[i] * current_equity * self.p.initRiskSize / Decimal('100') / Decimal(str(self.pairs_close[i][0]))
                    qty = int(qty / step_size[name]) * step_size[name]
                    if qty > 0:
                        self.order = self.buy(data=self.pairs[i], size=float(qty))
                        self.pairs_pyramiding[i] += 1
                        self.init_qty[i] = qty

    def stop(self):
        self.log(f'총 트레이딩 수 : {self.total_trading_count}')
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getcash())
        self.log(f"수익률 : {self.return_rate}%")

if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=30)
    cerebro.addstrategy(MultiBBV1Strategy)

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('start Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())