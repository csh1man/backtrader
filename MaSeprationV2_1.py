import backtrader as bt
from repository.Repository import DB
from util.Util import DataUtil
from indicator.Indicators import Indicator
from decimal import Decimal
import math
import pandas as pd
import quantstats as qs
import datetime
"""
<STEP_SIZE>
BTCUSDT 0.001
ETHUSDT 0.01
SOLUSDT 0.1
OPUSDT 0.1
TRBUSDT 0.001
"""
class MaSeparationStrategyV2(bt.Strategy):
    params = dict(
        risk_per_trade=10,  # 초기 진입 시드 비율
        add_risk_per_trade=5,  # 추가 진입 시드 비율
        ma_length=120,  # 이동평균선 주기
        sep_limit=102,  # 이격도 기준
        atr_length=3,  # atr 주기
        atr_constant=1.5,  # atr 상수
        pyramiding_limit=3,  # 피라미딩 제한 횟수
        percent_limit=5  # 현재 종가가 평단가보다 percent_limit% 보다 높은 지 확인
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 캔들 정보 초기화
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.date = self.datas[0].datetime

        # 디비 연동을 통해 종목의 수량 단위를 획득
        self.step_size = 0.001
        # self.db = DB()
        # self.step_size = self.db.get_currency_info(DataUtil.COMPANY_BYBIT, "BTCUSDT").step_size

        # 지표 정보 초기화
        self.ma = bt.indicators.SimpleMovingAverage(self.close, period=self.p.ma_length)
        self.separation = Indicator.get_ma_separation(self.close, self.ma)
        self.atr = bt.indicators.AverageTrueRange(period=self.p.atr_length)

        # 거래 정보에 대한 추적을 위한 변수 초기화
        self.pyramiding_count = 0
        self.active_orders = []
        self.stop_price = None
        self.leverage = None

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
        진입 조건 확인 => 이격도 값이 이격도 기준을 상향 돌파
        :return: True / False
        """
        if self.separation[-1] < self.p.sep_limit < self.separation[0]:
            return True
        return False

    def exit_condition(self):
        """
        종료 조건 확인 => 이격도 값이 이격도 기준을 하향 돌파
        :return: True / False
        """
        if self.separation[-1] > self.p.sep_limit > self.separation[0]:
            return True
        return False

    def cut_condition(self):
        """
        손절 조건 확인
        :return: True / False
        """
        if self.close[0] < self.stop_price:
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
                    f"[{self.date.datetime(0)}] 진입 완료. 진입 가격 : {order.executed.price} / 진입 수량 : {order.executed.size}, 레버리지 : {self.leverage}")
                self.pyramiding_count += 1
                self.total_trading_count += 1
            elif order.issell():
                self.log(
                    f"[{self.date.datetime(0)}] 종료 완료. 종료 가격 : {order.executed.price} / 종료 수량 : {order.executed.size}")
                for buy_order in self.active_orders:
                    if order.executed.price > buy_order.executed.price:
                        self.winning_trading_count += 1
                self.active_orders.clear()
                self.pyramiding_count = 0
            self.log(f"피라미딩 카운트 : {self.pyramiding_count}")
            self.log("")

    def next(self):
        if self.date.datetime(0) > datetime.datetime(2024, 1, 6, 0, 0, 0):
            return
        # 자산 추적을 위해 현재 포토폴리오 가치 저장
        self.date_value.append(self.date.datetime(0))
        self.my_assets.append(self.broker.getvalue() + self.getposition(self.datas[0]).size * self.low[0])

        if not self.position:
            if self.entry_condition():
                self.stop_price = Indicator.get_cut_price(self.close[0], self.atr[0], self.p)
                diff_percent = Indicator.get_diff_percent(self.close[0], self.stop_price)
                # 손절가와 진입가격 간의 차이 퍼센트가 0보다 클때만 진입을 진행
                if diff_percent > Decimal("0"):
                    # 레버리지 계산
                    self.leverage = Indicator.get_leverage(self.p.risk_per_trade, diff_percent)
                    # 초기 진입 수량 획득
                    position_size = self.leverage * Decimal(str(self.broker.getvalue())) * \
                                                    Decimal(str(self.p.risk_per_trade)) / \
                                                    Decimal("100") / \
                                                    Decimal(str(self.close[0]))
                    # 자산에 대한 수량 단위 설정
                    position_size = math.floor(position_size /
                                               Decimal(str(self.step_size))) * \
                                               Decimal(str(self.step_size))
                    # 롱 진입
                    order = self.buy(size=float(position_size))
                    self.active_orders.append(order)

        else:
            # 손절 조건이 만족하는 지 확인
            if self.cut_condition():
                self.sell(size=self.getposition(self.datas[0]).size)

            # 종료 조건이 만족하는 지 확인
            elif self.exit_condition():
                self.log(f"종료 사이즈 : [{self.getposition(self.datas[0]).size}]")
                self.sell(size=self.getposition(self.datas[0]).size)

            # 아직 피라미딩 제한 만큼 진입하지 않았다면
            elif self.pyramiding_count < self.p.pyramiding_limit:
                # 평단가와 종가간의 퍼센트 획득
                average_price = self.position.price
                percent = Indicator.customized_round((self.close[0] - average_price) * 100 / average_price)
                if percent > self.p.percent_limit:
                    self.log(f"[{self.date.datetime(0)}] => {percent}%")
                    # 추가 진입 수량 획득
                    position_size = self.leverage * Decimal(str(self.broker.getvalue())) * \
                                    Decimal(str(self.p.add_risk_per_trade)) / Decimal("100") / \
                                    Decimal(str(self.close[0]))
                    # 자산에 대한 수량 단위 설정
                    position_size = math.floor(position_size /
                                               Decimal(str(self.step_size))) * \
                                    Decimal(str(self.step_size))
                    order = self.buy(size=float(position_size))
                    self.active_orders.append(order)

    def stop(self):
        self.winning_rate = self.winning_trading_count * 100 / self.total_trading_count
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getvalue())

        self.log("total trading count %.2f" % self.total_trading_count)
        self.log("winning percent : [%.2f]" % self.winning_rate)
        self.log(f"수익률 : {self.return_rate}%")


if __name__ == '__main__':
    # config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    # DB.init_connection_pool(config_path)

    df = DataUtil.load_candle_data_as_df(DataUtil.CANDLE_DATA_DIR_PATH_V2, DataUtil.COMPANY_BYBIT,
                                         "BTCUSDT", DataUtil.CANDLE_TICK_2HOUR)
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.0002, leverage=50)

    # 백테스팅할 데이터 및 전략 셋팅
    cerebro.adddata(data)
    cerebro.addstrategy(MaSeparationStrategyV2)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가
    results = cerebro.run()

    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    mdd = Indicator.calculate_max_draw_down(asset_list)
    print(f"quanstats's my function MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f"quanstats's  returns MDD : {mdd * 100:.2f} %")

    cagr = qs.stats.cagr(returns)
    print(f"CACR : {cagr * 100 :.2f}%")

    sharpe = qs.stats.sharpe(returns)
    print(f"SHARPE :{sharpe:.2f}%")

    qs.reports.html(returns, output=f'result/maSeparation_v2_btcusdt.html', title='result')