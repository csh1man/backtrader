import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtils
from api.ApiUtil import DataUtil
from api.Api import Common, Download
from decimal import Decimal

config_file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
# config_file_path = "C:/Users/user/Desktop/개인자료/콤트/config/config.json"

download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
# download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
# download_dir_path = "/Users/tjgus/Desktop/project/krtrade/backData"

result_file_path = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
# result_file_path = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/"

result_file_prefix = "BinanceCopyTradingV1"

pairs = {
    '1000PEPEUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'ONDOUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'SUIUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'SEIUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'FETUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'JASMYUSDT': DataUtils.CANDLE_TICK_1HOUR,
    '1000SHIBUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'PYTHUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'HBARUSDT': DataUtils.CANDLE_TICK_1HOUR,
    'LDOUSDT': DataUtils.CANDLE_TICK_1HOUR,
}

exchange = DataUtil.BINANCE
leverage = 10

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)


class BinanceCopyTradingV1(bt.Strategy):
    params = dict(
        risks=[Decimal('0.5'), Decimal('1.0'), Decimal('2.0'), Decimal('4.0'), Decimal('4.0'), Decimal('8.0'), Decimal('8.0'), Decimal('16.0')],
        percents=[Decimal('2'), Decimal('3.0'), Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('12.0'), Decimal('14.0'), Decimal('16.0')],
        exit_percent=Decimal('1.0'),
        ma_length=[3, 5, 7],
        rsi_length=3,
        rsi_limit=40,
        atr_length=[3, 20],
        tick_size={
            '1000PEPEUSDT': common.fetch_tick_size(exchange, '1000PEPEUSDT'),
            'ONDOUSDT': common.fetch_tick_size(exchange, 'ONDOUSDT'),
            'SUIUSDT': common.fetch_tick_size(exchange, 'SUIUSDT'),
            'SEIUSDT': common.fetch_tick_size(exchange, 'SEIUSDT'),
            'FETUSDT': common.fetch_tick_size(exchange, 'FETUSDT'),
            '1000SHIBUSDT': common.fetch_tick_size(exchange, '1000SHIBUSDT'),
            'JASMYUSDT': common.fetch_tick_size(exchange, 'JASMYUSDT'),
            'PYTHUSDT': common.fetch_tick_size(exchange, 'PYTHUSDT'),
            'HBARUSDT': common.fetch_tick_size(exchange, 'HBARUSDT'),
            'LDOUSDT': common.fetch_tick_size(exchange, 'LDOUSDT'),
        },
        step_size={
            '1000PEPEUSDT': common.fetch_step_size(exchange, "1000PEPEUSDT"),
            'ONDOUSDT': common.fetch_step_size(exchange, "ONDOUSDT"),
            'SUIUSDT': common.fetch_step_size(exchange, "SUIUSDT"),
            'SEIUSDT': common.fetch_step_size(exchange, "SEIUSDT"),
            'FETUSDT': common.fetch_step_size(exchange, "FETUSDT"),
            '1000SHIBUSDT': common.fetch_step_size(exchange, "1000SHIBUSDT"),
            'JASMYUSDT': common.fetch_step_size(exchange, "JASMYUSDT"),
            'PYTHUSDT': common.fetch_step_size(exchange, "PYTHUSDT"),
            'HBARUSDT': common.fetch_step_size(exchange, "HBARUSDT"),
            'LDOUSDT': common.fetch_step_size(exchange, "LDOUSDT"),
        }
    )

    def log(self, txt):
        print(f'{txt}')

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []

        # RSI 변수 설정
        self.rsi = []

        # 이평선 변수 설정
        self.ma1 = []
        self.ma2 = []
        self.ma3 = []

        self.atr1 = []
        self.atr2 = []

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
            self.names.append(self.datas[i]._name)
            self.pairs.append(self.datas[i])

            self.opens.append(self.datas[i].open)
            self.highs.append(self.datas[i].high)
            self.lows.append(self.datas[i].low)
            self.closes.append(self.datas[i].close)
            self.dates.append(self.datas[i].datetime)

        for i in range(0, len(self.pairs)):
            name = self.names[i]

            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length)
            self.rsi.append(rsi)


            ma1 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[0])
            self.ma1.append(ma1)

            ma2 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[1])
            self.ma2.append(ma2)

            ma3 = bt.indicators.ExponentialMovingAverage(self.closes[i], period=self.p.ma_length[2])
            self.ma3.append(ma3)

            atr1 = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[0])
            self.atr1.append(atr1)

            atr2 = bt.indicators.AverageTrueRange(self.pairs[i], period=self.p.atr_length[1])
            self.atr2.append(atr2)

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

    def stop(self):
        self.log(f'전체 트레이딩 횟수 : {self.total_trading_count}')

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
            self.cancel_all(target_name=name)

        equity = DataUtils.convert_to_decimal(self.broker.getvalue())
        for i in range(0, len(self.pairs)):
            name = self.names[i]

            tick_size = self.p.tick_size[name]
            step_size = self.p.step_size[name]

            atr = int(DataUtils.convert_to_decimal(self.atr1[i][0]) / tick_size) * tick_size
            avg_atr = int(DataUtils.convert_to_decimal(self.atr2[i][0]) / tick_size) * tick_size

            vol_factor = int((atr / avg_atr) / tick_size) * tick_size

            for j in range(0, len(self.p.percents)):
                percent = self.p.percents[j]
                price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1') - percent / Decimal('100'))
                price = int(price / tick_size) * tick_size

                risk = self.p.risks[j]
                risk = risk * vol_factor

                qty = (equity * risk / Decimal('100')) / price
                qty = int(qty / step_size) * step_size
                if qty > 0:
                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty),
                                          price=float(price))

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size > 0:
                position_avg_price = DataUtils.convert_to_decimal(self.getposition(self.pairs[i]).price)
                exit_price = position_avg_price * (Decimal('1') + self.p.exit_percent / Decimal('100'))
                exit_price = int(exit_price / tick_size) * tick_size
                if self.closes[i] < self.ma1[i][0]:
                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i],
                                           size=float(current_position_size), price=float(exit_price))
                elif self.rsi[i][0] < self.p.rsi_limit:
                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i],
                                           size=float(current_position_size), price=float(exit_price))


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BinanceCopyTradingV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.001, leverage=leverage)
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

    file_name = result_file_path + exchange + "-" + result_file_prefix + "-"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"

    strat = results[0]
    order_balance_list = strat.order_balance_list
    df = pd.DataFrame(order_balance_list, columns=["date", "value"])
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    df = df.drop_duplicates('date', keep='last').sort_index()  # 각 날짜에 대해서 마지막 시간에 대한 값을 그날의 값으로 설정
    # df = df.sort_values('value', ascending=True).drop_duplicates('date', keep='last').sort_index()
    df['value'] = df['value'].astype('float64')
    # df['value'] = df['value'].pct_change()
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna()
    df = df.set_index('date')
    df.index.name = 'date'
    df.to_csv(f'{file_name}.csv')
    qs.reports.html(df['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)

    # returns = returns[returns.index >= '2021-11-01']
    returns.index.name = 'date'
    returns.name = 'value'
    # returns['date'] = returns['date'].dt.date

    returns.to_csv(f'{file_name}_close.csv')
    qs.reports.html(returns, output=f'{file_name}_종가 중심.html', title='result')