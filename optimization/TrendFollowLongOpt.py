# import backtrader as bt
# import pandas as pd
# import math
# import quantstats as qs
from util.Util import DataUtil
# from decimal import Decimal
# from operator import itemgetter
#
pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_4HOUR,
}

leverage = 3
#
#
# class TrendFollowLongOpt(bt.Strategy):
#     params = dict(
#         pfast=100,
#         pslow=350,
#         log=False,
#         risk=1,
#         high_band_length=30,
#         low_band_length=15,
#         high_band_constant=1,
#         low_band_constant=1,
#         atr_length=10,
#         atr_constant=Decimal('1.0'),
#         tick_size={
#             'BTCUSDT': Decimal('0.10'),
#             'ETHUSDT': Decimal('0.01'),
#             'SOLUSDT': Decimal('0.0100'),
#             'BCHUSDT': Decimal('0.05'),
#             'EOSUSDT': Decimal('0.001'),
#         },
#         step_size={
#             'BTCUSDT': Decimal('0.001'),
#             'ETHUSDT': Decimal('0.01'),
#             'SOLUSDT': Decimal('1'),
#             'BCHUSDT': Decimal('0.01'),
#             'EOSUSDT': Decimal('0.001'),
#         }
#     )
#
#     def log(self, txt):
#         if self.p.log:
#             print(f'{txt}')
#
#     # def __init__(self):
#     #     self.names = []
#     #     self.pairs = []
#     #     self.opens = []
#     #     self.highs = []
#     #     self.lows = []
#     #     self.closes = []
#     #     self.dates = []
#     #
#     #     self.long_stop_prices = []
#     #     self.short_stop_prices = []
#     #
#     #     self.long_high_bands = []
#     #     self.long_low_bands = []
#     #
#     #     self.short_high_bands = []
#     #     self.short_low_bands = []
#     #
#     #     self.long_atrs = []
#     #     self.short_atrs = []
#     #
#     #     # 자산 기록용 변수 셋팅
#     #     self.order = None
#     #     self.date_value = []
#     #     self.my_assets = []
#     #
#     #     # 승률 계산을 위함
#     #     self.order_balance_list = []
#     #     self.initial_asset = self.broker.getvalue()
#     #     self.return_rate = 0
#     #     self.total_trading_count = 0
#     #     self.winning_trading_count = 0
#     #     self.winning_rate = 0
#     #
#     #     for i in range(0, len(self.datas)):
#     #         self.names.append(self.datas[i]._name)
#     #         self.pairs.append(self.datas[i])
#     #
#     #         self.opens.append(self.datas[i].open)
#     #         self.highs.append(self.datas[i].high)
#     #         self.lows.append(self.datas[i].low)
#     #         self.closes.append(self.datas[i].close)
#     #         self.dates.append(self.datas[i].datetime)
#     #
#     #         self.long_stop_prices.append(Decimal('0'))
#     #         self.short_stop_prices.append(Decimal('0'))
#     #
#     #     for i in range(0, len(self.pairs)):
#     #         name = self.names[i]
#     #
#     #         long_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length)
#     #         self.long_high_bands.append(long_high_band)
#     #
#     #         long_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length)
#     #         self.long_low_bands.append(long_low_band)
#     #
#     #         short_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length)
#     #         self.short_high_bands.append(short_high_band)
#     #
#     #         short_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length)
#     #         self.short_low_bands.append(short_low_band)
#     #
#     #         long_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length)
#     #         self.long_atrs.append(long_atr)
#     #
#     #         short_atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length)
#     #         self.short_atrs.append(short_atr)
#
#     def cancel_all(self, target_name=None):
#         open_orders = self.broker.get_orders_open()
#         for order in open_orders:
#             if target_name and order.data._name != target_name:
#                 continue
#             if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
#                 self.broker.cancel(order)
#
#     def notify_order(self, order):
#         cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
#         if order.status in [order.Completed]:
#             if order.isbuy():
#                 self.log(f'{order.ref:<3} {cur_date} =>'
#                          f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
#                          f'수량:{order.size} \t'
#                          f'가격:{order.created.price:.4f}')
#                 self.total_trading_count += 1
#             elif order.issell():
#                 self.log(f'{order.ref:<3} {cur_date} =>'
#                          f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
#                          f'수량:{order.size} \t'
#                          f'가격:{order.created.price:.4f}\n')
#
#     def stop(self):
#         self.log(f'전체 트레이딩 횟수 : {self.total_trading_count}')
#
#     def record_asset(self):
#         account_value = self.broker.get_cash()  # 현재 현금(보유 포지션 제외) 자산의 가격을 획득
#         broker_leverage = self.broker.comminfo[None].p.leverage  # cerebro에 설정한 레버리지 값 -> setcommission
#         position_value = 0.0
#         bought_value = 0.0
#         for pair in self.pairs:
#             position_value += self.getposition(pair).size * pair.low[0]
#             bought_value += self.getposition(pair).size * self.getposition(
#                 pair).price  # 진입한 수량 x 평단가 즉, 현재 포지션 전체 가치를 의미(현금 제외)
#
#         account_value += position_value - bought_value * (broker_leverage - 1) / broker_leverage
#         self.order_balance_list.append([self.dates[0].datetime(0), account_value])
#         self.date_value.append(self.dates[0].datetime(0))
#         position_value = self.broker.getvalue()
#         for i in range(1, len(self.datas)):
#             position_value += self.getposition(self.datas[i]).size * self.lows[i][0]
#
#         self.my_assets.append(position_value)
#
#     def __init__(self):
#         self.pfast = bt.ind.SMA(period=self.p.pfast)
#         self.pslow = bt.ind.SMA(period=self.p.pslow)
#
#         # 자산 기록용 변수 셋팅
#         self.order = None
#         self.date_value = []
#         self.my_assets = []
#
#         # 승률 계산을 위함
#         self.order_balance_list = []
#         self.initial_asset = self.broker.getvalue()
#         self.return_rate = 0
#         self.total_trading_count = 0
#         self.winning_trading_count = 0
#         self.winning_rate = 0
#
#     def next(self):
#         mypos = self.getposition(self.datas[0]).size  # 내 현재 포지션
#         if self.pfast[0] > self.pslow[0] and mypos <= 0:
#             self.buy(size=abs(mypos))  # 기존 포지션 청산
#             order_size = math.floor(self.broker.get_value() / self.datas[0].close * 0.95)
#             self.buy(size=order_size)  # 롱 포지션 진입
#         if self.pfast[0] < self.pslow[0] and mypos >= 0:
#             self.sell(size=abs(mypos))  # 기존 포지션 청산
#             order_size = math.floor(self.broker.get_value() / self.datas[0].close * 0.95)
#             self.sell(size=order_size)  # 숏 포지션 진입
#     #
#     # def next(self):
#     #     self.record_asset()
#     #     equity = DataUtil.convert_to_decimal(self.broker.getvalue())
#     #     for i in range(0, len(self.pairs)):
#     #         name = self.names[i]
#     #         self.cancel_all(target_name=name)
#     #
#     #         long_high_band = DataUtil.convert_to_decimal(self.long_high_bands[i][0])
#     #         long_low_band = DataUtil.convert_to_decimal(self.long_low_bands[i][0])
#     #
#     #         long_adj_high_band = long_high_band - (long_high_band - long_low_band) * DataUtil.convert_to_decimal(self.p.high_band_constant) / Decimal('100')
#     #         long_adj_high_band = int(long_adj_high_band / self.p.tick_size[name]) * self.p.tick_size[name]
#     #
#     #         long_adj_low_band = long_low_band + (long_high_band - long_low_band) * DataUtil.convert_to_decimal(self.p.low_band_constant) / Decimal('100')
#     #         long_adj_low_band = int(long_adj_low_band / self.p.tick_size[name]) * self.p.tick_size[name]
#     #
#     #         long_atr = DataUtil.convert_to_decimal(self.long_atrs[i][0])
#     #
#     #         before_close = DataUtil.convert_to_decimal(self.closes[i][-1])
#     #         current_close = DataUtil.convert_to_decimal(self.closes[i][0])
#     #
#     #         current_position_size = self.getposition(self.pairs[i]).size
#     #         if current_position_size == 0:
#     #             long_stop_price = long_adj_high_band - long_atr * self.p.atr_constant
#     #             long_stop_price = int(long_stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
#     #             self.long_stop_prices[i] = long_stop_price
#     #
#     #             long_qty = equity * (DataUtil.convert_to_decimal(self.p.risk) / Decimal('100')) / abs(long_adj_high_band - long_stop_price)
#     #             if long_qty * long_adj_high_band / leverage >= equity:
#     #                 long_qty = equity * Decimal('0.98') / long_adj_high_band
#     #             long_qty = int(long_qty / self.p.step_size[name]) * self.p.step_size[name]
#     #             self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(long_adj_high_band), size=float(long_qty))
#     #
#     #         elif current_position_size > 0:
#     #             if before_close >= self.long_stop_prices[i] > current_close:
#     #                 self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
#     #             else:
#     #                 self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(current_position_size), price=float(long_adj_low_band))
#

