from api.Api import ApiBase, Binance, ByBit, Download, UpBit
from api.ApiUtil import TimeUtil, DataUtil
if __name__ == '__main__':
    file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
    # download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    upBit = UpBit(file_path)

    symbol = "KRW-BTC"
    end_time = "2026-03-17 17:00:00+09:00"
    timeframe = TimeUtil.CANDLE_TIMEFRAME_4HOURS
    # end_time = TimeUtil.add_times(end_time, timeframe, 300)
    print(end_time)
    # candles = upBit.fetch_all_candles(symbol, timeframe)
    candles = upBit.fetch_candle_sticks_with_end_time(symbol, timeframe, end_time, 190)
    i=0
    for candle in candles:
        print(f"[{i+1}] {candle}")
        i+=1
    # candles = upBit.fetch_candle_sticks_with_end_time(symbol, TimeUtil.CANDLE_TIMEFRAME_4HOURS, TimeUtil.get_current_time_yyyy_mm_dd_hh_mm_ss(True), 190)
    # for candle in candles:
    #     print(candle)






