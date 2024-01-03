import math

import backtrader as bt
from util.Util import DataUtil
import pandas as pd
import quantstats as qs
from indicator.Indicators import Indicator


class MASeparationStrategy(bt.Strategy):
    params = dict(
        risk_per_trade=10,
        ma_length=120,
        sep_limit=103,
        atr_length=3,
        atr_constant=1.5,
        tick_size=0.01,
        step_size=0.01
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 캔들 데이터 초기화
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.date = self.datas[0].datetime

        # 지표 데이터 초기화
        self.ma = bt.indicators.SimpleMovingAverage(self.close, period=self.p.ma_length)
        self.separation = Indicator.get_ma_separation(self.close, self.ma)
        self.atr = bt.indicators.AverageTrueRange(period=self.p.atr_length)

        # 거래 추적용 데이터 초기화
        self.order = None
        self.stop_price = None

        # 자산 추적용 데이터 초기화
        self.date_value = []
        self.my_assets = []

        # 수익률 및 MDD 계산을 위한 추적 데이터 초기화
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

    def entry_condition(self):
        """
        진입 조건 확인 - 이격도가 이격도 지정값을 상향 돌파
        :return: True or False
        """
        if self.separation[-1] < self.p.sep_limit <= self.separation[0]:
            return True
        else:
            return False

    def exit_condition(self):
        """
        종료 조건 확인 - 이격도가 이격도 지정값을 하향 돌파
        :return: True or False
        """
        if self.separation[-1] > self.p.sep_limit > self.separation[0]:
            return True
        else:
            return False

    def cut_condition(self):
        """
        손절 조건 확인 - 종가가 정해진 손절가격보다 낮아지는 지 여부 확인
        :return: True or False
        """
        if self.stop_price > self.close[0]:
            return True
        return False

    def notify_order(self, order):
        """
        주문 상태 모니터링 함수
        :param order: 주문에 대한 객체
        :return: None
        """
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"[{self.date.datetime(0)}] 진입 완료. 진입 가격 : {order.executed.price} / 진입 수량 : {order.executed.size}")
            elif order.issell():
                self.log(
                    f"[{self.date.datetime(0)}] 종료 완료. 종료 가격 : {order.executed.price} / 종료 수량 : {order.executed.size}")
                self.log("")
                self.total_trading_count += 1
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

        self.order = None

    def next(self):
        self.date_value.append(self.date.datetime(0))
        self.my_assets.append(self.broker.getvalue() + self.getposition(self.datas[0]).size * self.low[0])

        if not self.position:
            if self.separation[-1] < self.p.sep_limit < self.separation[0] :
                self.stop_price = self.close[0] - self.atr[0] * self.p.atr_constant
                diff_percent = Indicator.get_diff_percent(self.close, self.stop_price)
                if diff_percent != 0:
                    leverage = Indicator.get_leverage(self.p.risk_per_trade, diff_percent)
                    position_size = leverage * self.broker.getvalue() * self.p.risk_per_trade / 100 / self.close[0]
                    position_size = math.floor(position_size / self.p.step_size) * self.p.step_size
                    self.buy(size=position_size, price=self.close[0])
        else:
            if self.exit_condition() or self.cut_condition():
                self.sell(size=self.getposition(self.datas[0]).size, price=self.close[0])

    def stop(self):
        self.winning_rate = self.winning_trading_count * 100 / self.total_trading_count
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getvalue())

        self.log("total trading count %.2f" % self.total_trading_count)
        self.log("winning percent : [%.2f]" % self.winning_rate)
        self.log(f"수익률 : {self.return_rate}%")


if __name__ == '__main__':
    # backtesting 할 데이터 추출
    df = DataUtil.load_candle_data_as_df(DataUtil.CANDLE_DATA_DIR_PATH_V2, DataUtil.COMPANY_BYBIT,
                                         "ETHUSDT", DataUtil.CANDLE_TICK_2HOUR)

    data = bt.feeds.PandasData(dataname=df, datetime='datetime')
    
    # cerebro 트레이딩 기본 셋팅
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.0002, leverage=20)

    # 백테스팅할 데이터 및 전략 셋팅
    cerebro.adddata(data)
    cerebro.addstrategy(MASeparationStrategy)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가
    results = cerebro.run()

    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    asset_list = pd.DataFrame({'asset':strat.my_assets}, index=pd.to_datetime(strat.date_value))
    mdd = Indicator.calculate_max_draw_down(asset_list)
    print(f"quanstats's my function MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f"quanstats's  returns MDD : {mdd * 100:.2f} %")

    cagr = qs.stats.cagr(returns)
    print(f"CACR : {cagr * 100 :.2f}%")

    sharpe = qs.stats.sharpe(returns)
    print(f"SHARPE :{sharpe:.2f}%")

    # qs.reports.html(returns, output=f'result/maSeparation_btcusdt.html', title='result')