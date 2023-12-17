import pandas as pd

from repository.Repository import DB

if __name__ == '__main__':
    config_path = "/Users/tjgus/Desktop/project/krtrade/testDataDirectory/config/config.json"
    DB.init_connection_pool(config_path)

    db = DB()
    connection = db.get_db_connect()
    try:
        with connection.cursor() as cursor:
            sql = "select date, open, high, low, close, volume from candle_info where currency='LINKUSDT' and " \
                  "tick_kind='1d' order by date asc"
            cursor.execute(sql)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
    finally:
        connection.close()

    df.to_csv('linkusdt_1d.csv', index=False)

