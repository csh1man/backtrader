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

exchange = DataUtil.BYBIT
leverage = 10

common = Common(config_file_path)
download = Download(config_file_path, download_dir_path)

pairs = {
    'BTCUSDT': DataUtils.CANDLE_TICK_1DAY,
}

class JanusCompareStrategy(bt.Strategy):
    params= dict(
        percents=[Decimal('3.0'), Decimal('5.0')],
        tick_size={
            'BTCUSDT': common.fetch_tick_size(exchange, 'BTCUSDT'),
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

    def next(self):
        for i in range(0, len(self.pairs)):
            name = self.names[i]
            tick_size = self.p.tick_size[name]
            prices = []
            for j in range(0, len(self.p.percents)):
                percent = self.p.percents[j]
                price = DataUtils.convert_to_decimal(self.closes[i][0]) * (Decimal('1') - percent / Decimal('100'))
                price = int(price / tick_size) * tick_size
                prices.append(price)
            self.log(f'{self.dates[i].datetime(0)} => price1 : {prices[0]}, price2 : {prices[1]}')

            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size == 0:
                for j in range(0, len(prices)):
                    price = prices[j]
                    self.buy(exectype=bt.Order.Market, data=self.pairs[i], size=1, price=float(price))

            elif current_position_size > 0:
                self.sell(exectype=bt.Order.Market, data=self.pairs[i], size=current_position_size)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(JanusCompareStrategy)

    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0, leverage=1)
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

    mdd = qs.stats.max_drawdown(returns)
    print(f" quanstats's my returns MDD : {mdd * 100:.2f} %")


