import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'ETHUSDT': DataUtil.CANDLE_TICK_4HOUR
}


class TrendFollowV1(bt.Strategy):
    params = dict(
        risk={
            'ETHUSDT':{
                'long': Decimal('2'),
                'short': Decimal('2')
            }
        },
        high_band_length={
            'ETHUSDT': {
                'long': 30,
                'short': 5,
            }
        },
        low_band_length={
            'ETHUSDT': {
                'long': 15,
                'short': 20
            }
        },
        high_band_constant={
            'ETHUSDT': {
                'long': 10,
                'short': 50,
            }
        },
        low_band_constant={
            'ETHUSDT': {
                'long': 5,
                'short': 5
            }
        },
        atr_length={
            'ETHUSDT':{
                'long': 10,
                'short': 10
            }
        },
        atr_constant={
            'ETHUSDT': {
                'long': Decimal('1.0'),
                'short': Decimal('2.0')
            }
        },
        tick_size={
            'ETHUSDT': Decimal('0.01'),
        },
        step_size={
            'ETHUSDT': Decimal('0.01'),
        }
    )

    def log(self, txt):
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

            long_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['long'])
            self.long_high_bands.append(long_high_band)

            long_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['long'])
            self.long_low_bands.append(long_low_band)

            short_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['short'])
            self.short_high_bands.append(short_high_band)

            short_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['short'])
            self.short_low_bands.append(short_low_band)

            long_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name]['long'])
            self.long_atrs.append(long_atr)

            short_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name]['short'])
            self.short_atrs.append(short_atr)

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
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(target_name=name)

            long_high_band = DataUtil.convert_to_decimal(self.long_high_bands[i][0])
            long_low_band = DataUtil.convert_to_decimal(self.long_low_bands[i][0])

            long_adj_high_band = long_high_band - (long_high_band - long_low_band) * self.p.high_band_constant[name]['long'] / Decimal('100')
            long_adj_high_band = int(long_adj_high_band / self.p.tick_size[name]) * self.p.tick_size[name]

            long_adj_low_band = long_low_band + (long_high_band - long_low_band) * self.p.low_band_constant[name]['long'] / Decimal('100')
            long_adj_low_band = int(long_adj_low_band / self.p.tick_size[name]) * self.p.tick_size[name]

            short_high_band = DataUtil.convert_to_decimal(self.short_high_bands[i][0])
            short_low_band = DataUtil.convert_to_decimal(self.short_low_bands[i][0])

            short_adj_high_band = short_high_band - (short_high_band - short_low_band) * self.p.high_band_constant[name]['short'] / Decimal('100')
            short_adj_high_band = int(short_adj_high_band / self.p.tick_size[name]) * self.p.tick_size[name]

            short_adj_low_band = short_low_band + (short_high_band - short_low_band) * self.p.low_band_constant[name]['short'] / Decimal('100')
            short_adj_low_band = int(short_adj_low_band / self.p.tick_size[name]) * self.p.tick_size[name]

            long_atr = DataUtil.convert_to_decimal(self.long_atrs[i][0])
            short_atr = DataUtil.convert_to_decimal(self.short_atrs[i][0])

            before_close = DataUtil.convert_to_decimal(self.closes[i][-1])
            current_close = DataUtil.convert_to_decimal(self.closes[i][0])

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                equity = DataUtil.convert_to_decimal(self.broker.getvalue())

                long_stop_price = long_adj_high_band - long_atr * self.p.atr_constant[name]['long']
                long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.long_stop_prices[i] = long_stop_price

                long_qty = equity * (self.p.risk[name]['long'] / Decimal('100')) / abs(long_adj_high_band - long_stop_price)
                if long_qty * long_adj_high_band >= equity:
                    long_qty = equity * Decimal('0.98') / long_adj_high_band
                long_qty = int(long_qty / self.p.step_size[name]) * self.p.step_size[name]
                self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(long_adj_high_band), size=float(long_qty))

                short_stop_price = short_adj_low_band + short_atr * self.p.atr_constant[name]['short']
                short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.short_stop_prices[i] = short_stop_price

                short_qty = equity * (self.p.risk[name]['short'] / Decimal('100')) / abs(short_adj_low_band - short_stop_price)
                if short_qty * short_adj_low_band >= equity:
                    short_qty = equity * Decimal('0.98') / short_adj_low_band
                short_qty = int(short_qty / self.p.step_size[name]) * self.p.step_size[name]
                self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], price=float(short_adj_low_band), size=float(short_qty))
            elif current_position_size > 0:
                if before_close >= self.long_stop_prices[i] > current_close:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
                else:
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(current_position_size), price=float(long_adj_low_band))
            elif current_position_size < 0:
                if before_close < self.short_stop_prices[i] <= current_close:
                    self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(abs(current_position_size)))
                else:
                    self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=float(abs(current_position_size)), price=float(short_adj_high_band))

if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendFollowV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.0005, leverage=4)
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

