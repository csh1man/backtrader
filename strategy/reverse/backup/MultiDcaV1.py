import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal

pairs = {
    '1000PEPEUSDT' : DataUtils.CANDLE_TICK_30M
}

class MultiDcaV1(bt.Strategy):
    params=dict(
        start_percent=Decimal('1.5'),
        init_target_percent={
            'POPCATUSDT': Decimal('1.0'),
            '1000PEPEUSDT': Decimal('1.0')
        },
        init_target_percent2={
            'POPCATUSDT': Decimal('2.5'),
            '1000PEPEUSDT': Decimal('2.5')
        },
        add_target_percent={
            'POPCATUSDT': Decimal('1.0'),
            '1000PEPEUSDT': Decimal('1.0')
        },
        profit_percent=Decimal('0.5'),
        add_profit_percent=Decimal('0.5'),
        acc=Decimal('0.5'),
        rsi_length=2,
        rsi_low_limit=50,
        ma_len1=5,
        ma_len2=7,
        ma_len3=9,
        step_size={
            'POPCATUSDT': Decimal('1'),
            '1000PEPEUSDT': Decimal('100')
        },
        tick_size={
            'POPCATUSDT': Decimal('0.0001'),
            '1000PEPEUSDT': Decimal('0.0000001')
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
        self.rsis = []
        self.ma1 = []
        self.ma2 = []
        self.ma3 = []

        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            rsi = bt.ind.RSI_Safe(self.closes[i], period=self.p.rsi_length)
            self.rsis.append(rsi)
            self.ma1.append(bt.indicators.MovingAverageSimple(self.pairs[i], period=self.p.ma_len1))
            self.ma2.append(bt.indicators.MovingAverageSimple(self.pairs[i], period=self.p.ma_len2))
            self.ma3.append(bt.indicators.MovingAverageSimple(self.pairs[i], period=self.p.ma_len3))


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

            ma1 = round(DataUtils.convert_to_decimal(self.ma1[i][0]) / self.p.tick_size[name]) * self.p.tick_size[name]
            ma2 = round(DataUtils.convert_to_decimal(self.ma2[i][0]) / self.p.tick_size[name]) * self.p.tick_size[name]
            ma3 = round(DataUtils.convert_to_decimal(self.ma3[i][0]) / self.p.tick_size[name]) * self.p.tick_size[name]

            is_trend = ma3 < ma2 < ma1
            position_size = self.getposition(self.pairs[i]).size
            if position_size == 0:
                init_total_value = DataUtils.convert_to_decimal(self.broker.getvalue())
                init_qty = (init_total_value * self.p.start_percent / Decimal('100')) / DataUtils.convert_to_decimal(self.closes[i][0])
                init_qty = int(init_qty / self.p.step_size[name]) * self.p.step_size[name]

                price = 0.0
                if is_trend:
                    price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1.0') - self.p.init_target_percent[name] / Decimal('100'))
                    price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
                else:
                    price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1.0') - self.p.init_target_percent2[name] / Decimal('100'))
                    price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]

                self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price), size=float(init_qty))
            elif position_size > 0:
                cur_qty = DataUtils.convert_to_decimal(position_size) * self.p.acc / Decimal('2')
                cur_qty = int(cur_qty / self.p.step_size[name]) * self.p.step_size[name]

                avg_price = self.getposition(self.pairs[i]).price
                price = DataUtils.convert_to_decimal(avg_price) * (Decimal('1') - self.p.add_target_percent[name] / Decimal('100'))
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price), size=float(cur_qty))

                exit_percent = self.p.profit_percent
                if self.rsis[i][0] < self.p.rsi_low_limit:
                    exit_percent += self.p.add_profit_percent
                exit_price = DataUtils.convert_to_decimal(avg_price) * (Decimal('1') + exit_percent / Decimal('100'))
                exit_price = int(exit_price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(exit_price), size=float(position_size))


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiDcaV1)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002, leverage=3)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BYBIT, pair, tick_kind)
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
    file_name += "MultiDcaV1"

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