import backtrader as bt
import pandas as pd
import quantstats as qs
import math
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'BTCUSDT' : DataUtil.CANDLE_TICK_1HOUR,
    'ETHUSDT' : DataUtil.CANDLE_TICK_1HOUR,
    'SOLUSDT':DataUtil.CANDLE_TICK_1HOUR,
    '1000BONKUSDT':DataUtil.CANDLE_TICK_1HOUR,
    '1000PEPEUSDT':DataUtil.CANDLE_TICK_1HOUR,
    'WIFUSDT':DataUtil.CANDLE_TICK_1HOUR,
    'SHIB1000USDT':DataUtil.CANDLE_TICK_1HOUR,
    'ONDOUSDT':DataUtil.CANDLE_TICK_1HOUR,
    # 'ORDIUSDT':DataUtil.CANDLE_TICK_1HOUR,
}

class TailStrategyWithTrendV1(bt.Strategy):
    params=dict(
        risk={
            'BTCUSDT': [Decimal('1.0')],
            'ETHUSDT' : [Decimal('1.0')],
            'SOLUSDT' : [Decimal('1.0')],
            '1000PEPEUSDT' : [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'WIFUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'ONDOUSDT':[Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'ORDIUSDT':[Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            'SHIB1000USDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
            '1000BONKUSDT': [Decimal('2.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0')],
        },
        percent={
            'BTCUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('7.0'), Decimal('10.0'), Decimal('12.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'ETHUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('7.0'), Decimal('10.0'), Decimal('12.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'SOLUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('7.0'), Decimal('10.0'), Decimal('12.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            },
            '1000PEPEUSDT':{
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('7.0'), Decimal('10.0'), Decimal('12.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'WIFUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'ONDOUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            },
            'ORDIUSDT': {
                'bull': [Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0')],
                'def': [Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0')],
                'bear': [Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0')],
            },
            'SHIB1000USDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            },
            '1000BONKUSDT':{
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'def': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('6.0'), Decimal('9.0'), Decimal('12.0'), Decimal('15.0')],
            }
        },
        atr_length={
            'BTCUSDT': 10,
            'ETHUSDT': 10,
            'SOLUSDT': 10,
            '1000PEPEUSDT': 3,
            'WIFUSDT': 3,
            'ONDOUSDT': 3,
            'ORDIUSDT': 3,
            'SHIB1000USDT': 3,
            '1000BONKUSDT': 3,
        },
        atr_constant={
            'BTCUSDT': Decimal('2.0'),
            'ETHUSDT': Decimal('1.0'),
            'SOLUSDT': Decimal('2.0'),
            '1000PEPEUSDT': Decimal('1.0'),
            'WIFUSDT': Decimal('1.0'),
            'ONDOUSDT': Decimal('1.0'),
            'ORDIUSDT': Decimal('1.0'),
            'SHIB1000USDT': Decimal('1.0'),
            '1000BONKUSDT': Decimal('1.0'),
        },
        bb_length={
            'BTCUSDT': 80,
            'ETHUSDT': 80,
            'SOLUSDT': 80,
            '1000PEPEUSDT': 3,
            'WIFUSDT': 3,
            'ONDOUSDT': 3,
            'ORDIUSDT': 3,
            'SHIB1000USDT': 3,
            '1000BONKUSDT': 3,
        },
        bb_mult={
            'BTCUSDT': 1.0,
            'ETHUSDT': 1.0,
            'SOLUSDT': 1.0,
            '1000PEPEUSDT': 3,
            'WIFUSDT': 3,
            'ONDOUSDT': 3,
            'ORDIUSDT': 3,
            'SHIB1000USDT': 3,
            '1000BONKUSDT': 3,
        },
        rsi_length={
            'BTCUSDT': 3,
            'ETHUSDT': 3,
            'SOLUSDT': 3,
            '1000PEPEUSDT': 3,
            'WIFUSDT': 3,
            'ONDOUSDT': 3,
            'ORDIUSDT': 3,
            'SHIB1000USDT': 3,
            '1000BONKUSDT': 3,
        },
        rsi_limit={
            'BTCUSDT': 3,
            'ETHUSDT': 3,
            'SOLUSDT': 3,
            '1000PEPEUSDT': 60,
            'WIFUSDT': 70,
            'ONDOUSDT': 70,
            'ORDIUSDT': 70,
            'SHIB1000USDT': 60,
            '1000BONKUSDT': 60
        },
        high_band_span={
            'BTCUSDT': 3,
            'ETHUSDT': 3,
            'SOLUSDT': 3,
            '1000PEPEUSDT': 3,
            'WIFUSDT': 3,
            'ONDOUSDT': 3,
            'ORDIUSDT': 3,
            'SHIB1000USDT': 3,
            '1000BONKUSDT': 2,
        },
        low_band_span={
            'BTCUSDT': 3,
            'ETHUSDT': 3,
            'SOLUSDT': 3,
            '1000PEPEUSDT': 3,
            'WIFUSDT': 3,
            'ONDOUSDT': 3,
            'ORDIUSDT': 3,
            'SHIB1000USDT': 3,
            '1000BONKUSDT': 2,
        },
        tick_size={
            'BTCUSDT': Decimal('0.10'),
            'ETHUSDT': Decimal('0.01'),
            'SOLUSDT': Decimal('0.010'),
            '1000PEPEUSDT': Decimal('0.0000010'),
            'WIFUSDT': Decimal('0.0001'),
            'ONDOUSDT': Decimal('0.0001'),
            'ORDIUSDT': Decimal('0.001'),
            'SHIB1000USDT': Decimal('0.000001'),
            '1000BONKUSDT': Decimal('0.0000010')
        },
        step_size={
            'BTCUSDT': Decimal('0.001'),
            'ETHUSDT': Decimal('0.01'),
            'SOLUSDT': Decimal('0.1'),
            '1000PEPEUSDT': Decimal('100'),
            'WIFUSDT': Decimal('1'),
            'ONDOUSDT': Decimal('1'),
            'ORDIUSDT': Decimal('0.01'),
            'SHIB1000USDT': Decimal('10'),
            '1000BONKUSDT': Decimal('100')
        }
    )
    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        self.pairs = []
        self.names = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.stop_prices = []
        self.entry_prices = []
        self.entry_atrs = []
        # 기본 정보 획득
        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
            self.stop_prices.append(Decimal('0'))
            self.entry_prices.append(Decimal('0'))
            self.entry_atrs.append(Decimal('0'))

        # 지표 정보 획득
        self.high_bands = []
        self.low_bands = []
        self.rsis = []
        self.atrs = []
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # 고가 채널 저장
            high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_span[name])
            self.high_bands.append(high_band)

            # 저가 채널 저장
            low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_span[name])
            self.low_bands.append(low_band)

            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
            self.rsis.append(rsi)

            atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name])
            self.atrs.append(atr)

            bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_length[name], devfactor=self.p.bb_mult[name])
            self.bb_top.append(bb.lines.top)
            self.bb_mid.append(bb.lines.mid)
            self.bb_bot.append(bb.lines.bot)


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
            if name in ['ETHUSDT', 'SOLUSDT', 'BTCUSDT']:
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size == 0:
                    if self.closes[i][0] >= self.bb_top[i][0]:
                        stop_price = DataUtil.convert_to_decimal(self.closes[i][0]) - DataUtil.convert_to_decimal(self.atrs[i][0]) * self.p.atr_constant[name]
                        stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.stop_prices[i] = stop_price
                        self.entry_prices[i] = DataUtil.convert_to_decimal(self.closes[i][0])
                        self.entry_atrs[i] = DataUtil.convert_to_decimal(self.atrs[i][0])

                        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                        qty = equity * self.p.risk[name][0] / Decimal('100') / abs(DataUtil.convert_to_decimal(self.closes[i][0]) - stop_price)
                        if qty * DataUtil.convert_to_decimal(self.closes[i][0]) >= equity:
                            qty = equity * Decimal('0.98') / DataUtil.convert_to_decimal(self.closes[i][0])
                        qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                elif current_position_size > 0:
                    # if DataUtil.convert_to_decimal(self.closes[i][0]) > self.entry_prices[i] and \
                    #         (DataUtil.convert_to_decimal(self.closes[i][0]) - self.entry_prices[i]) >= self.entry_atrs[i]:
                    #     self.stop_prices[i] = self.stop_prices[i] + self.entry_atrs[i] / Decimal('2')
                    #     self.entry_prices[i] = DataUtil.convert_to_decimal(self.closes[i][0])
                    #     self.entry_atrs[i] = DataUtil.convert_to_decimal(self.atrs[i][0])

                    if DataUtil.convert_to_decimal(self.closes[i][0]) < self.stop_prices[i]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
                    elif self.closes[i][0] < self.bb_mid[i][0]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
            else:
                self.cancel_all(name)

                tick_size = self.p.tick_size[name]
                step_size = self.p.step_size[name]

                # 진입모드(bull, def, bear) 계산
                entry_mode = None
                if self.closes[i][0] >= self.high_bands[i][-1]:
                    entry_mode = 'bull'
                elif self.low_bands[i][-1] <= self.closes[i][0] < self.high_bands[i][-1]:
                    entry_mode = 'def'
                else:
                    entry_mode = 'bear'

                # 진입할 퍼센트를 이용하여 진입 가격 계산
                prices = []
                for j in range(0, len(self.p.percent[name][entry_mode])):
                    percent = self.p.percent[name][entry_mode][j]
                    price = DataUtil.convert_to_decimal(self.closes[i][0]) * (Decimal('1') - percent / Decimal('100'))
                    price = int(price / tick_size) * tick_size
                    prices.append(price)

                # 현재 포지션 정보 획득
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size > 0:
                    avg_price = self.getposition(self.pairs[i]).price
                    if self.rsis[i][0] >= self.p.rsi_limit[name] and self.closes[i][0] >= avg_price:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i],
                                               size=float(current_position_size))

                equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                qtys = []
                for j in range(0, len(prices)):
                    price = prices[j]
                    risk = self.p.risk[name][j]
                    qty = equity * risk / Decimal('100') / price
                    qty = int(qty / step_size) * step_size
                    qtys.append(qty)

                for j in range(0, len(qtys)):
                    qty = qtys[j]
                    price = prices[j]
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty),
                                          price=float(price))




if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TailStrategyWithTrendV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.0005, leverage=3)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
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
    file_name += "TailStrategyWithTrendV1"

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