from datetime import datetime
import backtrader as bt
import math
import quantstats as qs
import pandas as pd
from scipy import stats
from decimal import Decimal
from operator import itemgetter
import numpy as np


# DoubleMA 전략
class DoubleMA(bt.Strategy):
    params = dict(
        pfast=100,
        pslow=350,
        log=False,
        risk=1,
        tick_size={
            'BTCUSDT': 0.1,
        },
        step_size={
            'BTCUSDT': 0.001,
        }
    )

    def __init__(self):
        self.pfast = bt.ind.SMA(period=self.p.pfast)
        self.pslow = bt.ind.SMA(period=self.p.pslow)

    def next(self):
        mypos = self.getposition(self.datas[0]).size  # 내 현재 포지션
        if self.pfast[0] > self.pslow[0] and mypos <= 0:
            self.buy(size=abs(mypos))  # 기존 포지션 청산
            order_size = math.floor(self.broker.get_value() * self.p.risk / self.datas[0].close * 0.95)
            order_size = int(order_size / self.p.step_size['BTCUSDT']) * self.p.step_size['BTCUSDT']
            self.buy(size=order_size)  # 롱 포지션 진입
        if self.pfast[0] < self.pslow[0] and mypos >= 0:
            self.sell(size=abs(mypos))  # 기존 포지션 청산
            order_size = math.floor(self.broker.get_value() * self.p.risk / self.datas[0].close * 0.95)
            order_size = int(order_size / self.p.step_size['BTCUSDT']) * self.p.step_size['BTCUSDT']
            self.sell(size=order_size)  # 숏 포지션 진입

    def log(self, message):
        if self.p.log:
            print(message)

    def stop(self):
        print('progress...', self.p.pfast, self.p.pslow)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        cur_date = order.data.datetime.date(0)
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'{cur_date} [매수 주문 실행] 종목: {order.data._name} \t 수량: {order.size} \t 가격: {order.executed.price:.4f}')
            elif order.issell():
                self.log(
                    f'{cur_date} [매도 주문 실행] 종목: {order.data._name} \t 수량: {order.size} \t 가격: {order.executed.price:.4f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(
                f'{cur_date} 주문이 거부되었습니다. 종목: {order.data._name} \t 수량: {order.size} \t 가격: {order.executed.price:.4f}')


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro(optreturn=False, stdstats=False)  # 최적화를 위한 옵션 설정
    cerebro.broker.setcommission(commission=0.003)  # 0.3% 수수료 설정
    cerebro.broker.setcash(10_000_000)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BINANCE, 'BTCUSDT', pairs['BTCUSDT'])
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')
    cerebro.adddata(data)  # 데이터 피드 추가

    # 최적화 찾기 추가
    # 너무 많은 변수 찾기는 메모리 부족을 일으킬 수 있음
    cerebro.optstrategy(DoubleMA, log=False, pfast=range(50, 150, 10), pslow=range(300, 500, 10))

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석 추가

    result_list = cerebro.run()
    result_string_list = []
    for results in result_list:
        try:
            strat = results[0]
            pyfoliozer = strat.analyzers.getbyname('pyfolio')

            returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
            returns.index = returns.index.tz_convert(None)

            # 간단한 결과 저장
            comp = qs.stats.comp(returns) * 100
            cagr = qs.stats.cagr(returns)
            mdd = qs.stats.max_drawdown(returns)
            sharpe = qs.stats.sharpe(returns)
            result_string = f"Return : {comp:.2f}, SHARPE: {sharpe:.2f}, CAGR: {cagr * 100:.2f} %, MDD : {mdd * 100:.2f} % {strat.p.pfast} {strat.p.pslow}"
            result_string_list.append([sharpe, result_string])
        except:
            pass

    # 샤프 지수 순서대로 정렬
    result_string_list = sorted(result_string_list, key=itemgetter(0))[::-1]

    print()
    print(f"[DoubleMA]")

    # 상위 10개만 출력
    for v in result_string_list[:10]:
        print(v[1])
