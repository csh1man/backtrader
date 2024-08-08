import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal
from datetime import datetime

pairs={
    'BTCUSDT' : DataUtil.CANDLE_TICK_30M,
    'BONDUSDT' : DataUtil.CANDLE_TICK_30M,
    'BAKEUSDT': DataUtil.CANDLE_TICK_30M,
    '1000BONKUSDT': DataUtil.CANDLE_TICK_30M
}


class MultiAtrDcaWithBtcV1(bt.Strategy):
    params = dict(
        leverage=Decimal('10'),
        bb_length=50,
        bb_mult=1.0,
        atr_length=100,
        atr_avg_length=100,
        rsi_length=2,
        rsi_low=10,
        init_risks=[Decimal('1'), Decimal('1'), Decimal('1'), Decimal('1'), Decimal('1')],
        add_risks=[Decimal('2'), Decimal('2'), Decimal('2'), Decimal('2'), Decimal('2')],
        target_percent=Decimal('0.4'),
        add_target_percent=Decimal('0.6'),
        bull_constants={
            '1000BONKUSDT' : [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')],
            'STORJUSDT': [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')],
            'BAKEUSDT': [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')],
            'BONDUSDT': [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')]
        },
        def_constants={
            '1000BONKUSDT': [Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('6.0')],
            'STORJUSDT': [Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('6.0')],
            'BAKEUSDT': [Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('6.0')],
            'BONDUSDT': [Decimal('2.0'), Decimal('3.0'), Decimal('4.0'), Decimal('5.0'), Decimal('6.0')]
        },
        bear_constants={
            '1000BONKUSDT' : [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')],
            'STORJUSDT': [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')],
            'BAKEUSDT': [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')],
            'BONDUSDT': [Decimal('1.0'), Decimal('1.2'), Decimal('1.5'), Decimal('1.8'), Decimal('2.0')]
        },
        tick_size={
            '1000BONKUSDT': Decimal('0.0000010'),
            'STORJUSDT': Decimal('0.0001'),
            'BAKEUSDT': Decimal('0.0001'),
            'BONDUSDT': Decimal('0.001')
        },
        step_size={
            '1000BONKUSDT': Decimal('100'),
            'STORJUSDT': Decimal('0.1'),
            'BAKEUSDT': Decimal('0.1'),
            'BONDUSDT': Decimal('0.1')
        }
    )

    def log(self, txt=None):
        print(f'{txt}')

    def __init__(self):
        # 캔들 정보 기본 변수 추가
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.atrs = []
        self.rsis = []
        self.bb = []
        self.bb_top=[]
        self.bb_mid=[]
        self.bb_bot=[]

        # 자산 추정용 변수 추가
        self.order = None
        self.date_value = []
        self.my_assets = []
        self.order_balance_list = []
        self.initial_asset = self.broker.getvalue()
        self.return_rate = 0
        self.total_trading_count = 0
        self.winning_trading_count = 0
        self.winning_rate = 0

        # 캔들 기본 정보 셋팅
        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)
        
        # ATR 정보 셋팅
        for i in range(0, len(self.pairs)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.SmoothedMovingAverage(tr, period=self.p.atr_length)
            atr = bt.indicators.MovingAverageSimple(atr, period=self.p.atr_avg_length)
            self.atrs.append(atr)

        # RSI 정보 셋팅
        for i in range(0, len(self.pairs)):
            rsi = bt.ind.RSI_Safe(self.closes[i], period=self.p.rsi_length)
            self.rsis.append(rsi)

        # 비트코인 볼린저밴드 정보 셋팅
        self.bb = bt.indicators.BollingerBands(self.closes[0], period=self.p.bb_length, devfactor=self.p.bb_mult)
        self.bb_top = self.bb.lines.top
        self.bb_mid = self.bb.lines.mid
        self.bb_bot = self.bb.lines.bot

    """
    모든 미체결 주문 취소
    """
    def cancel_all(self):
        for order in self.broker.get_orders_open():
            self.broker.cancel(order)

    """
    자산 정보 기록 
    """
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
    
    """
    주문 체결 정보 출력
    """
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

    """
    실제 수행 함수 
    """
    def next(self):
        self.cancel_all()
        self.record_asset()

        comparison_date = datetime(2024, 7, 1, 0, 0, 0)
        for i in range(1, len(self.pairs)):
            name = self.names[i]

            # 설정한 날짜보다 이전이면 테스트에서 제외시킨다.
            current_date = self.dates[i].datetime(0)
            if current_date < comparison_date:
                continue
            
            # 상황에 맞는 곱셈 상수 배열 설정
            constants = []
            if self.closes[0][0] > self.bb_top[0] or self.closes[0][0] < self.bb_bot[0]:
                constants = self.p.bear_constants[self.names[i]]

            elif self.bb_mid[0] < self.closes[0][0] < self.bb_top[0]:
                constants = self.p.bull_constants[self.names[i]]

            elif self.bb_bot[0] < self.closes[0][0] < self.bb_mid[0]:
                constants = self.p.def_constants[self.names[i]]

            # 지정가 주문에 사용할 가격 계산
            prices = []
            for j in range(0, len(constants)):
                price = DataUtil.convert_to_decimal(self.closes[i][0]) - DataUtil.convert_to_decimal(self.atrs[i][0]) * constants[j]
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
                prices.append(price)


            # 최초진입 여부에 따라서 리스크 사이즈 설정
            entry_position_size = self.getposition(self.pairs[i]).size
            risks = []
            if entry_position_size == 0:
                risks = self.p.init_risks
            elif entry_position_size > 0:
                risks = self.p.add_risks

            equity = DataUtil.convert_to_decimal(self.broker.getcash())
            for j in range(0, len(prices)):
                if prices[j] == Decimal('0'):
                    continue
                qty = self.p.leverage * equity * risks[j] / Decimal(100) / prices[j]
                self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(prices[j]),
                                      size=float(qty))

            if entry_position_size > 0:
                target_percent = self.p.target_percent
                if self.rsis[i][0] < self.p.rsi_low:
                    target_percent += self.p.add_target_percent

                target_price = DataUtil.convert_to_decimal(self.getposition(self.pairs[i]).price) * (Decimal('1') + target_percent / Decimal('100'))
                target_price = int(target_price / self.p.tick_size[name]) * self.p.tick_size[name]
                self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], size=self.getposition(self.pairs[i]).size, price=float(target_price))

if __name__ == '__main__':
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MultiAtrDcaWithBtcV1)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002, leverage=10)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    # data loading
    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')

        cerebro.adddata(data, name=pair)

    print('Before Portfolio Value: %.2f' % cerebro.broker.getvalue())
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
    file_name += "multiAtrDcaWithBtcV1"

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