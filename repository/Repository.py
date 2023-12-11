import pymysql

from dbutils.pooled_db import PooledDB
from util.FileUtil import FileUtil
from repository.entity import CandleInfo

class DB:
    connection_pool = None

    @classmethod
    def init_connection_pool(cls, file_path):
        db_config = FileUtil.load_db_config(file_path)
        cls.connection_pool = PooledDB(
            creator=pymysql,
            host=db_config.ip,
            user=db_config.user,
            password=db_config.password,
            database=db_config.database,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_db_connect(self):
        return self.connection_pool.connection()

    def get_symbol_list(self):
        sql = "select distinct currency from candle_info"
        conn = self.get_db_connect()
        curs = conn.cursor()
        curs.execute(sql)

        symbols = []
        for result in curs.fetchall():
            symbols.append(result['currency'])

        return symbols

    def get_candle_info(self, company, currency, tick_kind, start_time=None, end_time=None):
        sql = "select * from candle_info where company = %s and currency = %s and tick_kind = %s"
        params = [company, currency, tick_kind]

        if start_time is not None:
            sql += " and date >= %s"
            params.append(start_time)

        if end_time is not None:
            sql += " and date <= %s"
            params.append(end_time)

        sql += " order by date asc"

        conn = self.get_db_connect()
        curs = conn.cursor()
        curs.execute(sql, params)

        candle_infos = []
        for result in curs.fetchall():
            candle_infos.append(CandleInfo(result))

        return candle_infos

