import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    '1000BONKUSDT' : DataUtil.CANDLE_TICK_30M,
}

class MultiDcaLongShortV1(bt.Strategy):
    params = dict(
        init_risk={
            '1000PEPEUSDT': Decimal('1.5'),
            '1000BONKUSDT': Decimal('1.5')
        },
        acc={
            '1000PEPEUSDT': Decimal('0.5'),
            '1000BONKUSDT': Decimal('0.5')
        },
        step_size={
            '1000PEPEUSDT': Decimal('100'),
            '1000BONKUSDT': Decimal('100')
        },
        tick_size={
            '1000PEPEUSDT': Decimal('0.0000001'),
            '1000BONKUSDT' : Decimal('0.0000010')
        },
        init_long_order_percent={
            '1000PEPEUSDT': Decimal('4.0'),
            '1000BONKUSDT': Decimal('4.0')
        },
        init_short_order_percent={
            '1000PEPEUSDT': Decimal('3.0'),
            '1000BONKUSDT': Decimal('3.0')
        },
        add_long_order_percent={
            '1000PEPEUSDT': Decimal('3'),
            '1000BONKUSDT': Decimal('3'),
        },
        add_short_order_percent={
            '1000PEPEUSDT': Decimal('3'),
            '1000BONKUSDT': Decimal('3')
        },
        long_take_profit_percent={
            '1000PEPEUSDT': Decimal('1.0'),
            '1000BONKUSDT': Decimal('1.0')
        },
        long_add_take_profit_percent={
            '1000PEPEUSDT': Decimal('1.0'),
            '1000BONKUSDT': Decimal('1.0')
        },
        short_take_profit_percent={
            '1000PEPEUSDT': Decimal('0.5'),
            '1000BONKUSDT': Decimal('0.5')
        },
        short_add_take_profit_percent={
            '1000PEPEUSDT': Decimal('0.5'),
            '1000BONKUSDT': Decimal('0.5')
        },

        high_band_length=5,
        low_band_length=5,

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

        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            rsi = bt.ind.RSI_Safe(self.closes[i], period=self.p.rsi_length)
            self.rsis.append(rsi)

            highest = bt.indicators.Highest(self.pairs[i].high, period=self.p.high_band_length)
            self.highest.append(highest)

            lowest = bt.indicators.Lowest(self.pairs[i].low, period=self.p.low_band_length)
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

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}')
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def next(self):
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                init_total_value = DataUtil.convert_to_decimal(self.broker.get_cash())
                init_qty = init_total_value * self.p.init_risk[name] / Decimal('100') / Decimal(self.closes[i][0])
                init_qty = int(init_qty / self.p.step_size[name]) * self.p.step_size[name]

                long_entry_price = DataUtil.convert_to_decimal(self.highest[i][0]) * (Decimal('1') - self.p.init_long_order_percent[name] / Decimal('100'))
                long_entry_price = int(long_entry_price / self.p.tick_size[name]) * self.p.tick_size[name]
                if DataUtil.convert_to_decimal(self.closes[i][0]) < long_entry_price:
                    self.log(f'{self.dates[i].datetime(0)} => {self.closes[i][0]}')
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(init_qty), price=self.closes[i][0])

            elif current_position_size > 0:
                cur_qty = DataUtil.convert_to_decimal(current_position_size) * self.p.acc[name] / Decimal('2')
                cur_qty = int(cur_qty / self.p.step_size[name]) * self.p.step_size[name]

                entry_avg_price = DataUtil.convert_to_decimal(self.getposition(self.pairs[i]).price)
                long_entry_price = entry_avg_price * (Decimal('1') - self.p.add_long_order_percent[name] / Decimal('100'))
                long_entry_price = int(long_entry_price / self.p.tick_size[name]) * self.p.tick_size[name]
                if self.closes[i][0] < long_entry_price:
                    self.order = self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=float(cur_qty))

                profit_percent = self.p.long_take_profit_percent[name]
                if self.rsis[i][0] < self.p.rsi_low_limit:
                    profit_percent += self.p.long_add_take_profit_percent[name]

                exit_price = entry_avg_price * (Decimal('1') + profit_percent / Decimal('100'))
                exit_price = int(exit_price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(exit_price), size=float(current_position_size))

if __name__ == '__main__':
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiDcaLongShortV1)

    cerebro.broker.setcash(1500)
    cerebro.broker.setcommission(0.0025, leverage=1)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('Before Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())