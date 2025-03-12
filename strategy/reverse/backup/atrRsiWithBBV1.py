import backtrader as bt
import quantstats as qs
import pandas as pd
from util.Util import DataUtils
from decimal import  Decimal
from indicator.Indicators import Indicator
pairs = {
    'BTCUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'XRPUSDT': DataUtils.CANDLE_TICK_30M,
    'DOGEUSDT': DataUtils.CANDLE_TICK_30M,
}


'''
전략에 대한 아이디어
1. 모든 알트코인은 비트코인의 행보에 매우 큰 영향을 받는다.
    - 비트코인이 상승추세일 경우, 알트코인도 상승 추세이므로 아래 지정가 주문의 간격을 좁힌다.
    - 비트코인이 횡보추세일 경우, 알트코인도 횡보 추세이므로 아래 지정가 주문의 간격을 기본 값으로 셋팅한다.
    - 비트코인이 하락추세일 경우, 알트코인은 더 큰 하락추세를 겪으므로 아래 지정가 주문의 간격을 매우 넓힌다.
2. 비트코인의 추세 판단 여부
    - 상승장 : 1시간봉 캔들이 볼린저밴드 상단선보다 위에 존재
    - 횡보장 : 1시간봉 캔들이 볼랜저밴드 하단선보다 위, 상단선보다 밑에 존재
    - 하락장 : 1시간봉 캔들이 볼린저밴드 하단선보다 아래에 존재
3. 종료 조건은 가장 최근의 캔들 추세 강도를 나타내는 rsi 값을 통해 수행한다.
    - rsi만을 보므로 자동으로 손절의 조건이 될 수도, 익절의 조건이 될 수도 있다.
4. 변동성 변수 ATR을 이용하여 간격을 계산한다.
    - 단순히 퍼센트로 계산 시, 현재의 변동성을 반영하지 못해 계속 안들어가거나 계속 들어가거나 하는 위험성이 존재한다.
    - 이런 단순 퍼센트 계산 방식을 개선하고자 ATR을 이용한다.
'''
class AtrRsiWithBBV1(bt.Strategy):
    params = dict(
        leverage=4,
        atr_avg_length=3,
        atr_length=10,
        rsi_length=2,
        rsi_high=50,
        bb_span = 80,
        bb_mult=1,

        risks = [
          Decimal('1'),
            Decimal('1'),
            Decimal('2'),
            Decimal('4'),
            Decimal('8'),
        ],
        bull_atr_constants={
            '1000BONKUSDT': [Decimal('1.0'), Decimal('1.5'), Decimal('2.0'), Decimal('2.5'), Decimal('3.0')],
            '1000PEPEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0')],
            'XRPUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0')],
            'DOGEUSDT': [Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0')]

        },

        default_atr_constants={
            '1000BONKUSDT': [Decimal('1.0'), Decimal('1.5'), Decimal('2.0'), Decimal('2.5'), Decimal('3.0')],
            '1000PEPEUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
            'XRPUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
            'DOGEUSDT': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')]
        },

        bear_atr_constants={
            '1000BONKUSDT': [Decimal('2.0'), Decimal('2.5'), Decimal('3.0'), Decimal('3.5'), Decimal('4.0')],
            '1000PEPEUSDT': [Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            'XRPUSDT': [Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')],
            'DOGEUSDT': [Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0'), Decimal('12.0')]
        },

        tick_size={
            '1000BONKUSDT': Decimal('0.0000010'),
            '1000PEPEUSDT': Decimal('0.0000001'),
            'XRPUSDT': Decimal('0.0001'),
            'DOGEUSDT': Decimal('0.00001')
        },
        step_size={
            '1000BONKUSDT': Decimal('100'),
            '1000PEPEUSDT': Decimal('100'),
            'XRPUSDT': Decimal('1'),
            'DOGEUSDT': Decimal('1')
        }
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.pairs = []
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])

        self.pairs_open = []
        for i in range(0, len(self.pairs)):
            self.pairs_open.append(self.pairs[i].open)

        self.pairs_high = []
        for i in range(0, len(self.pairs)):
            self.pairs_high.append(self.pairs[i].high)

        self.pairs_low = []
        for i in range(0, len(self.pairs)):
            self.pairs_low.append(self.pairs[i].low)

        self.pairs_close = []
        for i in range(0, len(self.pairs)):
            self.pairs_close.append(self.pairs[i].close)

        self.pairs_date = []
        for i in range(0, len(self.pairs)):
            self.pairs_date.append(self.pairs[i].datetime)

        # 내장 ATR의 경우, 계산 방식이 옳지 못한 것으로 보여, TR 계산 후 직접 ATR을 계산한다.
        # 계산방식은 Simple Moving Avrage 방식이다.
        self.pairs_atr = []
        for i in range(0, len(self.pairs)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            self.pairs_atr.append(bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length))

        self.pair_rsi = []
        for i in range(0, len(self.pairs)):
            rsi = bt.ind.RSI_Safe(self.pairs_close[i], period=self.p.rsi_length)
            self.pair_rsi.append(rsi)

        self.btc_bb = bt.indicators.BollingerBands(self.pairs_close[0], period=self.p.bb_span, devfactor=self.p.bb_mult)
        self.btc_top = self.btc_bb.lines.top
        self.btc_mid = self.btc_bb.lines.mid
        self.btc_bot = self.btc_bb.lines.bot

        self.order = None
        self.date_value = []
        self.my_assets = []

        self.return_rate = 0
        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

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
            position_value = 0.0
            bough_value = 0.0
            account_value = self.broker.get_cash()
            broker_leverage = self.broker.comminfo[None].p.leverage
            for pair in self.pairs:
                position_value += self.getposition(pair).size * pair.low[0]
                bough_value += self.getposition(pair).size * self.getposition(pair).price

            account_value += position_value - bough_value * (broker_leverage-1) / broker_leverage
            self.order_balance_list.append([self.pairs_date[1].datetime(0), account_value])

            self.cancel_all()
            for i in range(1, len(self.pairs)):
                currency = self.pairs[i]._name
                position_size = self.getposition(self.pairs[i]).size
                if position_size > 0:
                    if self.pair_rsi[i][0] > self.p.rsi_high:
                        self.order = self.sell(data=self.pairs[i], size=position_size)

                pair_minutes = self.pairs_date[i].datetime(0).minute
                btc_index = -1
                if pair_minutes == 30:
                    btc_index = 0

                prices = []
                if self.pairs_close[0][btc_index] > self.btc_top[btc_index]:
                    for j in range(0, 5):
                        price = Decimal(self.pairs_close[i][0]) - Decimal(self.pairs_atr[i][0]) * self.p.bull_atr_constants[currency][j]
                        price = int(price / self.p.tick_size[currency]) * self.p.tick_size[currency]
                        prices.append(float(price))

                elif self.btc_bot[btc_index] < self.pairs_close[0][btc_index] < self.btc_top[btc_index]:
                    for j in range(0, 5):
                        price = Decimal(self.pairs_close[i][0]) - Decimal(self.pairs_atr[i][0]) * self.p.default_atr_constants[currency][j]
                        price = int(price / self.p.tick_size[currency]) * self.p.tick_size[currency]
                        prices.append(float(price))
                elif self.pairs_close[0][btc_index] < self.btc_bot[btc_index]:
                    for j in range(0, 5):
                        price = Decimal(self.pairs_close[i][0]) - Decimal(self.pairs_atr[i][0]) * self.p.bear_atr_constants[currency][j]
                        price = int(price / self.p.tick_size[currency]) * self.p.tick_size[currency]
                        prices.append(float(price))

                self.log(f'{self.pairs_date[i].datetime(0)}')
                for j in range(0, 5):
                    self.log(f'{prices[j]}')
                current_equity = Decimal(str(self.broker.get_cash()))
                for j in range(0, 5):
                    if prices[j] <= 0:
                        continue
                    qty = self.p.leverage * current_equity * self.p.risks[j] / Decimal('100') / Decimal(prices[j])
                    qty = int(qty / self.p.step_size[currency]) * self.p.step_size[currency]
                    if qty > 0:
                        self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=prices[j], size=float(qty))
        except:
            raise

    def stop(self):
        self.winning_rate = self.winning_trading_count * 100 / self.total_trading_count
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getvalue())

        self.log("total trading count %.2f" % self.total_trading_count)
        self.log("winning percent : [%.2f]" % self.winning_rate)
        self.log(f"수익률 : {self.return_rate}%")

    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=4)
    cerebro.addstrategy(AtrRsiWithBBV1)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtils.load_candle_data_as_df(data_path, DataUtils.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    order_balance_list = strat.order_balance_list

    file_name = ""
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "multiRsiWithBTC"
    qs.reports.html(returns, output=f'alt_multipair.html', title=file_name)

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
    qs.reports.html(df['value'], output="result.html", download_filename="result.html", title="Result")