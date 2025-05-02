import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal
import math

pairs = {
    # 'ETHUSDT': DataUtil.CANDLE_TICK_4HOUR,
    # 'BTCUSDT' : DataUtil.CANDLE_TICK_4HOUR,
    'BCHUSDT' : DataUtils.CANDLE_TICK_4HOUR,
    # 'BNBUSDT': DataUtil.CANDLE_TICK_4HOUR,
}


class MultiLongAndShortV1(bt.Strategy):
    params = dict(
        entry_mode={  # 0 : 롱만 진입 / 1: 숏만 진입 / 2: 롱 숏 모두 진입
            'ETHUSDT': 2,
            'BTCUSDT': 0,
            'BNBUSDT': 0,
            'BCHUSDT': 1,
        },
        leverage={
            'ETHUSDT': {
                'long': Decimal('2.0'),
                'short': Decimal('2.0')
            },
            'BTCUSDT': {
                'long': Decimal('2.0'),
            },
            'BNBUSDT': {
                'long': Decimal('1.0'),
            },
            'BCHUSDT': {
                'long': Decimal('2.0'),
                'short': Decimal('1.0')
            }
        },
        risks={
            'ETHUSDT': {
                'long': [Decimal('2.0'), Decimal('4.0')],
                'short': [Decimal('4.0'), Decimal('2.0')],
            },
            'BTCUSDT': {
                'long': [Decimal('2.0'), Decimal('1.0')],
            },
            'BNBUSDT': {
                'long': [Decimal('4.0'), Decimal('0.5')],
            },
            'BCHUSDT': {
                'long': [Decimal('2.0'), Decimal('3.0')],
                'short': [Decimal('3.0'), Decimal('1.0')],
            }
        },
        tick_size={
            'ETHUSDT': Decimal('0.01'),
            'BTCUSDT' : Decimal('0.10'),
            'BNBUSDT' : Decimal('0.010'),
            'BCHUSDT': Decimal('0.01'),
        },
        step_size={
            'ETHUSDT': Decimal('0.01'),
            'BTCUSDT': Decimal('0.001'),
            'BNBUSDT' : Decimal('0.01'),
            'BCHUSDT': Decimal('0.001'),
        },

        high_band_length={
            'ETHUSDT': {
                'long': 50,
                'short': 15,
            },
            'BTCUSDT':{
                'long':30,
                'short': 15,
            },
            'BNBUSDT': {
                'long': 50,
                'short': 15,
            },
            'BCHUSDT': {
                'long': 50,
                'short': 15,
            }
        },
        low_band_length={
            'ETHUSDT': {
                'long': 15,
                'short': 50,
            },
            'BTCUSDT': {
                'long' : 15,
                'short': 50,
            },
            'BNBUSDT': {
                'long' : 15,
                'short': 50,
            },
            'BCHUSDT': {
                'long': 15,
                'short': 50
            }
        },
        atr={
            'length': {
                'ETHUSDT': {
                    'long': 10,
                    'short': 10
                },
                'BTCUSDT': {
                    'long': 10,
                    'short': 10
                },
                'BNBUSDT': {
                    'long': 10,
                    'short': 10
                },
                'BCHUSDT': {
                    'long': 10,
                    'short' : 1,
                }
            },
            'constant': {
                'ETHUSDT': {
                    'long': Decimal('1.0'),
                    'short': Decimal('1.0')
                },
                'BTCUSDT': {
                    'long': Decimal('2.0'),
                    'short': Decimal('1.0')
                },
                'BNBUSDT': {
                    'long': Decimal('2.0'),
                    'short': Decimal('1.0')
                },
                'BCHUSDT': {
                    'long': Decimal('1.0'),
                    'short': Decimal('1.0')
                }
            }
        },
        is_cut={
            'ETHUSDT': {
                'long': False,
                'short': False
            },
            'BTCUSDT': {
                'long': False,
            },
            'BNBUSDT': {
                'long': False,
            },
            'BCHUSDT': {
                'long': False,
                'short' : False
            }
        },
        stop_price={
            'ETHUSDT': {
                'long': Decimal('-1'),
                'short': Decimal('-1')
            },
            'BTCUSDT':{
                'long' : Decimal('-1')
            },
            'BNBUSDT': {
                'long': Decimal('-1')
            },
            'BCHUSDT': {
                'short': Decimal('-1')
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

        # 기본 캔들 정보 저장
        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        # 지표 데이터 저장용 변수 초기화
        self.long_highest = []
        self.short_highest = []

        self.long_lowest = []
        self.short_lowest = []

        self.long_atrs = []
        self.short_atrs = []

        self.long_stop_prices = []
        self.short_stop_prices = []
        # 지표 데이터 저장
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # 고가 채널 저장

            # atr 저장
            long_highest = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['long'])
            self.long_highest.append(long_highest)

            long_lowest = bt.indicators.Lowest(self.lows[i], period=self.p.high_band_length[name]['long'])
            self.long_lowest.append(long_lowest)

            long_atr = bt.indicators.eRange(self.pairs[i], period=self.p.atr['length'][name]['long'])
            self.long_atrs.append(long_atr)

            short_highest = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['short'])
            self.short_highest.append(short_highest)

            short_lowest = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['short'])
            self.short_lowest.append(short_lowest)

            short_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr['length'][name]['short'])
            self.short_atrs.append(short_atr)

            self.long_stop_prices.append(Decimal('-1'))
            self.short_stop_prices.append(Decimal('-1'))

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
        self.record_asset()  # 자산 기록

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(target_name=name)  # 미체결 주문 모두 취소

            entry_mode = self.p.entry_mode[name]
            long_leverage = None
            short_leverage = None
            if entry_mode == 0:
                long_leverage = self.p.leverage[name]['long']
            elif entry_mode == 1:
                short_leverage = self.p.leverage[name]['short']
                long_leverage = self.p.leverage[name]['long']
            elif entry_mode == 2:
                long_leverage = self.p.leverage[name]['long']
                short_leverage = self.p.leverage[name]['short']

            current_position_size = self.getposition(self.pairs[i]).size
            # 진입 포지션이 없을 경우
            if current_position_size == 0:
                if entry_mode == 2:
                    long_atr = int(DataUtils.convert_to_decimal(self.long_atrs[i][0]) / self.p.tick_size[name]) * self.p.tick_size[name]
                    short_atr = int(DataUtils.convert_to_decimal(self.short_atrs[i][0]) / self.p.tick_size[name]) * self.p.tick_size[name]
                    if self.closes[i][-1] < self.short_lowest[i][-2] and self.closes[i][0] > self.short_lowest[i][-1]:
                        short_risk = self.p.risks[name]['short'][0]
                        if self.p.is_cut[name]['short']:
                            short_risk = self.p.risks[name]['short'][1]

                        short_stop_price = DataUtils.convert_to_decimal(self.closes[i][0]) + short_atr * \
                                           self.p.atr['constant'][name]['short']
                        short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.short_stop_prices[i] = short_stop_price

                        short_qty = DataUtils.convert_to_decimal(self.broker.get_cash()) * short_risk / Decimal('100')
                        short_qty = short_qty / abs((DataUtils.convert_to_decimal(self.closes[i][0])) - short_stop_price)
                        short_qty = int(short_qty / self.p.step_size[name]) * self.p.step_size[name]

                        if short_qty * DataUtils.convert_to_decimal(
                                self.closes[i][0]) >= short_leverage * DataUtils.convert_to_decimal(
                                self.broker.get_cash()):
                            short_qty = short_leverage * DataUtils.convert_to_decimal(self.broker.get_cash()) * Decimal(
                                '0.98') / DataUtils.convert_to_decimal(self.closes[i][0])
                            short_qty = int(short_qty / self.p.step_size[name]) * self.p.step_size[name]

                        # 시장가 주문 진입
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(short_qty))
                    else:
                        long_stop_price = DataUtils.convert_to_decimal(
                            self.long_highest[i][0]) - long_atr * self.p.atr['constant'][name]['long']
                        long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.long_stop_prices[i] = long_stop_price

                        long_risk = self.p.risks[name]['long'][0]
                        if self.p.is_cut[name]['long']:
                            long_risk = self.p.risks[name]['long'][1]

                        long_qty = DataUtils.convert_to_decimal(self.broker.get_cash()) * long_risk / Decimal('100')
                        long_qty = long_qty / abs(
                            DataUtils.convert_to_decimal(self.long_highest[i][0]) - long_stop_price)
                        long_qty = int(long_qty / self.p.step_size[name]) * self.p.step_size[name]

                        if long_qty * DataUtils.convert_to_decimal(
                                self.long_highest[i][0]) >= long_leverage * DataUtils.convert_to_decimal(
                                self.broker.get_cash()):
                            long_qty = long_leverage * DataUtils.convert_to_decimal(self.broker.get_cash()) * Decimal(
                                '0.98') / DataUtils.convert_to_decimal(self.long_highest[i][0])
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i],
                                              price=float(self.long_highest[i][0]), size=float(long_qty))

                elif entry_mode == 0:  # 롱만 진입
                    long_stop_price = DataUtils.convert_to_decimal(
                        self.long_highest[i][0]) - DataUtils.convert_to_decimal(self.long_atrs[i][0]) * \
                                      self.p.atr['constant'][name]['long']
                    long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.long_stop_prices[i] = long_stop_price

                    long_risk = self.p.risks[name]['long'][0]
                    if self.p.is_cut[name]['long']:
                        long_risk = self.p.risks[name]['long'][1]

                    long_qty = DataUtils.convert_to_decimal(self.broker.get_cash()) * long_risk / Decimal('100')
                    long_qty = long_qty / abs(DataUtils.convert_to_decimal(self.long_highest[i][0]) - long_stop_price)
                    long_qty = int(long_qty / self.p.step_size[name]) * self.p.step_size[name]

                    if long_qty * DataUtils.convert_to_decimal(
                            self.long_highest[i][0]) >= long_leverage * DataUtils.convert_to_decimal(
                        self.broker.get_cash()):
                        long_qty = long_leverage * DataUtils.convert_to_decimal(self.broker.get_cash()) * Decimal(
                            '0.98') / DataUtils.convert_to_decimal(self.long_highest[i][0])
                    self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i],
                                          price=float(self.long_highest[i][0]), size=float(long_qty))
                elif entry_mode == 1:
                    # if not math.isnan(self.short_lowest[i][-2]) and not math.isnan(self.short_lowest[i][-1]):
                    #     if self.closes[i][-1] > DataUtil.convert_to_decimal(
                    #             self.short_lowest[i][-2]) and self.closes[i][0] < DataUtil.convert_to_decimal(
                    #             self.short_lowest[i][-1]) and name == 'BCHUSDT':
                    #         stop_price = DataUtil.convert_to_decimal(self.closes[i][0]) + DataUtil.convert_to_decimal(self.short_atrs[i][0]) * self.p.atr['constant'][name]['short']
                    #         stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    #         self.short_stop_prices[i] = stop_price
                    #         long_risk = self.p.risks[name]['long'][0]
                    #         if self.p.is_cut[name]['long']:
                    #             long_risk = self.p.risks[name]['long'][1]
                    #
                    #         qty = short_leverage * DataUtil.convert_to_decimal(self.broker.get_cash()) * \
                    #               long_risk / Decimal('100') / abs(DataUtil.convert_to_decimal(self.closes[i][0]) - stop_price)
                    #         qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                    #         if qty * DataUtil.convert_to_decimal(self.closes[i][0]) >= short_leverage * DataUtil.convert_to_decimal(self.broker.get_cash()):
                    #             qty = short_leverage * DataUtil.convert_to_decimal(self.broker.get_cash()) * Decimal(
                    #                 '0.98') / DataUtil.convert_to_decimal(self.closes[i][0])
                    #             qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                    #         self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                    #     else:
                    #         stop_price = DataUtil.convert_to_decimal(self.long_highest[i][0]) - DataUtil.convert_to_decimal(self.long_atrs[i][0]) * self.p.atr['constant'][name]['long']
                    #         stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    #         self.long_stop_prices[i] = stop_price
                    #         short_risk = self.p.risks[name]['short'][0]
                    #         if self.p.is_cut[name]['short']:
                    #             short_risk = self.p.risks[name]['short'][1]
                    #
                    #         qty = DataUtil.convert_to_decimal(self.broker.get_cash()) * short_risk / Decimal('100') / abs(DataUtil.convert_to_decimal(self.long_highest[i][0]) - stop_price)
                    #         qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                    #         # 진입하려는 수량에 대한 시드 값이 현재 현금보다 클 경우, 들어가지 않는 오류가 발생한다. 따라서, 만약 진입하려는 수량의 시드가 현금보다 클 경우 현금의 98%만을 진입한다.
                    #         if qty * DataUtil.convert_to_decimal(self.long_highest[i][0]) >= long_leverage * DataUtil.convert_to_decimal(self.broker.get_cash()):
                    #             qty = long_leverage * DataUtil.convert_to_decimal(self.broker.get_cash()) * Decimal(
                    #                 '0.98') / DataUtil.convert_to_decimal(self.long_highest[i][0])
                    #             qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                    #         self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(self.long_highest[i][0]),
                    #                               size=float(qty))
                    short_stop_price = DataUtils.convert_to_decimal(
                        self.short_lowest[i][0]) \
                                       + DataUtils.convert_to_decimal(self.short_atrs[i][0]) * \
                                       self.p.atr['constant'][name]['short']
                    short_stop_price = int(short_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.short_stop_prices[i] = short_stop_price

                    short_risk = self.p.risks[name]['short'][0]
                    if self.p.is_cut[name]['short']:
                        short_risk = self.p.risks[name]['short'][1]

                    short_qty = DataUtils.convert_to_decimal(self.broker.get_cash()) * short_risk / Decimal('100')
                    short_qty = short_qty / abs(DataUtils.convert_to_decimal(self.short_lowest[i][0]) - short_stop_price)
                    if short_qty * DataUtils.convert_to_decimal(
                            self.short_lowest[i][0]) >= short_leverage * DataUtils.convert_to_decimal(
                        self.broker.get_cash()):
                        short_qty = short_leverage * DataUtils.convert_to_decimal(self.broker.get_cash()) * Decimal(
                            '0.98') / DataUtils.convert_to_decimal(self.short_lowest[i][0])
                    short_qty = int(short_qty / self.p.step_size[name]) * self.p.step_size[name]
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i],
                                           price=float(self.short_lowest[i][0]), size=float(short_qty))
            # 현재 포지션이 존재할 경우
            if current_position_size > 0:
                # 현재 가격이 손절 가격 밑으로 내려왔을 경우 손절
                if self.closes[i][-1] > self.long_stop_prices[i] > self.closes[i][0]:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)
                    self.long_stop_prices[i] = Decimal('-1')
                    self.p.is_cut[name]['long'] = True

                else:
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=current_position_size,
                                           price=float(self.long_lowest[i][0]))
                    self.p.is_cut[name]['long'] = False
            elif current_position_size < 0:
                if self.closes[i][-1] < self.short_stop_prices[i] < self.closes[i][0]:
                    self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                    self.short_stop_prices[i] = Decimal('-1')
                    self.p.is_cut[name]['short'] = True
                else:
                    self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=abs(current_position_size),
                                          price=float(self.short_highest[i][0]))
                    self.p.is_cut[name]['short'] = False


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiLongAndShortV1)

    cerebro.broker.setcash(50000000)
    cerebro.broker.setcommission(commission=0.0005, leverage=2)
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
    file_name += "MultiDonchianv1"

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
