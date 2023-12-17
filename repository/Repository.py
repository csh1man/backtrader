import pymysql

from dbutils.pooled_db import PooledDB
from util.FileUtil import FileUtil
from repository.entity import CandleInfo


class DB:
    connection_pool = None

    @classmethod
    def init_connection_pool(cls, file_path):
        """
        디비의 커넥션 풀 인스턴스를 초기화한다.
        :param file_path: config file path
        :return: null
        """
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
        """
        Connection Pool에서 Connection instance 하나를 반환한다.
        :return: Connection Pool instance
        """
        return self.connection_pool.connection()

    def get_symbol_list(self):
        """
        현재 캔들 정보가 들어있는 디비 테이블에서 어떤 종목들이 들어가있는지에 대한 종목 리스트를 반환한다.

        :return: string array list
        """
        sql = "select distinct currency from candle_info"
        conn = self.get_db_connect()
        curs = conn.cursor()
        curs.execute(sql)

        symbols = []
        for result in curs.fetchall():
            symbols.append(result['currency'])

        return symbols

    def get_candle_info(self, company, currency, tick_kind, start_time=None, end_time=None):
        """
        candle정보 목록을 가져온다.(olhcv)

        :param company: 거래소명
        :param currency: 종목명
        :param tick_kind: 시간 종류
        :param start_time: 시작 시간
        :param end_time: 종료 시간
        :return: CandleInfo list
        """
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

