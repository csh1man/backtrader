import backtrader as bt
import pandas as pd
import quantstats as qs
import math
from util.Util import DataUtil
from decimal import Decimal

pair = {
    '1000SHIBUSDT': DataUtil.CANDLE_TICK_1HOUR
}


class BinanceTailCatchV3(bt.Strategy):
    params=dict(
        log=True,
    )

    def log(self, txt):
        if self.p.log:
            print(f'{txt}')