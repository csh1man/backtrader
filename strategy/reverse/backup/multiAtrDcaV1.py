import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'XRPUSDT' : DataUtil.CANDLE_TICK_30M,
    'TONUSDT': DataUtil.CANDLE_TICK_30M,
    # 'POPCATUSDT' : DataUtil.CANDLE_TICK_30M
}


class MultiAtrDcaV1(bt.Strategy):
    params=dict(
        atr_length={
            'TONUSDT': 5,
            'POPCATUSDT': 5,
            'XRPUSDT': 5
        },
        atr_avg_length={
            'TONUSDT': 2,
            'POPCATUSDT': 2,
            'XRPUSDT': 2
        },
        atr_constant={
            'TONUSDT' : Decimal('1.0'),
            'POPCATUSDT': Decimal('1.0'),
            'XRPUSDT': Decimal('1.0')
        },
        rsi_length=2,
        rsi_low_limit = {
            'TONUSDT': 10,
            'POPCATUSDT': 10,
            'XRPUSDT': 10,
        },
        exit_percent={
            'TONUSDT': Decimal('0.5'),
            'POPCATUSDT': Decimal('0.5'),
            'XRPUSDT': Decimal('0.5')
        },
        add_exit_percent={
            'TONUSDT': Decimal('0.5'),
            'POPCATUSDT' : Decimal('0.5'),
            'XRPUSDT': Decimal('0.5')
        },
        step_size={
            'TONUSDT': Decimal('0.1'),
            'POPCATUSDT': Decimal('1'),
            'XRPUSDT': Decimal('1'),
        },
        tick_size={
            'TONUSDT': Decimal('0.0001'),
            'POPCATUSDT': Decimal('0.0001'),
            'XRPUSDT': Decimal('0.0001'),
        },
        low_band_length={
            'TONUSDT': 5,
            'POPCATUSDT': 5,
            'XRPUSDT': 5,
        },
        risk={
            'TONUSDT': Decimal('3'),
            'POPCATUSDT': Decimal('3'),
            'XRPUSDT': Decimal('3')
        }
    )

    def log(self, txt=None):
        print(f'{txt}')

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.atrs = []
        self.rsis = []
        self.low_band = []

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

            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.SmoothedMovingAverage(tr, period=self.p.atr_length[name])
            atr = bt.indicators.MovingAverageSimple(atr, period=self.p.atr_avg_length[name])
            self.atrs.append(atr)

            rsi = bt.ind.RSI_Safe(self.closes[i], period=self.p.rsi_length)
            self.rsis.append(rsi)

            self.low_band.append(bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]))
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
                self.total_trading_count += 1
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def next(self):
        for i in range(0, len(self.pairs)):
            self.cancel_all()
            self.record_asset()
            name = self.names[i]
            price = DataUtil.convert_to_decimal(self.low_band[i][-1]) - DataUtil.convert_to_decimal(self.atrs[i][0]) * self.p.atr_constant[name]
            price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]

            current_position_size = self.getposition(self.pairs[i]).size
            equity = DataUtil.convert_to_decimal(self.broker.get_cash())
            if current_position_size == 0:
                qty = equity * self.p.risk[name] / Decimal('100') / price
                qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
                if qty > 0:
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price),
                                          size=float(qty))
            elif current_position_size > 0:
                qty = current_position_size
                if qty > 0:
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price),
                                          size=float(qty))
                percent = self.p.exit_percent[name]
                if self.rsis[i][0] < self.p.rsi_low_limit[name]:
                    percent += self.p.add_exit_percent[name]

                exit_price = DataUtil.convert_to_decimal(self.getposition(self.pairs[i]).price) * (Decimal('1') + percent / Decimal('100'))
                exit_price = int(exit_price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(exit_price), size=float(qty))

    def stop(self):
        self.log(f'total trading count : {self.total_trading_count}')

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiAtrDcaV1)

    cerebro.broker.setcash(5000000)
    cerebro.broker.setcommission(0.0002, leverage=1)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('Before Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

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
    file_name += "MultiAtrDcaV1"

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