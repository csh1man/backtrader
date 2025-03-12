import backtrader as bt
from util.Util import DataUtils
from decimal import Decimal, ROUND_HALF_UP
from indicator.Indicators import Indicator
import pandas as pd
import quantstats as qs

pairs = {
    "KRW-ETH": DataUtils.CANDLE_TICK_4HOUR,
    "KRW-BTC": DataUtils.CANDLE_TICK_4HOUR,
    "KRW-BCH": DataUtils.CANDLE_TICK_4HOUR,
    "KRW-XRP": DataUtils.CANDLE_TICK_4HOUR,
    "KRW-DOGE": DataUtils.CANDLE_TICK_4HOUR,
    "KRW-SOL": DataUtils.CANDLE_TICK_4HOUR,
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

class UpbitBBWithTrendFollowV1(bt.Strategy):
    params=dict(
        log=True,
        risk={
            'KRW-ETH': Decimal('1.0'),
            'KRW-BTC': Decimal('1.0'),
            'KRW-BCH': Decimal('1.0'),
            'KRW-SOL': Decimal('1.0'),
            'KRW-XRP': Decimal('1.0'),
            'KRW-DOGE': Decimal('1.0'),
        },
        bb_length={
            'KRW-ETH': 80,
            'KRW-BTC': 50,
            'KRW-BCH': 80,
            'KRW-SOL': 30,
            'KRW-XRP': 30,
            'KRW-DOGE': 30,
        },
        bb_mult={
            'KRW-ETH': 2.0,
            'KRW-BTC': 2.0,
            'KRW-BCH': 2.0,
            'KRW-SOL': 2.0,
            'KRW-XRP': 2.0,
            'KRW-DOGE': 2.0,
        },
        high_band_length={
            'KRW-ETH': 50,
            'KRW-BTC': 30,
            'KRW-BCH': 30,
            'KRW-SOL': 30,
            'KRW-XRP': 30,
            'KRW-DOGE': 30,
        },
        low_band_length={
            'KRW-ETH': 20,
            'KRW-BTC': 15,
            'KRW-BCH': 20,
            'KRW-SOL': 15,
            'KRW-XRP': 20,
            'KRW-DOGE': 20,
        },
        low_band_const={
            'KRW-ETH': 60,
            'KRW-BTC': 30,
            'KRW-BCH': 50,
            'KRW-SOL': 45,
            'KRW-XRP': 20,
            'KRW-DOGE': 20,
        },
        low_band_const2={
            'KRW-ETH': 50,
            'KRW-BTC': 30,
            'KRW-BCH': 50,
            'KRW-SOL': 45,
            'KRW-XRP': 20,
            'KRW-DOGE': 20,
        },
    )
    def log(self, txt):
        if self.p.log:
            print(f'{txt}')

    def __init__(self):
        # 기본 데이터 정보 초기화
        self.pairs = []
        self.names = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.stop_price = []

        # 지표 데이터 정보 초기화
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []
        self.adj_high_bands = []
        self.adj_low_bands = []
        self.adj_low_bands2 = []
        self.stop_price = []

        # 자산 추적용 변수 할당
        self.order = None
        self.date_value = []
        self.my_assets = []

        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

        # 기본 데이터 정보 할당
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
            self.stop_price.append(Decimal('-1'))

        # 지표 데이터 정보 계산 및 할당
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_length[name], devfactor=self.p.bb_mult[name])
            self.bb_top.append(bb.lines.top)
            self.bb_mid.append(bb.lines.mid)
            self.bb_bot.append(bb.lines.bot)

            high_band = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name])
            low_band = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name])

            adj_low_band = low_band + (high_band - low_band) * (self.p.low_band_const[name] / 100)
            adj_low_band2 = low_band + (high_band - low_band) * (self.p.low_band_const2[name] / 100)
            self.adj_low_bands.append(adj_low_band)
            self.adj_low_bands2.append(adj_low_band2)

    # 거래내역 추적
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
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    # 모든 미체결 지정가 주문 취소
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


    def next(self):
        self.record_asset()

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            pair = self.pairs[i]
            tick_size = get_tick_size(self.closes[i][0])

            current_position_size = self.getposition(pair).size
            if current_position_size == 0:
                if self.closes[i][-1] < self.bb_top[i][-1] and self.closes[i][0] >= self.bb_top[i][0]:
                    stop_price = DataUtils.convert_to_decimal(self.adj_low_bands[i][0])
                    stop_price = int(stop_price / tick_size) * tick_size

                    qty = DataUtils.convert_to_decimal(self.broker.getvalue()) * self.p.risk[name] / Decimal('100')
                    qty = qty / abs(DataUtils.convert_to_decimal(self.closes[i][0]) - stop_price)
                    if qty * Decimal(str(self.closes[i][0])) >= Decimal(str(self.broker.getcash())):
                        qty = Decimal(str(self.broker.getcash())) * Decimal('0.98') / Decimal(str(self.closes[i][0]))
                    qty = qty.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
                    self.order = self.buy(data=self.pairs[i], size=float(qty))
                    self.stop_price.append(stop_price)

            elif current_position_size > 0:
                if self.closes[i][-1] > self.stop_price[i] > self.closes[i][0]:
                    self.order = self.sell(data=self.pairs[i], size=current_position_size)
                    self.stop_price[i] = Decimal('-1')
                elif self.closes[i][0] < self.bb_mid[i][0]:
                    self.order = self.sell(data=self.pairs[i], size=current_position_size)
                    self.stop_price[i] = Decimal('-1')
                elif DataUtils.convert_to_decimal(self.closes[i][0]) <  DataUtils.convert_to_decimal(self.adj_low_bands2[i][-1]):
                    self.order = self.sell(data=self.pairs[i], size=current_position_size)
                    self.stop_price[i] = Decimal('-1')

if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData";
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(50000000) # 초기 시드 설정
    cerebro.broker.setcommission(0.002, leverage=1) # 수수료 설정
    cerebro.addstrategy(UpbitBBWithTrendFollowV1) # 전략 추가
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # 데이터 INSERT
    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_UPBIT, pair, tick_kind)
        # df = DataUtil.get_candle_data_in_scape(df, "2022-01-01", "2026-01-01")
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

    # file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    # file_name = "/Users/tjgus/Desktop/project/krtrade/backData/result/"
    file_name = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "UpbitBBWithTrendFollowV1"

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


