from api.Api import ApiBase, Binance, Download
from api.ApiUtil import TimeUtil, DataUtil
if __name__ == '__main__':
    file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
    download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"
    download = Download(file_path, download_dir_path)

    exchange = DataUtil.BINANCE
    symbol = "ETHUSDT"
    timeframe = TimeUtil.CANDLE_TIMEFRAME_1DAY

    download.download_candles(exchange, symbol, timeframe)






