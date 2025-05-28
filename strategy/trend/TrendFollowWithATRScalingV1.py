import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from api.Api import Common, Download
from decimal import Decimal

config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
# config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"

download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
# download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
# download_dir_path = "/Users/tjgus/Desktop/project/krtrade/backData"

result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
# result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"

result_file_prefix = "TrendFollowWithATRScalingV1"

pairs = {
    'BTCUSDT': DataUtils.CANDLE_TICK_4HOUR,
    'ETHUSDT': DataUtils.CANDLE_TICK_4HOUR,
    'SOLUSDT': DataUtils.CANDLE_TICK_4HOUR,
    'AVAXUSDT': DataUtils.CANDLE_TICK_4HOUR,
    '1000PEPEUSDT': DataUtils.CANDLE_TICK_4HOUR,
    '1000BONKUSDT': DataUtils.CANDLE_TICK_4HOUR,
    'ADAUSDT': DataUtils.CANDLE_TICK_4HOUR,
    # 'FETUSDT': DataUtils.CANDLE_TICK_4HOUR,
}

exchange = DataUtil.BYBIT
leverage = 4

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)


class TrendFollowWithATRScalingV1(bt.Strategy):
    params = dict(
        entry_mode={  # 0 : only long, 1 : only short, 2 : long and short
            'BTCUSDT': 0,
            'ETHUSDT': 2,
            'SOLUSDT': 2,
            'AVAXUSDT': 2,
            '1000PEPEUSDT': 2,
            '1000BONKUSDT': 2,
            'ADAUSDT': 0,
            'FETUSDT': 0,
        },
        risk={
            'BTCUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('1.5')
            },
            'ETHUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('1.5')
            },
            'SOLUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('1.5')
            },
            'AVAXUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('3')
            },
            '1000PEPEUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('1.5')
            },
            '1000BONKUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('1.5')
            },
            'ADAUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('1.5')
            },
            'FETUSDT': {
                'long': Decimal('1.5'),
                'short': Decimal('1.5')
            },
        },
        high_band_length={
            'BTCUSDT': {
                'long': 45,
                'short': 30,
            },
            'ETHUSDT': {
                'long': 40,
                'short': 15,
            },
            'SOLUSDT': {
                'long': 45,
                'short': 50,
            },
            'AVAXUSDT': {
                'long': 45,
                'short': 50,
            },
            '1000PEPEUSDT': {
                'long': 40,
                'short': 40,
            },
            '1000BONKUSDT': {
                'long': 30,
                'short': 15,
            },
            'ADAUSDT': {
                'long': 40,
                'short': 15,
            },
            'FETUSDT': {
                'long': 45,
                'short': 15,
            },
        },
        low_band_length={
            'BTCUSDT': {
                'long': 25,
                'short': 50,
            },
            'ETHUSDT': {
                'long': 25,
                'short': 50,
            },
            'SOLUSDT': {
                'long': 25,
                'short': 90,
            },
            'AVAXUSDT': {
                'long': 25,
                'short': 75,
            },
            '1000PEPEUSDT': {
                'long': 25,
                'short': 60,
            },
            '1000BONKUSDT': {
                'long': 20,
                'short': 30,
            },
            'ADAUSDT': {
                'long': 15,
                'short': 50,
            },
            'FETUSDT': {
                'long': 30,
                'short': 50,
            },
        },
        high_band_constant={
            'BTCUSDT': {
                'long': 5,
                'short': 55,
            },
            'ETHUSDT': {
                'long': 5,
                'short': 60,
            },
            'SOLUSDT': {
                'long': 10,
                'short': 40,
            },
            'AVAXUSDT': {
                'long': 15,
                'short': 40,
            },
            '1000PEPEUSDT': {
                'long': 10,
                'short': 40,
            },
            '1000BONKUSDT': {
                'long': 10,
                'short': 0,
            },
            'ADAUSDT': {
                'long': 0,
                'short': 15,
            },
            'FETUSDT': {
                'long': 5,
                'short': 15,
            },
        },
        low_band_constant={
            'BTCUSDT': {
                'long': 50,
                'short': 10,
            },
            'ETHUSDT': {
                'long': 50,
                'short': 5,
            },
            'SOLUSDT': {
                'long': 40,
                'short': 10,
            },
            'AVAXUSDT': {
                'long': 45,
                'short': 10,
            },
            '1000PEPEUSDT': {
                'long': 50,
                'short': 20,
            },
            '1000BONKUSDT': {
                'long': 50,
                'short': 0,
            },
            'ADAUSDT': {
                'long': 65,
                'short': 0,
            },
            'FETUSDT': {
                'long': 55,
                'short': 0,
            },
        },
        rsi_length={
            'BTCUSDT': {
                'long': 2,
                'short': 14,
            },
            'ETHUSDT': {
                'long': 2,
                'short': 3,
            },
            'SOLUSDT': {
                'long': 2,
                'short': 14,
            },
            'AVAXUSDT': {
                'long': 2,
                'short': 3,
            },
            '1000PEPEUSDT': {
                'long': 2,
                'short': 2,
            },
            '1000BONKUSDT': {
                'long': 2,
                'short': 3,
            },
            'ADAUSDT': {
                'long': 2,
                'short': 3,
            },
            'FETUSDT': {
                'long': 2,
                'short': 3,
            },
        },
        rsi_limit={
            'BTCUSDT': {
                'long': 0,
                'short': 50,
            },
            'ETHUSDT': {
                'long': 0,
                'short': 30,
            },
            'SOLUSDT': {
                'long': 0,
                'short': 50,
            },
            'AVAXUSDT': {
                'long': 0,
                'short': 30,
            },
            '1000PEPEUSDT': {
                'long': 50,
                'short': 30,
            },
            '1000BONKUSDT': {
                'long': 70,
                'short': 30,
            },
            'ADAUSDT': {
                'long': 0,
                'short': 30,
            },
            'FETUSDT': {
                'long': 0,
                'short': 30,
            },
        },
        ma_length={
            'BTCUSDT': {
                'long': 120,
                'short': [160, 200]
            },
            'ETHUSDT': {
                'long': 200,
                'short': [150, 200],
            },
            'SOLUSDT': {
                'long': 120,
                'short': [160, 200]
            },
            'AVAXUSDT': {
                'long': 100,
                'short': [130, 150],
            },
            '1000PEPEUSDT': {
                'long': 100,
                'short': [130, 150],
            },
            '1000BONKUSDT': {
                'long': 120,
                'short': [60, 120],
            },
            'ADAUSDT': {
                'long': 120,
                'short': [160, 200],
            },
            'FETUSDT': {
                'long': 100,
                'short': [160, 200],
            },
        },
        atr_length={
            'BTCUSDT': [5, 50],
            'ETHUSDT': [5, 50],
            'SOLUSDT': [5, 50],
            'AVAXUSDT': [5, 50],
            '1000PEPEUSDT': [20, 50],
            '1000BONKUSDT': [5, 50],
            'ADAUSDT': [5, 70],
            'FETUSDT': [14, 50],
        },
        tick_size={
            'BTCUSDT': common.fetch_tick_size(exchange, 'BTCUSDT'),
            'ETHUSDT': common.fetch_tick_size(exchange, 'ETHUSDT'),
            'SOLUSDT': common.fetch_tick_size(exchange, 'SOLUSDT'),
            'AVAXUSDT': common.fetch_tick_size(exchange, 'AVAXUSDT'),
            '1000PEPEUSDT': common.fetch_tick_size(exchange, '1000PEPEUSDT'),
            '1000BONKUSDT': common.fetch_tick_size(exchange, '1000BONKUSDT'),
            'ADAUSDT': common.fetch_tick_size(exchange, 'ADAUSDT'),
            'FETUSDT': common.fetch_tick_size(exchange, 'FETUSDT'),
        },
        step_size={
            'BTCUSDT': common.fetch_step_size(exchange, "BTCUSDT"),
            'ETHUSDT': common.fetch_step_size(exchange, "ETHUSDT"),
            'SOLUSDT': common.fetch_step_size(exchange, "SOLUSDT"),
            'AVAXUSDT': common.fetch_step_size(exchange, "AVAXUSDT"),
            '1000PEPEUSDT': common.fetch_step_size(exchange, "1000PEPEUSDT"),
            '1000BONKUSDT': common.fetch_step_size(exchange, "1000BONKUSDT"),
            'ADAUSDT': common.fetch_step_size(exchange, "ADAUSDT"),
            'FETUSDT': common.fetch_step_size(exchange, "FETUSDT"),
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

        # 롱 채널 변수 설정
        self.long_high_bands = []
        self.long_low_bands = []
        self.short_high_bands = []
        self.short_low_bands = []

        self.adj_long_high_bands = []
        self.adj_long_low_bands = []

        # 숏 채널 변수 설정
        self.adj_short_high_bands = []
        self.adj_short_low_bands = []

        # RSI 변수 설정
        self.long_rsi = []
        self.short_rsi = []

        # 이평선 변수 설정
        self.long_ma = []
        self.short_ma1 = []
        self.short_ma2 = []

        self.atr1 = []
        self.atr2 = []

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
            self.long_high_bands.append(long_high_band)

            long_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['long'])
            self.long_low_bands.append(long_low_band)

            short_high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name]['short'])
            self.short_high_bands.append(short_high_band)

            short_low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name]['short'])
            self.short_low_bands.append(short_low_band)

            long_rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name]['long'])
            self.long_rsi.append(long_rsi)

            short_rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name]['short'])
            self.short_rsi.append(short_rsi)

            long_ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['long'])
            self.long_ma.append(long_ma)

            short_ma1 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['short'][0])
            self.short_ma1.append(short_ma1)

            short_ma2 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name]['short'][1])
            self.short_ma2.append(short_ma2)

            atr1 = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name][0])
            self.atr1.append(atr1)

            atr2 = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name][1])
            self.atr2.append(atr2)

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

        equity = DataUtils.convert_to_decimal(self.broker.getvalue())
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            tick_size = self.p.tick_size[name]
            step_size = self.p.step_size[name]

            long_high_band = DataUtils.convert_to_decimal(self.long_high_bands[i][0])
            long_low_band = DataUtils.convert_to_decimal(self.long_low_bands[i][0])

            short_high_band = DataUtils.convert_to_decimal(self.short_high_bands[i][0])
            short_low_band = DataUtils.convert_to_decimal(self.short_low_bands[i][0])

            atr = int(DataUtils.convert_to_decimal(self.atr1[i][0]) / tick_size) * tick_size
            avg_atr = int(DataUtils.convert_to_decimal(self.atr2[i][0]) / tick_size) * tick_size
            vol_factor = int((atr / avg_atr) / tick_size) * tick_size

            adj_long_high_band = long_high_band - (long_high_band - long_low_band) * (DataUtils.convert_to_decimal(self.p.high_band_constant[name]['long']) / Decimal('100'))
            adj_long_high_band = int(adj_long_high_band / tick_size) * tick_size

            adj_long_low_band = long_low_band + (long_high_band - long_low_band) * (DataUtils.convert_to_decimal(self.p.low_band_constant[name]['long']) / Decimal('100'))
            adj_long_low_band = int(adj_long_low_band / tick_size) * tick_size

            adj_short_high_band = short_high_band - (short_high_band - short_low_band) * (DataUtils.convert_to_decimal(self.p.high_band_constant[name]['short']) / Decimal('100'))
            adj_short_high_band = int(adj_short_high_band / tick_size) * tick_size

            adj_short_low_band = short_low_band + (short_high_band - short_low_band) * (DataUtils.convert_to_decimal(self.p.low_band_constant[name]['short']) / Decimal('100'))
            adj_short_low_band = int(adj_short_low_band / tick_size) * tick_size

            long_band_width = abs(adj_long_high_band-adj_long_low_band)
            long_stop_distance = long_band_width * vol_factor
            long_stop_price = adj_long_high_band - long_stop_distance
            long_stop_price = int(long_stop_price / tick_size) * tick_size

            short_band_width = abs(adj_short_low_band-adj_short_high_band)
            short_stop_distance = short_band_width * vol_factor
            short_stop_price = adj_short_low_band + short_stop_distance
            short_stop_price = int(short_stop_price / tick_size) * tick_size

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                entry_mode = self.p.entry_mode[name]

                # 롱 포지션 사이즈 계산
                long_qty = equity * (self.p.risk[name]['long'] / Decimal('100')) / long_stop_distance
                long_qty = int(long_qty / step_size) * step_size

                # 숏 포지션 사이즈 계산
                short_qty = equity * (self.p.risk[name]['short'] / Decimal('100')) / short_stop_distance
                short_qty = int(short_qty / step_size) * step_size

                if entry_mode in [0, 2]:  # long position 진입
                    if self.long_rsi[i][0] >= self.p.rsi_limit[name]['long'] and self.closes[i][0] >= self.long_ma[i][0]:
                        self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], price=float(adj_long_high_band), size=float(long_qty))

                if entry_mode in [1, 2]:  # short position 진입
                    if self.short_ma1[i][0] <= self.short_ma2[i][0]:
                        self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i],price=float(adj_short_low_band), size=float(short_qty))

            elif current_position_size > 0:
                self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(current_position_size), price=float(long_stop_price))
            elif current_position_size < 0:
                self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i],size=float(abs(current_position_size)), price=float(short_stop_price))


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendFollowWithATRScalingV1)

    cerebro.broker.setcash(80000)
    cerebro.broker.setcommission(commission=0.0002, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        download.download_candles(exchange, pair, tick_kind)
        df = DataUtils.load_candle_data_as_df(download_dir_path, exchange, pair, tick_kind)
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

    file_name = result_file_path + exchange + "-" + result_file_prefix + "-"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"

    strat = results[0]
    order_balance_list = strat.order_balance_list
    df = pd.DataFrame(order_balance_list, columns=["date", "value"])
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    df = df.drop_duplicates('date', keep='last').sort_index()  # 각 날짜에 대해서 마지막 시간에 대한 값을 그날의 값으로 설정
    # df = df.sort_values('value', ascending=True).drop_duplicates('date', keep='last').sort_index()
    df['value'] = df['value'].astype('float64')
    # df['value'] = df['value'].pct_change()
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna()
    df = df.set_index('date')
    df.index.name = 'date'
    df.to_csv(f'{file_name}.csv')
    qs.reports.html(df['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)

    returns = returns[returns.index >= '2023-04-30']
    returns.index.name = 'date'
    returns.name = 'value'
    # returns['date'] = returns['date'].dt.date

    returns.to_csv(f'{file_name}_close.csv')
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')