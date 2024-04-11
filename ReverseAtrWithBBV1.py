from indicator.Indicators import Indicator
import backtrader as bt
import backtrader.indicators as btind
import pandas as pd
import quantstats as qs
from util.Util import DataUtil

if __name__ == '__main__':
    # 백테스팅용 데이터 디렉토리 결로 설정
    dir_path = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    # 페어 설정
    currency = "DOGEUSDT"

    # 페어 데이터 로딩
    df = DataUtil.load_candle_data_as_df(dir_path, DataUtil.COMPANY_BYBIT, currency, DataUtil.CANDLE_TICK_1HOUR)
    
    # 특정 시점의 데이터만을 추출
    start_date = '2021-06-02 19:00:00'
    end_date = '2024-04-03 09:00:00'

    # cerebro가 읽을 수 있는 형태로 변경
    df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    data = bt.feeds.PandasData(dataname=df, datetime='datetime')

    # 머신 Cerebro 초기화
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(0.0002)

    cerebro.adddata(data)