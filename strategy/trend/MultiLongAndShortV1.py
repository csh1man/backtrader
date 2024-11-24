import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'BTCUSDT' : DataUtil.CANDLE_TICK_4HOUR
}

class MultiLongAndShortV1(bt.Strategy):
    params = dict(
        # 롱/숏 레버리지 셋팅
        leverage={
            'BTCUSDT': {
                'long': Decimal('1.0'),
                'short': Decimal('1.0')
            }
        },
        # 롱/숏 손실 비율 셋팅
        risk={
            'BTCUSDT': {
                'long': Decimal('1.0'),
                'short': Decimal('1.0')
            }
        },
        # 가격 단위 셋팅
        tick_size={
            'BTCUSDT': Decimal('0.10')
        },
        # 수량 단위 셋팅
        step_size={
            'BTCUSDT': Decimal('0.001')
        },
        # 고가 채널 주기 셋팅
        high_band_length={
            'BTCUSDT': 30,
        },
        # 저가 채널 주기 셋팅
        low_band_length={
            'BTCUSDT': 15,
        },
        # 볼린저밴드 주기 셋팅
        bb={
            'length': {
                'BTCUSDT':80,
            },
            'mult': {
                'BTCUSDT':2,
            }
        },

        #ATR 주기 셋팅
        atr={
            'length': {
                'BTCUSDT': 10,
            },
            'constant': {
                'BTCUSDT': Decimal('1.0')
            }
        }
    )

    def __init__(self):

        # 기본 캔들 정보 저장용 변수 초기화
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []

        # 손절 가격 저장용 변수 초기화
        self.long_stop_prices = []
        self.short_stop_prices = []

        # 기본 캔들 정보 저장
        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
            self.long_stop_prices.append(Decimal('0'))
            self.short_stop_prices.append(Decimal('0'))

        # 지표 데이터 저장용 변수 초기화
        self.bb_top = []
        self.bb_mid = []
        self.bb_low = []
        self.highest = []
        self.lowest = []
        self.atrs = []

        # 지표 데이터 저장
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # 고가 채널 저장
            highest = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name])
            self.highest.append(highest)

            # 저가 채널 저장
            lowest = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name])
            self.lowest.append(lowest)

            # 볼린저밴드 저장 
            # bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb['length'][name], devfactor=self.p.bb['mult'][name])
            # self.bb_top.append(bb.lines.top)
            # self.bb_mid.append(bb.lines.mid)
            # self.bb_low.append(bb.lines.bot)

            # atr 저장
            atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr['length'][name])
            self.atrs.append(atr)

            # 자산 기록용 변수 셋팅
            self.order = None
            self.date_value = []
            self.my_assets = []

            # 승률 계산을 위함
            self.order_balance_list = []
            self.initial_asset = self.broker.getvalue()
            self.return_rate = 0
            self.total_trading_count = 0
            self.winning_trading_count = 0
            self.winning_rate = 0

    # logging data
    def log(self, txt):
        print(f'{txt}')

    def cancel_all(self, target_name=None):
        open_orders = self.broker.get_orders_open()
        for order in open_orders:
            if target_name and order.data._name != target_name:
                continue
            self.log(
                f"Cancelling Order: Ref: {order.ref}, Name: {order.data._name}, Price: {order.created.price}, Status: {order.status}")
            if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
                self.broker.cancel(order)
                self.log(f"Order Ref: {order.ref} for {order.data._name} is now cancelled")
            else:
                self.log(f"Order Ref: {order.ref} cannot be cancelled, Status: {order.status}")

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                self.total_trading_count += 1
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')

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
        self.order_balance_list.append([self.dates[0].datetime(0), account_value])
        self.date_value.append(self.dates[0].datetime(0))
        position_value = self.broker.getvalue()
        for i in range(1, len(self.datas)):
            position_value += self.getposition(self.datas[i]).size * self.lows[i][0]

        self.my_assets.append(position_value)

    def next(self):
        self.record_asset()  # 자산 기록

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # self.cancel_all(target_name=name)  # 미체결 주문 모두 취소
            open_orders = self.broker.get_orders_open()
            self.log(f'{self.dates[i].datetime(0)} => open order count : {len(open_orders)}')
            for order in open_orders:
                if order.data._name != name:
                    continue
                self.log(
                    f"Cancelling Order: Ref: {order.ref}, Name: {order.data._name}, Price: {order.created.price}, Status: {order.status}")
                if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
                    self.broker.cancel(order)
                    self.log(f"Order Ref: {order.ref} for {order.data._name} is now cancelled")
                else:
                    self.log(f"Order Ref: {order.ref} cannot be cancelled, Status: {order.status}")

            leverage = self.p.leverage[name]['long']
            date = self.dates[i].datetime(0)

            close = DataUtil.convert_to_decimal(self.closes[i][0])
            before_close = DataUtil.convert_to_decimal(self.closes[i][-1])

            atr = DataUtil.convert_to_decimal(self.atrs[i][0])
            highest = DataUtil.convert_to_decimal(self.highest[i][0])
            lowest = DataUtil.convert_to_decimal(self.lowest[i][0])
            self.log(f'{date} => open : {self.opens[i][0]} / high : {self.highs[i][0]} / low : {self.lows[i][0]} / close : {self.closes[i][0]} / highest : {self.highest[i][0]}')

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                stop_price = highest - atr * self.p.atr['constant'][name]
                stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.long_stop_prices[i] = stop_price

                qty = leverage * DataUtil.convert_to_decimal(self.broker.get_cash()) * self.p.risk[name]['long'] / Decimal('100') / abs(highest - stop_price)
                qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(
                    
                ), size=float(qty))
            if current_position_size > 0:
                if before_close > self.long_stop_prices[i] > close:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)
                    self.long_stop_prices[i] = Decimal('0')
                else:
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=current_position_size, price=float(lowest))

if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiLongAndShortV1)

    cerebro.broker.setcash(50000000)
    cerebro.broker.setcommission(commission=0.0005, leverage=1)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('Before Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    order_balance_list = strat.order_balance_list
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")