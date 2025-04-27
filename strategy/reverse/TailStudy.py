import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from api.Api import Common, Download
from decimal import Decimal

# config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"

# download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
# download_dir_path = "/Users/tjgus/Desktop/project/krtrade/backData"

# result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"

result_file_prefix = "TailStudy"

pairs={
    '1000PEPEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'XRPUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'DOGEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'SNXUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'ONDOUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'SUIUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # '1000SHIBUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'ALGOUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'QTUMUSDT': DataUtils.CANDLE_TICK_1HOUR,
}

exchange = DataUtil.BINANCE
leverage=4

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)

class TailStudy(bt.Strategy):
    params=dict(
        log=True,
        atr_length=10,
        ma_lengths=[5, 10],
        percents={
          '1000SHIBUSDT': {
            'type1': [Decimal(2.0), Decimal(3.0), Decimal(5.0), Decimal(10), Decimal(15), Decimal(20)], # 상승장이면서 변동폭 작은 경우
            'type2': [Decimal(2.0), Decimal(4.0), Decimal(6.0), Decimal(12), Decimal(15), Decimal(20)], # 상승장이면서 변동폭 큰 경우
            'type3': [Decimal(3.0), Decimal(5.0), Decimal(8.0), Decimal(15), Decimal(20), Decimal(25)], # 하락장이면서 변동폭 작은 경우
            'type4': [Decimal(4.0), Decimal(5.0), Decimal(8.0), Decimal(15), Decimal(20), Decimal(25)], # 하락장이면서 변동폭 큰 경우
          },
            '1000PEPEUSDT': {
            'type1': [Decimal(2.0), Decimal(3.0), Decimal(5.0), Decimal(10), Decimal(15), Decimal(20)], # 상승장이면서 변동폭 작은 경우
            'type2': [Decimal(2.0), Decimal(4.0), Decimal(6.0), Decimal(12), Decimal(15), Decimal(20)], # 상승장이면서 변동폭 큰 경우
            'type3': [Decimal(3.0), Decimal(5.0), Decimal(8.0), Decimal(15), Decimal(20), Decimal(25)], # 하락장이면서 변동폭 작은 경우
            'type4': [Decimal(4.0), Decimal(5.0), Decimal(8.0), Decimal(15), Decimal(20), Decimal(25)], # 하락장이면서 변동폭 큰 경우
          }
        },
        risks=[Decimal(0.5), Decimal(1), Decimal(2), Decimal(4), Decimal(8), Decimal(16)],
        rsi_length=3,
        rsi_limit=40,
        exit_percent=Decimal(0.5),
        tick_size={
            'XRPUSDT': common.fetch_tick_size(exchange, 'XRPUSDT'),
            'DOGEUSDT': common.fetch_tick_size(exchange, 'DOGEUSDT'),
            '1000SHIBUSDT': common.fetch_tick_size(exchange, '1000SHIBUSDT'),
            '1000PEPEUSDT': common.fetch_tick_size(exchange, '1000PEPEUSDT'),
        },
        step_size={
            'XRPUSDT': common.fetch_step_size(exchange, 'XRPUSDT'),
            'DOGEUSDT': common.fetch_step_size(exchange, 'DOGEUSDT'),
            '1000SHIBUSDT': common.fetch_step_size(exchange, '1000SHIBUSDT'),
            '1000PEPEUSDT': common.fetch_step_size(exchange, '1000PEPEUSDT'),
        }
    )
    def log(self, txt):
        if self.p.log:
            print(f'{txt}')

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.tr = []
        self.atr = []
        self.rsi = []
        self.ma1 = []
        self.ma2 = []

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
        self.percent1 = [[0 for _ in range(50)] for _ in range(3)]
        self.percent2 = [[0 for _ in range(50)] for _ in range(3)]
        self.percent3 = [[0 for _ in range(50)] for _ in range(3)]
        self.percent4 = [[0 for _ in range(50)] for _ in range(3)]

        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            tr = bt.indicators.TrueRange(self.pairs[i])
            self.tr.append(tr)

            atr = bt.indicators.MovingAverageSimple(tr, period=self.p.atr_length)
            self.atr.append(atr)

            ma1 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_lengths[0])
            ma2 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_lengths[1])

            self.ma1.append(ma1)
            self.ma2.append(ma2)

            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length)
            self.rsi.append(rsi)

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
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            percents = self.p.percents[name]['type1']
            # 상승장인데 변동성은 작을 경우
            if self.tr[i][-1] < self.atr[i][-1] and self.ma1[i][-1] >= self.ma2[i][-1]:
                percents = self.p.percents[name]['type1']
            # 상승장인데 변동성은 클 경우
            elif self.tr[i][-1] >= self.atr[i][-1] and self.ma1[i][-1] >= self.ma2[i][-1]:
                percents = self.p.percents[name]['type2']
            # 하락장인데 변동성은 작을 경우 
            elif self.tr[i][-1] < self.atr[i][-1] and self.ma1[i][-1] < self.ma2[i][-1]:
                percents = self.p.percents[name]['type3']
            # 하락장인데 변동성도 클 경우
            elif self.tr[i][-1] >= self.atr[i][-1] and self.ma1[i][-1] < self.ma2[i][-1]:
                percents = self.p.percents[name]['type4']

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size > 0:
                if self.rsi[i][0] < self.p.rsi_limit:
                    exit_price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal(1) + self.p.exit_percent / Decimal('100'))
                    exit_price = int(exit_price / self.p.tick_size[name]) * self.p.tick_size[name]

                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], price=float(exit_price), size=current_position_size)

            equity = DataUtils.convert_to_decimal(self.broker.getvalue())
            for j in range(0, len(self.p.risks)):
                risk = self.p.risks[j]
                percent = percents[j]

                price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal(1) - percent / Decimal(100))
                price = int(price / self.p.tick_size[name]) * self.p.tick_size[name]

                qty = equity * risk / Decimal(100) / price
                qty = int(qty / self.p.step_size[name]) * self.p.step_size[name]

                cash = DataUtils.convert_to_decimal(self.broker.get_cash())
                margin = qty * price / Decimal(leverage)

                if cash > margin:
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], price=float(price),
                                          size=float(qty))

    # def stop(self):
    #     for i in range(0, len(self.pairs)):
    #         self.log(f'변동폭은 크면서 상승장인 경우')
    #         for j in range(0, len(self.percent1[i])):
    #             if self.percent1[i][j] > 0:
    #                 self.log(f'[{j} => {self.percent1[i][j]}')
    #
    #         self.log(f'변동폭은 크면서 하락장인 경우')
    #         for j in range(0, len(self.percent2[i])):
    #             if self.percent2[i][j] > 0:
    #                 self.log(f'[{j} => {self.percent2[i][j]}')
    #
    #         self.log(f'변동폭은 작으면서 상승장인 경우')
    #         for j in range(0, len(self.percent3[i])):
    #             if self.percent3[i][j] > 0:
    #                 self.log(f'[{j} => {self.percent3[i][j]}')
    #
    #         self.log(f'변동폭은 작으면서 하락장 경우')
    #         for j in range(0, len(self.percent4[i])):
    #             if self.percent4[i][j] > 0:
    #                 self.log(f'[{j} => {self.percent4[i][j]}')

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TailStudy)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.001, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        download.download_candles(exchange, pair, tick_kind)
        df = DataUtils.load_candle_data_as_df(download_dir_path, DataUtils.COMPANY_BINANCE, pair, tick_kind)
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

    file_name = result_file_path + result_file_prefix
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"


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