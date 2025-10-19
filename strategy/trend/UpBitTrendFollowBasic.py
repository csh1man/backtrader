import decimal

import backtrader as bt
import pandas as pd
import quantstats as qs
import math
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from decimal import Decimal, ROUND_HALF_UP
from api.Api import Common, Download
# config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"
# config_file_path = "/Users/choeseohyeon/Desktop/data/config/config.json"

# download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
# download_dir_path = "/Users/choeseohyeon/Desktop/data/candle"

# result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
# result_file_path = "/Users/choeseohyeon/Desktop/data/result/"

result_file_prefix = "UpBitTrendFollowBasic"

pairs = {
    'KRW-ETH': DataUtils.CANDLE_TICK_4HOUR,
    'KRW-BTC': DataUtils.CANDLE_TICK_4HOUR,
    'KRW-SOL': DataUtils.CANDLE_TICK_4HOUR,
    # 'KRW-DOGE': DataUtils.CANDLE_TICK_4HOUR,
}

exchange = DataUtil.UPBIT
leverage = 1

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)

def get_tick_size(price):
    if price >= 2000000:
        return Decimal('1000')
    elif price >= 1000000:
        return Decimal('500')
    elif price >= 500000:
        return Decimal('100')
    elif price >= 100000:
        return Decimal('50')
    elif price >= 10000:
        return Decimal('10')
    elif price >= 1000:
        return Decimal('5')
    elif price >= 100:
        return Decimal('1')
    elif price >= 10:
        return Decimal('0.1')
    else:
        return Decimal('0.01')

class UpBitTrendFollowBasic(bt.Strategy):
    params=dict(
        risk=Decimal(2),
        high_band_span={
            'KRW-ETH': 40,
            'KRW-BTC': 30,
            'KRW-SOL': 30,
            'KRW-DOGE': 35,
        },
        low_band_span={
            'KRW-ETH': 15,
            'KRW-BTC': 15,
            'KRW-SOL': 15,
            'KRW-DOGE': 20
        },
        high_band_const={
            'KRW-ETH': Decimal(15),
            'KRW-BTC': Decimal(15),
            'KRW-SOL': Decimal(10),
            'KRW-DOGE': Decimal(20),
        },
        low_band_const={
            'KRW-ETH': Decimal(30),
            'KRW-BTC': Decimal(30),
            'KRW-SOL': Decimal(30),
            'KRW-DOGE': Decimal(30)
        },
        ma_span={
            'KRW-ETH': 120,
            'KRW-BTC': 120,
            'KRW-SOL': 100,
            'KRW-DOGE': 120
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
        self.init_cash = Decimal(0)
        self.high_bands = []
        self.low_bands = []
        self.mas = []

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

            high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_span[name])
            self.high_bands.append(high_band)

            low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_span[name])
            self.low_bands.append(low_band)

            ma = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_span[name])
            self.mas.append(ma)

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

        equity = DataUtils.convert_to_decimal(self.broker.getvalue())
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            tick_size = get_tick_size(self.closes[i][-1])

            before_high_band = DataUtils.convert_to_decimal(self.high_bands[i][-1])
            before_low_band = DataUtils.convert_to_decimal(self.low_bands[i][-1])

            before_adj_high_band = before_high_band - (before_high_band-before_low_band) * (self.p.high_band_const[name]/ Decimal('100'))
            before_adj_high_band = int(before_adj_high_band / tick_size) * tick_size

            before_adj_low_band = before_low_band + (before_high_band-before_low_band) * (self.p.low_band_const[name] / Decimal('100'))
            before_adj_low_band = int(before_adj_low_band / tick_size) * tick_size

            two_before_high_band = DataUtils.convert_to_decimal(self.high_bands[i][-2])
            two_before_low_band = DataUtils.convert_to_decimal(self.low_bands[i][-2])

            two_before_adj_high_band = two_before_high_band - (two_before_high_band-two_before_low_band) * (self.p.high_band_const[name] / Decimal('100'))
            two_before_adj_high_band = int(two_before_adj_high_band / tick_size) * tick_size

            two_before_adj_low_band = two_before_low_band + (two_before_high_band-two_before_low_band) * (self.p.low_band_const[name] / Decimal('100'))
            two_before_adj_low_band = int(two_before_adj_low_band / tick_size) * tick_size

            before_close = DataUtils.convert_to_decimal(self.closes[i][-1])
            current_close = DataUtils.convert_to_decimal(self.closes[i][0])
            # self.log(f'{self.dates[i].datetime(0)} => {before_adj_low_band}')
            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                qty = equity * (self.p.risk / Decimal('100')) / (before_adj_high_band - before_adj_low_band)
                qty.quantize(Decimal('0.00000001'), rounding=decimal.ROUND_DOWN)
                if before_close < two_before_adj_high_band and current_close >= before_adj_high_band and self.closes[i][0] >= self.mas[i][0]:
                    self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
            elif current_position_size > 0:
                if before_close >= two_before_adj_low_band and current_close < before_adj_low_band:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(UpBitTrendFollowBasic)

    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001, leverage=leverage)
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
    # asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
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

    # returns = returns[returns.index >= '2023-05-01']
    # returns = returns[returns.index < '2025-10-01']
    returns.index.name = 'date'
    returns.name = 'value'
    # returns['date'] = returns['date'].dt.date

    returns.to_csv(f'{file_name}_close.csv')
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')