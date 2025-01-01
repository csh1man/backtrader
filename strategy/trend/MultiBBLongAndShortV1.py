import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal


pairs = {
    'ETHUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'BTCUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'SOLUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'BNBUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'BCHUSDT': DataUtil.CANDLE_TICK_4HOUR,
    # 'EOSUSDT': DataUtil.CANDLE_TICK_4HOUR,
}

class MultiBBLongAndShortV1(bt.Strategy):
    params=dict(
        use_short={
            'BTCUSDT':True,
            'ETHUSDT': True,
            'BCHUSDT': True,
            'SOLUSDT': True,
            'BNBUSDT': False,
            'EOSUSDT': True,
        },
        risk={
            'BTCUSDT':{
                'long':4,
                'short':4
            },
            'ETHUSDT': {
                'long': 3,
                'short': 3
            },
            'BCHUSDT': {
                'long': 4,
                'short': 4
            },
            'SOLUSDT': {
                'long': 5,
                'short': 3
            },
            'BNBUSDT': {
                'long': 4,
                'short': 2
            },
            'EOSUSDT': {
                'long': 4,
                'short': 4
            },
        },
        atr={
            'BTCUSDT':{
                'length':{
                    'long': 10,
                    'short': 3
                },
                'constant':{
                    'long': Decimal('1.0'),
                    'short': Decimal('2.0'),
                }
            },
            'ETHUSDT':{
                'length':{
                    'long': 10,
                    'short': 10
                },
                'constant':{
                    'long': Decimal('1.0'),
                    'short': Decimal('3.0'),
                }
            },
            'BCHUSDT':{
                'length':{
                    'long': 10,
                    'short': 10
                },
                'constant':{
                    'long': Decimal('2.0'),
                    'short': Decimal('2.0'),
                }
            },
            'SOLUSDT':{
                'length':{
                    'long': 10,
                    'short': 10
                },
                'constant':{
                    'long': Decimal('2.0'),
                    'short': Decimal('3.0'),
                }
            },
            'BNBUSDT':{
                'length':{
                    'long': 10,
                    'short': 10
                },
                'constant':{
                    'long': Decimal('2.0'),
                    'short': Decimal('3.0'),
                }
            },
            "EOSUSDT":{
                'length':{
                    'long': 10,
                    'short': 10
                },
                'constant':{
                    'long': Decimal('2.0'),
                    'short': Decimal('3.0'),
                }
            }
        },
        bb={
            'BTCUSDT': {
                'length': {
                    'long': 50,
                    'short': 50,
                },
                'mult': {
                    'long': 1,
                    'short': 2
                }
            },
            'ETHUSDT': {
                'length': {
                    'long': 50,
                    'short': 50,
                },
                'mult': {
                    'long': 1,
                    'short': 2
                }
            },
            'BCHUSDT': {
                'length': {
                    'long': 50,
                    'short': 50,
                },
                'mult': {
                    'long': 1,
                    'short': 2
                }
            },
            'SOLUSDT': {
                'length': {
                    'long': 60,
                    'short': 50,
                },
                'mult': {
                    'long': 1,
                    'short': 2
                }
            },
            'BNBUSDT': {
                'length': {
                    'long': 60,
                    'short': 50,
                },
                'mult': {
                    'long': 1,
                    'short': 2
                }
            },
            'EOSUSDT': {
                'length': {
                    'long': 60,
                    'short': 50,
                },
                'mult': {
                    'long': 1,
                    'short': 2
                }
            },
        },
        tick_size={
            'BTCUSDT' : Decimal('0.10'),
            'ETHUSDT': Decimal('0.01'),
            'BCHUSDT': Decimal('0.01'),
            'SOLUSDT': Decimal('0.0100'),
            'BNBUSDT' : Decimal('0.010'),
            'EOSUSDT': Decimal('0.001'),
        },
        step_size={
            'BTCUSDT': Decimal('0.001'),
            'ETHUSDT': Decimal('0.01'),
            'BCHUSDT': Decimal('0.001'),
            'SOLUSDT': Decimal('1'),
            'BNBUSDT' : Decimal('0.01'),
            'EOSUSDT': Decimal('0.1'),
        },
        high_band_length={
            'BTCUSDT': 15,
            'ETHUSDT': 15,
            'BCHUSDT': 15,
            'SOLUSDT': 15,
            'BNBUSDT' : 15,
            'EOSUSDT': 15,
        },
        low_band_length={
            'BTCUSDT': 50,
            'ETHUSDT': 50,
            'BCHUSDT': 50,
            'SOLUSDT': 50,
            'BNBUSDT': 50,
            'EOSUSDT': 50,
        },
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

        # 돈치안 채널
        self.high_band = []
        self.low_band = []

        # 롱/숏 ATR
        self.long_atrs = []
        self.short_atrs = []

        # 롱/숏 손절가
        self.long_stop_prices = []
        self.short_stop_prices = []

        # 롱/숏 볼린저밴드
        self.long_bb_top = []
        self.long_bb_mid = []
        self.long_bb_bot = []
        self.short_bb_top = []
        self.short_bb_mid = []
        self.short_bb_bot = []

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

        # 기본 캔들정보 할당
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
        
        # 지표 정보 계산 및 할당
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            long_bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb[name]['length']['long'], devfactor=self.p.bb[name]['mult']['long'])
            self.long_bb_top.append(long_bb.lines.top)
            self.long_bb_mid.append(long_bb.lines.mid)
            self.long_bb_bot.append(long_bb.lines.bot)

            short_bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb[name]['length']['short'], devfactor=self.p.bb[name]['mult']['short'])
            self.short_bb_top.append(short_bb.lines.top)
            self.short_bb_mid.append(short_bb.lines.mid)
            self.short_bb_bot.append(short_bb.lines.bot)

            self.high_band.append(bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]))
            self.low_band.append(bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]))

            long_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr[name]['length']['long'])
            self.long_atrs.append(long_atr)

            short_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr[name]['length']['short'])
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
        self.record_asset()

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(name)
            long_risk = self.p.risk[name]['long']
            short_risk = self.p.risk[name]['short']

            long_atr = DataUtil.convert_to_decimal(self.long_atrs[i][0])
            long_atr_constant = self.p.atr[name]['constant']['long']

            short_atr = DataUtil.convert_to_decimal(self.short_atrs[i][0])
            short_atr_constant = self.p.atr[name]['constant']['short']

            current_position_size = self.getposition(self.pairs[i]).size
            equity = DataUtil.convert_to_decimal(self.broker.get_cash())
            if name not in('BCHUSDT', 'EOSUSDT'):
                if current_position_size == 0:
                    if self.closes[i][-1] < self.long_bb_top[i][-1] and self.closes[i][0] > self.long_bb_top[i][0]:
                        long_stop_price = DataUtil.convert_to_decimal(self.closes[i][0]) - long_atr * long_atr_constant
                        long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.long_stop_prices[i] = long_stop_price

                        qty = equity * long_risk / Decimal('100') / abs(DataUtil.convert_to_decimal(self.closes[i][0]) - long_stop_price)
                        if qty * DataUtil.convert_to_decimal(self.closes[i][0]) >= equity:
                            qty = equity * Decimal('0.98') / DataUtil.convert_to_decimal(self.closes[i][0])
                        qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]

                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                    elif self.p.use_short[name] and self.closes[i][-1] > self.short_bb_bot[i][-1] and self.closes[i][0] < self.short_bb_bot[i][0]:
                        short_stop_price = DataUtil.convert_to_decimal(self.closes[i][0]) + short_atr * short_atr_constant
                        short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.short_stop_prices[i] = short_stop_price

                        qty = equity * short_risk / Decimal('100') / abs(DataUtil.convert_to_decimal(self.closes[i][0]) - short_stop_price)
                        if qty * DataUtil.convert_to_decimal(self.closes[i][0]) >= equity:
                            qty = equity * Decimal('0.98') / DataUtil.convert_to_decimal(self.closes[i][0])
                        qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]

                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))

                elif current_position_size > 0:
                    long_stop_price = self.long_stop_prices[i]
                    if self.closes[i][-1] > long_stop_price > self.closes[i][0]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)
                        self.long_stop_prices[i] = Decimal('0')
                    elif self.closes[i][-1] > self.long_bb_mid[i][-1] and self.closes[i][0] < self.long_bb_mid[i][0]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)
                        self.long_stop_prices[i] = Decimal('0')
                elif current_position_size < 0:
                    short_stop_price = self.short_stop_prices[i]
                    if self.closes[i][-1] < short_stop_price < self.closes[i][0]:
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                        self.short_stop_prices[i] = Decimal('0')
                    elif self.closes[i][-1] < self.short_bb_bot[i][-1] and self.short_bb_bot[i][0] < self.closes[i][0]:
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                        self.short_stop_prices[i] = Decimal('0')
            else:

                if current_position_size == 0:
                    short_stop_price = DataUtil.convert_to_decimal(self.low_band[i][0]) - short_atr * short_atr_constant
                    short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.short_stop_prices[i] = short_stop_price

                    qty = equity * short_risk / Decimal('100') / abs(DataUtil.convert_to_decimal(self.closes[i][0]) - short_stop_price)
                    if qty * DataUtil.convert_to_decimal(self.closes[i][0]) > equity:
                        qty = equity * Decimal('0.98') / DataUtil.convert_to_decimal(self.low_band[i][0])
                    qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                    if qty > 0:
                        self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], price=float(self.low_band[i][0]), size=float(qty))
                elif current_position_size < 0:
                    if DataUtil.convert_to_decimal(self.closes[i][-1]) < self.short_stop_prices[i] < DataUtil.convert_to_decimal(self.closes[i][0]):
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                    else:
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(self.high_band[i][0]), size=abs(current_position_size))


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiBBLongAndShortV1)

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

    # file_name = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
    # file_name = "/Users/tjgus/Desktop/project/krtrade/backData/result/"
    file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "MultiBBLongAndShortV1"

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

