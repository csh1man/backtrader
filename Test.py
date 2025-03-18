from api.Api import ApiBase, Binance, ByBit, Download, UpBit, Common
from api.ApiUtil import TimeUtil, DataUtil
if __name__ == '__main__':
    file_path = "C:\\Users\\KOSCOM\\Desktop\\각종자료\\개인자료\\krInvestment\\config.json"
    download_dir_path ="C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/백테스팅데이터"

    common = Common(file_path)
    download = Download(file_path, download_dir_path)

    exchange = DataUtil.UPBIT
    symbol = "KRW-XRP"
    timeframe = TimeUtil.CANDLE_TIMEFRAME_4HOURS
    download.download_candles(exchange, symbol, timeframe)

    






