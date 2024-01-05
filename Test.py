import math

from util.Util import DataUtil
from decimal import Decimal
import backtrader as bt


class MASeparationStrategy(bt.Strategy):
    params = dict(
        risk_per_trade=10,
        ma_length=111,
        sep_limit=102,
        atr_length=4,
        atr_constant=1,
        tick_size=0.01,
        step_size=0.1
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

    def next(self):
        # position_size = self.broker.getvalue() * self.p.risk_per_trade / 100 / self.close[0]
        # decimal_position_size = Decimal(str(math.floor(position_size / self.p.step_size))) * Decimal(str(self.p.step_size))
        position_size = Decimal(str(self.broker.getvalue())) * Decimal(str(self.p.risk_per_trade)) / Decimal("100") / Decimal(str(self.close[0]))
        decimal_position_size = math.floor(position_size / Decimal(str(self.p.step_size))) * Decimal(str(self.p.step_size))
        self.log(f"{self.date.datetime(0)} => {decimal_position_size}")


if __name__ == '__main__':
    # backtesting 할 데이터 추출
    df = DataUtil.load_candle_data_as_df(DataUtil.CANDLE_DATA_DIR_PATH_V2, DataUtil.COMPANY_BYBIT,
                                         "OPUSDT", DataUtil.CANDLE_TICK_2HOUR)
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
