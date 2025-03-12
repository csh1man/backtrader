import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal

pairs = {
    'ETHUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'ONDOUSDT': DataUtils.CANDLE_TICK_1HOUR,
    '1000PEPEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    '1000SHIBUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'SEIUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'SUIUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'JUPUSDT':DataUtils.CANDLE_TICK_1HOUR,
    'INJUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'LDOUSDT': DataUtils.CANDLE_TICK_1HOUR,
}

company = DataUtils.COMPANY_BYBIT
leverage=4
class TailStrategyV3(bt.Strategy):
    params=dict(
        log=True,
        risk={
            'ETHUSDT': [Decimal('1.0'), Decimal('2.0')],
            'ONDOUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
            '1000PEPEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
            '1000SHIBUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
            'SEIUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
            'SUIUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
            'JUPUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
            'INJUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
            'LDOUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0')],
        },
        percent={
            'ONDOUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def' : [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear' : [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            },
            '1000PEPEUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def' : [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear' : [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            },
            '1000SHIBUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def' : [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear' : [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            },
            'SEIUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def' : [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear' : [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            },
            'SUIUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def' : [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear' : [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            },
            'JUPUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def' : [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear' : [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            },
            'INJUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear': [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            },
            'LDOUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('20.0'), Decimal('25.0')],
                'bear': [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0')]
            }
        },
        rsi_length={
            'ETHUSDT': 3,
            'ONDOUSDT': 3,
            '1000PEPEUSDT': 3,
            '1000SHIBUSDT': 3,
            'SEIUSDT': 3,
            'SUIUSDT': 3,
            'JUPUSDT': 3,
            'INJUSDT': 3,
            'LDOUSDT': 3,
        },
        rsi_limit={
            'ONDOUSDT': 70,
            '1000PEPEUSDT': 70,
            '1000SHIBUSDT': 70,
            'SEIUSDT': 70,
            'SUIUSDT': 70,
            'JUPUSDT': 70,
            'INJUSDT': 70,
            'LDOUSDT': 70,
        },
        high_band_length={
            'ETHUSDT': {
                'long': 120,
                'short': 30,
            },
            'ONDOUSDT': {
                'long': 60,
                'short': 200,
            },
            '1000PEPEUSDT': {
                'long': 60,
                'short': 200,
            },
            '1000SHIBUSDT': {
                'long': 60,
                'short': 200,
            },
            'SEIUSDT': {
                'long': 60,
                'short': 200,
            },
            'SUIUSDT': {
                'long': 60,
                'short': 200,
            },
            'JUPUSDT': {
                'long': 60,
                'short': 200,
            },
            'INJUSDT': {
                'long': 60,
                'short': 200,
            },
            'LDOUSDT': {
                'long': 60,
                'short': 200,
            },
        },
        low_band_length={
            'ETHUSDT': {
                'long': 60,
                'short': 200,
            },
            'ONDOUSDT': {
                'long': 60,
                'short': 200,
            },
            '1000PEPEUSDT': {
                'long': 60,
                'short': 200,
            },
            '1000SHIBUSDT': {
                'long': 60,
                'short': 200,
            },
            'SEIUSDT': {
                'long': 60,
                'short': 200,
            },
            'SUIUSDT': {
                'long': 60,
                'short': 200,
            },
            'JUPUSDT': {
                'long': 60,
                'short': 200,
            },
            'INJUSDT': {
                'long': 60,
                'short': 200,
            },
            'LDOUSDT': {
                'long': 60,
                'short': 200,
            },
        },
        high_band_const={
            'ETHUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'ONDOUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            '1000PEPEUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            '1000SHIBUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'SEIUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'SUIUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'JUPUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'INJUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'LDOUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
        },
        low_band_const={
            'ETHUSDT': {
                'long': Decimal('20'),
                'short': Decimal('5')
            },
            'ONDOUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            '1000PEPEUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            '1000SHIBUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'SEIUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'SUIUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'JUPUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'INJUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
            'LDOUSDT': {
                'long': Decimal('0'),
                'short': Decimal('55')
            },
        },
        check_index={ # 'bull' : 몇개 캔들이전보다 많이 올라서 급락할 가능성이 있는 지, 'bear' : 몇개 캔들이전보다 많이 떨어져서 더이상 떨어지지않을 가능성이 존재하는 건지
            'ONDOUSDT':{
              'bull': 5,
              'bear': 5
            },
            '1000PEPEUSDT': {
                'bull': 5,
                'bear': 5
            },
            '1000SHIBUSDT': {
                'bull': 5,
                'bear': 5
            },
            'SEIUSDT': {
                'bull': 5,
                'bear': 5
            },
            'SUIUSDT': {
                'bull': 5,
                'bear': 5
            },
            'JUPUSDT': {
                'bull': 5,
                'bear': 5
            },
            'INJUSDT': {
                'bull': 5,
                'bear': 5
            },
            'LDOUSDT': {
                'bull': 5,
                'bear': 5
            },
        },
        check_percent={ # 'bull' : 얼마나 떨어져서 더이상 떨어지지 않을 지, 'bear': 얼마나 올라서 급락할 가능성이 있는 지
            'ONDOUSDT': {
                'bull': 5,
                'bear': 5,
            },
            '1000PEPEUSDT': {
                'bull': 15,
                'bear': 5,
            },
            '1000SHIBUSDT': {
                'bull': 20,
                'bear': 5,
            },
            'SEIUSDT': {
                'bull': 5,
                'bear': 5,
            },
            'SUIUSDT': {
                'bull': 5,
                'bear': 5,
            },
            'JUPUSDT': {
                'bull': 5,
                'bear': 5,
            },
            'INJUSDT': {
                'bull': 5,
                'bear': 5,
            },
            'LDOUSDT': {
                'bull': 5,
                'bear': 5,
            }
        },
        tick_size={
            'ETHUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.01'),
                DataUtils.COMPANY_BYBIT : Decimal('0.01')
            },
            'ONDOUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.0001000'),
                DataUtils.COMPANY_BYBIT: Decimal('0.0001')
            },
            '1000PEPEUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.0000010'),
                DataUtils.COMPANY_BYBIT: Decimal('0.0000010')
            },
            '1000SHIBUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.000001'),
                DataUtils.COMPANY_BYBIT: Decimal('0.000001')
            },
            'SEIUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.0001000'),
                DataUtils.COMPANY_BYBIT: Decimal('0.00010')
            },
            'SUIUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.000100'),
                DataUtils.COMPANY_BYBIT: Decimal('0.00010')
            },
            'JUPUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.0001000'),
                DataUtils.COMPANY_BYBIT: Decimal('0.0001')
            },
            'INJUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('0.001000'),
                DataUtils.COMPANY_BYBIT: Decimal('0.0010')
            },
            'LDOUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('0.000100'),
                DataUtils.COMPANY_BYBIT: Decimal('0.0005')
            }
        },
        step_size={
            'ETHUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('0.001'),
                DataUtils.COMPANY_BYBIT: Decimal('0.01')
            },
            'ONDOUSDT': {
                DataUtils.COMPANY_BINANCE : Decimal('0.1'),
                DataUtils.COMPANY_BYBIT: Decimal('1')
            },
            '1000PEPEUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('1'),
                DataUtils.COMPANY_BYBIT: Decimal('100')
            },
            '1000SHIBUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('1'),
                DataUtils.COMPANY_BYBIT: Decimal('10')
            },
            'SEIUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('1'),
                DataUtils.COMPANY_BYBIT: Decimal('1')
            },
            'SUIUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('0.1'),
                DataUtils.COMPANY_BYBIT: Decimal('10')
            },
            'JUPUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('1'),
                DataUtils.COMPANY_BYBIT: Decimal('1')
            },
            'INJUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('0.1'),
                DataUtils.COMPANY_BYBIT: Decimal('0.1')
            },
            'LDOUSDT': {
                DataUtils.COMPANY_BINANCE: Decimal('1'),
                DataUtils.COMPANY_BYBIT: Decimal('0.1')
            }
        }
    )

    def log(self, txt):
        if self.p.log:
            print(f'{txt}')

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.rsi = []

        self.long_high_bands = []
        self.long_low_bands = []
        self.long_stop_prices = []

        self.short_high_bands = []
        self.short_low_bands = []
        self.short_stop_prices = []

        self.order = None
        self.date_value = []
        self.my_assets = []

        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
            self.long_stop_prices.append(Decimal('0'))
            self.short_stop_prices.append(Decimal('0'))

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
            self.rsi.append(rsi)

            long_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['long'])
            self.long_high_bands.append(long_high_band)

            long_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['long'])
            self.long_low_bands.append(long_low_band)

            short_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['short'])
            self.short_high_bands.append(short_high_band)

            short_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['short'])
            self.short_low_bands.append(short_low_band)


    def cancel_all(self, target_name=None):
        open_orders = self.broker.get_orders_open()
        for order in open_orders:
            if target_name and order.data._name != target_name:
                continue
            if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
                self.broker.cancel(order)

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
                         f'가격:{order.created.price:.4f}\n')

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
        self.record_asset()

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(target_name=name)

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            if name == 'ETHUSDT':

                long_high_band = DataUtils.convert_to_decimal(self.long_high_bands[i][0])
                long_low_band = DataUtils.convert_to_decimal(self.long_low_bands[i][0])

                adj_long_high_band = long_high_band - (long_high_band-long_low_band) * (self.p.high_band_const[name]['long'] / Decimal('100'))
                adj_long_high_band = int(adj_long_high_band / self.p.tick_size[name][company]) * self.p.tick_size[name][company]

                adj_long_low_band = long_low_band + (long_high_band - long_low_band) * (self.p.low_band_const[name]['long'] / Decimal('100'))
                adj_long_low_band = int(adj_long_low_band / self.p.tick_size[name][company]) * self.p.tick_size[name][company]

                short_high_band = DataUtils.convert_to_decimal(self.short_high_bands[i][0])
                short_low_band = DataUtils.convert_to_decimal(self.short_low_bands[i][0])

                adj_short_high_band = short_high_band - (short_high_band-short_low_band) * (self.p.high_band_const[name]['short'] / Decimal('100'))
                adj_short_high_band = int(adj_short_high_band / self.p.tick_size[name][company]) * self.p.tick_size[name][company]

                adj_short_low_band = short_low_band + (short_high_band - short_low_band) * (self.p.low_band_const[name]['short'] / Decimal('100'))
                adj_short_low_band = int(adj_short_low_band / self.p.tick_size[name][company]) * self.p.tick_size[name][company]

                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size == 0:
                    self.long_stop_prices[i] = adj_long_low_band
                    self.short_stop_prices[i] = adj_short_high_band

                    equity = DataUtils.convert_to_decimal(self.broker.getvalue())
                    long_qty = equity * (self.p.risk[name][0] / Decimal('100')) / abs(adj_long_high_band-adj_long_low_band)
                    long_qty = int(long_qty / self.p.step_size[name][company]) * self.p.step_size[name][company]
                    self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=float(long_qty), price=float(adj_long_high_band))

                    qty = equity * (self.p.risk[name][1] / Decimal('100')) / abs(adj_short_low_band-adj_short_high_band)
                    qty = int(qty / self.p.step_size[name][company]) * self.p.step_size[name][company]
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(qty), price=float(adj_short_low_band))
                elif current_position_size > 0:
                    if DataUtils.convert_to_decimal(self.closes[i][-1]) <= self.long_stop_prices[i] < DataUtils.convert_to_decimal(self.closes[i][0]):
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                    else:
                        self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=abs(current_position_size), price=float(adj_long_low_band))
                elif current_position_size < 0:
                    if DataUtils.convert_to_decimal(self.closes[i][0]) > self.short_stop_prices[i] >= DataUtils.convert_to_decimal(self.closes[i][-1]):
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                    else:
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=abs(current_position_size), price=float(adj_short_high_band))

            else:
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size > 0:
                    avg_entry_price = self.getposition(self.pairs[i]).price
                    # if self.closes[i][0] >= avg_entry_price and self.rsi[i][0] >= self.p.rsi_limit[name]:
                    if self.closes[i][0] >= avg_entry_price and self.rsi[i][0] >= self.p.rsi_limit[name]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)

                bull_check_idx = self.p.check_index[name]['bull']
                bear_check_idx = self.p.check_index[name]['bear']

                # n개 이전 캔들보다 x% 이상 상승했다면 급락할 가능성이 있으므로 간격을 넓혀야한다.
                bear_condition = ((self.closes[i][0] > self.closes[i][-bear_check_idx])
                                  and (self.closes[i][0] - self.closes[i][-bear_check_idx]) * 100 / self.closes[i][-bear_check_idx] >= self.p.check_percent[name]['bear'])

                # n개 이전 캔들보다 y% 이상 하락했다면 더이상 크게 떨어지지 않을 가능성이 있으므로 간격을 좁힌다.
                bull_condition = ((self.closes[i][0] < self.closes[i][-bull_check_idx])
                                 and (self.closes[i][-bull_check_idx] - self.closes[i][0]) * 100 / self.closes[i][0] >= self.p.check_percent[name]['bull'])

                percents = self.p.percent[name]['def']

                if bear_condition:
                    percents = self.p.percent[name]['bear']
                elif bull_condition:
                    percents = self.p.percent[name]['bull']

                equity = DataUtils.convert_to_decimal(self.broker.getvalue())
                for j in range(0, len(self.p.risk[name])):
                    percent = percents[j]
                    price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1') - percent / Decimal('100'))
                    price = int(price / self.p.tick_size[name][company]) * self.p.tick_size[name][company]

                    risk = self.p.risk[name][j]
                    qty = equity * risk  / Decimal('100') / price
                    qty = int(qty / self.p.step_size[name][company]) * self.p.step_size[name][company]

                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty), price=float(price))


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TailStrategyV3)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.002, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, company, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    before_balance = cerebro.broker.getvalue()
    print('Before Portfolio Value: %.2f' % before_balance)
    results = cerebro.run()
    strat = results[0]
    after_balance = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % after_balance)

    # 수익률 계산
    return_percentage = ((after_balance - before_balance) / before_balance) * 100
    print('Strategy Return: %.2f%%' % return_percentage)

    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    order_balance_list = strat.order_balance_list
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")

    # file_name = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
    # file_name = "/Users/tjgus/Desktop/project/krtrade/backData/result/"
    file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/" + company + "-"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "TailCatchV3"

    strat = results[0]
    order_balance_list = strat.order_balance_list
    df = pd.DataFrame(order_balance_list, columns=["date", "value"])
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    df = df.sort_values('value', ascending=True).drop_duplicates('date').sort_index()
    df['value'] = df['value'].astype('float64')
    df['value'] = df['value'].pct_change()
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna()
    df = df.set_index('date')
    df.index.name = 'date'
    qs.reports.html(df['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)
