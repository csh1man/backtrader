import pymysql

from dbutils.pooled_db import PooledDB
from util.Util import FileUtil
from repository.entity import CurrencyInfo


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

    def get_currency_info(self, company, currency):
        """
        디비에 저장되어있는 코인의 가격 및 수량 단위를 획득

        :param company: 거래소명
        :param currency: 코인명
        :return: CurrencyInfo Instance
        """
        sql = "select * from currency_info where company = %s and currency = %s"
        conn = self.get_db_connect()
        curs = conn.cursor()
        curs.execute(sql, [company, currency])

        return CurrencyInfo(curs.fetchone())

    def get_currency_info_list(self, company):
        """
        디비에 저장되어 있는 모든 코인의 가격 및 수량 단위 리스트를 획득
        :param company: 코인명
        :return: CurrencyInfo Instance List
        """
        sql = "select * from currency_info where company = %s"
        conn = self.get_db_connect()
        curs = conn.cursor()
        curs.execute(sql, company)

        currency_info_list = []
        for curs_result in curs.fetchall():
            currency_info_list.append(CurrencyInfo(curs_result))

        return currency_info_list

