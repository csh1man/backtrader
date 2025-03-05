import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'ETHUSDT': DataUtil.CANDLE_TICK_4HOUR,
    'SOLUSDT': DataUtil.CANDLE_TICK_4HOUR,
}

leverage=4

class ByBitTrendFollowV1(bt.Strategy):
    params = dict(
        entry_mode={ # 0 : only long, 1 : only short, 2 : long and short
            'BTCUSDT': 0,
            'ETHUSDT': 2,
            'SOLUSDT': 0,
        },
        risk={
            'BTCUSDT':{
                'long': Decimal('2'),
                'short': Decimal('1')
            },
            'ETHUSDT':{
                'long': Decimal('2'),
                'short': Decimal('1')
            },
            'SOLUSDT':{
                'long': Decimal('2'),
                'short': Decimal('1')
            },
        },
        high_band_length={
            'BTCUSDT': {
                'long': 50,
                'short': 60,
            },
            'ETHUSDT': {
                'long': 40,
                'short': 15,
            },
            'SOLUSDT':{
                'long': 40,
                'short':15,
            },
        },
        low_band_length={
            'BTCUSDT': {
                'long': 15,
                'short': 20,
            },
            'ETHUSDT': {
                'long': 20,
                'short': 45
            },
            'SOLUSDT':{
                'long': 15,
                'short':30,
            },
        },
        high_band_constant={
            'BTCUSDT':{
                'long': 20,
                'short': 1,
            },
            'ETHUSDT': {
                'long': 10,
                'short': 50,
            },
            'SOLUSDT': {
                'long': 20,
                'short': 5,
            },
        },
        low_band_constant={
            'BTCUSDT': {
                'long': 50,
                'short': 1,
            },
            'ETHUSDT': {
                'long': 60,
                'short': 5,
            },
            'SOLUSDT': {
                'long': 25,
                'short': 5,
            },
        },
        tick_size={
            'BTCUSDT': Decimal('0.10'),
            'ETHUSDT': Decimal('0.01'),
            'SOLUSDT': Decimal('0.010'),
        },
        step_size={
            'BTCUSDT': Decimal('0.001'),
            'ETHUSDT': Decimal('0.01'),
            'SOLUSDT': Decimal('0.1'),
        }
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

        self.adj_long_high_bands = []
        self.adj_long_low_bands = []

        self.adj_short_high_bands = []
        self.adj_short_low_bands = []

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

            long_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['long'])
            long_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['long'])

            adj_long_high_band = long_high_band - (long_high_band-long_low_band) * (self.p.high_band_constant[name]['long'] / 100)
            self.adj_long_high_bands.append(adj_long_high_band)

            adj_long_low_band = long_low_band + (long_high_band-long_low_band) * (self.p.low_band_constant[name]['long'] / 100)
            self.adj_long_low_bands.append(adj_long_low_band)

            short_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['short'])
            short_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['short'])

            adj_short_high_band = short_high_band - (short_high_band-short_low_band) * (self.p.high_band_constant[name]['short'] / 100)
            self.adj_short_high_bands.append(adj_short_high_band)

            adj_short_low_band = short_low_band + (short_high_band-short_low_band) * (self.p.low_band_constant[name]['short'] / 100)
            self.adj_short_low_bands.append(adj_short_low_band)

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
        self.record_asset()

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(target_name=name)

        equity = DataUtil.convert_to_decimal(self.broker.getvalue())
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            tick_size = self.p.tick_size[name]
            step_size = self.p.tick_size[name]

            adj_long_high_band = DataUtil.convert_to_decimal(self.adj_long_high_bands[i][0])
            adj_long_low_band = DataUtil.convert_to_decimal(self.adj_long_low_bands[i][0])
            adj_short_high_band = DataUtil.convert_to_decimal(self.adj_short_high_bands[i][0])
            adj_short_low_band = DataUtil.convert_to_decimal(self.adj_short_low_bands[i][0])

            adj_long_high_band = int(adj_long_high_band / tick_size) * tick_size
            adj_long_low_band = int(adj_long_low_band / tick_size) * tick_size
            adj_short_high_band = int(adj_short_high_band / tick_size) * tick_size
            adj_short_low_band = int(adj_short_low_band / tick_size) * tick_size

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                entry_mode = self.p.entry_mode[name]

                # 롱 포지션 사이즈 계산
                long_qty = equity * (self.p.risk[name]['long'] / Decimal('100')) / abs(adj_long_high_band - adj_long_low_band)
                long_qty = int(long_qty / step_size) * step_size

                # 숏 포지션 사이즈 계산
                short_qty = equity * (self.p.risk[name]['short'] / Decimal('100')) / abs(adj_short_low_band - adj_short_high_band)
                short_qty = int(short_qty / step_size) * step_size

                if entry_mode in [0, 2]: # long position 진입
                    self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(adj_long_high_band), size=float(long_qty))

                if entry_mode in [1, 2]: # short position 진입
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], price=float(adj_short_low_band), size=float(short_qty))

            elif current_position_size > 0:
                self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(current_position_size), price=float(adj_long_low_band))
            elif current_position_size < 0:
                self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=float(abs(current_position_size)), price=float(adj_short_high_band))


if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ByBitTrendFollowV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.001, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
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
    file_name += "ByBitTrendFollowV1"

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
    df.to_csv(f'{file_name}.csv')
    qs.reports.html(df['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)

    returns = returns[returns.index >= '2020-09-01']
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')