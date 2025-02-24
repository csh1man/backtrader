import pandas as pd
import quantstats as qs

if __name__ == '__main__':
    file_name = 'C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/TrendFollow Short and TailCatch V1'
    df1 = pd.read_csv('C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/ETHUSDT-BCHUSDT-TrendFollowV2.csv', parse_dates=['date'])
    df2 = pd.read_csv('C:/Users/KOSCOM\Desktop/각종자료/개인자료/krInvestment/백테스팅데이터/결과/XRPUSDT-DOGEUSDT-LTCUSDT-TailCatchWithDonchianV2.csv', parse_dates=['date'])
    # 날짜 컬럼을 datetime 형식으로 변환 (재확인)
    df1['date'] = pd.to_datetime(df1['date'])
    df2['date'] = pd.to_datetime(df2['date'])

    df_merged = pd.merge(df1, df2, on='date', suffixes=('_file1', '_file2'))
    df_merged['value'] = df_merged['value_file1'] + df_merged['value_file2']
    df_merged = df_merged.sort_values('date')

    df_merged = df_merged.set_index('date')
    df_merged.index.name ='date'
    df_merged = df_merged.drop(columns=['value_file1', 'value_file2'])

    qs.reports.html(df_merged['value'], output=f"{file_name}.html", download_filename=f"{file_name}.html", title=file_name)