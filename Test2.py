import backtrader as bt
import pandas as pd
import quantstats as qs
import math

class MaStrategy(bt.Strategy):
    params = (
        ("ma_length", 60),
        ("risk_per_trade", 10)
    )

    def log(self, txt):
        print(txt)

    def __init__(self):
        # 캔들 정보 설정
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.volume = self.datas[0].volume
        self.date = self.datas[0].datetime

        # 지표 정보 설정
        self.ma = bt.indicators.SimpleMovingAverage(self.close, period=self.params.ma_length)

        # 주문 추적용 객체 초기화
        self.position_size = 0

    def next(self):
        self.log(self.date.datetime(0))
        if not self.position:
            if self.close[-1] < self.ma[-1] and self.close[0] > self.ma[0]:
                equity = self.broker.getvalue()
                position_size = equity * self.params.risk_per_trade / 100 / self.close[0]
                position_size = math.floor(position_size)
                self.buy(size=position_size)

        size = self.getposition(self.datas[0]).size
        if size > 0:
            if self.close[-1] > self.ma[-1] and self.close[0] < self.ma[0]:
                self.close()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcommission(commission=0.02)
    cerebro.broker.setcash(1000)
    # 백테스팅 데이터 설정
    df = pd.read_csv('sample/linkusdt_30m.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    # 시작 날짜와 종료 날짜 설정
    start_date = pd.to_datetime('2022-12-30 18:30:00')
    end_date = pd.to_datetime('2023-12-01 00:00:00')

    # 시작 날짜와 종료 날짜 사이의 데이터만 필터링
    filtered_df = df[(df['datetime'] >= start_date) & (df['datetime'] < end_date)]

    data = bt.feeds.PandasData(dataname=filtered_df, datetime='datetime')

    cerebro.adddata(data)  # 데이터 피드 추가
    cerebro.addstrategy(MaStrategy)  # 전략 추가
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')  # 결과 분석 추가

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run()
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')

    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)

    # 간단한 결과 출력
    print(f'\n')
    print("Result:")
    cagr = qs.stats.cagr(returns)
    mdd = qs.stats.max_drawdown(returns)
    sharpe = qs.stats.sharpe(returns)
    print(f"SHARPE: {sharpe:.2f}")
    print(f"CAGR: {cagr * 100:.2f} %")
    print(f"MDD : {mdd * 100:.2f} %")

    # 자세한 결과 html 파일로 저장
    benchmark_data = pd.Series(data=cerebro.datas[0].close.plot(), index=returns.index)
    qs.reports.html(returns, benchmark=benchmark_data, output=f'sample/SMA_MSFT.html', title='result')
