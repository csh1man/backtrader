import backtrader as bt
import pandas as pd
import quantstats as qs

from strategy.trend.multiBBV1 import step_size
from util.Util import DataUtils
from decimal import Decimal

pairs = {
    # 'FETUSDT' : DataUtil.CANDLE_TICK_30M,
    '1000BONKUSDT' : DataUtils.CANDLE_TICK_30M,
    # 'ETCUSDT' : DataUtil.CANDLE_TICK_30M,
}

long_init_equity = {
    'FETUSDT' : Decimal('0'),
    '1000BONKUSDT' : Decimal('0'),
    'ETCUSDT' : Decimal('0')
}

short_init_equity = {
    'FETUSDT' : Decimal('0')
}

class MultiDcaLongShortV1(bt.Strategy):
    params = dict(
        long_leverage={
            'FETUSDT' : Decimal('5.0'),
            '1000BONKUSDT' : Decimal('5.0'),
            'ETCUSDT' : Decimal('5.0')
        },
        short_leverage={
            'FETUSDT' : Decimal('1.0'),
            '1000BONKUSDT': Decimal('1.0'),
        },
        init_risk={
            'FETUSDT': Decimal('1.5'),
            '1000BONKUSDT' : Decimal('1.5'),
            'ETCUSDT' : Decimal('1.5')
        },
        acc={
            'FETUSDT': Decimal('0.5'),
            '1000BONKUSDT' : Decimal('0.5'),
            'ETCUSDT' : Decimal('0.5')
        },
        step_size={
            'FETUSDT': Decimal('10000'),
            '1000BONKUSDT' :Decimal('1000000'),
            'ETCUSDT' : Decimal('100')
        },
        tick_size={
            'FETUSDT': Decimal('1'),
            '1000BONKUSDT' : Decimal('1'),
            'ETCUSDT' : Decimal('1')
        },
        init_long_order_percent={
            'FETUSDT': Decimal('4.0'),
            '1000BONKUSDT' :Decimal('5.0'),
            'ETCUSDT' : Decimal('3')
        },
        add_long_order_percent={
            'FETUSDT': Decimal('3.0'),
            '1000BONKUSDT' : Decimal('4.0'),
            'ETCUSDT' : Decimal('3.0')
        },
        long_take_profit_percent={
            'FETUSDT': Decimal('1.0'),
            '1000BONKUSDT' : Decimal('1.0'),
            'ETCUSDT' : Decimal('1.0')
        },
        long_add_take_profit_percent={
            'FETUSDT': Decimal('1.0'),
            '1000BONKUSDT' : Decimal('1.0'),
            'ETCUSDT' : Decimal('1.0')
        },
        init_short_order_percent={
            'FETUSDT' : Decimal('4'),
            '1000BONKUSDT' : Decimal('4'),
        },
        add_short_order_percent={
            'FETUSDT' : Decimal('3.0'),
            '1000BONKUSDT': Decimal('3'),
        },
        short_take_profit_percent={
            'FETUSDT' : Decimal('1.0'),
            '1000BONKUSDT': Decimal('1'),
        },
        short_add_take_profit_percent={
            'FETUSDT' : Decimal('1.0'),
            '1000BONKUSDT': Decimal('1'),
        },
        high_band_length={
            'FETUSDT' : 5,
            '1000BONKUSDT' : 10,
            'ETCUSDT' : 5
        },
        low_band_length={
            'FETUSDT' : 5,
            '1000BONKUSDT' : 10,
            'ETCUSDT' : 5
        },
        rsi_length=2,
        rsi_low_limit=Decimal('50'),
        rsi_high_limit=Decimal('50'),
    )

    def log(self, txt=None):
        print(f"{txt}")

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.highest = []
        self.lowest = []
        self.rsis = []

        # 기본 캔들 정보 및 페어 명 초기화
        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        # RSI, 고가 채널 저가 채널 설정
        for i in range(0, len(self.pairs)):
            rsi = bt.ind.RSI_Safe(self.closes[i], period=self.p.rsi_length)
            self.rsis.append(rsi)

            highest = bt.indicators.Highest(self.pairs[i].high, period=self.p.high_band_length[self.names[i]])
            self.highest.append(highest)

            lowest = bt.indicators.Lowest(self.pairs[i].low, period=self.p.low_band_length[self.names[i]])
            self.lowest.append(lowest)

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

    # 모든 미체결 종목 취소 함수
    def cancel_all(self, pair_name):
        for order in self.broker.get_orders_open():
            if order.data._name == pair_name:
                self.broker.cancel(order)

    # 자산 기록 함수
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

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                self.total_trading_count += 1
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def stop(self):
        self.log(f'total trading count : {self.total_trading_count}')

    def next(self):
        for i in range(0, len(self.pairs)):
            # 이름 획득
            name = self.names[i]

            # 롱/숏 레버리지 획득
            long_leverage = self.p.long_leverage[name]
            short_leverage = self.p.short_leverage[name]

            # 초기 진입 수량 획득
            init_risk = self.p.init_risk[name]
            add_risk = self.p.acc[name]

            # 수량 및 가격 단위 획득
            qty_unit = self.p.step_size[name]
            price_unit = self.p.tick_size[name]

            # 미체결 주문 모두 취소
            self.cancel_all(name)

            # 자산 기록
            self.record_asset()

            # 현재 포지션 정보 획득
            position_size = self.getposition(self.pairs[i]).size

            # 진입 포지션이 하나도 없을 경우
            if position_size == 0:
                # 진입 포지션이 하나도 없을 경우, 현재 진입가능 수량을 기록하여 둔다.
                # 진입이 다되었다고하면 더이상 진입이 안되도록 하기 위함이다.
                available_equity = DataUtils.convert_to_decimal(self.broker.get_cash())

                # 롱 초기 자산 기록
                long_init_equity[name] = long_leverage * available_equity
                short_init_equity[name] = short_leverage * available_equity

                # 롱 초기 진입 수량 계산
                long_init_entry_qty = long_init_equity[name] * init_risk / Decimal('100') / DataUtils.convert_to_decimal(self.closes[i][0])
                long_init_entry_qty = int(long_init_entry_qty / qty_unit) * qty_unit

                # 숏 초기 진입 수량 계산
                short_init_entry_qty = short_init_equity[name] * init_risk / Decimal('100') / DataUtils.convert_to_decimal(self.closes[i][0])
                short_init_entry_qty = int(short_init_entry_qty / qty_unit) * qty_unit

                # 롱 진입 기준 가격 계산
                long_init_entry_standard_price = DataUtils.convert_to_decimal(self.highest[i][0]) \
                                                 * (Decimal('1') - self.p.init_long_order_percent[name] / Decimal('100'))
                long_init_entry_standard_price = int(long_init_entry_standard_price / price_unit) * price_unit

                # 숏 진입 기준 가격 계산
                short_init_entry_standard_price = DataUtils.convert_to_decimal(self.lowest[i][0]) \
                                                  * (Decimal('1') + self.p.init_short_order_percent[name] / Decimal('100'))
                short_init_entry_standard_price = int(short_init_entry_standard_price / price_unit) * price_unit

                # if long_init_entry_qty > Decimal('0') and DataUtil.convert_to_decimal(self.closes[i][0]) < long_init_entry_standard_price:
                #     self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(long_init_entry_qty))
                if short_init_entry_qty > Decimal('0') and DataUtils.convert_to_decimal(self.closes[i][0]) > short_init_entry_standard_price:
                    self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(short_init_entry_qty))
            elif position_size > 0:
                long_add_entry_qty = DataUtils.convert_to_decimal(position_size) * add_risk / Decimal('2')
                long_add_entry_qty = int(long_add_entry_qty / qty_unit) * qty_unit

                entry_avg_price = DataUtils.convert_to_decimal(self.getposition(self.pairs[i]).price)
                if long_init_equity[name] > entry_avg_price * DataUtils.convert_to_decimal(position_size):
                    long_add_entry_standard_price = entry_avg_price * (Decimal('1') - self.p.add_long_order_percent[name] / Decimal('100'))
                    long_add_entry_standard_price = int(long_add_entry_standard_price / price_unit) * price_unit
                    if self.closes[i][0] < long_add_entry_standard_price:
                        self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(long_add_entry_qty))

                    profit_percent = self.p.long_take_profit_percent[name]
                    if self.rsis[i][0] < self.p.rsi_low_limit:
                        profit_percent += self.p.long_add_take_profit_percent[name]

                    exit_price = entry_avg_price * (Decimal('1') + profit_percent / Decimal('100'))
                    exit_price = int(exit_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(exit_price),
                                           size=float(position_size))
            elif position_size < 0:
                short_add_entry_qty = abs(DataUtils.convert_to_decimal(position_size)) * add_risk / Decimal('2')
                short_add_entry_qty = int(short_add_entry_qty / qty_unit) * qty_unit

                entry_avg_price = DataUtils.convert_to_decimal(self.getposition(self.pairs[i]).price)
                if short_init_equity[name] > entry_avg_price * abs(DataUtils.convert_to_decimal(position_size)):
                    short_add_entry_standard_price = entry_avg_price * (Decimal('1') - self.p.add_short_order_percent[name] / Decimal('100'))
                    short_add_entry_standard_price = int(short_add_entry_standard_price / price_unit) * price_unit
                    if self.closes[i][0] > short_add_entry_standard_price:
                        self.order = self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=float(short_add_entry_qty))

                    profit_percent = self.p.short_take_profit_percent[name]
                    if self.rsis[i][0] > self.p.rsi_high_limit:
                        profit_percent += self.p.short_add_take_profit_percent[name]
                    exit_price = entry_avg_price * (Decimal('1') - profit_percent / Decimal('100'))
                    exit_price = int(exit_price / self.p.tick_size[name]) * self.p.tick_size[name]
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(exit_price), size=float(position_size))

if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiDcaLongShortV1)

    cerebro.broker.setcash(200000000000000)
    cerebro.broker.set_slippage_perc(0)
    cerebro.broker.setcommission(0.0025, leverage=100)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BINANCE, pair, tick_kind)
        df = DataUtils.get_candle_data_in_scape(df, '2023-01-01 00:00:00', '2024-11-13 00:00:00')
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('Before Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    order_balance_list = strat.order_balance_list
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")

    # file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    file_name = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"

    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "MultiDcaLongShortV1"

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