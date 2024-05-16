import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal, ROUND_HALF_UP
import quantstats as qs
import pandas as pd
import matplotlib.pyplot as plt
import pyfolio as pf
from indicator.Indicators import Indicator
pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
    '1000BONKUSDT': DataUtil.CANDLE_TICK_30M,
    '1000PEPEUSDT': DataUtil.CANDLE_TICK_30M,
    'SOLUSDT': DataUtil.CANDLE_TICK_30M,
    'DOGEUSDT': DataUtil.CANDLE_TICK_30M,
    # 'XRPUSDT': DataUtil.CANDLE_TICK_30M,
    # 'SEIUSDT': DataUtil.CANDLE_TICK_30M,
    # 'TIAUSDT': DataUtil.CANDLE_TICK_30M,
}


class MultiRsiWithBtcBB(bt.Strategy):
    # 환경설정 파라미터값 선언
    params = dict(
        leverage=Decimal('4'),
        risks=[
            Decimal('1'),  # 1차 진입% 
            Decimal('1'),  # 2차 진입%
            Decimal('2'),  # 3차 진입%
            Decimal('4'),  # 4차 진입%
            Decimal('8')  # 5차 진입%
        ],
        bb_span=80,
        bb_mult=1,
        rsi_length=2,
        rsi_high=50,

        bull_percents = {
            '1000BONKUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('7.0')],
            '1000PEPEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('5.0'), Decimal('7.0')],
            'SEIUSDT': [Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
            'TIAUSDT': [Decimal('1.0'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('9.0')],
            'SOLUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
            'DOGEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
            'XRPUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
        },

        bear_percents = {
            '1000BONKUSDT': [Decimal('10.0'), Decimal('12.0'), Decimal('14.0'), Decimal('16.0'), Decimal('18.0')],
            '1000PEPEUSDT': [Decimal('10.0'), Decimal('12.0'), Decimal('14.0'), Decimal('16.0'), Decimal('18.0')],
            'SEIUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0'), Decimal('11.0')],
            'TIAUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0'), Decimal('11.0')],
            'SOLUSDT': [Decimal('5.0'), Decimal('7.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0')],
            'DOGEUSDT': [Decimal('5.0'), Decimal('7.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0')],
            'XRPUSDT': [Decimal('5.0'), Decimal('7.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0')],
        },

        default_percents = {
            '1000BONKUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
            '1000PEPEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
            'SEIUSDT': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0')],
            'TIAUSDT': [Decimal('3.0'), Decimal('6.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0')],
            'SOLUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
            'DOGEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
            'XRPUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('9.0')],
        },

        tick_size = {
            '1000BONKUSDT': Decimal('0.0000010'),
            '1000PEPEUSDT': Decimal('0.0000001'),
            'SEIUSDT': Decimal('0.00010'),
            'TIAUSDT': Decimal('0.001'),
            'XRPUSDT': Decimal('0.0001'),
            'SOLUSDT': Decimal('0.010'),
            'DOGEUSDT': Decimal('0.00001')
        },
        step_size={
            '1000BONKUSDT': Decimal('100'),
            '1000PEPEUSDT': Decimal('100'),
            'SEIUSDT': Decimal('1'),
            'TIAUSDT': Decimal('0.1'),
            'XRPUSDT': Decimal('1'),
            'SOLUSDT': Decimal('0.1'),
            'DOGEUSDT': Decimal('1')
        },
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        try:
            # data feeds 초기화
            self.btc = self.datas[0]

            # 비트코인 정보초기화
            self.btc_open = self.btc.open
            self.btc_high = self.btc.high
            self.btc_low = self.btc.low
            self.btc_close = self.btc.close
            self.btc_date = self.btc.datetime

            self.bb = bt.indicators.BollingerBands(self.btc.close, period=self.p.bb_span, devfactor=self.p.bb_mult)
            self.bb_top = self.bb.lines.top
            self.bb_mid = self.bb.lines.mid
            self.bb_bot = self.bb.lines.bot

            # 멀티페어 페어 초기화
            self.pairs = []
            for i in range(0, len(self.datas)):
                self.pairs.append(self.datas[i])

            self.pair_open = []
            for i in range(0, len(self.pairs)):
                self.pair_open.append(self.pairs[i].open)

            self.pair_high = []
            for i in range(0, len(self.pairs)):
                self.pair_high.append(self.pairs[i].high)

            self.pair_low = []
            for i in range(0, len(self.pairs)):
                self.pair_low.append(self.pairs[i].low)

            self.pair_close = []
            for i in range(0, len(self.pairs)):
                self.pair_close.append(self.pairs[i].close)

            self.pair_date = []
            for i in range(0, len(self.pairs)):
                self.pair_date.append(self.pairs[i].datetime)

            self.pair_rsi = []
            for i in range(0, len(self.pairs)):
                rsi = bt.ind.RSI_Safe(self.pair_close[i], period=self.p.rsi_length)
                self.pair_rsi.append(rsi)

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

        except Exception as e:
            raise (e)

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
        try:
            account_value = self.broker.get_cash() # 현재 현금(보유 포지션 제외) 자산의 가격을 획득
            broker_leverage = self.broker.comminfo[None].p.leverage # cerebro에 설정한 레버리지 값 -> setcommission
            position_value = 0.0
            bought_value = 0.0
            for pair in self.pairs:
                position_value += self.getposition(pair).size * pair.low[0]
                bought_value += self.getposition(pair).size * self.getposition(pair).price # 진입한 수량 x 평단가 즉, 현재 포지션 전체 가치를 의미(현금 제외)

            account_value += position_value - bought_value * (broker_leverage-1) / broker_leverage
            self.order_balance_list.append([self.pair_date[1].datetime(0), account_value])

            # order_balance = self.broker.get_cash()
            # self.order_balance_list.append([self.pair_date[0].datetime(0), order_balance])
            self.date_value.append(self.pair_date[1].datetime(0))
            position_value = self.broker.getvalue()
            for i in range(1, len(self.datas)):
                position_value += self.getposition(self.datas[i]).size * self.pair_low[i][0]

            self.my_assets.append(position_value)
            # self.my_assets.append(self.broker.getvalue() + self.getposition(self.datas[1]).size * self.pair_low[1][0] + self.getposition(self.datas[2]).size * self.pair_low[2][0])
            self.cancel_all()
            for i in range(1, len(self.pairs)):
                currency_name = self.pairs[i]._name
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size > 0:
                    if self.pair_rsi[i][0] > self.p.rsi_high:
                        self.order = self.sell(data=self.pairs[i], size=current_position_size)

                pair_minutes = self.pair_date[i].datetime(0).minute
                btc_index = -1
                if pair_minutes == 30:
                    btc_index = 0
                self.log(f'btc time : {self.btc_date.datetime(btc_index)} <=> {currency_name} time : {self.pair_date[i].datetime(0)}')
                prices = []
                if self.btc_close[btc_index] > self.bb_top[btc_index]:
                    self.log(f'상승장 {self.pair_date[i].datetime(0)}')
                    for j in range(0, 5):
                        price = Decimal(self.pair_close[i][0]) * (
                                    Decimal('1') - self.p.bull_percents[currency_name][j] / Decimal('100'))
                        price = int(price / self.p.tick_size[currency_name]) * self.p.tick_size[currency_name]
                        price = price.quantize(self.p.tick_size[currency_name], rounding=ROUND_HALF_UP)
                        prices.append(float(price))
                elif self.bb_bot[btc_index] < self.btc_close[btc_index] < self.bb_top[btc_index]:
                    self.log(f'횡보장 {self.pair_date[i].datetime(0)}')
                    for j in range(0, 5):
                        price = Decimal(self.pair_close[i][0]) * (
                                Decimal('1') - self.p.default_percents[currency_name][j] / Decimal('100'))
                        price = int(price / self.p.tick_size[currency_name]) * self.p.tick_size[currency_name]
                        price = price.quantize(self.p.tick_size[currency_name], rounding=ROUND_HALF_UP)
                        prices.append(float(price))
                elif self.btc_close[btc_index] < self.bb_bot[btc_index]:
                    self.log(f'하락장 {self.pair_date[i].datetime(0)}')
                    for j in range(0, 5):
                        price = Decimal(self.pair_close[i][0]) * (
                                    Decimal('1') - self.p.bear_percents[currency_name][j] / Decimal('100'))
                        price = int(price / self.p.tick_size[currency_name]) * self.p.tick_size[currency_name]
                        price = price.quantize(self.p.tick_size[currency_name], rounding=ROUND_HALF_UP)
                        prices.append(float(price))

                for price in prices:
                    self.log(price)
                current_equity = Decimal(str(self.broker.getvalue()))
                for j in range(0, 5):
                    qty = self.p.leverage * current_equity * self.p.risks[j] / Decimal('100') / Decimal(prices[j])
                    qty = int(qty / self.p.step_size[currency_name]) * self.p.step_size[currency_name]
                    if qty > 0:
                        self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=prices[j],
                                              size=float(qty))
        except:
            raise

    def stop(self):
        self.winning_rate = self.winning_trading_count * 100 / self.total_trading_count
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getvalue())
        self.log(f'my assets type : {type(self.my_assets)}')

        self.log("total trading count %.2f" % self.total_trading_count)
        self.log("winning percent : [%.2f]" % self.winning_rate)
        self.log(f"수익률 : {self.return_rate}%")

    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)


if __name__ == '__main__':
    data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    # data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    start_date = '2022-04-01 00:00:00'
    end_date = '2024-04-17 00:00:00'

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=4)
    cerebro.addstrategy(MultiRsiWithBtcBB)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        # df = DataUtil.get_candle_data_in_scape(df, start_date, end_date)
        # df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')

        cerebro.adddata(data, name=pair)

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    order_balance_list = strat.order_balance_list

    mdd = qs.stats.max_drawdown(asset_list).iloc[0]
    print(f" quanstats's my variable MDD : {mdd * 100:.2f} %")
    mdd = Indicator.calculate_max_draw_down(asset_list)
    print(f" quanstats's my function MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")

    file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"

    for pair, tick_kind in pairs.items():
        file_name += pair +"-"
    file_name += "multiRsiWithBTC"

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