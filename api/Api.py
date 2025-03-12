import os.path
from datetime import datetime
from textwrap import indent

from api.ApiUtil import TimeUtil, DataUtil, FileUtil
import requests
from decimal import Decimal
from urllib.parse import urlencode
import json

class ApiBase:
    def __init__(self, file_path, exchange_name, base_url):
        # 공통된 config 로드
        config_json = FileUtil.load_account_config(file_path)

        # Base URL 셋팅
        self.base_url = base_url

        # API 키와 비밀 키를 공통 처리
        self.api_key = config_json['key'][exchange_name]['access']
        self.api_secret = config_json['key'][exchange_name]['secret']
        self.exchange_info = None

    def send_request(self, method, headers=None, params=None, url=None):
        if method == 0:  # GET
            if params:
                url += "?" + urlencode(params)
            response = self.get(url, headers=headers)
        elif method == 1:  # POST
            response = self.post(url, headers=headers, params=params)
        elif method == 2:  # DELETE
            if params:
                url += "?" + urlencode(params)
            response = self.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        return response

    def get(self, url, headers=None):
        response = requests.get(url, headers=headers, verify=False)
        return response

    def post(self, url, headers=None, params=None):
        response = requests.post(url, headers=headers, data=params, verify=False)
        return response

    def delete(self, url, headers=None):
        response = requests.delete(url, headers=headers, verify=False)
        return response


class Bybit(ApiBase):
    def __init__(self, file_path):
        super().__init__(file_path, 'bybit', "https://api.bybit.com")


class Binance(ApiBase):
    def __init__(self, file_path: str):
        super().__init__(file_path, 'binance', "https://fapi.binance.com")
        self.exchange_info = self.fetch_exchange_info()

    def fetch_exchange_info(self):
        url = self.base_url + "/fapi/v1/exchangeInfo"
        response = self.send_request(0, None, None, url)
        if response.status_code == 200:
            exchange_info = response.json()
            return exchange_info['symbols']

        return None

    def fetch_tick_size(self, symbol: str):
        for info in self.exchange_info:
            if info['symbol'] == symbol:
                filters = info['filters']
                for filter in filters:
                    if filter['filterType'] == 'PRICE_FILTER':
                        return Decimal(filter['tickSize'])
        return None

    def fetch_step_size(self, symbol: str):
        for info in self.exchange_info:
            if info['symbol'] == symbol:
                filters = info['filters']
                for filter in filters:
                    if filter['filterType'] == 'LOT_SIZE':
                        return Decimal(filter['stepSize'])
        return None

    def fetch_candle_sticks(self, symbol: str, timeframe: str, count: int):
        url = self.base_url + "/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': TimeUtil.get_timeframe(DataUtil.BINANCE, timeframe),
            'limit': count
        }

        response = self.send_request(0, None, params, url)
        if response.status_code == 200:
            candles = response.json()

            returns = []
            for candle in candles:
                candle_time = TimeUtil.timestamp_to_candle_time(str(candle[0]), timeframe, True)

                # JSON 데이터 만들기
                candle_data = {
                    "exchange": DataUtil.BINANCE,
                    "candle_time": candle_time,
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                }
                returns.append(candle_data)

            return returns

        return None

    def fetch_candle_sticks_with_start_time(self, symbol: str, timeframe: str, start: str, count: int):
        url = self.base_url + "/fapi/v1/klines"
        if count > 500:
            count = 500
        to = TimeUtil.add_times(start, timeframe, count)
        print(f'download {start} ~ {to}')
        params = {
            "symbol": symbol,
            "interval": TimeUtil.get_timeframe(DataUtil.BINANCE, timeframe),
            "startTime": TimeUtil.str_to_timestamp(start, True),
            "endTime": TimeUtil.str_to_timestamp(to, True), # endTime 캔들은 미포함
            "limit": count
        }

        response = self.send_request(0, None, params, url)
        if response.status_code == 200:
            candles = response.json()

            returns = []
            for candle in reversed(candles):
                candle_time = TimeUtil.timestamp_to_candle_time(str(candle[0]), timeframe, True)

                # JSON 데이터 만들기
                candle_data = {
                    "exchange": DataUtil.BINANCE,
                    "candle_time": candle_time,
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                }
                returns.append(candle_data)

            return returns

    def fetch_candle_sticks_with_end_time(self, symbol: str, timeframe: str, to: str, count: int):
        url = self.base_url + "/fapi/v1/klines"
        if count > 500:
            count = 500
        to = TimeUtil.add_times(to, timeframe, 1)
        start = TimeUtil.minus_times(to, timeframe, count)

        params = {
            "symbol": symbol,
            "interval": TimeUtil.get_timeframe(DataUtil.BINANCE, timeframe),
            "startTime": TimeUtil.str_to_timestamp(start, True),
            "endTime": TimeUtil.str_to_timestamp(to, True),
            "limit": count
        }

        response = self.send_request(0, None, params, url)
        if response.status_code == 200:
            candles = response.json()

            returns = []
            for candle in reversed(candles):
                candle_time = TimeUtil.timestamp_to_candle_time(str(candle[0]), timeframe, True)

                # JSON 데이터 만들기
                candle_data = {
                    "exchange": DataUtil.BINANCE,
                    "candle_time": candle_time,
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                }
                returns.append(candle_data)

            return returns

    def fetch_all_candles_from_start(self, symbol: str, timeframe: str, start: str):
        total_candles = []
        while True:
            candles = self.fetch_candle_sticks_with_start_time(symbol, timeframe, start, 491)
            if not candles or len(candles) == 0:
                print(f'[{symbol}] no more candle data to download.')
                break
            print(f'{symbol} download done : {candles[-1]["candle_time"]} ~ {candles[0]["candle_time"]}')
            total_candles.extend(reversed(candles))

            start = TimeUtil.add_times(candles[0]['candle_time'], timeframe, 1)
            TimeUtil.delay(0.8)

        return reversed(total_candles)

    def fetch_all_candles(self, symbol: str, timeframe: str):
        total_candles = []
        end_time = TimeUtil.get_current_time_yyyy_mm_dd_hh_mm_ss(True)
        while True:
            candles = self.fetch_candle_sticks_with_end_time(symbol, timeframe, end_time, 491)
            if not candles or candles[0]['candle_time'] == candles[-1]['candle_time']:
                print(f"[{symbol}] no more candle data to download.")
                break

            print(f'{symbol} download done : {candles[-1]["candle_time"]} ~ {candles[0]["candle_time"]}')
            total_candles.extend(candles)

            end_time = TimeUtil.minus_times(candles[-1]['candle_time'], timeframe, 1)
            TimeUtil.delay(0.8)

        return total_candles


