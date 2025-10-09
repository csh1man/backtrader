import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from api.Api import Common, Download
from decimal import Decimal

# config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
# config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"
config_file_path = "/Users/choeseohyeon/Desktop/data/config/config.json"

# download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
# download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
download_dir_path = "/Users/choeseohyeon/Desktop/data/candle"

# result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
# result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
result_file_path = "/Users/choeseohyeon/Desktop/data/result/"

result_file_prefix = "TrendFollowBasicShortV1"

pairs = {
    'ETHUSDT': DataUtils.CANDLE_TICK_1DAY
}

exchange = DataUtil.BYBIT
leverage = 5

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)

class TrendFollowBasicShortV1(bt.Strategy):
    params = dict(
        risk={
            'ETHUSDT': Decimal('2.0')
        },
        high_band_span={
            'ETHUSDT': 25,
        },
        low_band_span={
            'ETHUSDT': 60,
        },
        high_band_const={
            'ETHUSDT': Decimal('60.0')
        },
        low_band_const={
            'ETHUSDT': Decimal('5.0')
        },
        tick_size={
            'ETHUSDT': common.fetch_tick_size(exchange, 'ETHUSDT'),
        },
        step_size={
            'ETHUSDT': common.fetch_step_size(exchange, 'ETHUSDT'),
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

        self.high_bands = []
        self.low_bands = []

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
        # This is the correct, standard way to calculate total equity.
        # Start with the current available cash.
        account_value = self.broker.get_cash()

        # Add the current market value of each open position, valued conservatively.
        for pair in self.pairs:
            pos = self.getposition(pair)

            if pos.size == 0:
                continue

            if pos.size > 0:
                # For a LONG position, the conservative value is at the LOW price.
                account_value += pos.size * pair.low[0]
            elif pos.size < 0:
                # For a SHORT position, the conservative value is at the HIGH price.
                # pos.size is already negative, so the result is correctly subtracted.
                account_value += pos.size * pair.high[0]

        # Append the correctly calculated total equity to the list.
        self.order_balance_list.append([self.dates[0].datetime(0), account_value])

        # The 'self.date_value' and 'self.my_assets' lists seem to be for a different calculation.
        # To avoid confusion, you might want to simplify or remove them if they are not essential.
        # For now, we focus on fixing the order_balance_list which is used for the quantstats report.
        self.date_value.append(self.dates[0].datetime(0))

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

            high_band = DataUtils.convert_to_decimal(self.high_bands[i][0])
            low_band = DataUtils.convert_to_decimal(self.low_bands[i][0])

            adj_high_band = high_band - (high_band - low_band) * (self.p.high_band_const[name] / Decimal('100'))
            adj_high_band = int(adj_high_band / tick_size) * tick_size

            adj_low_band = low_band + (high_band - low_band) * (self.p.low_band_const[name] / Decimal('100'))
            adj_low_band = int(adj_low_band / tick_size) * tick_size

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                self.log(f'[{self.dates[i].datetime(0)}] low : [{self.lows[i][0]}], high : [{self.highs[i][0]}]')
                qty = equity * (self.p.risk[name] / Decimal('100')) / abs(adj_high_band - adj_low_band)
                qty = int(qty / step_size) * step_size

                if qty > 0:
                    self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], size=float(qty), price=float(adj_low_band))

            elif current_position_size < 0:
                self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=float(abs(current_position_size)), price=float(adj_high_band))

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendFollowBasicShortV1)

    cerebro.broker.setcash(1000000)
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

    returns = returns[returns.index >= '2023-05-01']
    # returns = returns[returns.index < '2025-10-01']
    returns.index.name = 'date'
    returns.name = 'value'
    # returns['date'] = returns['date'].dt.date

    returns.to_csv(f'{file_name}_close.csv')
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')
