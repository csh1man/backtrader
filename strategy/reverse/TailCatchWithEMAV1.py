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
# result_file_path = "/Users/tjgus/Desktop/project/krtrade/backData/result/"

result_file_prefix = "TailCatchWithEMAV1"

pairs = {
    'XRPUSDT': DataUtils.CANDLE_TICK_1HOUR,
    # 'SUIUSDT': DataUtils.CANDLE_TICK_1HOUR,
}


exchange = DataUtil.BINANCE
leverage=3

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)

class TailCatchWithEMAV1(bt.Strategy):
    params=dict(
        log=True,
        risks={
            'XRPUSDT': [Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')],
            'SUIUSDT': [Decimal('0.2'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')],
        },
        percents={
            'XRPUSDT': {
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0'), Decimal('25.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12.0'), Decimal('15.0')],
                'bear': [Decimal('4.0'), Decimal('8.0'), Decimal('16.0'), Decimal('20.0'), Decimal('25.0'), Decimal('30.0')],
            },
            'SUIUSDT': {
                'bull': [Decimal('1.5'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0')],
                'def': [Decimal('1.5'), Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0')],
                'bear': [Decimal('2.0'), Decimal('4.0'), Decimal('8.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20'), Decimal('25.0')],
            },
        },
        exit_percent={
            'XRPUSDT': Decimal('0.5'),
            'SUIUSDT': Decimal('0.2')
        },
        rsi_length={
            'XRPUSDT': 2,
            'SUIUSDT': 2,
        },
        rsi_limit={
            'XRPUSDT': 50,
            'SUIUSDT': 50,
        },
        ma_length={
            'XRPUSDT': [10, 20, 60],
            'SUIUSDT': [5, 10, 15]
        },
        bb_length={
            'XRPUSDT': 30,
            'SUIUSDT': 30,
        },
        bb_mult={
            'XRPUSDT': 0.5,
            'SUIUSDT': 0.5,
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

        self.bull_percents = []
        self.def_percents = []
        self.bear_percents = []

        self.ema1 = []
        self.ema2 = []
        self.ema3 = []

        self.top = []
        self.mid = []
        self.bot = []

        self.rsi = []

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

        for i in range(0, len(self.datas)):
            self.pairs.append(self.datas[i])
            self.names.append(self.datas[i]._name)
            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            name = self.names[i]

            ema1 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name][0])
            self.ema1.append(ema1)

            ema2 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name][1])
            self.ema2.append(ema2)

            ema3 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[name][2])
            self.ema3.append(ema3)

            bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_length[name], devfactor=self.p.bb_mult[name])
            self.top.append(bb.lines.top)
            self.mid.append(bb.lines.mid)
            self.bot.append(bb.lines.bot)

            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
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
        self.record_asset()

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            self.cancel_all(name)

        for i in range(0, len(self.pairs)):
            name = self.names[i]

            tick_size = common.fetch_tick_size(exchange, name)
            step_size = common.fetch_step_size(exchange, name)

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size > 0:
                if self.rsi[i][0] >= self.p.rsi_limit[name]:
                    exit_price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1') + self.p.exit_percent[name] / Decimal('100'))
                    exit_price = int(exit_price / tick_size) * tick_size

                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], size=current_position_size, price=float(exit_price))

            percents = self.p.percents[name]['def']
            if self.closes[i][0] >= self.top[i][0]:
                percents = self.p.percents[name]['bull']
            elif self.closes[i][0] < self.bot[i][0]:
                percents = self.p.percents[name]['bear']

            equity = DataUtils.convert_to_decimal(self.broker.getvalue())
            for j in range(0, len(self.p.risks[name])):
                percent = percents[j]
                price = DataUtils.convert_to_decimal(self.closes[i][0]) * (
                        Decimal('1') - percent / Decimal('100'))
                price = int(price / tick_size) * tick_size
                risk = self.p.risks[name][j]
                qty = equity * risk / Decimal('100') / price
                qty = int(qty / step_size) * step_size

                cash = DataUtils.convert_to_decimal(self.broker.get_cash())
                margin = qty * price / Decimal(leverage)
                if cash >= margin:
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty), price=float(price))
            # equity = DataUtils.convert_to_decimal(self.broker.getvalue())
            # for j in range(0, len(self.p.risks[name])):
            #     try:
            #         risk = self.p.risks[name][j]
            #         percent = percents[j]
            #         price = DataUtils.convert_to_decimal(self.closes[i][0]) * (
            #                     Decimal('1.0') - percent / Decimal('100'))
            #         price = int(price / tick_size) * tick_size
            #         qty = equity * risk / Decimal('100') / price
            #         qty = int(qty / step_size) * step_size
            #         self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty), price=float(price))
            #     except Exception as e:
            #         self.log(f'error occured : {e}')
            #         pass


            # candle_percent = (self.closes[i][0]-self.opens[i][0]) * 100 / self.opens[i][0]
    #         candle_percent = (self.lows[i][0] - self.closes[i][0]) * 100 / self.lows[i][0]
    #         if candle_percent < 0:
    #             if self.closes[i][-1] >= self.top[i][-1]:
    #                 self.bull_percents.append(candle_percent)
    #             elif self.closes[i][-1] < self.bot[i][-1]:
    #                 self.bear_percents.append(candle_percent)
    #             else:
    #                 self.def_percents.append(candle_percent)
    #
    # def stop(self):
    #     ranges =[]
    #     for j in range(0, 100):
    #         ranges.append(0)
    #
    #     for j in range(0, len(self.bear_percents)):
    #         percent = int(abs(self.bear_percents[j]))
    #         ranges[percent] += 1
    #
    #     for j in range(0, len(ranges)):
    #         if ranges[j] > 0:
    #             print(f'[{j}] => {ranges[j]}개')
    #
    #     bear_percents = sorted(self.bear_percents)
    #     for j in range(0, 10):
    #         print(bear_percents[j])

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TailCatchWithEMAV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.003, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        download.download_candles(exchange, pair, tick_kind)
        df = DataUtils.load_candle_data_as_df(download_dir_path, exchange, pair, tick_kind)
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
    df.to_csv(f'{file_name}.csv')
    qs.reports.html(df['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)

    returns = returns[returns.index >= '2021-11-01']
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')


