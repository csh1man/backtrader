import backtrader as bt
import pandas as pd
import quantstats as qs
import math
from util.Util import DataUtils
from decimal import Decimal

pairs = {
    'BTCUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'ETHUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'SOLUSDT': DataUtils.CANDLE_TICK_1HOUR,
    '1000PEPEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'JASMYUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'SEIUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'STXUSDT': DataUtils.CANDLE_TICK_1HOUR,
    '1000SHIBUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'INJUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'ONDOUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'IMXUSDT': DataUtil.CANDLE_TICK_1HOUR
}

class TailCatchV3(bt.Strategy):
    params=dict(
        log=True,
        risk={
            'BTCUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'ETHUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'SOLUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'ONDOUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            '1000PEPEUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'SEIUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'STXUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            '1000SHIBUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'INJUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'JASMYUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'IMXUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
        },
        percent={
            'BTCUSDT': {
                'bullish': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'ETHUSDT': {
                'bullish': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'SOLUSDT': {
                'bullish': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'ONDOUSDT': {
                'bullish': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            '1000PEPEUSDT': {
                'bullish': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('20.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'SEIUSDT': {
                'bullish': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'default': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'STXUSDT': {
                'bullish': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'default': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            '1000SHIBUSDT': {
                'bullish': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'INJUSDT': {
                'bullish': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'JASMYUSDT': {
                'bullish': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
            'IMXUSDT': {
                'bullish': [Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'default': [Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0')],
                'bearish': [Decimal('4.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('20.0')]
            },
        },
        rsi_length={
            'BTCUSDT': 3,
            'ETHUSDT': 3,
            'SOLUSDT': 3,
            'ONDOUSDT': 3,
            '1000PEPEUSDT': 3,
            'SEIUSDT': 3,
            'STXUSDT': 3,
            '1000SHIBUSDT': 3,
            'INJUSDT': 3,
            'JASMYUSDT': 3,
            'IMXUSDT': 3,
        },
        rsi_limit={
            'BTCUSDT': 60,
            'ETHUSDT': 60,
            'SOLUSDT': 60,
            'ONDOUSDT': 60,
            '1000PEPEUSDT': 60,
            'SEIUSDT': 60,
            'STXUSDT': 60,
            '1000SHIBUSDT': 60,
            'INJUSDT': 60,
            'JASMYUSDT': 70,
            'IMXUSDT': 60,
        },
        high_band_length={
            'BTCUSDT': 3,
            'ETHUSDT': 3,
            'SOLUSDT': 3,
            'ONDOUSDT': 3,
            '1000PEPEUSDT': 3,
            'SEIUSDT': 3,
            'STXUSDT': 3,
            '1000SHIBUSDT': 3,
            'INJUSDT': 3,
            'JASMYUSDT': 3,
            'IMXUSDT': 3,
        },
        low_band_length={
            'BTCUSDT': 3,
            'ETHUSDT': 3,
            'SOLUSDT': 3,
            'ONDOUSDT': 3,
            '1000PEPEUSDT': 3,
            'SEIUSDT': 3,
            'STXUSDT': 3,
            '1000SHIBUSDT': 3,
            'INJUSDT': 3,
            'JASMYUSDT': 3,
            'IMXUSDT': 3,
        },
        bb_length={
            'BTCUSDT': 80,
            'ETHUSDT': 80,
            'SOLUSDT': 80,
            'ONDOUSDT': 80,
            '1000PEPEUSDT': 80,
            'SEIUSDT': 80,
            'STXUSDT': 80,
            '1000SHIBUSDT': 80,
            'INJUSDT': 80,
            'JASMYUSDT': 80,
            'IMXUSDT': 80,
        },
        bb_mult={
            'BTCUSDT': 1.0,
            'ETHUSDT': 1.0,
            'SOLUSDT': 1.0,
            'ONDOUSDT': 1.0,
            '1000PEPEUSDT': 1.0,
            'SEIUSDT': 1.0,
            'STXUSDT': 1.0,
            '1000SHIBUSDT': 1.0,
            'INJUSDT': 1.0,
            'JASMYUSDT': 1.0,
            'IMXUSDT': 1.0,
        },
        atr_length={
            'BTCUSDT': 10,
            'ETHUSDT': 10,
            'SOLUSDT': 10,
            'ONDOUSDT': 10,
            '1000PEPEUSDT': 10,
            'SEIUSDT': 10,
            'STXUSDT': 10,
            '1000SHIBUSDT': 10,
            'INJUSDT': 10,
            'JASMYUSDT': 10,
            'IMXUSDT': 10,
        },
        atr_constant={
            'BTCUSDT': Decimal('2.0'),
            'ETHUSDT': Decimal('2.0'),
            'SOLUSDT': Decimal('2.0'),
            'ONDOUSDT': Decimal('2.0'),
            '1000PEPEUSDT': Decimal('2.0'),
            'SEIUSDT': Decimal('2.0'),
            'STXUSDT': Decimal('2.0'),
            '1000SHIBUSDT': Decimal('2.0'),
            'INJUSDT': Decimal('2.0'),
            'JASMYUSDT': Decimal('2.0'),
            'IMXUSDT': Decimal('2.0'),
        },
        tick_size={
            'BTCUSDT': Decimal('0.10'),
            'ETHUSDT': Decimal('0.01'),
            'SOLUSDT': Decimal('0.0100'),
            'ONDOUSDT': Decimal('0.0001000'),
            '1000PEPEUSDT': Decimal('0.0000001'),
            'SEIUSDT': Decimal('0.0001000'),
            'STXUSDT': Decimal('0.0001000'),
            '1000SHIBUSDT': Decimal('0.000001'),
            'INJUSDT': Decimal('0.001000'),
            'JASMYUSDT': Decimal('0.000001'),
            'IMXUSDT': Decimal('0.0001')
        },
        step_size={
            'BTCUSDT': Decimal('0.001'),
            'ETHUSDT': Decimal('0.001'),
            'SOLUSDT': Decimal('1'),
            'ONDOUSDT': Decimal('0.1'),
            'XRPUSDT': Decimal('0.1'),
            'DOGEUSDT': Decimal('1'),
            '1000PEPEUSDT': Decimal('1'),
            'SEIUSDT': Decimal('1'),
            'STXUSDT': Decimal('1'),
            '1000SHIBUSDT': Decimal('1'),
            'INJUSDT': Decimal('0.1'),
            'JASMYUSDT': Decimal('1'),
            'IMXUSDT': Decimal('1')
        }
    )

    def log(self, txt):
        if self.p.log:
            print(txt)

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []

        self.high_band = []
        self.low_band = []
        self.rsi = []
        self.atr = []
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []

        self.bullish = []
        self.default = []
        self.bearish = []
        self.stop_price = []

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
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
            self.bullish.append(0)
            self.default.append(0)
            self.bearish.append(0)
            self.stop_price.append(Decimal('-1'))

        for i in range(0, len(self.pairs)):
            name = self.names[i]

            high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name])
            self.high_band.append(high_band)

            low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name])
            self.low_band.append(low_band)

            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
            self.rsi.append(rsi)

            atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name])
            self.atr.append(atr)

            bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_length[name], devfactor=self.p.bb_mult[name])
            self.bb_top.append(bb.lines.top)
            self.bb_mid.append(bb.lines.mid)
            self.bb_bot.append(bb.lines.bot)

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
                data_idx = self.pairs.index(order.data)
                if self.closes[data_idx][0] >= self.high_band[data_idx][-1]:
                    self.bullish[data_idx] += 1
                elif self.low_band[data_idx][-1] <= self.closes[data_idx][0] < self.high_band[data_idx][-1]:
                    self.default[data_idx] += 1
                else:
                    self.bearish[data_idx] += 1
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

    def stop(self):
        self.log(f'전체 트레이딩 횟수 : {self.total_trading_count}')
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.log(f'[{name}] bullish : [{self.bullish[i]}], default : [{self.default[i]}], bearish : [{self.bearish[i]}]')


    def next(self):
        self.record_asset()
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(target_name=name)

            tick_size = self.p.tick_size[name]
            step_size = self.p.step_size[name]

            prices = []
            mode = "default"
            for j in range(0, len(self.p.percent[name])):
                if self.closes[i][0] >= self.high_band[i][-1]:
                    mode = "bullish"
                elif self.low_band[i][-1] <= self.closes[i][0] < self.high_band[i][-1]:
                    mode = "default"
                elif self.closes[i][0] < self.low_band[i][-1]:
                    mode = "bearish"

                percent = self.p.percent[name][mode][j]
                price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1') - percent / Decimal('100'))
                price = int(price / tick_size) * tick_size
                prices.append(price)

            current_position_size = self.getposition(self.pairs[i]).size
            if name not in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']:
                if current_position_size > 0:
                    avg_price = self.getposition(self.pairs[i]).price
                    if self.rsi[i][0] >= self.p.rsi_limit[name] and self.closes[i][0] >= avg_price:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)

                if mode is not "bullish":
                    equity = DataUtils.convert_to_decimal(self.broker.get_value())
                    qties = []
                    for j in range(0, len(prices)):
                        qty = equity * (self.p.risk[name][j] / Decimal('100')) / prices[j]
                        qty = int(qty / step_size) * step_size
                        qties.append(qty)

                    for j in range(0, len(prices)):
                        qty = qties[j]
                        price = prices[j]
                        self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty), price=float(price))
            else:
                if current_position_size == 0:
                    if self.closes[i][-1] < self.bb_top[i][-1] and self.closes[i][0] >= self.bb_top[i][0]:
                        stop_price = DataUtils.convert_to_decimal(self.closes[i][0]) - DataUtils.convert_to_decimal(self.atr[i][0]) * self.p.atr_constant[name]
                        stop_price = int(stop_price / tick_size) * tick_size
                        self.stop_price[i] = stop_price

                        equity = DataUtils.convert_to_decimal(self.broker.get_value())
                        qty = equity * (self.p.risk[name][0] / Decimal('100')) / abs(DataUtils.convert_to_decimal(self.closes[i][0]) - stop_price)
                        qty = int(qty / step_size) * step_size

                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                elif current_position_size > 0:
                    if DataUtils.convert_to_decimal(self.closes[i][-1]) >= self.stop_price[i] > DataUtils.convert_to_decimal(self.closes[i][0]):
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
                    elif self.closes[i][-1] >= self.bb_mid[i][-1] and self.closes[i][0] < self.bb_mid[i][0]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i],size=float(current_position_size))
if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TailCatchV3)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.0005, leverage=5)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BINANCE, pair, tick_kind)
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