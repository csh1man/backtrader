import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from api.Api import Common, Download
from decimal import Decimal

# config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"
# download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
# download_dir_path = "/Users/tjgus/Desktop/project/krtrade/backData"

# result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
# result_file_path = "/Users/tjgus/Desktop/project/krtrade/backData/result/"

result_file_prefix = "TrendFollow1H"

pairs = {
    # 'ETHUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'SUIUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # '1000PEPEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'XRPUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'DOGEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'CRVUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'STXUSDT': DataUtils.CANDLE_TICK_1HOUR,
}


exchange = DataUtil.BINANCE
leverage=3

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)

class TrendFollow1H(bt.Strategy):
    params = dict(
        risk={
            'ETHUSDT':{
                'long': Decimal('2'),
                'short': Decimal('2')
            },
            'TRXUSDT': {
                'long': Decimal('2'),
                'short': Decimal('2')
            },
            '1000PEPEUSDT': [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
            'SUIUSDT': [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
            'STXUSDT': [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
            '1000BONKUSDT': [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
            'XRPUSDT': [Decimal('0.1'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
            'DOGEUSDT': [Decimal('0.1'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'),Decimal('16'), Decimal('20')],
            '1000SHIBUSDT': [Decimal('0.1'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
            'CRVUSDT': [Decimal('0.1'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
            'ZECUSDT': [Decimal('0.1'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16'), Decimal('20')],
        },
        entry_mode={ # 0 : only long, 1 : only short, 2: long and short, 3: counter trend
            'ETHUSDT': 2,
            'TRXUSDT': 1,
            '1000PEPEUSDT': 3,
            'SUIUSDT': 3,
            'STXUSDT': 3,
            '1000BONKUSDT': 3,
            'XRPUSDT': 3,
            'DOGEUSDT': 3,
            '1000SHIBUSDT': 3,
            'CRVUSDT': 3,
            'ZECUSDT': 3,
        },
        high_band_length={
            'ETHUSDT': {
                'long': 230,
                'short': 30,
            },
            'TRXUSDT': {
                'long': 230,
                'short': 20,
            },
            '1000PEPEUSDT': {
                'long': 200,
                'short': 30,
            },
            'SUIUSDT': {
                'long': 200,
                'short': 30,
            },
            'STXUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000BONKUSDT': {
                'long': 200,
                'short': 30,
            },
            'XRPUSDT': {
                'long': 200,
                'short': 30,
            },
            'DOGEUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000SHIBUSDT': {
                'long': 200,
                'short': 30,
            },
            'CRVUSDT': {
                'long': 200,
                'short': 30,
            },
            'ZECUSDT': {
                'long': 200,
                'short': 30,
            },
        },
        low_band_length={
            'ETHUSDT': {
                'long': 50,
                'short': 230
            },
            'TRXUSDT': {
                'long': 50,
                'short': 230,
            },
            '1000PEPEUSDT': {
                'long': 200,
                'short': 30,
            },
            'SUIUSDT': {
                'long': 200,
                'short': 30,
            },
            'STXUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000BONKUSDT': {
                'long': 200,
                'short': 30,
            },
            'XRPUSDT': {
                'long': 200,
                'short': 30,
            },
            'DOGEUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000SHIBUSDT': {
                'long': 200,
                'short': 30,
            },
            'CRVUSDT': {
                'long': 200,
                'short': 30,
            },
            'ZECUSDT': {
                'long': 200,
                'short': 30,
            },
        },
        high_band_constant={
            'ETHUSDT': {
                'long': -25,
                'short': 55,
            },
            'TRXUSDT': {
                'long': -25,
                'short': 60,
            },
            '1000PEPEUSDT': {
                'long': 200,
                'short': 30,
            },
            'SUIUSDT': {
                'long': 200,
                'short': 30,
            },
            'STXUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000BONKUSDT': {
                'long': 200,
                'short': 30,
            },
            'XRPUSDT': {
                'long': 200,
                'short': 30,
            },
            'DOGEUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000SHIBUSDT': {
                'long': 200,
                'short': 30,
            },
            'CRVUSDT': {
                'long': 200,
                'short': 30,
            },
            'ZECUSDT': {
                'long': 200,
                'short': 30,
            },
        },
        low_band_constant={
            'ETHUSDT': {
                'long': 50,
                'short': 5
            },
            'TRXUSDT': {
                'long': 50,
                'short': 5,
            },
            '1000PEPEUSDT': {
                'long': 200,
                'short': 30,
            },
            'SUIUSDT': {
                'long': 200,
                'short': 30,
            },
            'STXUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000BONKUSDT': {
                'long': 200,
                'short': 30,
            },
            'XRPUSDT': {
                'long': 200,
                'short': 30,
            },
            'DOGEUSDT': {
                'long': 200,
                'short': 30,
            },
            '1000SHIBUSDT': {
                'long': 200,
                'short': 30,
            },
            'CRVUSDT': {
                'long': 200,
                'short': 30,
            },
            'ZECUSDT': {
                'long': 200,
                'short': 30,
            },
        },
        ma_length={
          'ETHUSDT': {
              'long': [5, 10, 15],
              'short': [5, 10, 15]
          },
          'TRXUSDT': {
              'long': [5, 10, 15],
              'short': [5, 10, 15]
          },
          '1000PEPEUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          'SUIUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          'STXUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          '1000BONKUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          'XRPUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          'DOGEUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          '1000SHIBUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          'CRVUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
          'ZECUSDT': {
              'long': [5, 10, 15],
              'short': [10, 20, 30]
          },
        },
        rsi_length={
            'ETHUSDT': 2,
            '1000PEPEUSDT': 2,
            'SUIUSDT': 3,
            'STXUSDT': 2,
            'XRPUSDT': 2,
            'DOGEUSDT': 2,
            'CRVUSDT': 2,
        },
        rsi_limit={
            'ETHUSDT': 50,
            '1000PEPEUSDT': 50,
            'SUIUSDT': 50,
            'STXUSDT': 50,
            'XRPUSDT': 50,
            'DOGEUSDT': 50,
            'CRVUSDT': 50,
        },
        bb_length={
            'ETHUSDT': 30,
            'TRXUSDT': 30,
            '1000PEPEUSDT': 30,
            'SUIUSDT': 30,
            'STXUSDT': 30,
            '1000BONKUSDT': 30,
            'XRPUSDT': 30,
            'DOGEUSDT': 30,
            '1000SHIBUSDT': 30,
            'CRVUSDT': 30,
            'ZECUSDT': 30,
        },
        bb_mult={
            'ETHUSDT': 0.5,
            'TRXUSDT': 0.5,
            '1000PEPEUSDT': 0.5,
            'SUIUSDT': 0.5,
            'STXUSDT': 0.5,
            '1000BONKUSDT': 0.5,
            'XRPUSDT': 0.5,
            'DOGEUSDT': 0.5,
            '1000SHIBUSDT': 0.5,
            'CRVUSDT': 0.5,
            'ZECUSDT': 0.5,
        },
        exit_percent={
            '1000PEPEUSDT': Decimal('0'),
            'SUIUSDT': Decimal('0'),
            'STXUSDT': Decimal('0'),
            'XRPUSDT': Decimal('0'),
            'DOGEUSDT': Decimal('0'),
            'CRVUSDT': Decimal('0'),
        },
        percent={
            '1000PEPEUSDT': {
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12'), Decimal('30.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
            },
            'SUIUSDT': {
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12'), Decimal('30.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
            },
            'STXUSDT': {
                'bull': [Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
                'def': [Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
                'bear': [Decimal('4.0'), Decimal('5.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
            },
            '1000BONKUSDT': {
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12'), Decimal('30.0')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('30.0')],
            },
            'XRPUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'bear': [Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('25.0'), Decimal('30.0'), Decimal('40.0')],
            },
            'DOGEUSDT': {
                'bull': [Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'bear': [Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('25.0'), Decimal('30.0'), Decimal('40.0')],
            },
            '1000SHIBUSDT': {
                'bull': [Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'bear': [Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('25.0'), Decimal('30.0'), Decimal('40.0')],
            },
            'CRVUSDT': {
                'bull': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('40.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'bear': [Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('25.0'), Decimal('30.0'), Decimal('40.0')],
            },
            'ZECUSDT': {
                'bull': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('40.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'), Decimal('25.0'), Decimal('40.0')],
                'bear': [Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'), Decimal('25.0'), Decimal('30.0'), Decimal('40.0')],
            },
        },
        tick_size={
            'ETHUSDT': common.fetch_tick_size(exchange, 'ETHUSDT'),
            'SUIUSDT': common.fetch_tick_size(exchange, 'SUISUDT'),
            '1000PEPEUSDT': common.fetch_tick_size(exchange, '1000PEPEUSDT'),
            'XRPUSDT': common.fetch_tick_size(exchange, 'XRPUSDT'),
            'DOGEUSDT': common.fetch_tick_size(exchange, 'DOGEUSDT'),
            'CRVUSDT': common.fetch_tick_size(exchange, 'CRVUSDT'),
            'STXUSDT': common.fetch_tick_size(exchange, 'STXUSDT'),
        },
        step_size={
            'ETHUSDT': common.fetch_step_size(exchange, 'ETHUSDT'),
            'SUIUSDT': common.fetch_step_size(exchange, 'SUISUDT'),
            '1000PEPEUSDT': common.fetch_step_size(exchange, '1000PEPEUSDT'),
            'XRPUSDT': common.fetch_step_size(exchange, 'XRPUSDT'),
            'DOGEUSDT': common.fetch_step_size(exchange, 'DOGEUSDT'),
            'CRVUSDT': common.fetch_step_size(exchange, 'CRVUSDT'),
            'STXUSDT': common.fetch_step_size(exchange, 'STXUSDT'),
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
        self.short_ma = []
        self.mid_ma = []
        self.long_ma = []
        self.rsi = []

        self.long_high_bands = []
        self.long_low_bands = []

        self.short_high_bands = []
        self.short_low_bands = []

        self.short_short_ma = []
        self.short_mid_ma = []
        self.short_long_ma = []

        self.long_short_ma = []
        self.long_mid_ma = []
        self.long_long_ma = []

        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []

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

            short_short_ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['short'][0])
            self.short_short_ma.append(short_short_ma)

            short_mid_ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['short'][1])
            self.short_mid_ma.append(short_mid_ma)

            short_long_ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['short'][2])
            self.short_long_ma.append(short_long_ma)

            long_short_ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['long'][0])
            self.long_short_ma.append(long_short_ma)

            long_mid_ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['long'][1])
            self.long_mid_ma.append(long_mid_ma)

            long_long_ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['long'][2])
            self.long_long_ma.append(long_long_ma)

            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
            self.rsi.append(rsi)

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
            self.cancel_all(target_name=name)

        for i in range(0, len(self.pairs)):

            name = self.names[i]
            tick_size = common.fetch_tick_size(exchange, name)
            step_size = common.fetch_step_size(exchange, name)

            long_high_band = DataUtils.convert_to_decimal(self.long_high_bands[i][0])
            long_low_band = DataUtils.convert_to_decimal(self.long_low_bands[i][0])

            long_adj_high_band = long_high_band - (long_high_band-long_low_band) * (self.p.high_band_constant[name]['long'] / Decimal('100'))
            long_adj_high_band = int(long_adj_high_band / tick_size) * tick_size

            long_adj_low_band = long_low_band + (long_high_band-long_low_band) * (self.p.low_band_constant[name]['long'] / Decimal('100'))
            long_adj_low_band = int(long_adj_low_band / tick_size) * tick_size

            short_high_band = DataUtils.convert_to_decimal(self.short_high_bands[i][0])
            short_low_band = DataUtils.convert_to_decimal(self.short_low_bands[i][0])

            short_adj_high_band = short_high_band - (short_high_band-short_low_band) * (self.p.high_band_constant[name]['short'] / Decimal('100'))
            short_adj_high_band = int(short_adj_high_band / tick_size) * tick_size

            short_adj_low_band = short_low_band + (short_high_band-short_low_band) * (self.p.low_band_constant[name]['short'] / Decimal('100'))
            short_adj_low_band = int(short_adj_low_band / tick_size) * tick_size

            entry_mode = self.p.entry_mode[name]
            equity = DataUtils.convert_to_decimal(self.broker.getvalue())
            current_position_size = self.getposition(self.pairs[i]).size
            if entry_mode in [0, 1, 2]:
                if current_position_size == 0:
                    if entry_mode in [0, 2]:
                        long_qty = equity * self.p.risk[name]['long'] / Decimal('100') / abs(long_adj_high_band-long_adj_low_band)
                        long_qty = int(long_qty / step_size) * step_size
                        if long_qty > 0 and self.long_short_ma[i][0] >= self.long_mid_ma[i][0] >= self.long_long_ma[i][0]:
                            self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(long_adj_high_band), size=float(long_qty))
                    if entry_mode in [1, 2]:
                        short_qty = equity * self.p.risk[name]['short'] / Decimal('100') / abs(short_adj_low_band-short_adj_high_band)
                        short_qty = int(short_qty / step_size) * step_size
                        if short_qty > 0 and self.short_short_ma[i][0] <= self.short_mid_ma[i][0] <= self.short_long_ma[i][0]:
                            self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], price=float(short_adj_low_band), size=float(short_qty))
                elif current_position_size > 0:
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], price=float(long_adj_low_band), size=float(current_position_size))
                elif current_position_size < 0:
                    self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(short_adj_high_band), size=float(abs(current_position_size)))
            else:
                if current_position_size > 0:
                    if self.rsi[i][0] >= self.p.rsi_limit[name]:
                        exit_price = DataUtils.convert_to_decimal(self.closes[i][0]) * (
                                Decimal('1') + self.p.exit_percent[name] / Decimal('100'))
                        exit_price = int(exit_price / tick_size) * tick_size

                        self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], size=current_position_size,
                                               price=float(exit_price))
                if self.closes[i][0] >= self.bb_top[i][0]:
                    percents = self.p.percent[name]['bull']
                elif self.bb_bot[i][0] <= self.closes[i][0] < self.bb_top[i][0]:
                    percents = self.p.percent[name]['def']
                else:
                    percents = self.p.percent[name]['bear']

                equity = DataUtils.convert_to_decimal(self.broker.getvalue())
                for j in range(0, len(self.p.risk[name])):
                    percent = percents[j]
                    price = DataUtils.convert_to_decimal(self.closes[i][0]) * (
                            Decimal('1') - percent / Decimal('100'))
                    price = int(price / tick_size) * tick_size
                    risk = self.p.risk[name][j]
                    qty = equity * risk / Decimal('100') / price
                    qty = int(qty / step_size) * step_size

                    cash = DataUtils.convert_to_decimal(self.broker.get_cash())
                    margin = qty * price / Decimal(leverage)
                    if cash >= margin:
                        self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty), price=float(price))

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendFollow1H)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.001, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        download.download_candles(exchange, pair, tick_kind)
        df = DataUtils.load_candle_data_as_df(download_dir_path, exchange, pair, tick_kind)
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

    file_name = result_file_path + result_file_prefix
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"

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
    df.to_csv(f'{file_name}.csv')
    qs.reports.html(df['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)

    returns = returns[returns.index >= '2021-11-01']
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')