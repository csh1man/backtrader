import backtrader as bt
from util.Util import DataUtil
from decimal import Decimal, ROUND_HALF_UP
import quantstats as qs
import pyfolio as pf
import pandas as pd
from indicator.Indicators import Indicator


class RsiWithBtcBB(bt.Strategy):

    # 환경설정 파라미터값 선언
    params = dict(
        leverage=Decimal('3'),
        risks=[Decimal('1'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8')],
        bb_span=70,
        bb_mult=1,
        rsi_length=2,
        rsi_high=90,
        bull_percents=[Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
        default_percents=[Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0')],
        bear_percents=[Decimal('7.0'), Decimal('9.0'), Decimal('11.0'), Decimal('13.0'), Decimal('15.0')],
        xrp_tick_size=Decimal('0.0005'),
        xrp_step_size=Decimal('0.01'),
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
                         f'가격:{order.created.price:.10f}')
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.10f}')
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def next(self):
        try:
            self.date_value.append(self.pair_date.datetime(0))
            position_value = self.broker.getvalue()
            for i in range(1, len(self.datas)):
                position_value += self.getposition(self.datas[i]).size * self.pair_low[0]
            self.my_assets.append(position_value)

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
                qty = self.p.leverage * current_equity * self.p.risks[i] / Decimal('100') / Decimal(prices[i])
                qty = int(Decimal(qty) / self.p.xrp_step_size) * self.p.xrp_step_size
                if qty > 0:
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pair, price=prices[i], size=float(qty))
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
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    start_date = '2023-01-01 00:00:00'
    end_date = '2024-04-16 00:00:00'

    pairs = {
        'BTCUSDT': DataUtil.CANDLE_TICK_1HOUR,
        'APTUSDT': DataUtil.CANDLE_TICK_30M,
    }

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=5)
    cerebro.addstrategy(RsiWithBtcBB)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        # df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')

        cerebro.adddata(data, name=pair)


    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    mdd = qs.stats.max_drawdown(asset_list).iloc[0]
    print(f" quanstats's my variable MDD : {mdd * 100:.2f} %")
    mdd = Indicator.calculate_max_draw_down(asset_list)
    print(f" quanstats's my function MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")

    file_name = ""
    for pair, tick_kind in pairs.items():
        file_name += pair +"-"
    qs.reports.html(returns, output=f'{file_name}.html', title='result')