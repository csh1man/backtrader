import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal
from indicator.Indicators import Indicator
from datetime import datetime

pairs = {
    'BTCUSDT': DataUtil.CANDLE_TICK_30M,
    'XRPUSDT': DataUtil.CANDLE_TICK_30M
}


'''
 1. BTC BB 값 : 정상
 2. BTC 캔들과 리플 캔들 시간 동기화 : 정상
 3. 지표값 ATR : 정상
 4. 지표값 RSI : 정상
 5. BTC 위치 확인 : 정상
 6. 타겟 가격 확인 : 정상
 7. 손절 가격 확인 : 정상
 8. 진입 타점 : 비정상
 219672024-05-01 16:00:00 => [매수Completed ] 종목 : XRPUSDT 	수량:45677724.0 	가격:0.4897	피라미딩 횟수:1
 219682024-05-01 19:30:00 => [매도Completed ] 종목 : XRPUSDT 	수량:-45677724.0 	가격:0.4928
 만 들어가지고, 17:00:00에 진입이 안되고있음.
'''
class RsiWithStopPriceWithBTCV2(bt.Strategy):
    params = dict(
        bb_span=100,
        bb_mult=1.0,
        atr_length={
            'BTCUSDT':10,
            'XRPUSDT':10,
        },
        atr_constant={
            'BTCUSDT':Decimal('2.0'),
            'XRPUSDT':Decimal('2.0'),
        },
        bullish_percent={
            'XRPUSDT': Decimal('2'),
        },
        bearish_percent={
            'XRPUSDT': Decimal('2'),
        },
        default_percent={
            'XRPUSDT': Decimal('4'),
        },
        tick_size={
            'XRPUSDT': Decimal('0.0001')
        },
        step_size={
            'XRPUSDT': Decimal('1')
        },
        rsi_length=2,
        rsi_high=80,
        pyramiding=3,
        risk=Decimal('1'),
    )

    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        '''
        피라미딩 횟수 초기화
        '''
        self.pairs_pyramiding = {
            'XRPUSDT': 0
        }

        '''
        손절가격 초기화
        '''
        self.pairs_stop_price = {
            'XRPUSDT': Decimal('-1')
        }

        '''
        비트코인 정보 초기화
        '''
        self.btc = self.datas[0]
        self.btc_open = self.datas[0].open
        self.btc_high = self.datas[0].high
        self.btc_low = self.datas[0].low
        self.btc_close = self.datas[0].close
        self.btc_date = self.datas[0].datetime

        self.btc_bb = bt.indicators.BollingerBands(self.btc.close, period=self.p.bb_span, devfactor=self.p.bb_mult)
        self.btc_bb_top = self.btc_bb.lines.top
        self.btc_bb_mid = self.btc_bb.lines.mid
        self.btc_bb_bot = self.btc_bb.lines.bot

        '''
        페어 전체 정보 초기화
        '''
        self.names = []
        self.pairs = []
        self.pairs_open = []
        self.pairs_high = []
        self.pairs_low = []
        self.pairs_close = []
        self.pairs_date = []
        self.pairs_atr = []
        self.pairs_rsi = []

        for i in range(0, len(self.datas)):
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])
            self.pairs_open.append(self.datas[i].open)
            self.pairs_high.append(self.datas[i].high)
            self.pairs_low.append(self.datas[i].low)
            self.pairs_close.append(self.datas[i].close)
            self.pairs_date.append(self.datas[i].datetime)

            # RSI 지표 초기화
            rsi = bt.ind.RSI_Safe(self.pairs_close[i], period=self.p.rsi_length)
            self.pairs_rsi.append(rsi)

            # ATR 지표 초기화
            tr = bt.indicators.TrueRange(self.pairs[i])
            atr = bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length[self.names[i]])
            self.pairs_atr.append(atr)

        '''
        자산 추적용 변수 초기화
        '''
        # 자산 추적용 변수 할당
        self.order = None
        self.date_value = []
        self.my_assets = []

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
        self.order_balance_list.append([self.pairs_date[0].datetime(0), account_value])
        self.date_value.append(self.pairs_date[0].datetime(0))
        position_value = self.broker.getvalue()
        for i in range(1, len(self.datas)):
            position_value += self.getposition(self.datas[i]).size * self.pairs_low[i][0]

        self.my_assets.append(position_value)

    def notify_order(self, order):
        cur_date = f"{order.data.datetime.date(0)} {str(order.data.datetime.time(0)).split('.')[0]}"
        if order.status in [order.Completed]:
            if order.isbuy():
                self.pairs_pyramiding[order.data._name] += 1
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매수{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}\t'
                         f'피라미딩 횟수:{self.pairs_pyramiding[order.data._name]}')
            elif order.issell():
                self.log(f'{order.ref:<3}{cur_date} =>'
                         f' [매도{order.Status[order.status]:^10}] 종목 : {order.data._name} \t'
                         f'수량:{order.size} \t'
                         f'가격:{order.created.price:.4f}\n')
                self.pairs_pyramiding[order.data._name] = 0
                self.pairs_stop_price[order.data._name] = Decimal('-1')
                # buy와 Sell이 한 쌍이므로 팔렸을 때 한 건으로 친다.
                self.total_trading_count += 1
                # 팔렸을 때 만약 이익이 0보다 크면 승리한 거래 건이므로 승리 횟수를 증가시킨다.
                if order.executed.pnl > 0:
                    self.winning_trading_count += 1

    def next(self):
        # 비트코인을 뺀 나머지 페어들에 대해서 스캔 시작
        for i in range(1, len(self.pairs)):
            name = self.names[i]
            self.record_asset()
            self.cancel_all()

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size > 0:
                # 종료 조건 만족 시 모두 종료
                if self.pairs_rsi[i][0] > self.p.rsi_high:
                    self.order = self.sell(data=self.pairs[i], size=current_position_size)
                # 손절라인보다 낮아졌을 경우 모두 종료
                elif DataUtil.convert_to_decimal(self.pairs_close[i][0]) < self.pairs_stop_price[name]:
                    self.order = self.sell(data=self.pairs[i], size=current_position_size)
            situation = ""
            price = 0
            # case.1 btc 종가가 btc bb 상한선보다 위에있을 때
            if self.btc_close[0] >= self.btc_bb_top[0]:
                situation = "bullish"
                price = DataUtil.convert_to_decimal(self.pairs_close[i][0]) * \
                        (Decimal('1') - self.p.bullish_percent[name] / Decimal('100'))
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
            # case.2 btc 종가가 btc bb 하한선, 상한선 사이에 있을 때
            elif self.btc_bb_bot[0] <= self.btc_close[0] < self.btc_bb_top[0]:
                situation = "default"
                price = DataUtil.convert_to_decimal(self.pairs_close[i][0]) * \
                        (Decimal('1') - self.p.default_percent[name] / Decimal('100'))
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]
            # case.3 btc종가가 btc bb 하한선 보다 밑에 있을 때
            elif self.btc_close[0] < self.btc_bb_bot[0]:
                situation = "bearish"
                price = DataUtil.convert_to_decimal(self.pairs_close[i][0]) * \
                        (Decimal('1') - self.p.bearish_percent[name] / Decimal('100'))
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]

            stop_price = DataUtil.convert_to_decimal(price) \
                         - DataUtil.convert_to_decimal(self.pairs_atr[i][0]) * self.p.atr_constant[name]
            stop_price = int(stop_price / self.p.tick_size[name]) * self.p.tick_size[name]

            portion = self.p.risk / Decimal('100')
            portion = portion / (price - stop_price)
            qty = DataUtil.convert_to_decimal(self.broker.get_cash()) * portion
            qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]
            # self.log(f'{self.pairs_date[i].datetime(0)} => {price}, pyramiding : {self.pairs_pyramiding[name]}')
            if self.pairs_pyramiding[name] < self.p.pyramiding:
                self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price), size=float(qty))

    def stop(self):
        self.log(f'총 트레이딩 수 : {self.total_trading_count}')
        self.return_rate = Indicator.get_percent(self.initial_asset, self.broker.getcash())
        self.log(f"수익률 : {self.return_rate}%")


if __name__ == '__main__':
    data_path = "/Users/tjgus/Desktop/project/krtrade/backData"

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000000)
    cerebro.broker.setcommission(0.0002, leverage=100)
    cerebro.addstrategy(RsiWithStopPriceWithBTCV2)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석기 추가

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, DataUtil.COMPANY_BYBIT, pair, tick_kind)
        # df = DataUtil.get_candle_data_in_scape(df, '2022-12-31 00:00:00', '2024-05-18 23:00:00')
        # df = DataUtil.get_candle_data_in_scape(df, '2024-04-28 00:00:00', '2024-05-18 23:00:00')
        data = bt.feeds.PandasData(dataname=df, datetime='datetime')
        cerebro.adddata(data, name=pair)

    print('Init Portfolio Value: %.2f' % cerebro.broker.getvalue())

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

    file_name = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/"

    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
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