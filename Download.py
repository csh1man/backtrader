import pandas as pd
from util.Util import DataUtil

from repository.Repository import DB
if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    DB.init_connection_pool(config_path)

    # file_path = "/Users/tjgus/Desktop/project/krtrade/candle_data/bybit/linkusdt.json"
    dir_path = "/Users/tjgus/Desktop/project/krtrade/candle_data"
    df = DataUtil.load_candle_data_as_df(DataUtil.CANDLE_DATA_DIR_PATH,
                                         DataUtil.COMPANY_BYBIT,
                                         "BTCUSDT",
                                         DataUtil.CANDLE_TICK_30M)
    print(df)
