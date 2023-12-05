import backtrader as bt
import yfinance as yf

# create strategy
class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s', (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.log('Close, %.2f' % self.dataclose[0])


if __name__ == '__main__':
    #cerebro 인스턴스 초기화
    cerebro = bt.Cerebro()

    # cerebro에 전략 셋팅
    cerebro.addstrategy(TestStrategy)

    # 백테스팅할 데이터 설정
    data = bt.feeds.PandasData(dataname=yf.download('036570.KS', '2018-01-01', '2021-12-01'))
    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value : %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value : %.2f' % cerebro.broker.getvalue())
