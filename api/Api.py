import os.path
from datetime import datetime
from textwrap import indent

from api.ApiUtil import TimeUtil, DataUtil, FileUtil
import requests
from decimal import Decimal
from urllib.parse import urlencode
import json
import hashlib
import uuid
import time
import random
import hmac
import jwt
from hashlib import sha512


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


class ByBit(ApiBase):
    def __init__(self, file_path):
        super().__init__(file_path, 'bybit', "https://api.bybit.com")
        self.exchange_info = self.fetch_exchange_info()

    def fetch_exchange_info(self):
        url = self.base_url + "/v5/market/instruments-info"
        params = {
            "category": "linear",
            'limit': 1000,
        }
        response = self.send_request(0, None, params, url)
        if response.status_code == 200:
            exchange_info = response.json()
            return exchange_info['result']['list']

        return None

    def fetch_tick_size(self, symbol: str):
        for info in self.exchange_info:
            if symbol == info['symbol']:
                return Decimal(info['priceFilter']['tickSize'])
        return None

    def fetch_step_size(self, symbol: str):
        for info in self.exchange_info:
            if symbol == info['symbol']:
                return Decimal(info['lotSizeFilter']['qtyStep'])
        return None

    def fetch_candle_sticks(self, symbol: str, timeframe: str, count: int):
        url = self.base_url + "/v5/market/kline"
        if count > 1000:
            count = 1000

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": TimeUtil.get_timeframe(DataUtil.BYBIT, timeframe),
            "limit": count
        }

        response = self.send_request(0, None, params, url)
        if response.status_code == 200:
            candles = response.json()['result']['list']

            returns = []
            for candle in candles:
                candle_time = TimeUtil.timestamp_to_candle_time(str(candle[0]), timeframe, True)

                # JSON 데이터 만들기
                candle_data = {
                    "exchange": DataUtil.BYBIT,
                    "candle_time": candle_time,
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                }
                returns.append(candle_data)
            return list(reversed(returns))
        return None

    def fetch_candle_sticks_with_start_time(self, symbol: str, timeframe: str, start: str, count: int):
        url = self.base_url + "/v5/market/kline"
        if count > 1000:
            count = 1000
        to = TimeUtil.add_times(start, timeframe, count)
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": TimeUtil.get_timeframe(DataUtil.BYBIT, timeframe),
            "start": TimeUtil.str_to_timestamp(start, True),
            "end": TimeUtil.str_to_timestamp(to, True),  # endTime 캔들은 미포함
            "limit": count
        }

        response = self.send_request(0, None, params, url)
        if response.status_code == 200:
            candles = response.json()['result']['list']

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

            return list(reversed(returns))

    def fetch_candle_sticks_with_end_time(self, symbol: str, timeframe: str, to: str, count: int):
        url = self.base_url + "/v5/market/kline"
        if count > 1000:
            count = 1000

        to = TimeUtil.add_times(to, timeframe, 1)
        start = TimeUtil.minus_times(to, timeframe, count)

        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": TimeUtil.get_timeframe(DataUtil.BYBIT, timeframe),
            "start": TimeUtil.str_to_timestamp(start, True),
            "end": TimeUtil.str_to_timestamp(to, True),  # endTime 캔들은 미포함
            "limit": count
        }

        response = self.send_request(0, None, params, url)
        if response.status_code == 200:
            candles = response.json()['result']['list']

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

            return list(reversed(returns))

    def fetch_all_candles_from_start(self, symbol: str, timeframe: str, start: str):
        total_candles = []
        while True:
            candles = self.fetch_candle_sticks_with_start_time(symbol, timeframe, start, 980)
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
            candles = self.fetch_candle_sticks_with_end_time(symbol, timeframe, end_time, 980)
            if not candles or candles[0]['candle_time'] == candles[-1]['candle_time']:
                print(f"[{symbol}] no more candle data to download.")
                break

            print(f'{symbol} download done : {candles[-1]["candle_time"]} ~ {candles[0]["candle_time"]}')
            total_candles.extend(candles)

            end_time = TimeUtil.minus_times(candles[-1]['candle_time'], timeframe, 1)
            TimeUtil.delay(0.8)

        return total_candles


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
        params = {
            "symbol": symbol,
            "interval": TimeUtil.get_timeframe(DataUtil.BINANCE, timeframe),
            "startTime": TimeUtil.str_to_timestamp(start, True),
            "endTime": TimeUtil.str_to_timestamp(to, True),  # endTime 캔들은 미포함
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


class UpBit(ApiBase):
    def __init__(self, file_path):
        super().__init__(file_path, 'upbit', "https://api.upbit.com/v1")

    def get_remaining_req(self, headers):
        for header in headers:
            header_key = header[0]
            if header_key == "Remaining-Req":
                header_value = header[1]
                start = header_value.index("sec=") + 4
                return int(header_value[start:])
        return 0

    def send_request_with_checking_remaining_seq(self, method, headers, params, url):
        while True:
            response = self.send_request(method, headers, params, url)  # 실제 요청을 보내는 함수

            remain_req = self.get_remaining_req(response.headers)  # 남은 요청 수 확인
            if remain_req < 3:
                time.sleep(0.3)  # 300ms 대기

            status_code = response.status_code

            if status_code == 200 or status_code == 201:
                break
            elif status_code == 429:
                time.sleep(0.3)  # 429 상태 코드 (Too Many Requests)일 경우 300ms 대기
            else:
                raise RuntimeError(response.text)
        return response

    def get_nonce(self):
        nonce = int(time.time() * 1000) + 1000
        nonce += random.randint(0, 99)

        return str(nonce)

    def get_query_string(self, params):
        return urlencode(params)

    def get_authentication(self, params=None):
        authentication = None
        try:
            access = self.api_key
            secret = self.api_secret

            if params:
                query = self.get_query_string(params)
                query_hash = hashlib.sha512(query.encode('utf-8')).hexdigest()

                algorithm = hmac.new(secret.encode('utf-8'), query_hash.encode('utf-8'), hashlib.sha256)
                authentication = jwt.encode({
                    'access_key': access,
                    'nonce': str(uuid.uuid4()),
                    'timestamp': str(int(time.time() * 1000)),
                    'query_hash': query_hash,
                    'query_hash_alg': 'SHA512'
                }, secret, algorithm='HS256')  # HS256을 사용하여 서명

            else:
                # params가 없을 경우, 기본적인 JWT 생성
                algorithm = hmac.new(secret.encode('utf-8'), access.encode('utf-8'), hashlib.sha256)
                authentication = jwt.encode({
                    'access_key': access,
                    'nonce': self.get_nonce(),  # nonce를 가져오는 함수
                    'timestamp': str(int(time.time() * 1000))
                }, secret, algorithm='HS256')

        except Exception as e:
            raise RuntimeError(e)

        return authentication

    def fetch_current_price(self, symbol: str):
        url = self.base_url + "/ticker"
        params = {
            "markets": symbol
        }

        headers = {
            "Authorization": self.get_authentication(params)
        }

        response = self.send_request(0, headers, params, url)
        if response.status_code == 200:
            return Decimal(response.json()[0]['trade_price'])

    def fetch_tick_size(self, symbol: str) -> Decimal:
        price = self.fetch_current_price(symbol)

        if price >= Decimal("2000000"):
            return Decimal("1000")
        elif price >= Decimal("1000000"):
            return Decimal("500")
        elif price >= Decimal("500000"):
            return Decimal("100")
        elif price >= Decimal("100000"):
            return Decimal("50")
        elif price >= Decimal("10000"):
            return Decimal("10")
        elif price >= Decimal("1000"):
            return Decimal("5")
        elif price >= Decimal("100"):
            return Decimal("1")
        elif price >= Decimal("10"):
            return Decimal("0.1")
        elif price >= Decimal("0"):
            return Decimal("0.01")

        return Decimal("0")

    def fetch_step_size(self, symbol):
        return Decimal("0.00000001")

    def fetch_candle_sticks_with_end_time(self, symbol: str, timeframe: str, to: str, count: int):
        url = self.base_url + "/candles"
        if timeframe == TimeUtil.CANDLE_TIMEFRAME_15MINUTES:
            url += "/minutes/15"
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_30MINUTES:
            url += "/minutes/30"
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1HOURS:
            url += "/minutes/60"
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_4HOURS:
            url += "/minutes/240"
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1DAY:
            url += "/days"

        params = {
            "market": symbol,
            "to": to.replace(' ', 'T'),
            "count": count
        }

        headers = {
            "Authorization": self.get_authentication(params)
        }

        response = self.send_request_with_checking_remaining_seq(0, headers, params, url)
        if response.status_code == 200:
            candles = response.json()
            returns = []
            for candle in reversed(candles):
                candle_time = candle["candle_date_time_kst"].replace('T', ' ')  # 공백으로 교체
                open = candle["opening_price"]
                high = candle["high_price"]
                low = candle["low_price"]
                close = candle["trade_price"]
                volume = candle["candle_acc_trade_volume"]

                # JSON 데이터 만들기
                candle_data = {
                    "exchange": DataUtil.UPBIT,
                    "candle_time": candle_time,
                    "open": open,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume
                }
                returns.append(candle_data)

            return list(reversed(returns))

    def fetch_all_candles(self, symbol: str, timeframe: str):
        total_candles = []
        end_time = TimeUtil.get_current_time_yyyy_mm_dd_hh_mm_ss(True)
        while True:
            candles = self.fetch_candle_sticks_with_end_time(symbol, timeframe, end_time, 200)
            if not candles or candles[0]['candle_time'] == candles[-1]['candle_time']:
                print(f"[{symbol}] no more candle data to download.")
                break

            print(f'{symbol} download done : {candles[-1]["candle_time"]} ~ {candles[0]["candle_time"]}')
            total_candles.extend(candles)

            end_time = TimeUtil.minus_times(candles[-1]['candle_time'], timeframe, 0) + "+09:00"

        return total_candles

    def fetch_all_candles_from_start(self, symbol: str, timeframe: str, start_time: str):
        total_candles = []
        last_candle_time = TimeUtil.get_latest_candle_time(timeframe, True)
        end_time = TimeUtil.add_times(last_candle_time, timeframe, 1) + "+09:00"
        exit_while = False
        while not exit_while:
            candles = self.fetch_candle_sticks_with_end_time(symbol, timeframe, end_time, 200)
            for candle in candles:
                candle_time = candle['candle_time']
                if TimeUtil.compare_times(start_time, candle_time) > 0:
                    exit_while = True
                    break
                else:
                    total_candles.append(candle)
            end_time = TimeUtil.minus_times(candles[-1]['candle_time'], timeframe, 0) + "+09:00"

        return total_candles


class Common:
    def __init__(self, config_file_path):
        self.bybit = ByBit(config_file_path)
        self.binance = Binance(config_file_path)
        self.upbit = UpBit(config_file_path)

    def fetch_tick_size(self, exchange, symbol):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_tick_size(symbol)
        elif exchange == DataUtil.BYBIT:
            return self.bybit.fetch_tick_size(symbol)
        elif exchange == DataUtil.UPBIT:
            return self.upbit.fetch_tick_size(symbol)

    def fetch_step_size(self, exchange, symbol):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_step_size(symbol)
        elif exchange == DataUtil.BYBIT:
            return self.bybit.fetch_step_size(symbol)
        elif exchange == DataUtil.UPBIT:
            return self.upbit.fetch_step_size(symbol)

    def fetch_candle_sticks(self, exchange: str, symbol: str, timeframe: str, count: int):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_candle_sticks(symbol, timeframe, count)
        elif exchange == DataUtil.BYBIT:
            return self.bybit.fetch_candle_sticks(symbol, timeframe, count)

    def fetch_candle_sticks_with_start_time(self, exchange: str, symbol: str, timeframe: str, start: str, count: int):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_candle_sticks_with_start_time(symbol, timeframe, start, count)
        elif exchange == DataUtil.BYBIT:
            return self.bybit.fetch_candle_sticks_with_start_time(symbol, timeframe, start, count)
        elif exchange == DataUtil.UPBIT:
            return self.upbit.fetch_candle_sticks_with_end_time(symbol, timeframe, start, count)

    def fetch_candle_sticks_with_end_time(self, exchange: str, symbol: str, timeframe: str, to: str, count: int):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_candle_sticks_with_end_time(symbol, timeframe, to, count)
        elif exchange == DataUtil.BYBIT:
            return self.bybit.fetch_candle_sticks_with_end_time(symbol, timeframe, to, count)
        elif exchange == DataUtil.UPBIT:
            return self.upbit.fetch_candle_sticks_with_end_time(symbol, timeframe, to, count)

    def fetch_all_candles_from_start(self, exchange: str, symbol: str, timeframe: str, start: str):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_all_candles_from_start(symbol, timeframe, start)
        elif exchange == DataUtil.BYBIT:
            return self.bybit.fetch_all_candles_from_start(symbol, timeframe, start)
        elif exchange == DataUtil.UPBIT:
            return self.upbit.fetch_all_candles_from_start(symbol, timeframe, start)

    def fetch_all_candles(self, exchange: str, symbol: str, timeframe: str):
        if exchange == DataUtil.BINANCE:
            return self.binance.fetch_all_candles(symbol, timeframe)
        elif exchange == DataUtil.BYBIT:
            return self.bybit.fetch_all_candles(symbol, timeframe)
        elif exchange == DataUtil.UPBIT:
            return self.upbit.fetch_all_candles(symbol, timeframe)


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
            latest_candle_time = max(json_data[timeframe].keys(),
                                     key=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
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
