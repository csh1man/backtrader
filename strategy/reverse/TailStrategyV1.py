import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal

pairs = {
    '1000PEPEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'SHIB1000USDT': DataUtil.CANDLE_TICK_1HOUR,
    # '1000LUNCUSDT': DataUtil.CANDLE_TICK_1HOUR,
    # 'JASMYUSDT': DataUtil.CANDLE_TICK_1HOUR,
    # 'INJUSDT': DataUtil.CANDLE_TICK_1HOUR,
    # 'ONDOUSDT': DataUtil.CANDLE_TICK_1HOUR,
    # 'JTOUSDT': DataUtil.CANDLE_TICK_1HOUR,
    # 'WIFUSDT': DataUtil.CANDLE_TICK_1HOUR,
}


class TailStrategyV1(bt.Strategy):
    params = dict(
        leverage={
            'BCHUSDT': 2,
        },
        risks={
            'DOGEUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'XRPUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            '1000BONKUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            '1000PEPEUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'JTOUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'TIAUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'APTUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'INJUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'ONDOUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'JASMYUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            '1000LUNCUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'WIFUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'SHIB1000USDT': [Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0')],
            'BCHUSDT': [Decimal('4.0'), Decimal('2.0')],
        },
        limit_percents={
            'DOGEUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            'XRPUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            '1000BONKUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            '1000PEPEUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            'JTOUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            'TIAUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            'APTUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            'INJUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('12.0')],
            'ONDOUSDT': [Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('12.0')],
            'JASMYUSDT': [Decimal('5.0'), Decimal('7.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0')],
            '1000LUNCUSDT': [Decimal('5.0'), Decimal('7.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0')],
            'WIFUSDT': [Decimal('4.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0'), Decimal('15.0')],
            'SHIB1000USDT': [Decimal('3.0'), Decimal('5.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
        },
        rsi_length={
            'DOGEUSDT':2,
            'XRPUSDT':2,
            '1000BONKUSDT':2,
            '1000PEPEUSDT': 2,
            'JTOUSDT': 2,
            'TIAUSDT': 2,
            'APTUSDT': 2,
            'INJUSDT': 2,
            'ONDOUSDT': 2,
            'JASMYUSDT': 2,
            '1000LUNCUSDT': 2,
            'WIFUSDT': 2,
            'SHIB1000USDT': 2,
            'BCHUSDT': 2,
        },
        rsi_limit={
            'DOGEUSDT': 50,
            'XRPUSDT': 50,
            '1000BONKUSDT': 60,
            '1000PEPEUSDT': 70,
            'JTOUSDT': 60,
            'TIAUSDT': 60,
            'APTUSDT': 60,
            'INJUSDT': 60,
            'ONDOUSDT' : 80,
            'JASMYUSDT': 50,
            '1000LUNCUSDT': 80,
            'WIFUSDT': 80,
            'SHIB1000USDT': 80,
            'BCHUSDT': 50,
        },
        tick_size={
            'DOGEUSDT' : Decimal('0.000010'),
            'XRPUSDT': Decimal('0.0001'),
            '1000BONKUSDT': Decimal('0.0000010'),
            '1000PEPEUSDT': Decimal('0.0000010'),
            'JTOUSDT': Decimal('0.001'),
            'TIAUSDT': Decimal('0.0010'),
            'APTUSDT': Decimal('0.0005'),
            'INJUSDT': Decimal('0.0010'),
            'ONDOUSDT': Decimal('0.0001'),
            'JASMYUSDT': Decimal('0.000001'),
            '1000LUNCUSDT': Decimal('0.00001'),
            'SHIB1000USDT':  Decimal('0.000001'),
            'BCHUSDT': Decimal('0.10'),
            'WIFUSDT': Decimal('0.0001')
        },
        step_size={
            'DOGEUSDT': Decimal('1'),
            'XRPUSDT': Decimal('0.1'),
            '1000BONKUSDT': Decimal('100'),
            '1000PEPEUSDT': Decimal('100'),
            'JTOUSDT': Decimal('0.1'),
            'TIAUSDT': Decimal('0.1'),
            'APTUSDT' : Decimal('0.01'),
            'INJUSDT': Decimal('0.1'),
            'ONDOUSDT': Decimal('1.0'),
            'JASMYUSDT': Decimal('1'),
            '1000LUNCUSDT': Decimal('1'),
            'SHIB1000USDT': Decimal('10'),
            'BCHUSDT': Decimal('0.01'),
            'WIFUSDT': Decimal('1')
        },
    )

    def log(self, txt):
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
        self.short_highest = []
        self.short_lowest = []
        self.short_atrs = []
        self.short_stop_prices = []
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
            rsi = bt.ind.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
            self.rsis.append(rsi)

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

    def cancel_all(self, target_name=None):
        open_orders = self.broker.get_orders_open()
        for order in open_orders:
            if target_name and order.data._name != target_name:
                continue
            if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
                self.broker.cancel(order)

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{order.ref:<3} {cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                self.total_trading_count += 1
            elif order.issell():
                self.log(f'{order.ref:<3} {cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}\n')


    def stop(self):
        self.log(f'전체 트레이딩 횟수 : {self.total_trading_count}')

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

    def next(self):
        self.record_asset()  # 자산 기록

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(target_name=name)  # 미체결 주문 모두 취소

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size > 0:
                if self.rsis[i][0] > self.p.rsi_limit[name] and self.closes[i][0] > self.getposition(self.pairs[i]).price:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)

            prices = []
            limit_percents = self.p.limit_percents[name]
            for j in range(0, len(limit_percents)):
                price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1.0') - limit_percents[j] / Decimal('100'))
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
                prices.append(price)

            equity = DataUtils.convert_to_decimal(self.broker.get_cash())
            for j in range(0, len(prices)):
                price = prices[j]
                risk = self.p.risks[name][j]
                qty = equity * risk / Decimal('100') / price
                if qty > Decimal('0'):
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price), size=float(qty))

if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TailStrategyV1)

    cerebro.broker.setcash(6900)
    cerebro.broker.setcommission(commission=0.0005, leverage=2)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BYBIT, pair, tick_kind)
        df = DataUtils.get_candle_data_in_scape(df, '2024-01-01 00:00:00', '2024-12-31 00:00:00')
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    before_balance = cerebro.broker.getvalue()
    print('Before Portfolio Value: %.2f' % before_balance)
    results = cerebro.run()
    strat = results[0]
    after_balance = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % after_balance)

    # 수익률 계산
    return_percentage = ((after_balance - before_balance) / before_balance) * 100
    print('Strategy Return: %.2f%%' % return_percentage)

    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    order_balance_list = strat.order_balance_list
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")

    file_name = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
    # file_name = "/Users/tjgus/Desktop/project/krtrade/backData/result/"
    # file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "TailStrategyV1"

    strat = results[0]
    order_balance_list = strat.order_balance_list
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

