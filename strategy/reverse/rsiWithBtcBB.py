import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal, ROUND_HALF_UP
import quantstats as qs
import pyfolio as pf
from indicator.Indicators import Indicator


class RsiWithBtcBB(bt.Strategy):

    # 환경설정 파라미터값 선언
    params = dict(
        leverage=Decimal('3'),
        risks=[Decimal('1'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8')],
        bb_span=80,
        bb_mult=1,
        rsi_length=2,
        rsi_high=90,
        # bull_percents=[0.5, 0.5, 0.5, 0.5, 0.5],
        # bear_percents=[0.5, 0.5, 0.5, 0.5, 0.5],
        # default_percents=[0.5, 0.5, 0.5, 0.5, 0.5],
        bull_percents=[Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0')],
        bear_percents=[Decimal('1.0'), Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0')],
        default_percents=[Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
        xrp_tick_size=Decimal('0.0001'),
        xrp_step_size=Decimal('1'),
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        try:
            # data feeds 초기화
            self.btc = self.datas[0]
            self.pair = self.datas[1]

            # 테스팅용 종목 ohlc 초기화
            self.pair_open = self.pair.open
            self.pair_high = self.pair.high
            self.pair_low = self.pair.low
            self.pair_close = self.pair.close
            self.pair_date = self.pair.datetime
            self.pair_rsi = bt.ind.RSI_Safe(self.pair_close, period=self.p.rsi_length)
            # self.pair_rsi = bt.ind.RSI_Safe(bt.ind.RSI(self.pair_close), period=self.p.rsi_length)

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

            self.order = None
            self.date_value = []
            self.my_assets = []

            self.initial_asset = self.broker.getvalue()
            self.return_rate = 0
            self.total_trading_count = 0
            self.winning_trading_count = 0
            self.winning_rate = 0
        except Exception as e:
            raise(e)

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

    def next(self):
        try:
            self.log(f'BTC: {self.btc_date.datetime(0)}, XRP :{self.pair_date.datetime(0)}')

            self.cancel_all()
            current_position_size = self.getposition(self.datas[1]).size

            if current_position_size > 0:
                if self.pair_rsi[0] > self.p.rsi_high:
                    self.order = self.sell(data=self.pair, size=current_position_size)

            prices = []
            if self.btc_close[0] > self.bb_top[0]:
                for i in range(0, 5):
                    price = Decimal(self.pair_close[0]) * (Decimal('1') - self.p.bull_percents[i] / Decimal('100'))
                    price = int(price / self.p.xrp_tick_size) * self.p.xrp_tick_size
                    price = price.quantize(self.p.xrp_tick_size, rounding=ROUND_HALF_UP)
                    prices.append(float(price))

            elif self.bb_bot[0] < self.btc_close[0] < self.bb_top[0]:
                for i in range(0, 5):
                    price = Decimal(self.pair_close[0]) * (Decimal('1') - self.p.default_percents[i] / Decimal('100'))
                    price = int(price / self.p.xrp_tick_size) * self.p.xrp_tick_size
                    price = price.quantize(self.p.xrp_tick_size, rounding=ROUND_HALF_UP)
                    prices.append(float(price))

            elif self.btc_close[0] < self.bb_bot[0]:
                for i in range(0, 5):
                    price = Decimal(self.pair_close[0]) * (Decimal('1') - self.p.bear_percents[i] / Decimal('100'))
                    price = int(price / self.p.xrp_tick_size) * self.p.xrp_tick_size
                    price = price.quantize(self.p.xrp_tick_size, rounding=ROUND_HALF_UP)
                    prices.append(float(price))

            current_equity = Decimal(str(self.broker.getvalue()))
            for i in range(0, 5):
                qty = self.p.leverage * current_equity * self.p.risks[i] / 100 / Decimal(prices[i])
                qty = int(Decimal(qty) / self.p.xrp_step_size) * self.p.xrp_step_size
                if qty > 0:
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pair, price=prices[i], size=float(qty))
        except:
            raise

    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)



if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    start_date = '2020-01-01 00:00:00'
    end_date = '2024-04-11 00:00:00'

    pairs = {
        'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
        'SOLUSDT': DataUtil.CANDLE_TICK_30M,
    }

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=100)
    cerebro.addstrategy(RsiWithBtcBB)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        # df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')

        cerebro.adddata(data, name=pair)

    print('시작 포트폴리오 가격: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    print('끝 포트폴리오 가격: %.2f' % cerebro.broker.getvalue())

    qs.reports.html(returns, output=f'xrpusdt.html', title='result')