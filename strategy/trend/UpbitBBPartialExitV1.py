import backtrader as bt
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from api.Api import Common, Download
from decimal import Decimal, ROUND_HALF_UP
from indicator.Indicators import Indicator
import pandas as pd
import quantstats as qs

# config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"

# download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"

# result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"

result_file_prefix = "UpbitBBPartialExitV1"

pairs = {
    "KRW-BTC": DataUtils.CANDLE_TICK_1DAY,
    "KRW-ETH": DataUtils.CANDLE_TICK_1DAY,
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


class UpbitBBPartialExitV1(bt.Strategy):
    params = dict(
        risk=Decimal('4'),
        bb_span={
            'KRW-BTC': 50,
            'KRW-ETH': 50,
        },
        bb_mult={
            'KRW-BTC': 2.0,
            'KRW-ETH': 2.0,
        },
        atr_length={
            'KRW-BTC': 14,
            'KRW-ETH': 14,
        },
        atr_const={
            'KRW-BTC': {
                'cut': Decimal('1.5'),
                'exit': Decimal('6.0'),
            },
            'KRW-ETH': {
                'cut': Decimal('1.5'),
                'exit': Decimal('6.0'),
            },
        }
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 기본 데이터 정보 초기화
        self.pairs = []
        self.names = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.stop_prices = []
        self.partial_exit = []
        self.partial_exit_price = []
        self.top = []
        self.mid = []
        self.bot = []

        self.atr = []

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
            self.stop_prices.append(Decimal('-1'))
            self.partial_exit.append(False)
            self.partial_exit_price.append(Decimal('-1'))

        # 지표 데이터 정보 계산 및 할당
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_span[name], devfactor=self.p.bb_mult[name])
            self.top.append(bb.lines.top)
            self.mid.append(bb.lines.mid)
            self.bot.append(bb.lines.bot)

        # ATR 셋팅
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[name])
            self.atr.append(atr)

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
        # 자산 기록 및 추적
        self.record_asset()

        # 각 페어를 돌면서
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # self.log(f'[{self.dates[i].datetime(0)}] => close : {self.closes[i][0]} / top : {self.top[i][0]} / mid : {self.mid[i][0]} / bot : {self.bot[i][0]}')
            # 포지션 획득
            entry_position_size = self.getposition(self.pairs[i]).size
            equity = DataUtils.convert_to_decimal(self.broker.get_cash())
            # 진입 포지션이 없을 경우
            if entry_position_size == 0:
                if self.closes[i][0] > self.top[i][0]:
                    self.log(f'{self.dates[i].datetime(0)} -> 상단선 돌파')
                    stop_loss = DataUtils.convert_to_decimal(self.atr[i][0]) * self.p.atr_const[name]['cut']
                    self.stop_prices[i] = DataUtils.convert_to_decimal(self.closes[i][0]) - stop_loss
                    qty = equity * self.p.risk / Decimal('100') / stop_loss
                    if equity < qty * DataUtils.convert_to_decimal(self.closes[i][0]):
                        qty = equity * Decimal('0.98') / DataUtils.convert_to_decimal(self.closes[i][0])
                    qty = qty.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
                    self.partial_exit[i] = False
                    self.partial_exit_price[i] = DataUtils.convert_to_decimal(self.closes[i][0]) + DataUtils.convert_to_decimal(self.atr[i][0]) * self.p.atr_const[name]['exit']
                    if qty > Decimal('0'):
                        self.order = self.buy(data=self.pairs[i], size=float(qty))

            # 진입 포지션이 존재할 경우 종료 조건 확인 또는 손절가 지정가 주문 생성
            elif entry_position_size > 0:
                if DataUtils.convert_to_decimal(self.closes[i][0]) > self.partial_exit_price[i] and not self.partial_exit[i]:
                    self.order = self.sell(data=self.pairs[i], size=entry_position_size/2)
                    self.log(f'{self.dates[i][0]} => partial Exit')
                    self.partial_exit[i] = True
                else:
                    exit_price = DataUtils.convert_to_decimal(self.top[i][0]) - DataUtils.convert_to_decimal(self.atr[i][0]) * self.p.atr_const[name]['cut']
                    if DataUtils.convert_to_decimal(self.closes[i][0]) < exit_price:
                        self.order = self.sell(data=self.pairs[i], size=entry_position_size)
                        self.log(f'{self.dates[i][0]} => total Exit')



    def stop(self):
        self.log(f'총 트레이딩 수 : {self.total_trading_count}')


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData";
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000) # 초기 시드 설정
    cerebro.broker.setcommission(0.003, leverage=1) # 수수료 설정
    cerebro.addstrategy(UpbitBBPartialExitV1) # 전략 추가
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

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

    returns = returns[returns.index >= '2017-10-01']
    returns = returns[returns.index < '2025-07-07']
    returns.index.name = 'date'
    returns.name = 'value'
    # returns['date'] = returns['date'].dt.date

    returns.to_csv(f'{file_name}_close.csv')
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')