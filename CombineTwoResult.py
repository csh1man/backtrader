import pandas as pd
import quantstats as qs

if __name__ == '__main__':
    # file_name = 'C:/Users/user/Desktop/개인자료/콤트/백테스트결과/TrendFollow Short and TailCatch V1'
    # df1 = pd.read_csv('C:/Users/user/Desktop/개인자료/콤트/백테스트결과/ETHUSDT-BCHUSDT-TrendFollowV2.csv', parse_dates=['date'])
    # df2 = pd.read_csv('C:/Users/user/Desktop/개인자료/콤트/백테스트결과/BINANCE-XRPUSDT-DOGEUSDT-1000SHIBUSDT-TailCatchWithBBV2.csv', parse_dates=['date'])

    df1 = pd.read_csv('C:/Users/user/Desktop/개인자료/콤트/백테스트결과/TrendFollow Short and TailCatch V1.csv', parse_dates=['date'])
    df2 = pd.read_csv('C:/Users/user/Desktop/개인자료/콤트/백테스트결과/KRW-ETH-KRW-BTC-KRW-BCH-UpbitBBWithTrendFollowV1.csv', parse_dates=['date'])
    file_name = 'C:/Users/user/Desktop/개인자료/콤트/백테스트결과/Binance and UPBIT V1'

    # 날짜 컬럼을 datetime 형식으로 변환 (재확인)
    df1['date'] = pd.to_datetime(df1['date'])
    df2['date'] = pd.to_datetime(df2['date'])
    df_merged = pd.merge(df1, df2, on='date', suffixes=('_file1', '_file2'))
    df_merged['value'] = df_merged['value_file1'] + df_merged['value_file2']
    df_merged = df_merged.sort_values('date')

    df_merged = df_merged.set_index('date')
    df_merged.index.name ='date'
    df_merged = df_merged.drop(columns=['value_file1', 'value_file2'])
    # df_merged.to_csv(f'{file_name}.csv')
    qs.reports.html(df_merged['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)