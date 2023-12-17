from config.Configuration import DBConfig
import json


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