class Common:
    def __init__(self, config_file_path):
        self.bybit = Bybit(config_file_path)
        self.binance = Binance(config_file_path)

    def fetch_step_size(self, exchange, symbol):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_tick_size(symbol)

    def fetch_tick_size(self, exchange, symbol):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_step_size(symbol)

    def fetch_candle_sticks(self, exchange: str, symbol: str, timeframe: str, count: int):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_candle_sticks(symbol, timeframe, count)

    def fetch_candle_sticks_with_start_time(self, exchange: str, symbol: str, timeframe: str, start: str, count: int):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_candle_sticks_with_start_time(symbol, timeframe, start, count)

    def fetch_candle_sticks_with_end_time(self, exchange: str, symbol: str, timeframe: str, to: str, count: int):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_candle_sticks_with_end_time(symbol, timeframe, to, count)

    def fetch_all_candles_from_start(self, exchange: str, symbol: str, timeframe: str, start: str):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_all_candles_from_start(symbol, timeframe, start)

    def fetch_all_candles(self, exchange: str, symbol: str, timeframe: str):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_all_candles(symbol, timeframe)

class Download:
    def __init__(self, config_file_path, download_dir_path):
        self.common = Common(config_file_path)
        self.download_dir_path = download_dir_path

    def download_candles(self, exchange, symbol, timeframe):
        download_file_path = f'{self.download_dir_path}/{exchange.lower()}/{symbol.lower()}.json'
        # json 파일이 존재하지 않으면 빈 json 값을 가진 json 파일 생성
        if not os.path.exists(download_file_path):
            with open(download_file_path, 'w') as file:
                json.dump({}, file, indent=4)
            print(f'{download_file_path} not existed. so create empty json file.')

        # json 파일 로드
        json_data = FileUtil.read_json_file(download_file_path)

        # 다운받고자하는 timeframe이 key로 존재하는 지 여부 확인
        if timeframe in json_data:
            # 해당 캔들이 존재할 경우, 가장 최신의 캔들 시간을 획득
            latest_candle_time = max(json_data[timeframe].keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
            latest_candle_time = TimeUtil.add_times(latest_candle_time, timeframe, 1)
            added_candles = self.common.fetch_all_candles_from_start(exchange, symbol, timeframe, latest_candle_time)
            for candle in reversed(list(added_candles)):
                json_data[timeframe][candle['candle_time']] = {
                    'open': candle['open'],
                    'high': candle['high'],
                    'low': candle['low'],
                    'close': candle['close'],
                    'volume': candle['volume']
                }
            FileUtil.write_json_file(download_file_path, json_data)

        else:
            # 해당 타임프레임 데이터가 존재하지 않으므로, 전체 데이터 다운로드
            total_candles = self.common.fetch_all_candles(exchange, symbol, timeframe)

            new_json = {}
            for candle in reversed(total_candles):
                new_json[candle['candle_time']] = {
                    'open': candle['open'],
                    'high': candle['high'],
                    'low': candle['low'],
                    'close': candle['close'],
                    'volume': candle['volume']
                }
            json_data[timeframe] = new_json
            FileUtil.write_json_file(download_file_path, json_data)



    def download_all_candles(self, exchange, symbol, timeframe):
        total_candles = self.common.fetch_all_candles(exchange, symbol, timeframe)

        json = {}
        for candle in reversed(total_candles):
            json[candle['candle_time']] = {
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close'],
                'volume': candle['volume']
            }

        total_json = {
            timeframe: json
        }

        download_file_path = f'{self.download_dir_path}/{exchange.lower()}/{symbol.lower()}.json'
        FileUtil.write_json_file(download_file_path, total_json)





