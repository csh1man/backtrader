import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal
import math

pairs = {
    'BCHUSDT' : DataUtils.CANDLE_TICK_4HOUR,
    'EOSUSDT' : DataUtils.CANDLE_TICK_4HOUR,
    'NEARUSDT' : DataUtils.CANDLE_TICK_4HOUR,
}

class MultiDonchianShortV1(bt.Strategy):
    params = dict(
        # 롱/숏 레버리지 셋팅
        leverage={
            'BCHUSDT': {
                'short': Decimal('4.0'),
            },
            'EOSUSDT': {
                'short' : Decimal('2.0'),
            },
            'NEARUSDT': {
                'short' : Decimal('2.0'),
            }
        },
        risk={
            'BCHUSDT': {
                'short': Decimal('1.0'),
            },
            'EOSUSDT': {
                'short': Decimal('1.0'),
            },
            'NEARUSDT': {
                'short': Decimal('1.0'),
            }
        },
        tick_size={
            'BCHUSDT': Decimal('0.10'),
            'EOSUSDT': Decimal('0.0001'),
            'NEARUSDT': Decimal('0.001'),
        },
        step_size={
            'BCHUSDT': Decimal('0.01'),
            'EOSUSDT': Decimal('0.1'),
            'NEARUSDT': Decimal('0.1'),
        },
        high_band_length={
            'BCHUSDT': 15,
            'EOSUSDT': 20,
            'NEARUSDT': 10,
        },
        low_band_length={
            'BCHUSDT': 50,
            'EOSUSDT': 80,
            'NEARUSDT': 100
        },
        atr={
            'length': {
                'BCHUSDT': 10,
                'EOSUSDT': 3,
                'NEARUSDT': 3,
            },
            'constant': {
                'BCHUSDT': {
                    'short' : Decimal('1.0'),
                },
                'EOSUSDT': {
                    'short' : Decimal('2.0'),
                },
                'NEARUSDT': {
                    'short' : Decimal('1.0'),
                }
            }
        }
    )

    def __init__(self):

        # 기본 캔들 정보 저장용 변수 초기화
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []

        # 손절 가격 저장용 변수 초기화
        self.short_stop_prices = []

        # 기본 캔들 정보 저장
        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
            self.short_stop_prices.append(Decimal('0'))

        # 지표 데이터 저장용 변수 초기화
        self.highest = []
        self.lowest = []
        self.atrs = []

        # 지표 데이터 저장
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # 고가 채널 저장
            highest = bt.indicators.Highest(self.highs[i], period=self.p.high_band_length[name])
            self.highest.append(highest)

            # 저가 채널 저장
            lowest = bt.indicators.Lowest(self.lows[i], period=self.p.low_band_length[name])
            self.lowest.append(lowest)

            # atr 저장
            atr = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr['length'][name])
            self.atrs.append(atr)

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

    # logging data
    def log(self, txt):
        print(f'{txt}')

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
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def stop(self):
        self.log(f'전체 트레이딩 횟수 : {self.total_trading_count}')

    def record_asset(self):
        account_value = self.broker.get_cash()  # 현재 현금(보유 포지션 제외) 자산의 가격을 획득
        broker_leverage = self.broker.comminfo[None].p.leverage  # cerebro에 설정한 레버리지 값 -> setcommission
        position_value = 0.0
        bought_value = 0.0

        # 롱과 숏 포지션에 대한 자산 계산
        for pair in self.pairs:
            position = self.getposition(pair)
            size = position.size
            if size > 0:  # 롱 포지션
                position_value += size * pair.low[0]  # 포지션 크기 * 현재 가격 (롱은 가격 상승에 따른 자산 증가)
                bought_value += size * position.price  # 진입한 수량 x 평단가
                account_value += position_value - bought_value * (broker_leverage - 1) / broker_leverage
            elif size < 0:  # 숏 포지션
                position_value += abs(size) * pair.high[0]  # 포지션 크기 * 현재 가격 (숏은 가격 하락에 따른 자산 증가)
                bought_value += abs(size) * position.price  # 숏의 경우 평단가가 중요하므로 계산에 포함
                account_value += bought_value * (broker_leverage - 1) / broker_leverage - position_value

        self.order_balance_list.append([self.dates[0].datetime(0), account_value])
        self.date_value.append(self.dates[0].datetime(0))

        # 전체 자산 기록
        position_value = self.broker.getvalue()
        for i in range(1, len(self.datas)):
            position_value += self.getposition(self.datas[i]).size * self.lows[i][0]

        self.my_assets.append(position_value)

    def next(self):
        self.record_asset()  # 자산 기록

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(target_name=name)  # 미체결 주문 모두 취소

            leverage = self.p.leverage[name]['short']
            close = DataUtils.convert_to_decimal(self.closes[i][0])
            before_close = DataUtils.convert_to_decimal(self.closes[i][-1])
            atr = DataUtils.convert_to_decimal(self.atrs[i][0])
            highest = DataUtils.convert_to_decimal(self.highest[i][0])
            lowest = DataUtils.convert_to_decimal(self.lowest[i][0])
            current_position_size = self.getposition(self.pairs[i]).size

            # 진입 포지션이 없을 경우
            if current_position_size == 0:
                # 손절 가격 계산 및 저장
                if name != 'NEARUSDT':
                    stop_price = close + atr * self.p.atr['constant'][name]['short']
                    stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.short_stop_prices[i] = stop_price
                else:
                    stop_price = lowest + atr * self.p.atr['constant'][name]['short']
                    stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.short_stop_prices[i] = stop_price

                # 수량 계산
                qty = leverage * DataUtils.convert_to_decimal(self.broker.get_cash()) * self.p.risk[name]['short'] / Decimal('100') / abs(lowest - stop_price)
                qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]

                # 계산된 수량에 대해서 진입하는데 필요한 자산이 레버리지 * 현재 자산보다 크면 진입이 되지 않는다.
                # 따라서 현재 자산의 98% x 레버리지 만큼 진입한다.
                if qty * lowest >= leverage * DataUtils.convert_to_decimal(self.broker.get_cash()):
                    qty = leverage * DataUtils.convert_to_decimal(self.broker.get_cash()) * Decimal('0.98') / lowest
                    qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]

                # 지정가 주문 체결
                self.order = self.sell(exectype=bt.Order.Stop, data=self.pairs[i], price=float(lowest), size=float(qty))

            # 현재 포지션이 존재할 경우
            if current_position_size < 0:
                # 현재 가격이 손절 가격 밑으로 내려왔을 경우 손절
                if before_close < self.short_stop_prices[i] <= close:
                    self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=abs(current_position_size))
                    self.short_stop_prices[i] = Decimal('0')
                else:
                    self.order = self.buy(exectype=bt.Order.Stop, data=self.pairs[i], size=abs(current_position_size), price=float(highest))

if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiDonchianShortV1)

    cerebro.broker.setcash(50000000)
    cerebro.broker.setcommission(commission=0.0005, leverage=100)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BYBIT, pair, tick_kind)
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
    file_name += "MultiDonchianShortV1"

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