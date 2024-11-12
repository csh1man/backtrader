import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal
import backtrader as bt
import pandas as pd
pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_4HOUR,
    '1000BONKUSDT': DataUtil.CANDLE_TICK_30M,
    '1000PEPEUSDT' : DataUtil.CANDLE_TICK_30M,
}


class PercentGridWithBTCBBV1(bt.Strategy):
    params = dict(
        leverage=Decimal(5),
        btc_bb_span=600,
        btc_bb_mult=1.0,
        target_percents={
            '1000BONKUSDT' : Decimal(1.0),
            '1000PEPEUSDT' : Decimal(1.0),
        },
        bullish_entry_percents={
            '1000BONKUSDT': [Decimal(2), Decimal(3), Decimal(4), Decimal(6), Decimal(8.0), Decimal(10)],
            '1000PEPEUSDT': [Decimal(2), Decimal(3), Decimal(4), Decimal(6), Decimal(8.0), Decimal(10)],
        },
        default_entry_percents={
            '1000BONKUSDT': [Decimal(4), Decimal(6), Decimal(8), Decimal(10), Decimal(12.0), Decimal(14)],
            '1000PEPEUSDT': [Decimal(4), Decimal(6), Decimal(8), Decimal(10), Decimal(12.0), Decimal(14)],
        },
        bearish_entry_percents={
            '1000BONKUSDT': [Decimal(4), Decimal(6), Decimal(8), Decimal(10), Decimal(12.0), Decimal(14)],
            '1000PEPEUSDT': [Decimal(4), Decimal(6), Decimal(8), Decimal(10), Decimal(12.0), Decimal(14)],
        },
        tick_size={
            '1000BONKUSDT' : Decimal('0.0000010'),
            '1000PEPEUSDT' : Decimal('0.0000001'),
        },
        step_size={
            '1000BONKUSDT' : Decimal('100'),
            '1000PEPEUSDT': Decimal('100'),
        },
        risks={
            '1000BONKUSDT' : [Decimal('1'), Decimal('2'), Decimal('3'), Decimal('4'), Decimal('5'), Decimal('8')],
            '1000PEPEUSDT': [Decimal('1'), Decimal('2'), Decimal('3'), Decimal('4'), Decimal('5'), Decimal('8')],
        }
    )

    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        self.percents = {}
        self.ol_percents= {}
        self.pairs = []
        self.names = []
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)

        self.pair_open = []
        self.pair_high = []
        self.pair_low = []
        self.pair_close = []
        self.pair_date = []

        for i in range(0, len(self.pairs)):
            self.pair_open.append(self.pairs[i].open)
            self.pair_high.append(self.pairs[i].high)
            self.pair_low.append(self.pairs[i].low)
            self.pair_close.append(self.pairs[i].close)
            self.pair_date.append(self.pairs[i].datetime)

        self.bb = bt.indicators.BollingerBands(self.pair_close[0], period=self.p.btc_bb_span, devfactor=self.p.btc_bb_mult)
        self.bb_top = self.bb.lines.top
        self.bb_mid = self.bb.lines.mid
        self.bb_bot = self.bb.lines.bot

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
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

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
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

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
        self.order_balance_list.append([self.pair_date[0].datetime(0), account_value])
        self.date_value.append(self.pair_date[0].datetime(0))
        position_value = self.broker.getvalue()
        for i in range(1, len(self.datas)):
            position_value += self.getposition(self.datas[i]).size * self.pair_low[i][0]

        self.my_assets.append(position_value)

    def next(self):
        for i in range(1, len(self.pairs)):
            self.record_asset()
            name = self.names[i]
            bullish_percents = self.p.bullish_entry_percents[name]
            default_percents = self.p.default_entry_percents[name]
            bearish_percents = self.p.bearish_entry_percents[name]
            risks = self.p.risks[name]
            step_size = self.p.step_size[name]
            tick_size = self.p.tick_size[name]

            prices = []
            """
            <비트의 4시간봉이 볼린저밴드 상단에 존재한다는 것의 의미>
                1. 현재 비트가 상승세에 들어섰다는 것을 의미한다. (일시적이든, 장기의 시작이든)
                2. 비트가 상승세에 돌아서면, 다른 알트 코인들은 당연히 상승세에 돌입한다.

            <이 조건의 목적>
                1. 비트가 상승세에 있을 때, 일시적으로 떨어진 그 지점에서 매수하여 다시 오르면 파는 것을 목표로 한다.
            """
            self.cancel_all()

            if self.pair_close[0][0] >= self.bb_top[0]:
                for j in range(0, len(bullish_percents)):
                    price = DataUtil.convert_to_decimal(self.pair_close[i][0]) * (Decimal('1') - bullish_percents[j] / Decimal('100'))
                    price = int(Decimal(price) / tick_size) * tick_size
                    prices.append(price)
            elif self.bb_bot[0] <= self.pair_close[0][0] < self.bb_top[0]:
                for j in range(0, len(default_percents)):
                    price = DataUtil.convert_to_decimal(self.pair_close[i][0]) * (
                                Decimal('1') - default_percents[j] / Decimal('100'))
                    price = int(Decimal(price) / tick_size) * tick_size
                    prices.append(price)
            elif self.pair_close[0][0] < self.bb_bot[0]:
                for j in range(0, len(bearish_percents)):
                    price = DataUtil.convert_to_decimal(self.pair_close[i][0]) * (
                                Decimal('1') - bearish_percents[j] / Decimal('100'))
                    price = int(Decimal(price) / tick_size) * tick_size
                    prices.append(price)

            equity = DataUtil.convert_to_decimal(self.broker.get_cash())
            for j in range(0, len(prices)):
                if prices[j] == Decimal('0'):
                    continue
                qty = self.p.leverage * equity * risks[j] / Decimal(100) / prices[j]
                qty = int(qty / step_size) * step_size
                if qty > Decimal(0):
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(prices[j]),
                                          size=float(qty))

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size > 0:
                avg_price = DataUtil.convert_to_decimal(self.getposition(self.pairs[i]).price)
                target_price = avg_price * (Decimal('1') + self.p.target_percents[name] / Decimal('100'))
                self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(target_price),
                                       size=current_position_size)

if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)  # 초기 시드 설정
    cerebro.broker.setcommission(0.0002, leverage=5)  # 수수료 설정
    cerebro.addstrategy(PercentGridWithBTCBBV1)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('First Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

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
    file_name += "DataAnalysis"

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