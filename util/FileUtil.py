from config.Configuration import DBConfig
import json


class FileUtil:
    @staticmethod
    def load_db_config(file_path):
        with open(file_path, 'r') as file:
            config_data = json.load(file)
            return DBConfig(**config_data['db'])