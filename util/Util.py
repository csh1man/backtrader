import pandas as pd
from decimal import Decimal
import json
from config.Configuration import DBConfig


class FileUtil:
    @staticmethod
    def load_db_config(file_path):
        """
        나의 환경설정 파일에서 데이터베이스의 설정값을 반환

        :param file_path: 'config.json' 파일 경로
        :return: db 정보가 담겨진 DBConfig instance
        """
        with open(file_path, 'r') as file:
            config_data = json.load(file)
            return DBConfig(**config_data['db'])

    @staticmethod
    def load_strategy_config(file_path):
        """
        전략에 대한 수치 값들이 저장된 strategy.json 획득

        :param file_path: 'strategy.json' 파일경로
        :return: strategy.json
        """
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def load_candle_data(file_path):
        """
        로컬 디렉토리에 저장된 캔들 데이터를 획득하여 json으로 반환
        :param file_path: 로컬 디렉토리 캔들 데이터 경로
        :return: json data for candle information
        """
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def load_account_config(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)


class DataUtils:
    """
    캔들 tick_kind static 변수 선언
    """
    CANDLE_TICK_30M = "30m"
    CANDLE_TICK_1HOUR = "1h"
    CANDLE_TICK_2HOUR = "2h"
    CANDLE_TICK_4HOUR = "4h"
    CANDLE_TICK_1DAY = "1d"

    """
    거래소명 static 변수 선언
    """
    COMPANY_BYBIT = "BYBIT"
    COMPANY_BINANCE = "BINANCE"
    COMPANY_UPBIT = "UPBIT"
    COMPANY_BITHUMB = "BITHUMB"
    COMPANY_NASDAQ = "nasdaq"

    """
    캔들 데이터가 저장된 디렉토리 경로 저장
    """
    CANDLE_DATA_DIR_PATH = "/Users/tjgus/Desktop/project/krtrade/candle_data"
    CANDLE_DATA_DIR_PATH_V2 = "C:/Users/KOSCOM/Desktop/각종자료/개인자료/krInvestment/backtrader/backtrader/sample"

    @staticmethod
    def load_candle_data_as_df(dir_path, company, currency, tick_kind):
        """
        로컬의 캔들 파일 경로를 입력하면 캔들.json을 읽어 Pandas의 DataFrame으로 변환

        :param dir_path: candle.json이 저장되어있는 디렉토리 경로(거래소명 전까지)
        :param company : 거래소명
        :param currency: 코인명
        :param tick_kind 시간종류
        :return: DataFrame
        """
        file_path = dir_path + "/" + company.lower() + "/" + currency.lower() + ".json"
        candle_data = FileUtil.load_candle_data(file_path)

        df_data = []
        for time, candle_info in candle_data[tick_kind.lower()].items():
            row = [time] + [float(candle_info[k]) for k in ["open", "high", "low", "close", "volume"]]
            df_data.append(row)

        # DataFrame 생성
        df = pd.DataFrame(df_data, columns=["datetime", "open", "high", "low", "close", "volume"])

        # datetime 열을 datetime 객체로 변환
        df['datetime'] = pd.to_datetime(df['datetime'])

        return df

    @staticmethod
    def get_candle_data_in_scape(df, start_date, end_date):
        """
        Pandas의 DataFrame으로 저장된 캔들 정보에 날짜 범위를 정해서 해당 범위만큼만 추출

        :param df: 특정 종목의 전체 캔들 정보
        :param start_date: 시작 날짜
        :param end_date: 끝 날짜
        :return: 날짜 범위만큼 추출된 DataFrame
        """
        return df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]

    @staticmethod
    def convert_to_decimal(data):
        return Decimal(str(data))

    '''
    getTickSize(float price) =>
    if price >= 1000000
        1000
    else if price >= 500000
        500
    else if price >= 100000
        100
    else if price >= 50000
        50
    else if price >= 10000
        10
    else if price >= 5000
        5
    else if price >= 1000
        1
    else if price >= 100
        1
    else if price >= 10
        0.01
    else if price >= 1
        0.001
    else
        0.0001
    '''
    @staticmethod
    def get_bithumb_tick_size(price):
        if price >= 1000000:
            return Decimal('1000')
        elif price >= 500000:
            return Decimal('500')
        elif price >= 100000:
            return Decimal('100')
        elif price >= 50000:
            return Decimal('50')
        elif price >= 10000:
            return Decimal('10')
        elif price >= 5000:
            return Decimal('5')
        elif price >= 1000:
            return Decimal('1')
        elif price >= 100:
            return Decimal('1')
        elif price >= 10:
            return Decimal('0.01')
        elif price >= 1:
            return Decimal('0.001')
        else:
            return Decimal('0.0001')

class JsonUtil:
    @staticmethod
    def get_candle_date_list(candle_data, tick_kind, is_ascend):
        tick_data = candle_data[tick_kind]
        if is_ascend:
            return sorted(tick_data.keys())
        else:
            return sorted(tick_data.keys(), reverse=True)