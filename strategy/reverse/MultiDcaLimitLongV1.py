import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from decimal import Decimal
import math


pairs = {
    'JTOUSDT' : DataUtils.CANDLE_TICK_30M,
}

long_init_equity = {
    'JTOUSDT' : Decimal('0'),
    '1000BONKUSDT' : Decimal('0'),
}

class MultiDcaLimitLongV1(bt.Strategy):
    params = dict(
        # 롱/숏 레버리지 셋팅
        leverage={
          'JTOUSDT' : Decimal('3')
        },
        tick_size={
            'JTOUSDT': Decimal('0.0001'),
        },
        step_size={
            'JTOUSDT': Decimal('1'),
        },
        high_band={
            'JTOUSDT': {
                'length' : 10,
                'initStandard' : Decimal('4.0'),
                'addStandard' : Decimal('5.0')
            },
        },
        limit_percent={
            'JTOUSDT': {
                'init' : [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('10')],
                'add': [Decimal('2'), Decimal('4'), Decimal('6'), Decimal('8'), Decimal('10')],
                'exit': [Decimal('1'), Decimal('3'), Decimal('2'), Decimal('1'), Decimal('1')],
            }
        },
        risk={
            'JTOUSDT': {
                'init' : [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('10')],
                'add': [Decimal('2'), Decimal('4'), Decimal('6'), Decimal('8'), Decimal('10')],
            },
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
        self.long_init_balance = Decimal('0')
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

        # 지표 데이터 저장용 변수 초기화
        self.highest = []
        self.lowest = []

        # 지표 데이터 저장
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # 고가 채널 저장
            highest = bt.indicators.Highest(self.highs[i], period=self.p.high_band[name]['length'])
            self.highest.append(highest)

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

            close = DataUtils.convert_to_decimal(self.closes[i][0])
            before_close = DataUtils.convert_to_decimal(self.closes[i][-1])
            highest = DataUtils.convert_to_decimal(self.highest[i][0])
            current_position_size = self.getposition(self.pairs[i]).size

            # 진입 포지션이 없을 경우
            if current_position_size == 0:
                # 손절 가격 계산 및 저장
                long_init_equity[name] = self.p.leverage[name] * DataUtils.convert_to_decimal(self.broker.get_cash())
                init_long_standard_price = DataUtils.convert_to_decimal(highest) * (Decimal('1.0') - self.p.high_band[name]['initStandard'] / Decimal('100'))
                init_long_standard_price = int(init_long_standard_price / self.p.tick_size[name]) * self.p.tick_size[name]
                if init_long_standard_price > close:
                    for j in range(0, len(self.p.limit_percent[name]['init'])):
                        init_limit_percent = self.p.limit_percent[name]['init'][j]
                        init_long_risk = self.p.risk[name]['init'][j]
                        entry_price = close * (Decimal('1') - init_limit_percent / Decimal('100'))
                        entry_price = int(entry_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        qty = long_init_equity[name] * init_long_risk / Decimal('100') / entry_price
                        if qty > 0:
                            self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(entry_price), size=float(qty))
            # 현재 포지션이 존재할 경우
            if current_position_size > 0:
                entry_avg_price = DataUtils.convert_to_decimal(self.getposition(self.pairs[i]).price)
                long_add_equity = self.p.leverage[name] * DataUtils.convert_to_decimal(self.broker.get_cash())
                if long_init_equity[name] > entry_avg_price * DataUtils.convert_to_decimal(current_position_size):
                    add_long_standard_price = DataUtils.convert_to_decimal(highest) * (Decimal('1.0') - self.p.high_band[name]['addStandard'] / Decimal('100'))
                    if add_long_standard_price > close:
                        for j in range(0, len(self.p.limit_percent[name]['add'])):
                            add_limit_percent = self.p.limit_percent[name]['add'][j]
                            add_long_risk = self.p.risk[name]['add'][j]
                            entry_price = close * (Decimal('1') - add_limit_percent / Decimal('100'))
                            entry_price = int(entry_price / self.p.tick_size[name]) * self.p.tick_size[name]
                            qty = long_add_equity * add_long_risk / Decimal('100') / entry_price
                            if qty > 0:
                                self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i],
                                                      price=float(entry_price), size=float(qty))
                    qty1 = current_position_size / 5
                    qty2 = current_position_size / 5
                    qty3 = current_position_size / 5
                    qty4 = current_position_size / 5
                    qty5 = current_position_size -(qty1+qty2+qty3+qty4)
                    qtys = [qty1, qty2, qty3, qty4, qty5]
                    for j in range(0, len(qtys)):
                        qty = qtys[j]
                        exit_percent = self.p.limit_percent[name]['exit'][0]
                        exit_price = entry_avg_price * (Decimal('1') + exit_percent / Decimal('100'))
                        exit_price = int(exit_price / self.p.tick_size[name]) * self.p.tick_size[name]
                        self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(exit_price), qty=float(qty))


if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiDcaLimitLongV1)

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