from repository.Repository import DB
import pandas as pd
if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    DB.init_connection_pool(config_path)

    # CSV 파일 로드
    df = pd.read_csv('linkusdt_30m.csv')

    # 'datetime' 컬럼을 datetime 객체로 변환 (밀리초 제거)
    df['datetime'] = pd.to_datetime(df['datetime']).dt.floor('S')


