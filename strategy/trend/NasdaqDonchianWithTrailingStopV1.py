import backtrader as bt

from util.Util import DataUtils
from decimal import Decimal, getcontext, ROUND_FLOOR, ROUND_DOWN
import quantstats as qs
import pandas as pd

pairs = {
    'TSLA': DataUtils.CANDLE_TICK_1DAY,
    'AAPL': DataUtils.CANDLE_TICK_1DAY,
    'NVDA': DataUtils.CANDLE_TICK_1DAY,
    'MSFT': DataUtils.CANDLE_TICK_1DAY,
    'NFLX': DataUtils.CANDLE_TICK_1DAY,
}

# result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"

result_file_prefix = "NasdaqDonchianWithTrailingStopV1"

class NasdaqDonchianWithTrailingStopV1(bt.Strategy):
    params = dict(
        risk={
            'TSLA': Decimal(2.0),
            'AAPL': Decimal(2.0),
            'NVDA': Decimal(2.0),
            'MSFT': Decimal(2.0),
            'NFLX': Decimal(2.0),
        },
        high_band_span={
            'TSLA' : 20,
            'AAPL' : 20,
            'NVDA' : 20,
            'MSFT' : 20,
            'NFLX' : 20,
        },
        low_band_span={
            'TSLA': 20,
            'AAPL': 20,
            'NVDA': 20,
            'MSFT': 20,
            'NFLX': 20,
        },
        atr_length={
            'TSLA': 14,
            'AAPL': 14,
            'NVDA': 14,
            'MSFT': 14,
            'NFLX': 14,
        },
        atr_mult={
            'TSLA': Decimal(1.5),
            'AAPL': Decimal(1.5),
            'NVDA': Decimal(1.5),
            'MSFT': Decimal(1.5),
            'NFLX': Decimal(1.5),
        },
        atr_mult2={
            'TSLA': Decimal(3.0),
            'AAPL': Decimal(3.0),
            'NVDA': Decimal(3.0),
            'MSFT': Decimal(3.0),
            'NFLX': Decimal(3.0),
        }
    )
    def log(self, txt):
        print(txt)

    def __init__(self):
        self.pairs = []
        self.names = []
        self.stop_price = []

        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []

        self.high_band = []
        self.low_band = []
        self.atr = []
        self.entry_atr = []
        self.partial_exit = []
        self.partial_exit_price = []

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
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
            self.stop_price.append(Decimal('-1'))
            self.entry_atr.append(Decimal(0))
            self.partial_exit.append(False)
            self.partial_exit_price.append(Decimal('0'))

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_span[name])
            self.high_band.append(high_band)

            low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_span[name])
            self.low_band.append(low_band)

            atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name])
            self.atr.append(atr)


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
                         f'가격:{order.created.price:.4f}')
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
        self.order_balance_list.append([self.dates[0].datetime(0), account_value])
        self.date_value.append(self.dates[0].datetime(0))
        position_value = self.broker.getvalue()
        for i in range(1, len(self.datas)):
            position_value += self.getposition(self.datas[i]).size * self.lows[i][0]

        self.my_assets.append(position_value)

    def cancel_all(self):
        open_orders = self.broker.get_orders_open()
        for order in open_orders:
            if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
                self.broker.cancel(order)

    def next(self):
        self.record_asset()
        self.cancel_all()

        for i in range(0, len(self.pairs)):
            # 이름 획득
            name = self.names[i]

            # 현재 포지션 사이즈 획득
            current_position_size = self.getposition(self.pairs[i]).size

            # 포지션이 하나도 없을 경우
            if current_position_size == 0:
                # 종가가 돈치안 상단 채널을 상향 돌파할 경우 매수
                if self.closes[i][-1] < self.high_band[i][-2] and self.closes[i][0] >= self.high_band[i][-1]:
                    risk = self.p.risk[name]
                    equity = DataUtils.convert_to_decimal(self.broker.getvalue())
                    entry_price = DataUtils.convert_to_decimal(self.closes[i][0])

                    stop_price = entry_price - DataUtils.convert_to_decimal(self.atr[i][0]) * self.p.atr_mult[name]
                    self.stop_price[i] = stop_price

                    qty = equity * (risk / Decimal('100')) / abs(entry_price - stop_price)
                    qty = qty.quantize(Decimal('1'), rounding=ROUND_FLOOR)

                    if qty > 0:
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                        self.partial_exit_price[i] = DataUtils.convert_to_decimal(self.closes[i][0]) + DataUtils.convert_to_decimal(self.atr[i][0]) * self.p.atr_mult2[name]

            elif current_position_size > 0:
                if DataUtils.convert_to_decimal(self.closes[i][0]) >= self.partial_exit_price[i] and not self.partial_exit[i]:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i],size=float(current_position_size/2))
                    self.partial_exit[i] = True
                if self.closes[i][-1] >= self.low_band[i][-2] and self.closes[i][0] < self.low_band[i][-1]:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(current_position_size))
                elif DataUtils.convert_to_decimal(self.closes[i][0]) < self.stop_price[i]:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i],size=float(current_position_size))




if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(NasdaqDonchianWithTrailingStopV1)

    cerebro.broker.setcash(10000)
    cerebro.broker.setcommission(commission=0.002, leverage=1)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_NASDAQ, pair, tick_kind)
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


    file_name = result_file_path + DataUtils.COMPANY_NASDAQ + "-" + result_file_prefix + "-"
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

    returns.index.name = 'date'
    returns.name = 'value'

    returns.to_csv(f'{file_name}_close.csv')
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')

