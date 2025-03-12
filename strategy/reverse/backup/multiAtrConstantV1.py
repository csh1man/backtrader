import backtrader as bt
from util.Util import DataUtils
from decimal import Decimal, ROUND_HALF_UP
import quantstats as qs
import pandas as pd
import matplotlib.pyplot as plt
import pyfolio as pf
from indicator.Indicators import Indicator
pairs = {
    'BTCUSDT': DataUtils.CANDLE_TICK_1DAY,
    '1000BONKUSDT': DataUtils.CANDLE_TICK_1HOUR,
}


class MultiAtrConstantStrategy(bt.Strategy):
    params = dict(
        leverage=Decimal('10'),
        risks=[
            Decimal('1'), Decimal('1'), Decimal('1'),
            Decimal('2'), Decimal('2'), Decimal('2'), Decimal('2'),
            Decimal('3'), Decimal('3'), Decimal('3')
        ],
        addRisks=[
            Decimal('2'), Decimal('2'), Decimal('2'),
            Decimal('3'), Decimal('3'), Decimal('3'), Decimal('3'),
            Decimal('4'), Decimal('4'), Decimal('4')
        ],
        atr_length=150,
        atr_avg_length=50,
        bearish_atr_constants={
            '1000BONKUSDT': [
                                Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('10.0'),
                                Decimal('12.0'), Decimal('14.0'), Decimal('16.0'), Decimal('18.0'), Decimal('20.0')
                            ]
        },
        default_atr_constants={
            '1000BONKUSDT': [
                Decimal('1.5'), Decimal('1.8'), Decimal('2.0'), Decimal('2.5'), Decimal('3.5'),
                Decimal('4.0'), Decimal('4.5'), Decimal('5.0'), Decimal('5.5'), Decimal('6.0')
            ]
        },
        step_size={
            '1000BONKUSDT': Decimal('0.000001')
        },
        tick_size={
            '1000BONKUSDT': Decimal('100')
        },
        exitPercent={
            '1000BONKUSDT' : Decimal('0.8'),
        }
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        self.btc = self.datas[0]
        self.btc_open = self.btc.open
        self.btc_high = self.btc.high
        self.btc_low = self.btc.low
        self.btc_close = self.btc.close
        self.btc_date = self.btc.datetime

        self.pairs = []
        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])

        self.pairs_open = []
        self.pairs_high = []
        self.pairs_low = []
        self.pairs_close = []
        self.pairs_date = []
        self.pairs_atr = []
        for i in range(0, len(self.pairs)):
            self.pairs_open.append(self.pairs[i].open)
            self.pairs_high.append(self.pairs[i].high)
            self.pairs_low.append(self.pairs[i].low)
            self.pairs_close.append(self.pairs[i].close)
            self.pairs_date.append(self.pairs[i].datetime)
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.SmoothedMovingAverage(tr, period=self.p.atr_length)
            atr = bt.indicators.MovingAverageSimple(atr, period=self.p.atr_avg_length)
            self.pairs_atr.append(atr)

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
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

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
        self.order_balance_list.append([self.pairs_date[0].datetime(0), account_value])
        self.date_value.append(self.pairs_date[0].datetime(0))
        position_value = self.broker.getvalue()
        for i in range(1, len(self.datas)):
            position_value += self.getposition(self.datas[i]).size * self.pairs_low[i][0]

        self.my_assets.append(position_value)

    def next(self):
        try:
            for i in range(1, len(self.pairs)):
                self.record_asset()
                '''
                진입해야할 가격에 대해서 미리 계산을 수행한다.
                1. 비트코인이 전날 대비 0.2퍼센트 이상 떨어졌을 경우 => Bearish 상수를 사용한다.
                2. 비트코인이 전날 대비 1번에 해당하지 않을 경우 => Bullish 상수를 사용한다.
                '''
                name = self.pairs[i]._name
                prices = []
                if (self.btc_close[0] - self.btc_close[-1]) * 100 / self.btc_close[-1] < - 0.2:
                    for j in range(0, len(self.p.risks)):
                        price = DataUtils.convert_to_decimal(self.pairs_close[i][0]) - DataUtils.convert_to_decimal(self.pairs_atr[i][0]) * self.p.bearish_atr_constants[name][j]
                        price = price.quantize(self.p.step_size[name], rounding=ROUND_HALF_UP)
                        prices.append(price)
                else:
                    for j in range(0, len(self.p.risks)):
                        price = DataUtils.convert_to_decimal(self.pairs_close[i][0]) - DataUtils.convert_to_decimal(self.pairs_atr[i][0]) * self.p.default_atr_constants[name][j]
                        price = price.quantize(self.p.step_size[name], rounding=ROUND_HALF_UP)
                        prices.append(price)

                self.log(f'=========================={self.pairs_date[i].datetime(0)}=======================')
                for j in range(0, len(prices)):
                    self.log(prices[j])

                '''
                지정가 걸려있는 물량을 모두 취소한다.
                '''
                self.cancel_all()

                '''
                진입한 수량 존재여부 확인
                '''
                current_position = False
                current_position_size = self.getposition(self.pairs[i]).size
                if current_position_size > 0:
                    current_position = True

                '''
                현재 사용가능 시드 획득
                '''
                equity = DataUtils.convert_to_decimal(self.broker.get_cash())

                '''
                진입한 수량이 전혀 없을 경우에는 risks를 사용하여 진입 시드를 결정한다.
                '''
                if current_position == 0:
                    for j in range(0, len(prices)):
                        qty = self.p.leverage * equity * self.p.risks[j] / Decimal('100') / prices[j]
                        if qty > 0:
                            self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(prices[j]), size=float(qty))
                '''
                진입한 수량이 존재할 경우에는 addRisks를 사용하여 진입 시드를 결정한다.
                또한, 종료 주문(평단가 대비 +0.5% 위치)을 걸어두는 로직도 추가된다.
                '''
                if current_position > 0:
                    '''
                    평단가 획득 및 종료 가격을 계산하고 종료 주문을 넣는다.
                    '''
                    avg_price = self.getposition(self.pairs[i]).price
                    target_price = DataUtils.convert_to_decimal(avg_price) * self.p.exitPercent[name]
                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(target_price), size=current_position)

                    for j in range(0, len(prices)):
                        if prices[j] <= Decimal('0'):
                            continue
                        qty = self.p.leverage * equity * self.p.addRisks[j] / Decimal('100') / prices[j]
                        if qty > 0:
                            self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(prices[j]), size=float(qty))

        except:
            raise

if __name__ == '__main__':
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)  # 초기 시드 설정
    cerebro.broker.setcommission(0.0002, leverage=10)  # 수수료 설정
    cerebro.addstrategy(MultiAtrConstantStrategy)
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

    print(f'strat.my_assets type :{type(strat.my_assets)}')
    asset_list = pd.DataFrame({'asset': strat.my_assets}, index=pd.to_datetime(strat.date_value))
    order_balance_list = strat.order_balance_list

    mdd = qs.stats.max_drawdown(asset_list).iloc[0]
    print(f" quanstats's my variable MDD : {mdd * 100:.2f} %")
    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")

    # file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"
    file_name = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"

    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "MultiAtrConstantV1"

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