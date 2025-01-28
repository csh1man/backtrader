
import backtrader as bt
import pandas as pd
import quantstats as qs
import math
from util.Util import DataUtil
from decimal import Decimal, ROUND_HALF_UP

pairs = {
    "KRW-ETH": DataUtil.CANDLE_TICK_4HOUR,
    "KRW-BTC": DataUtil.CANDLE_TICK_4HOUR,
    "KRW-BCH": DataUtil.CANDLE_TICK_4HOUR,
    "KRW-SOL": DataUtil.CANDLE_TICK_4HOUR,
    "KRW-XRP": DataUtil.CANDLE_TICK_4HOUR,
    "KRW-DOGE": DataUtil.CANDLE_TICK_4HOUR
}

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


class UpBitTrendFollowV1(bt.Strategy):
    params=dict(
        log=True,
        risk=1,
        atr_length=10,
        atr_constant=Decimal('1.0'),
        high_band_length={
            'KRW-BTC': 30,
            'KRW-ETH': 50,
            'KRW-BCH': 20,
            'KRW-SOL': 30,
            'KRW-XRP': 20,
            'KRW-DOGE': 20
        },
        low_band_length={
            'KRW-BTC': 15,
            'KRW-ETH': 15,
            'KRW-BCH': 15,
            'KRW-SOL': 15,
            'KRW-XRP': 15,
            'KRW-DOGE': 15
        },
        high_band_constant={
            'KRW-BTC': Decimal('10'),
            'KRW-ETH': Decimal('30'),
            'KRW-BCH': Decimal('10'),
            'KRW-SOL': Decimal('50'),
            'KRW-XRP': Decimal('20'),
            'KRW-DOGE': Decimal('20')
        },
        low_band_constant={
            'KRW-BTC': Decimal('10'),
            'KRW-ETH': Decimal('30'),
            'KRW-BCH': Decimal('20'),
            'KRW-SOL': Decimal('30'),
            'KRW-XRP': Decimal('20'),
            'KRW-DOGE': Decimal('20')
        }
    )

    def log(self, txt):
        if self.p.log:
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
        self.stop_price = []
        self.entry_price = []
        self.entry_atr = []
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
            self.stop_price.append(Decimal('-1'))
            self.entry_price.append(Decimal('-1'))
            self.entry_atr.append(Decimal('-1'))

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length)
            self.atrs.append(atr)

            high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name])
            self.high_bands.append(high_band)

            low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name])
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
            before_high_band = DataUtil.convert_to_decimal(self.high_bands[i][-1])
            before_low_band = DataUtil.convert_to_decimal(self.low_bands[i][-1])
            before_adj_high_band = before_high_band - (before_high_band - before_low_band) * (self.p.high_band_constant[name] / Decimal('100'))
            before_adj_low_band = before_low_band + (before_high_band - before_low_band) * (self.p.low_band_constant[name] / Decimal('100'))

            two_before_high_band = DataUtil.convert_to_decimal(self.high_bands[i][-2])
            two_before_low_band = DataUtil.convert_to_decimal(self.low_bands[i][-2])
            two_before_adj_high_band = two_before_high_band - (two_before_high_band - two_before_low_band) * (self.p.high_band_constant[name] / Decimal('100'))
            two_before_adj_low_band = two_before_low_band + (two_before_high_band - two_before_low_band) * (self.p.low_band_constant[name] / Decimal('100'))

            before_close = DataUtil.convert_to_decimal(self.closes[i][-1])
            current_close = DataUtil.convert_to_decimal(self.closes[i][0])

            entry_position_size = self.getposition(self.pairs[i]).size
            if entry_position_size == 0:
                if not math.isnan(two_before_adj_low_band) and not math.isnan(two_before_adj_high_band) and  not math.isnan(before_adj_high_band) and not math.isnan(before_adj_low_band):
                    if before_close < two_before_adj_high_band and current_close >= before_adj_high_band:
                        stop_price = current_close - DataUtil.convert_to_decimal(self.atrs[i][0]) * self.p.atr_constant
                        stop_price = int(stop_price / get_tick_size(self.closes[i][0])) * get_tick_size(self.closes[i][0])
                        self.stop_price[i] = stop_price

                        cash = DataUtil.convert_to_decimal(self.broker.get_cash())
                        qty = cash * (self.p.risk / Decimal('100')) / abs(current_close-stop_price)
                        if qty * current_close >= cash:
                            qty = cash * Decimal('0.98') / current_close
                        qty.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(qty))
                        self.entry_price[i] = current_close
                        self.entry_atr[i] = DataUtil.convert_to_decimal(self.atrs[i][0])

            elif entry_position_size > 0:
                stop_price = self.stop_price[i]
                if before_close >= stop_price > current_close:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(entry_position_size))
                elif before_close >= two_before_adj_low_band and current_close < before_adj_low_band:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(entry_position_size))

                if (current_close - self.entry_price[i]) >= self.entry_atr[i]:
                    stop_price = stop_price + (self.entry_atr[i] / Decimal('2'))
                    self.stop_price[i] = stop_price
                    self.entry_price[i] = current_close
                    self.entry_atr[i] = DataUtil.convert_to_decimal(self.atrs[i][0])


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(UpBitTrendFollowV1)

    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(commission=0.0005, leverage=1)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_UPBIT, pair, tick_kind)
        df = DataUtil.get_candle_data_in_scape(df, "2022-01-01", "2026-01-01")
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


    # file_name = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
    # file_name = "/Users/tjgus/Desktop/project/krtrade/backData/result/"
    file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "UpBitTrendFollowV1"

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

