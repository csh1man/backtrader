import backtrader as bt
import pandas as pd
import quantstats as qs
import math

from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'ETHUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'SOLUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
    '1000PEPEUSDT': DataUtil.CANDLE_TICK_1HOUR,
    '1000SHIBUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'ONDOUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'ORDIUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'SUIUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'TAOUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'IMXUSDT':DataUtil.CANDLE_TICK_1HOUR,
}

leverage=5

class BinanceTailCatchWithTrendFollowV3(bt.Strategy):
    params=dict(
        log=True,
        risks={
            'ETHUSDT': [Decimal('1.0'), Decimal('2.0')],
            'BTCUSDT': [Decimal('1.0'), Decimal('1.5')],
            'SOLUSDT': [Decimal('1.0'), Decimal('1.5')],
            'BCHUSDT': [Decimal('1.5'), Decimal('1.5')],
            '1000PEPEUSDT': [Decimal('2'), Decimal('4'), Decimal('4'), Decimal('4'), Decimal('8')],
            '1000SHIBUSDT': [Decimal('2'), Decimal('4'), Decimal('4'), Decimal('4'), Decimal('8')],
            'ONDOUSDT': [Decimal('2'), Decimal('4'), Decimal('4'), Decimal('4'), Decimal('8')],
            'ORDIUSDT': [Decimal('2'), Decimal('4'), Decimal('4'), Decimal('4'), Decimal('8')],
            'SUIUSDT': [Decimal('2'), Decimal('4'), Decimal('4'), Decimal('4'), Decimal('8')],
            'TAOUSDT': [Decimal('2'), Decimal('4'), Decimal('4'), Decimal('4'), Decimal('8')],
            'IMXUSDT': [Decimal('2'), Decimal('4'), Decimal('4'), Decimal('4'), Decimal('8')],
        },
        entry_mode={
          'BTCUSDT': 0,
          'ETHUSDT': 2,
          'SOLUSDT': 0,
          'BCHUSDT': 0,
        },
        atr_length={
            'BTCUSDT': [10, 10],
            'ETHUSDT': [10, 10],
            'SOLUSDT': [10, 10],
            'BCHUSDT': [10, 10],
            '1000PEPEUSDT': [10, 10],
            '1000SHIBUSDT': [10, 10],
            'ONDOUSDT': [10, 10],
            'ORDIUSDT': [10, 10],
            'SUIUSDT': [10, 10],
            'TAOUSDT': [10, 10],
            'IMXUSDT': [10, 10],
        },
        atr_constant={
            'BTCUSDT': [Decimal('2.0'), Decimal('2.0')],
            'ETHUSDT': [Decimal('2.0'), Decimal('2.0')],
            'SOLUSDT': [Decimal('2.0'), Decimal('2.0')],
            'BCHUSDT': [Decimal('2.0'), Decimal('2.0')],
            '1000PEPEUSDT': [Decimal('1.0'), Decimal('1.0')],
            '1000SHIBUSDT': [Decimal('1.0'), Decimal('1.0')],
            'ONDOUSDT': [Decimal('1.0'), Decimal('1.0')],
            'ORDIUSDT': [Decimal('1.0'), Decimal('1.0')],
            'SUIUSDT': [Decimal('1.0'), Decimal('1.0')],
            'TAOUSDT': [Decimal('1.0'), Decimal('1.0')],
            'IMXUSDT': [Decimal('1.0'), Decimal('1.0')],
        },
        high_band_length={
            'BTCUSDT': [120, 20],
            'ETHUSDT': [160, 20],
            'SOLUSDT': [120, 15],
            'BCHUSDT': [160, 60],
            '1000PEPEUSDT': [40, 15],
            '1000SHIBUSDT': [40, 15],
            'ONDOUSDT': [40, 15],
            'ORDIUSDT': [40, 15],
            'SUIUSDT': [40, 15],
            'TAOUSDT': [40, 15],
            'IMXUSDT': [40, 15],
        },
        low_band_length={
            'BTCUSDT': [60, 80],
            'ETHUSDT': [80, 80],
            'SOLUSDT': [80, 30],
            'BCHUSDT': [80, 200],
            '1000PEPEUSDT': [15, 50],
            '1000SHIBUSDT': [15, 50],
            'ONDOUSDT': [40, 15],
            'ORDIUSDT': [40, 15],
            'SUIUSDT': [40, 15],
            'TAOUSDT': [40, 15],
            'IMXUSDT': [40, 15],
        },
        high_band_constant={
            'BTCUSDT': [Decimal('20'), Decimal('1')],
            'ETHUSDT': [Decimal('5'), Decimal('50')],
            'SOLUSDT': [Decimal('10'), Decimal('5')],
            'BCHUSDT': [Decimal('10'), Decimal('50')],
        },
        low_band_constant={
            'BTCUSDT': [Decimal('20'), Decimal('1')],
            'ETHUSDT': [Decimal('5'), Decimal('5')],
            'SOLUSDT': [Decimal('10'), Decimal('5')],
            'BCHUSDT': [Decimal('20'), Decimal('0')],
        },
        percent={
            '1000PEPEUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            },
            '1000SHIBUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'ONDOUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'ORDIUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'SUIUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'TAOUSDT': {
                'bull' : [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'IMXUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            }
        },
        rsi_length={
            'ETHUSDT': 2,
            'BTCUSDT': 2,
            'SOLUSDT': 2,
            'BCHUSDT': 2,
            '1000PEPEUSDT': 2,
            '1000SHIBUSDT': 2,
            'ONDOUSDT': 2,
            'ORDIUSDT': 2,
            'SUIUSDT': 2,
            'TAOUSDT': 2,
            'IMXUSDT': 2,
        },
        rsi_limit={
            'ETHUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'SOLUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'BTCUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'BCHUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            '1000PEPEUSDT': {
                'exit': 70,
                'bull' : 70,
                'bear': 30,
            },
            '1000SHIBUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'ONDOUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'ORDIUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'SUIUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'TAOUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            },
            'IMXUSDT': {
                'exit': 70,
                'bull': 70,
                'bear': 30,
            }
        },
        tick_size={
            'BTCUSDT': Decimal('0.10'),
            'ETHUSDT': Decimal('0.01'),
            'SOLUSDT': Decimal('0.0100'),
            'BCHUSDT': Decimal('0.01'),
            '1000PEPEUSDT': Decimal('0.0000001'),
            '1000SHIBUSDT': Decimal('0.000001'),
            'ONDOUSDT': Decimal('0.0001000'),
            'ORDIUSDT': Decimal('0.001000'),
            'SUIUSDT': Decimal('0.000100'),
            'TAOUSDT': Decimal('0.01'),
            'IMXUSDT': Decimal('0.0001')
        },
        step_size={
            'BTCUSDT': Decimal('0.001'),
            'ETHUSDT': Decimal('0.001'),
            'SOLUSDT': Decimal('1'),
            'BCHUSDT': Decimal('0.001'),
            '1000PEPEUSDT': Decimal('1'),
            '1000SHIBUSDT': Decimal('1'),
            'ONDOUSDT': Decimal('0.1'),
            'ORDIUSDT': Decimal('0.1'),
            'SUIUSDT': Decimal('0.1'),
            'TAOUSDT': Decimal('0.001'),
            'IMXUSDT': Decimal('1')
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

        self.long_stop_prices = []
        self.short_stop_prices = []

        self.long_high_bands = []
        self.long_low_bands = []

        self.short_high_bands = []
        self.short_low_bands = []

        self.long_atrs = []
        self.short_atrs = []

        self.rsi = []

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

        for i in range(0, len(self.pairs)):
            name = self.names[i]

            long_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name][0])
            self.long_high_bands.append(long_high_band)

            long_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name][0])
            self.long_low_bands.append(long_low_band)

            short_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name][1])
            self.short_high_bands.append(short_high_band)

            short_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name][1])
            self.short_low_bands.append(short_low_band)

            long_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name][0])
            self.long_atrs.append(long_atr)

            short_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name][1])
            self.short_atrs.append(short_atr)

            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
            self.rsi.append(rsi)


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
    def stop(self):
        self.log(f'전체 트레이딩 횟수 : {self.total_trading_count}')

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

        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            tick_size = self.p.tick_size[name]
            step_size = self.p.step_size[name]

            if name in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BCHUSDT']:
                long_atr = DataUtil.convert_to_decimal(self.long_atrs[i][0])
                long_high_band = DataUtil.convert_to_decimal(self.long_high_bands[i][0])
                long_low_band = DataUtil.convert_to_decimal(self.long_low_bands[i][0])
                long_high_band_constant = self.p.high_band_constant[name][0]
                long_low_band_constant = self.p.low_band_constant[name][0]

                long_adj_high_band = long_high_band - (
                            long_high_band - long_low_band) * long_high_band_constant / Decimal('100')
                long_adj_high_band = int(long_adj_high_band / tick_size) * tick_size

                long_adj_low_band = long_low_band + (long_high_band - long_low_band) * long_low_band_constant / Decimal(
                    '100')
                long_adj_low_band = int(long_adj_low_band / tick_size) * tick_size

                short_atr = DataUtil.convert_to_decimal(self.short_atrs[i][0])
                short_high_band = DataUtil.convert_to_decimal(self.short_high_bands[i][0])
                short_low_band = DataUtil.convert_to_decimal(self.short_low_bands[i][0])
                short_high_band_constant = self.p.high_band_constant[name][1]
                short_low_band_constant = self.p.low_band_constant[name][1]

                short_adj_high_band = short_high_band - (
                            short_high_band - short_low_band) * short_high_band_constant / Decimal('100')
                short_adj_high_band = int(short_adj_high_band / tick_size) * tick_size

                short_adj_low_band = short_low_band + (
                            short_high_band - short_low_band) * short_low_band_constant / Decimal('100')
                short_adj_low_band = int(short_adj_low_band / tick_size) * tick_size

                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size == 0:
                    long_stop_price = long_adj_high_band - long_atr * self.p.atr_constant[name][0]
                    long_stop_price = int(long_stop_price / tick_size) * tick_size
                    self.long_stop_prices[i] = long_stop_price

                    long_qty = equity * (self.p.risks[name][0] / Decimal('100')) / abs(
                        long_adj_high_band - long_stop_price)
                    long_qty = int(long_qty / step_size) * step_size

                    short_stop_price = short_adj_low_band + short_atr * self.p.atr_constant[name][1]
                    short_stop_price = int(short_stop_price / tick_size) * tick_size
                    self.short_stop_prices[i] = short_stop_price

                    short_qty = equity * (self.p.risks[name][1] / Decimal('100')) / abs(
                        short_adj_low_band - short_stop_price)
                    short_qty = int(short_qty / step_size) * step_size

                    current_cash = DataUtil.convert_to_decimal(self.broker.get_cash())
                    if self.p.entry_mode[name] in [0, 2]:
                        if long_qty * long_adj_high_band / Decimal(leverage) >= current_cash:
                            long_qty = Decimal(leverage) * current_cash / long_adj_high_band
                            long_qty = int(long_qty / step_size) * step_size
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i],
                                              price=float(long_adj_high_band),
                                              size=float(long_qty))
                    if self.p.entry_mode[name] in [1, 2]:
                        if short_qty * short_adj_low_band / Decimal(leverage) >= current_cash:
                            short_qty = Decimal(leverage) * current_cash / short_adj_low_band
                            short_qty = int(short_qty / step_size) * step_size
                        self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i],
                                               price=float(short_adj_low_band),
                                               size=float(short_qty))
                elif current_position_size > 0:
                    long_stop_price = self.long_stop_prices[i]
                    if DataUtil.convert_to_decimal(self.closes[i][0]) < long_stop_price:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i],
                                               size=float(current_position_size))
                    else:
                        self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i],
                                               price=float(long_adj_low_band), size=float(current_position_size))
                elif current_position_size < 0:
                    short_stop_price = self.short_stop_prices[i]
                    if DataUtil.convert_to_decimal(
                            self.closes[i][-1]) < short_stop_price <= DataUtil.convert_to_decimal(self.closes[i][0]):
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i],
                                              size=float(abs(current_position_size)))
                    else:
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i],
                                              price=float(short_adj_high_band), size=float(abs(current_position_size)))

            else:
                # 역추세 페어 필드
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size > 0 :
                    if self.closes[i][0] >= self.getposition(self.pairs[i]).price:
                        if self.rsi[i][0] >= self.p.rsi_limit[name]['exit']:
                            self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))

                percents = self.p.percent[name]['def']
                if self.rsi[i][0] >= self.p.rsi_limit[name]['bull']:
                    percents = self.p.percent[name]['bull']
                elif self.rsi[i][0] < self.p.rsi_limit[name]['bear']:
                    percents = self.p.percent[name]['bear']

                equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                for j in range(0, len(percents)):
                    risk = self.p.risks[name][j]
                    percent = percents[j]
                    price = DataUtil.convert_to_decimal(self.closes[i][0]) * (Decimal('1') - percent / Decimal('100'))
                    price = int(price / tick_size) * tick_size
                    qty = equity * risk / Decimal('100') / price
                    qty = int(qty / step_size) * step_size
                    if DataUtil.convert_to_decimal(self.broker.get_cash()) >= qty * price / Decimal(leverage) :
                        self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price), size=float(qty))




if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BinanceTailCatchWithTrendFollowV3)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.0005, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BINANCE, pair, tick_kind)
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
    file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "BinanceTailCatchWithTrendFollowV3"

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