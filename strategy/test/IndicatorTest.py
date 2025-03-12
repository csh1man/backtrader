import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal
import math

pairs = {
    'ETHUSDT': DataUtils.CANDLE_TICK_4HOUR,
    # 'BTCUSDT' : DataUtil.CANDLE_TICK_4HOUR,
    # 'BCHUSDT' : DataUtil.CANDLE_TICK_4HOUR,
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
                'short': Decimal('1.0')
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

            long_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr['length'][name]['long'])
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
            long_atr = int(DataUtils.convert_to_decimal(self.long_atrs[i][0]) / self.p.tick_size[name]) * self.p.tick_size[name]
            self.log(f"[{name}] [{self.dates[i].datetime(0)}] long atr : {long_atr}, short atr : {self.short_atrs[i][0]}")




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


