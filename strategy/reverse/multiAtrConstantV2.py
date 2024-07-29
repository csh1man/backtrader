import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal
from indicator.Indicators import Indicator

pairs = {
    'BTCUSDT' : DataUtil.CANDLE_TICK_4HOUR,
    "1000BONKUSDT" : DataUtil.CANDLE_TICK_30M,
    '1000PEPEUSDT' : DataUtil.CANDLE_TICK_30M,
    'INJUSDT' : DataUtil.CANDLE_TICK_30M,
    'SEIUSDT': DataUtil.CANDLE_TICK_30M
}


class MultiAtrConstantV2(bt.Strategy):
    params = dict(
        bb_span=20,
        bb_mult=1.0,
        leverage=Decimal('10'),
        risks=[Decimal(2), Decimal(2), Decimal(4), Decimal(6), Decimal(8)],
        step_size={
            'BTCUSDT': Decimal('0.001'),
            '1000BONKUSDT': Decimal('100'),
            '1000PEPEUSDT': Decimal('100'),
            'INJUSDT': Decimal('0.1'),
            'SEIUSDT': Decimal('1')
        },
        tick_size={
            'BTCUSDT': Decimal('0.10'),
            '1000BONKUSDT': Decimal('0.0000010'),
            '1000PEPEUSDT' : Decimal('0.0000001'),
            'SEIUSDT': Decimal('0.00010'),
            'INJUSDT': Decimal('0.001'),
            'SEIUSDT': Decimal('0.00010')
        },
        atr_length={
            'BTCUSDT': 1,
            '1000BONKUSDT': 1,
            '1000PEPEUSDT': 2,
            'INJUSDT': 2,
            'SEIUSDT': 2,
        },
        atr_avg_length={
            'BTCUSDT': 1,
            '1000BONKUSDT': 1,
            '1000PEPEUSDT': 1,
            'INJUSDT': 1,
            'SEIUSDT': 1
        },
        ma_length={
            'BTCUSDT': [20, 5],
            '1000BONKUSDT': [3, 5],
            '1000PEPEUSDT': [3, 5],
            'INJUSDT': [3, 5],
            'SEIUSDT': [3, 5]
        },
        bull_constants={
            '1000BONKUSDT': [Decimal(1.5), Decimal(1.8), Decimal(2), Decimal(4), Decimal(6)],
            '1000PEPEUSDT': [Decimal(1.5), Decimal(1.8), Decimal(2), Decimal(4), Decimal(6)],
            'INJUSDT': [Decimal(1.5), Decimal(1.8), Decimal(2), Decimal(4), Decimal(6)],
            'SEIUSDT': [Decimal(1.5), Decimal(1.8), Decimal(2), Decimal(4), Decimal(6)]
        },
        def_constants={
            '1000BONKUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)],
            '1000PEPEUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)],
            'INJUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)],
            'SEIUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)]
        },
        bear_constants={
            '1000BONKUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)],
            '1000PEPEUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)],
            'INJUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)],
            'SEIUSDT': [Decimal(2), Decimal(4), Decimal(6), Decimal(8), Decimal(10)]
        }
    )

    def log(self, txt):
        print(f'{txt}')

    def __init__(self):

        '''
        기본 캔들 데이터 변수 추가
        '''
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.atrs = []

        '''
        자산 추정용 변수 추가
        '''
        self.order = None
        self.date_value = []
        self.my_assets = []
        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

        for i in range(0, len(self.datas)):
            # 이름 및 캔들 데이터 초기화
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])

            # ohlc 데이터 초기화
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        # 비트코인 볼린저밴드 초기화
        self.bb = bt.indicators.BollingerBands(self.closes[0], period=self.p.bb_span, devfactor=self.p.bb_mult)
        self.bb_top = self.bb.lines.top
        self.bb_mid = self.bb.lines.mid
        self.bb_bot = self.bb.lines.bot

        # atr 초기화
        for i in range(0, len(self.datas)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.SmoothedMovingAverage(tr, period=self.p.atr_length[self.names[i]])
            atr = bt.indicators.MovingAverageSimple(atr, period=self.p.atr_avg_length[self.names[i]])
            self.atrs.append(atr)

        # 이평선 초기화
        self.short_ma = []
        self.long_ma = []
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.short_ma.append(bt.indicators.MovingAverageSimple(self.closes[i], period=self.p.ma_length[name][0]))
            self.long_ma.append(bt.indicators.MovingAverageSimple(self.closes[i], period=self.p.ma_length[name][1]))

    '''
    모든 미체결 지정가주문을 취소한다.
    '''
    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

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

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def next(self):
        self.cancel_all()
        self.record_asset()
        for i in range(1, len(self.pairs)):
            name = self.names[i]
            if self.short_ma[i][0] < self.long_ma[i][0]:
                self.order = self.sell(data=self.pairs[i], size=self.getposition(self.pairs[i]).size)

            constants = None
            if self.closes[0][-1] >= self.bb_top[-1]:
                constants = self.p.bull_constants[name]
            elif self.bb_bot[-1] <= self.closes[0][-1] < self.bb_top[-1]:
                constants = self.p.def_constants[name]
            elif self.bb_bot[-1] > self.closes[0][-1]:
                constants = self.p.bear_constants[name]

            prices = []
            for j in range(0, len(constants)):
                price = DataUtil.convert_to_decimal(self.closes[i][0]) - DataUtil.convert_to_decimal(self.atrs[i][0]) * constants[j]
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
                prices.append(price)

            equity = DataUtil.convert_to_decimal(self.broker.getcash())
            for j in range(0, len(prices)):
                if prices[j] == Decimal('0'):
                    continue
                qty = self.p.leverage * equity * self.p.risks[j] / Decimal(100) / prices[j]
                self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(prices[j]), size=float(qty))


if __name__ == '__main__':
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiAtrConstantV2)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002, leverage=10)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('Before Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    order_balance_list = strat.order_balance_list

    mdd = qs.stats.max_drawdown(asset_list).iloc[0]
    print(f" quanstats's my variable MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")

    # file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    file_name = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"

    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "multiAtrConstantV2"

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