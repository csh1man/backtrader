import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal
from indicator.Indicators import Indicator
from datetime import datetime

pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_30M,
    'XRPUSDT': DataUtil.CANDLE_TICK_30M
}


class RsiWithStopPriceWithBTC(bt.Strategy):
    params = dict(
        bb_span=100,
        bb_mult=1.0,
        atr_length={
            'BTCUSDT': 10,
            'XRPUSDT': 10,
        },
        atr_constant={
          'BTCUSDT': Decimal('1.5'),
          'XRPUSDT': Decimal('2.0')
        },
        bullish_percent={
            'XRPUSDT': Decimal('2'),
        },
        bearish_percent={
            'XRPUSDT': Decimal('2'),
        },
        default_percent={
            'XRPUSDT': Decimal('4'),
        },
        tick_size={
            'XRPUSDT': Decimal('0.0001')
        },
        step_size={
            'XRPUSDT': Decimal('1')
        },
        rsi_length=2,
        rsi_high=80,
        pyramiding=3,
        risk=Decimal('1'),
    )

    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        """
        비트코인 정보 초기화
        """
        self.btc = self.datas[0]
        self.btc_open = self.btc.open
        self.btc_high = self.btc.high
        self.btc_low = self.btc.low
        self.btc_close = self.btc.close
        self.btc_date = self.btc.datetime

        """
        비트코인 볼린저밴드 값 초기화
        """
        self.bb = bt.indicators.BollingerBands(self.btc.close, period=self.p.bb_span, devfactor=self.p.bb_mult)
        self.bb_top = self.bb.lines.top
        self.bb_mid = self.bb.lines.mid
        self.bb_bot = self.bb.lines.bot

        self.names = []
        self.pairs = []
        self.pairs_open = []
        self.pairs_high = []
        self.pairs_low = []
        self.pairs_close = []
        self.pairs_date = []
        self.pairs_atr = []
        self.pairs_rsi = []
        self.pairs_pyramiding = {
            'XRPUSDT':0
        }
        self.pairs_stop_price = {
            'XRPUSDT':Decimal('-1')
        }

        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.pairs_open.append(self.datas[i].open)
            self.pairs_high.append(self.datas[i].high)
            self.pairs_low.append(self.datas[i].low)
            self.pairs_close.append(self.datas[i].close)
            self.pairs_date.append(self.datas[i].datetime)
            self.pairs_pyramiding[self.datas[i]._name] = 0

        for i in range(0, len(self.pairs)):
            rsi = bt.ind.RSI_Safe(self.pairs_close[i], period=self.p.rsi_length)
            self.pairs_rsi.append(rsi)

        for i in range(0, len(self.pairs)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length[self.names[i]])
            self.pairs_atr.append(atr)

        '''
        자산 추적용 변수 초기화
        '''
        # 자산 추적용 변수 할당
        self.order = None
        self.date_value = []
        self.my_assets = []

        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

    def record_asset(self):
        account_value = self.broker.get_cash()  # 현재 현금(보유 포지션 제외) 자산의 가격을 획득
        broker_leverage = self.broker.comminfo[None].p.leverage  # cerebro에 설정한 레버리지 값 -> setcommission
        position_value = 0.0
        bought_value = 0.0
        for pair in self.pairs:
            position_value += self.getposition(pair).size * pair.low[0]
            bought_value += self.getposition(pair).size * self.getposition(
                pair).price  # 진입한 수량 x 평단가 즉, 현재 포지션 전체 가치를 의미(현금 제외)

        account_value += position_value - bought_value * (broker_leverage - 1) / broker_leverage
        self.order_balance_list.append([self.pairs_date[0].datetime(0), account_value])
        self.date_value.append(self.pairs_date[0].datetime(0))
        position_value = self.broker.getvalue()
        for i in range(1, len(self.datas)):
            position_value += self.getposition(self.datas[i]).size * self.pairs_low[i][0]

        self.my_assets.append(position_value)

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.pairs_pyramiding[order.data._name] += 1
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}\t'
                         f'피라미딩 횟수:{self.pairs_pyramiding[order.data._name]}')
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}\n')
                self.pairs_pyramiding[order.data._name] = 0
                self.pairs_stop_price[order.data._name] = Decimal('-1')
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def next(self):
        # 자산기록
        self.record_asset()
        # 미체결 주문 취소
        self.cancel_all()

        for i in range(1, len(self.pairs)):
            name = self.names[i]
            position_size = self.getposition(self.pairs[i]).size
            if position_size > 0:
                if self.pairs_rsi[i][0] >= self.p.rsi_high:
                    self.order = self.sell(data=self.pairs[i], size=position_size)
                elif self.pairs_close[i][0] < self.pairs_stop_price[name]:
                    self.order = self.sell(data=self.pairs[i], size=position_size)
                    # self.log(f'{self.pairs_date[i].datetime(0)} 지정가 종료 주문 생성 : {self.pairs_stop_price[name]}')
                    # self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(self.pairs_stop_price[name]), size=position_size)

            price = Decimal('0.0')
            situation = ""
            if self.btc_close[0] >= self.bb_top[0]:
                price = Decimal(str(self.pairs_close[i][0])) * (
                            Decimal('1') - self.p.bullish_percent[name] / Decimal('100'))
                situation = "bullish"
            elif self.bb_bot[0] <= self.btc_close[0] < self.bb_top[0]:
                price = Decimal(str(self.pairs_close[i][0])) * (
                            Decimal('1') - self.p.default_percent[name] / Decimal('100'))
                situation = "default"
            elif self.bb_bot[0] > self.btc_close[0]:
                price = Decimal(str(self.pairs_close[i][0])) * (
                            Decimal('1') - self.p.bearish_percent[name] / Decimal('100'))
                situation = "bearish"
            price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
            stop_price = Decimal(str(price)) - Decimal(str(self.pairs_atr[i][0])) * self.p.atr_constant[name]
            stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
            self.pairs_stop_price[name] = stop_price
            if self.pairs_pyramiding[name] < self.p.pyramiding:
                entry_size = self.p.risk / Decimal('100')
                entry_size = entry_size / (entry_size-stop_price)
                entry_size = entry_size * Decimal(str(self.broker.get_cash()))
                entry_size = int(entry_size / self.p.step_size[name]) * self.p.step_size[name]
                self.log(f'{self.pairs_date[i].datetime(0)} 지정가 진입 주문 생성 : {price} : 상황 : [{situation}]')
                self.order = self.buy(exectype=bt.Order.Limit,data=self.pairs[i],price=float(price),size=float(entry_size))

    def stop(self):
        self.log(f'총 트레이딩 수 : {self.total_trading_count}')
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getcash())
        self.log(f"수익률 : {self.return_rate}%")



if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=100)
    cerebro.addstrategy(RsiWithStopPriceWithBTC)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        df = DataUtil.get_candle_data_in_scape(df, '2022-12-31 00:00:00', '2024-05-17 23:00:00')
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('Init Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())