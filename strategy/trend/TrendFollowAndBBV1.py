import backtrader as bt
import pandas as pd
import quantstats as qs
import math
from util.Util import DataUtil
from decimal import Decimal


pairs = {
    'ETHUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'BTCUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'BCHUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'EOSUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'BNBUSDT': DataUtil.CANDLE_TICK_4HOUR,
}

class TrendFollowAndBBV1(bt.Strategy):
    params = dict(
        risk={
            'long': Decimal('2.0'),
            'short': Decimal('2.0')
        },
        entry_mode={
            'BTCUSDT': 'TB',  # Trend Follow 롱 + BollingerBand 숏
            'ETHUSDT': 'TB',  # Trend Follow 롱 + BollingerBand 숏
            'SOLUSDT': 'TB',
            'BCHUSDT': 'BT',  # BollingerBand 롱 + Trend Follow 숏
            'EOSUSDT': 'NT',  # Not 롱 + Trend Follow 숏
            'BNBUSDT': 'BN'  # Bollinger Band 롱 + Not 숏
        },
        high_band_length={
            'BTCUSDT': 30,
            'ETHUSDT': 30,
            'SOLUSDT': 30,
            'BCHUSDT': 15,
            'EOSUSDT': 15,
            'BNBUSDT': 30,
        },
        low_band_length={
            'BTCUSDT': 15,
            'ETHUSDT': 15,
            'SOLUSDT': 15,
            'BCHUSDT': 50,
            'EOSUSDT': 30,
            'BNBUSDT': 30,
        },
        band_constant={
            'BTCUSDT': {
                'high': Decimal('1'),
                'low': Decimal('1'),
            },
            'ETHUSDT': {
                'high': Decimal('10'),
                'low': Decimal('5'),
            },
            'SOLUSDT': {
                'high': Decimal('10'),
                'low': Decimal('5'),
            },
            'BCHUSDT': {
                'high': Decimal('50'),
                'low': Decimal('0'),
            },
            'EOSUSDT': {
                'high': Decimal('0'),
                'low': Decimal('0'),
            },
            'BNBUSDT': {
                'high': Decimal('0'),
                'low': Decimal('0'),
            },

        },
        bb_length={
            'BTCUSDT': 30,
            'ETHUSDT': 20,
            'SOLUSDT': 50,
            'BCHUSDT': 50,
            'EOSUSDT': 50,
            'BNBUSDT': 50
        },
        bb_mult={
            'BTCUSDT': 2.0,
            'ETHUSDT': 2.0,
            'SOLUSDT': 2.0,
            'BCHUSDT': 2.0,
            'EOSUSDT': 2.0,
            'BNBUSDT': 0.5
        },
        atr_length={
            'BTCUSDT': {
                'long': 10,
                'short': 10
            },
            'ETHUSDT': {
                'long': 10,
                'short': 10
            },
            'SOLUSDT': {
                'long': 10,
                'short': 10
            },
            'BCHUSDT': {
                'long': 10,
                'short': 10
            },
            'EOSUSDT': {
                'long': 10,
                'short': 10
            },
            'BNBUSDT': {
                'long': 10,
                'short': 10
            }
        },
        atr_constant={
            'BTCUSDT': {
                'long': Decimal('1.0'),
                'short': Decimal('1.0')
            },
            'ETHUSDT': {
                'long': Decimal('1.0'),
                'short': Decimal('2.0')
            },
            'SOLUSDT': {
                'long': Decimal('2.0'),
                'short': Decimal('2.0')
            },
            'BCHUSDT': {
                'long': Decimal('2.0'),
                'short': Decimal('2.0')
            },
            'EOSUSDT': {
                'long': Decimal('1.0'),
                'short': Decimal('2.0')
            },
            'BNBUSDT': {
                'long': Decimal('1.0'),
                'short': Decimal('2.0')
            }
        },
        tick_size={
            'ETHUSDT': Decimal('0.01'),
            'BTCUSDT' : Decimal('0.10'),
            'SOLUSDT': Decimal('0.0100'),
            'BCHUSDT': Decimal('0.05'),
            'EOSUSDT': Decimal('0.001'),
            'BNBUSDT': Decimal('0.010'),
        },
        step_size={
            'ETHUSDT': Decimal('0.01'),
            'BTCUSDT': Decimal('0.001'),
            'SOLUSDT': Decimal('1'),
            'BCHUSDT': Decimal('0.01'),
            'EOSUSDT': Decimal('0.1'),
            'BNBUSDT': Decimal('0.01'),
        }
    )
    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        # 캔들 기본 데이터
        self.pairs = []
        self.names = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []

        # 지표 변수
        self.highest = []
        self.lowest = []
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []

        # 손절 관련 변수
        self.long_atr = []
        self.short_atr = []
        self.long_stop_prices =[]
        self.short_stop_prices = []

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

        # 지표 데이터 저장
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # 고가 채널 저장
            highest = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name])
            self.highest.append(highest)

            # 저가 채널 저장
            lowest = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name])
            self.lowest.append(lowest)

            # atr 저장
            long_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name]['long'])
            self.long_atr.append(long_atr)
            short_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name]['short'])
            self.short_atr.append(short_atr)

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

            highest = DataUtil.convert_to_decimal(self.highest[i][0])
            lowest = DataUtil.convert_to_decimal(self.lowest[i][0])

            adj_highest = highest - (highest-lowest) * (self.p.band_constant[name]['high'] / Decimal('100'))
            adj_highest = int(adj_highest / self.p.tick_size[name]) * self.p.tick_size[name]

            adj_lowest = lowest + (highest-lowest) * (self.p.band_constant[name]['low'] / Decimal('100'))
            adj_lowest = int(adj_lowest / self.p.tick_size[name]) * self.p.tick_size[name]

            long_atr = DataUtil.convert_to_decimal(self.long_atr[i][0])
            short_atr = DataUtil.convert_to_decimal(self.short_atr[i][0])

            entry_mode = self.p.entry_mode[name]
            if entry_mode == 'TB': # 롱 : Trend Follow , 숏 : Bollinger Band
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size == 0:
                    # 볼린저밴드 하한선을 돌파할 경우
                    if self.closes[i][-1] > self.bb_bot[i][-1] and self.closes[i][0] < self.bb_bot[i][0]:
                        # 손절가 계산
                        short_stop_price = DataUtil.convert_to_decimal(self.closes[i][0]) + long_atr * self.p.atr_constant[name]['short']
                        short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.short_stop_prices[i] = short_stop_price

                        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                        qty = equity * (self.p.risk['short'] / Decimal('100')) / abs(DataUtil.convert_to_decimal(self.closes[i][0])-short_stop_price)
                        qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]

                        if qty > 0:
                            if qty * DataUtil.convert_to_decimal(self.closes[i][0]) >= equity:
                                qty = equity * Decimal('0.98') / DataUtil.convert_to_decimal(self.closes[i][0])
                            qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                            self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                    else:
                        # 롱 손절가 설정
                        long_stop_price = adj_highest - long_atr * self.p.atr_constant[name]['long']
                        long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.long_stop_prices[i] = long_stop_price

                        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                        qty = equity * (self.p.risk['long'] / Decimal('100')) / abs(adj_highest - long_stop_price)
                        if qty > 0:
                            if qty * adj_highest >= equity:
                                qty = equity * Decimal('0.98') / adj_highest
                            qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]

                            self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=float(qty), price=float(adj_highest))
                elif current_position_size > 0:
                    if DataUtil.convert_to_decimal(self.closes[i][-1]) > self.long_stop_prices[i] and DataUtil.convert_to_decimal(self.closes[i][0]) < self.long_stop_prices[i]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)
                    else:
                        self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=current_position_size, price=float(adj_lowest))
                elif current_position_size < 0:
                        if DataUtil.convert_to_decimal(self.closes[i][-1]) < self.short_stop_prices[i] and DataUtil.convert_to_decimal(self.closes[i][0]) > self.short_stop_prices[i]:
                            self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                        elif self.closes[i][-1] < self.bb_bot[i][-1] and self.closes[i][0] > self.bb_bot[i][0]:
                            self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i],size=abs(current_position_size))
            elif entry_mode == 'BT': # 볼린저밴드 롱 / Trend Follow 숏
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size == 0:
                    # 볼린저밴드 상한선을 뚫었을 경우
                    if self.closes[i][-1] < self.bb_top[i][-1] and self.closes[i][0] > self.bb_top[i][0]:
                        long_stop_price = DataUtil.convert_to_decimal(self.closes[i][0]) - long_atr * self.p.atr_constant[name]['long']
                        long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.long_stop_prices[i] = long_stop_price

                        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                        qty = equity * (self.p.risk['long'] / Decimal('100')) / abs(DataUtil.convert_to_decimal(self.closes[i][0]) - long_stop_price)
                        qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                        if qty * DataUtil.convert_to_decimal(self.closes[i][0]) >= equity:
                            qty = equity * Decimal('0.98') / DataUtil.convert_to_decimal(self.closes[i][0])
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                    else:
                        short_stop_price = adj_lowest + short_atr * self.p.atr_constant[name]['short']
                        short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.short_stop_prices[i] = short_stop_price

                        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                        qty = equity * (self.p.risk['short'] / Decimal('100')) / abs(adj_lowest - short_stop_price)
                        if qty > 0:
                            if qty * adj_lowest >= equity:
                                qty = equity * Decimal('0.98') / adj_highest
                            qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                            self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(qty), price=float(adj_lowest))
                elif current_position_size > 0:
                    if DataUtil.convert_to_decimal(self.closes[i][-1]) > self.long_stop_prices[i] and DataUtil.convert_to_decimal(self.closes[i][-1]) < self.long_stop_prices[i]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
                    elif self.closes[i][-1] > self.bb_mid[i][-1] and self.closes[i][0] < self.bb_mid[i][0]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i],size=float(current_position_size))
                elif current_position_size < 0:
                    if DataUtil.convert_to_decimal(self.closes[i][-1]) < self.short_stop_prices[i] and DataUtil.convert_to_decimal(self.closes[i][0]) > self.short_stop_prices[i]:
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i],size=float(abs(current_position_size)))
                    else:
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=float(abs(current_position_size)),price=float(adj_highest))
            elif entry_mode == 'NT': # 롱 X, Trend Follow 숏
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size == 0:
                    short_stop_price = adj_lowest + short_atr * self.p.atr_constant[name]['short']
                    short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.short_stop_prices[i] = short_stop_price

                    equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                    qty = equity * (self.p.risk['short']/ Decimal('100')) / abs(adj_lowest - short_stop_price)
                    if qty > 0:
                        if qty * adj_lowest >= equity:
                            qty = equity * Decimal('0.98') / adj_lowest
                        qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                        self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(qty), price=float(adj_lowest))
                if current_position_size < 0:
                    if DataUtil.convert_to_decimal(self.closes[i][-1]) < self.short_stop_prices[i] and DataUtil.convert_to_decimal(self.closes[i][0]) > self.short_stop_prices[i]:
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(abs(current_position_size)))
                    else:
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=float(abs(current_position_size)), price=float(adj_highest))

            elif entry_mode == 'BN': # 볼린저밴드 롱, 숏 X
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size == 0:
                    if self.closes[i][-1] < self.bb_top[i][-1] and self.closes[i][0] > self.bb_top[i][0]:
                        long_stop_price = DataUtil.convert_to_decimal(self.closes[i][0]) - long_atr * self.p.atr_constant[name]['long']
                        long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.long_stop_prices[i] = long_stop_price

                        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
                        qty = equity * (self.p.risk['long']/ Decimal('100')) / DataUtil.convert_to_decimal(DataUtil.convert_to_decimal(self.closes[i][0]) - long_stop_price)
                        if qty > 0:
                            if qty * DataUtil.convert_to_decimal(self.closes[i][0]) >= equity:
                                qty = equity * Decimal('0.98') / DataUtil.convert_to_decimal(self.closes[i][0])
                            qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                            self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                elif current_position_size > 0:
                    if DataUtil.convert_to_decimal(self.closes[i][-1]) >= self.long_stop_prices[i] and DataUtil.convert_to_decimal(self.closes[i][0]) < self.long_stop_prices[i]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
                    elif self.closes[i][-1] >= self.bb_mid[i][-1] and self.closes[i][0] < self.bb_mid[i][0]:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))

if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendFollowAndBBV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.0005, leverage=3)
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
    file_name += "TrendFollowAndBBV1"

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