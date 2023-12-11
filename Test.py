from repository.Repository import DB
import pandas as pd
if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    DB.init_connection_pool(config_path)

    db = DB()
    candle_infos = db.get_candle_info('BYBIT', 'KAVAUSDT', '30m')
    df = pd.DataFrame([vars(info) for info in candle_infos])

    df['datetime'] = pd.to_datetime(pd['date'])
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])

