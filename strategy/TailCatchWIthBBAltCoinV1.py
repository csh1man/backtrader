import backtrader as bt
import pandas as pd
import quantstats as qs
from util.Util import DataUtil
from decimal import Decimal

pairs = {
    '1000PEPEUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'SUIUSDT': DataUtil.CANDLE_TICK_1HOUR,
    # '1000BONKUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'XRPUSDT': DataUtil.CANDLE_TICK_1HOUR,
    'DOGEUSDT': DataUtil.CANDLE_TICK_1HOUR,
}

company = DataUtil.COMPANY_BINANCE
leverage=3

class TailCatchWithBBAltCoinV1(bt.Strategy):
    params=dict(
        log=True,
        risk={
            '1000PEPEUSDT': [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')],
            'SUIUSDT': [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')],
            '1000BONKUSDT': [Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')],
            'XRPUSDT': [Decimal('0.1'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')],
            'DOGEUSDT': [Decimal('0.1'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4'), Decimal('8'), Decimal('16')],
        },
        rsi_length={
            '1000PEPEUSDT': 3,
            'SUIUSDT': 3,
            '1000BONKUSDT': 3,
            'XRPUSDT': 3,
            'DOGEUSDT': 3
        },
        rsi_limit={
            '1000PEPEUSDT': 70,
            'SUIUSDT': 70,
            '1000BONKUSDT': 70,
            'XRPUSDT': 70,
            'DOGEUSDT': 70
        },
        bb_length={
            '1000PEPEUSDT': 30,
            'SUIUSDT': 30,
            '1000BONKUSDT': 30,
            'XRPUSDT': 30,
            'DOGEUSDT': 30
        },
        bb_mult={
            '1000PEPEUSDT': 0.5,
            'SUIUSDT': 0.5,
            '1000BONKUSDT': 0.5,
            'XRPUSDT': 0.5,
            'DOGEUSDT': 0.5,
        },
        exit_percent={
            '1000PEPEUSDT': Decimal('1'),
            'SUIUSDT': Decimal('1'),
            '1000BONKUSDT': Decimal('1'),
            'XRPUSDT': Decimal('1'),
            'DOGEUSDT': Decimal('1'),
        },
        percent={
            '1000PEPEUSDT': {
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0')],
            },
            'SUIUSDT': {
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0')],
            },
            '1000BONKUSDT': {
                'bull': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12')],
                'bear': [Decimal('3.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15.0'), Decimal('20.0')],
            },
            'XRPUSDT': {
                'bull': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'),
                         Decimal('20.0'), Decimal('25.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'),
                        Decimal('25.0')],
                'bear': [Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'),
                         Decimal('25.0'), Decimal('30.0')],
            },
            'DOGEUSDT': {
                'bull': [Decimal('4.0'), Decimal('6.0'), Decimal('8.0'), Decimal('12'), Decimal('16.0'),
                         Decimal('20.0'), Decimal('25.0')],
                'def': [Decimal('2.0'), Decimal('4.0'), Decimal('6.0'), Decimal('12.0'), Decimal('15'), Decimal('20.0'),
                        Decimal('25.0')],
                'bear': [Decimal('5.0'), Decimal('7.0'), Decimal('10.0'), Decimal('15.0'), Decimal('20.0'),
                         Decimal('25.0'), Decimal('30.0')],
            },
        },
        tick_size={
            '1000PEPEUSDT': {
                DataUtil.COMPANY_BINANCE : Decimal('0.0000001'),
                DataUtil.COMPANY_BYBIT : Decimal('0.0000010')
            },
            'SUIUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('0.000100'),
                DataUtil.COMPANY_BYBIT: Decimal('0.00010')
            },
            '1000BONKUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('0.0000010'),
                DataUtil.COMPANY_BYBIT: Decimal('0.00010')
            },
            'XRPUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('0.0001'),
                DataUtil.COMPANY_BYBIT: Decimal('0.0001')
            },
            'DOGEUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('0.000010'),
                DataUtil.COMPANY_BYBIT: Decimal('0.00001')
            },
        },
        step_size={
            '1000PEPEUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('1'),
                DataUtil.COMPANY_BYBIT: Decimal('100')
            },
            'SUIUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('0.1'),
                DataUtil.COMPANY_BYBIT: Decimal('10')
            },
            '1000BONKUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('1'),
                DataUtil.COMPANY_BYBIT: Decimal('10')
            },
            'XRPUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('0.1'),
                DataUtil.COMPANY_BYBIT: Decimal('0.01')
            },
            'DOGEUSDT': {
                DataUtil.COMPANY_BINANCE: Decimal('1'),
                DataUtil.COMPANY_BYBIT: Decimal('1')
            },
        }
    )
    def log(self, txt):
        if self.p.log:
            print(f"{txt}")

    def __init__(self):
        self.names = []
        self.pairs = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.dates = []
        self.rsi = []
        self.bb_top = []
        self.bb_mid = []
        self.bb_bot = []

        self.top_percents = []
        self.mid_percents = []
        self.bot_percents = []

        self.order = None
        self.date_value = []
        self.my_assets = []

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
            rsi = bt.indicators.RSI_Safe(self.closes[i], period=self.p.rsi_length[name])
            self.rsi.append(rsi)

            bb = bt.indicators.BollingerBands(self.closes[i], period=self.p.bb_length[name], devfactor=self.p.bb_mult[name])

            self.bb_top.append(bb.lines.top)
            self.bb_mid.append(bb.lines.mid)
            self.bb_bot.append(bb.lines.bot)

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
            self.cancel_all(target_name=name)

        for i in range(0, len(self.pairs)):
            name = self.names[i]
            # self.log(f'{self.dates[i].datetime(0)}')
            current_position_size = self.getposition(self.pairs[i]).size
            if current_position_size > 0:
                if self.rsi[i][0] >= self.p.rsi_limit[name]:
                    exit_price = DataUtil.convert_to_decimal(self.closes[i][0]) * (
                                Decimal('1') + self.p.exit_percent[name] / Decimal('100'))
                    exit_price = int(exit_price / self.p.tick_size[name][company]) * self.p.tick_size[name][company]

                    self.order = self.sell(exectype=bt.Order.Limit, data=self.pairs[i], size=current_position_size,
                                           price=float(exit_price))

            date = self.dates[i].datetime(0)
            candle_percent = (self.lows[i][0]-self.opens[i][0]) * 100  / self.opens[i][0]
            if self.closes[i][-1] >= self.bb_top[i][-1]:
                self.top_percents.append((date, candle_percent))
            elif self.bb_bot[i][-1] <= self.closes[i][-1] < self.bb_top[i][-1]:
                self.mid_percents.append((date, candle_percent))
            else:
                self.bot_percents.append((date, candle_percent))

            percents = self.p.percent[name]['def']
            is_entry = True
            if self.closes[i][-1] >= self.bb_top[i][-1]:
                percents = self.p.percent[name]['bull']
            elif self.bb_bot[i][-1] <= self.closes[i][-1] < self.bb_top[i][-1]:
                percents = self.p.percent[name]['def']
            else:
                percents = self.p.percent[name]['bear']

            equity = DataUtil.convert_to_decimal(self.broker.getvalue())
            if is_entry:
                for j in range(0, len(self.p.risk[name])):
                    percent = percents[j]
                    price = DataUtil.convert_to_decimal(self.closes[i][0]) * (Decimal('1') - percent / Decimal('100'))
                    price = int(price / self.p.tick_size[name][company]) * self.p.tick_size[name][company]

                    risk = self.p.risk[name][j]
                    qty = equity * risk / Decimal('100') / price
                    qty = int(qty / self.p.step_size[name][company]) * self.p.step_size[name][company]

                    self.order = self.buy(exectype=bt.Order.Limit, data=self.pairs[i], size=float(qty), price=float(price))

    # def stop(self):
    #     sorted_top_percents = sorted(self.top_percents, key=lambda x: x[1])
    #     sorted_mid_percents = sorted(self.mid_percents, key=lambda x: x[1])
    #     sorted_bot_percents = sorted(self.bot_percents, key=lambda x: x[1])
    #     self.log(f"top percents length : [{len(sorted_top_percents)}]")
    #     for key, value in sorted_top_percents[:51]:
    #         self.log(f'{key} -> {value}%')
    #     self.log("")
    #
    #     self.log(f"mid percents length : [{len(sorted_mid_percents)}]")
    #     for key, value in sorted_mid_percents[:51]:
    #         self.log(f'{key} -> {value}%')
    #     self.log("")
    #
    #     self.log(f"bot percents length : [{len(sorted_bot_percents)}]")
    #     for key, value in sorted_bot_percents[:51]:
    #         self.log(f'{key} -> {value}%')



if __name__ == '__main__':
    # data_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    data_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # data_path = "/Users/tjgus/Desktop/project/krtrade/backData"
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TailCatchWithBBAltCoinV1)

    cerebro.broker.setcash(13000)
    cerebro.broker.setcommission(commission=0.001, leverage=leverage)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    for pair, tick_kind in pairs.items():
        df = DataUtil.load_candle_data_as_df(data_path, company, pair, tick_kind)
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

    file_name = "C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/"
    # file_name = "C:/Users/user/Desktop/개인자료/콤트/백테스트결과/" + company + "-"
    # file_name = "/Users/tjgus/Desktop/project/krtrade/backData/result/"
    for pair, tick_kind in pairs.items():
        file_name += pair + "-"
    file_name += "TailCatchWithBBAltCoinV1"

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
    # print(df['value'])
    df.to_csv(f'{file_name}.csv')
    qs.reports.html(df['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)
