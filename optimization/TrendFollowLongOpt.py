# import backtrader as bt
# import pandas as pd
# import math
# import quantstats as qs
from util.Util import DataUtil
# from decimal import Decimal
# from operator import itemgetter
#
pairs = {
    'SOLUSDT': DataUtil.CANDLE_TICK_4HOUR,
}

leverage = 3

from datetime import datetime
import backtrader as bt
import math
import quantstats as qs
import pandas as pd
from scipy import stats
from decimal import Decimal
from operator import itemgetter
import numpy as np

class TrendFollowLongOpt(bt.Strategy):
    params = dict(
        high_band_length=30,
        low_band_length=15,
        high_band_const=10,
        low_band_const=5,
        atr_length=10,
        atr_const=1.0,
        log=True,
        risk=1,
        tick_size=0.0100,
        step_size=1
    )

    def __init__(self):
        self.closes = self.datas[0].close
        self.high_band = bt.indicators.Highest(self.datas[0].high, period=self.p.high_band_length)
        self.low_band = bt.indicators.Lowest(self.datas[0].low, period=self.p.low_band_length)
        self.atr = bt.indicators.AverageTrueRange(self.datas[0], period=self.p.atr_length)
        self.stop_price = 0

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

    def cancel_all(self):
        open_orders = self.broker.get_orders_open()
        for order in open_orders:
            if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
                self.broker.cancel(order)

    def next(self):
        equity = self.broker.get_value()
        self.cancel_all()
        mypos = self.getposition(self.datas[0]).size  # 내 현재 포지션
        if mypos == 0:
            adj_high_band = self.high_band[0] - (self.high_band[0]-self.low_band[0]) * (self.p.high_band_const / 100)
            adj_high_band = int(adj_high_band / self.p.tick_size) * self.p.tick_size

            stop_price = adj_high_band - self.atr[0] * self.p.atr_const
            stop_price = int(stop_price / self.p.tick_size) * self.p.tick_size
            self.stop_price = stop_price

            qty = equity * self.p.risk / 100 / abs(adj_high_band-stop_price)
            if qty * adj_high_band / leverage >= equity:
                qty= equity * 0.98 / adj_high_band
            self.order=self.buy(exectype=bt.Order.Stop, data=self.datas[0], price=adj_high_band, size=qty)

        elif mypos > 0:
            adj_low_band = self.low_band[0] + (self.high_band[0] - self.low_band[0]) * (self.p.low_band_const / 100)
            adj_low_band = int(adj_low_band / self.p.tick_size) * self.p.tick_size
            if self.closes[-1] >= self.stop_price > self.closes[0]:
                self.order=self.sell(exectype=bt.Order.Market, data=self.datas[0],size=mypos)
            else:
                self.order=self.sell(exectype=bt.Order.Stop, data=self.datas[0], size=mypos, price=adj_low_band)

    def log(self, message):
        if self.p.log:
            print(message)

    def stop(self):
        print('progress...', self.p.high_band_length, self.p.low_band_length)

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
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro(optreturn=False, stdstats=False)  # 최적화를 위한 옵션 설정
    cerebro.broker.setcommission(commission=0.003)  # 0.3% 수수료 설정
    cerebro.broker.setcash(10_000_000)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BINANCE, 'SOLUSDT', pairs['SOLUSDT'])
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')
    cerebro.adddata(data)  # 데이터 피드 추가

    # 최적화 찾기 추가
    # 너무 많은 변수 찾기는 메모리 부족을 일으킬 수 있음
    cerebro.optstrategy(TrendFollowLongOpt, log=False, high_band_length=range(20, 50, 5), low_band_length=range(5, 30, 5))
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
            result_string = f"Return : {comp:.2f}, SHARPE: {sharpe:.2f}, CAGR: {cagr * 100:.2f} %, MDD : {mdd * 100:.2f} % {strat.p.high_band_length} {strat.p.low_band_length}"
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
