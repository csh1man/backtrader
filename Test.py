from api.Api import ApiBase, Binance, ByBit, Download, UpBit, Common
from api.ApiUtil import TimeUtil, DataUtil
if __name__ == '__main__':
    file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
    # file_path = "C:\\Users\\user\\Desktop\\개인자료\\콤트\\config\\config.json"
    download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    # download_dir_path = "C:/Users/user/Desktop/개인자료/콤트/candleData"
    common = Common(file_path)
    download = Download(file_path, download_dir_path)

    # exchange = DataUtil.UPBIT
    # symbol = "KRW-DOGE"
    # timeframe = TimeUtil.CANDLE_TIMEFRAME_4HOURS
    # download.download_candles(exchange, symbol, timeframe)

    exchange = DataUtil.BINANCE
    symbol = "1000PEPEUSDT"
    tick_size = common.fetch_tick_size(exchange, symbol)
    step_size = common.fetch_step_size(exchange, symbol)
    print(str(tick_size))
    print(step_size)





