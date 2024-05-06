import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal
from indicator.Indicators import Indicator

pairs = {
    "KRW-BTC": DataUtil.CANDLE_TICK_4HOUR,
    # "KRW-ETH": DataUtil.CANDLE_TICK_4HOUR,
    # "KRW-BCH": DataUtil.CANDLE_TICK_4HOUR,
    # "KRW-SOL": DataUtil.CANDLE_TICK_4HOUR
}


def get_tick_size(price):
    if price >= 2000000:
        return Decimal('1000')
    elif price >= 1000000:
        return Decimal('500')
    elif price >= 500000:
        return Decimal('100')
    elif price >= 100000:
        return Decimal('50')
    elif price >= 1000:
        return Decimal('5')
    elif price >= 100:
        return Decimal('1')
    elif price >= 10:
        return Decimal('0.1')
    else:
        return Decimal('0.01')


class UpbitBBV2(bt.Strategy):
    params = dict(
        riskPerTrade=Decimal('2'),
        bb_span={
            'KRW-BTC': 80,
            'KRW-ETH': 50,
            'KRW-BCH': 50,
            'KRW-SOL': 50
        },
        bb_mult={
            'KRW-BTC': 1,
            'KRW-ETH': 1.5,
            'KRW-BCH': 1.5,
            'KRW-SOL': 1.5
        },
        atr_length={
            'KRW-BTC': 10,
            'KRW-ETH': 10,
            'KRW-BCH': 10,
            'KRW-SOL': 10
        },
        atr_constant={
            'KRW-BTC': Decimal('2.0'),
            'KRW-ETH': Decimal('1.5'),
            'KRW-BCH': Decimal('1.5'),
            'KRW-SOL': Decimal('1.5')
        }
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 기본 데이터 정보 초기화
        self.pairs = []
        self.names = []
        self.pairs_open = []
        self.pairs_high = []
        self.pairs_low = []
        self.pairs_close = []
        self.pairs_date = []
        self.pairs_stop_price = []

        # 지표 데이터 정보 초기화
        self.pairs_atr = []
        self.pairs_bb_top = []
        self.pairs_bb_mid = []
        self.pairs_bb_bot = []

        # 자산 추적용 변수 할당
        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

        # 기본 데이터 정보 할당
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.pairs_open.append(self.datas[i].open)
            self.pairs_high.append(self.datas[i].high)
            self.pairs_low.append(self.datas[i].low)
            self.pairs_close.append(self.datas[i].close)
            self.pairs_date.append(self.datas[i].datetime)
            self.pairs_stop_price.append(Decimal('-1'))

        # 지표 데이터 정보 계산 및 할당
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            bb = bt.indicators.BollingerBands(self.pairs_close[i], period=self.p.bb_span[name], devfactor=self.p.bb_mult[name])
            self.pairs_bb_top.append(bb.lines.top)
            self.pairs_bb_mid.append(bb.lines.mid)
            self.pairs_bb_bot.append(bb.lines.bot)

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length[name])
            self.pairs_atr.append(atr)

    # 거래내역 추적
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

    # 모든 미체결 지정가 주문 취소
    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

    def next(self):
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            entry_position_size = self.getposition(self.pairs[i]).size
            if entry_position_size > 0:
                if self.pairs_close[i][-1] > self.pairs_bb_mid[i][-1] and self.pairs_close[i][0] < self.pairs_bb_mid[i][0]:
                    self.order = self.sell(data=self.pairs[i], size=entry_position_size)
                else:
                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(self.pairs_stop_price[i]), size=entry_position_size)
            else:
                if self.pairs_close[i][-1] < self.pairs_bb_top[i][-1] and self.pairs_close[i][0] > self.pairs_bb_top[i][0]:
                    self.pairs_stop_price[i] = Decimal(str(self.pairs_close[i][0])) - Decimal(str(self.pairs_atr[i][0])) * self.p.atr_constant[name]
                    self.pairs_stop_price[i] = int(self.pairs_stop_price[i] / get_tick_size(self.pairs_close[i][0])) * get_tick_size(self.pairs_close[i][0])
                    qty = (self.p.riskPerTrade / Decimal('100')) / (Decimal(self.pairs_close[i][0]) - self.pairs_stop_price[i])
                    if qty > Decimal('0'):
                        self.order = self.buy(data=self.pairs[i], qty=float(qty))

    def stop(self):
        self.log(f'총 트레이딩 수 : {self.total_trading_count}')
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getcash())
        self.log(f"수익률 : {self.return_rate}%")

if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000) # 초기 시드 설정
    cerebro.broker.setcommission(0.0005, leverage=1) # 수수료 설정
    cerebro.addstrategy(UpbitBBV2) # 전략 추가
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # 데이터 INSERT
    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_UPBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    # 전략 실행
    print('Initial Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

