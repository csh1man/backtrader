from datetime import datetime, timedelta
import pytz, time, json


class DataUtil:
    BINANCE = "binance"
    BYBIT = "bybit"
    UPBIT = "upbit"


class FileUtil:
    @staticmethod
    def load_account_config(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def write_json_file(file_path, data):
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    @staticmethod
    def read_json_file(file_path: str):
        try:
            # JSON 파일 열기
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the file {file_path}.")
        except Exception as e:
            print(f"An error occurred: {e}")


class TimeUtil:
    CANDLE_TIMEFRAME_1MINUTES = "1m"
    CANDLE_TIMEFRAME_5MINUTES = "5m"
    CANDLE_TIMEFRAME_15MINUTES = "15m"
    CANDLE_TIMEFRAME_30MINUTES = "30m"
    CANDLE_TIMEFRAME_1HOURS = "1h"
    CANDLE_TIMEFRAME_2HOURS = "2h"
    CANDLE_TIMEFRAME_4HOURS = "4h"
    CANDLE_TIMEFRAME_1DAY = "1d"
    CANDLE_TIMEFRAME_1WEEK = "1w"
    CANDLE_TIMEFRAME_1MONTH = "1M"

    @staticmethod
    def get_latest_candle_time(timeframe, is_kst):
        # 현재 시간
        current_time_str = TimeUtil.get_current_time_yyyy_mm_dd_hh_mm_ss(is_kst)
        # 현재 시간을 datetime 객체로 변환
        current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")

        # 타임프레임에 따라 가장 최신 캔들 시간 계산
        if timeframe == TimeUtil.CANDLE_TIMEFRAME_1MINUTES:
            # 1분 단위: 가장 가까운 분
            latest_time = current_time.replace(second=0, microsecond=0)

        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_5MINUTES:
            # 5분 단위
            minutes = (current_time.minute // 5) * 5
            latest_time = current_time.replace(minute=minutes, second=0, microsecond=0)

        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_15MINUTES:
            # 15분 단위
            minutes = (current_time.minute // 15) * 15
            latest_time = current_time.replace(minute=minutes, second=0, microsecond=0)

        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_30MINUTES:
            # 30분 단위
            minutes = (current_time.minute // 30) * 30
            latest_time = current_time.replace(minute=minutes, second=0, microsecond=0)

        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1HOURS:
            # 1시간 단위
            latest_time = current_time.replace(minute=0, second=0, microsecond=0)

        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_4HOURS:
            # 4시간 단위
            closest_candle_hour = 1 + (current_time.hour - 1) // 4 * 4
            latest_time = current_time.replace(hour=closest_candle_hour, minute=0, second=0, microsecond=0)

        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1DAY:
            latest_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

        else:
            raise ValueError("Invalid timeframe")

        # 반환할 시간 문자열 형식: 'yyyy-mm-dd HH:mm:ss'
        return latest_time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def compare_times(time1: str, time2: str):
        date_format = '%Y-%m-%d %H:%M:%S'
        date1 = datetime.strptime(time1, date_format)
        date2 = datetime.strptime(time2, date_format)

        if date1 > date2:
            return 1
        elif date1 == date2:
            return 0
        else:
            return -1

    @staticmethod
    def delay(delay_time):
        try:
            time.sleep(delay_time)  # delay_time은 초 단위
        except Exception as e:
            raise RuntimeError(f"Error: {e}")

    @staticmethod
    def get_timeframe(exchange, timeframe):
        if exchange == DataUtil.BINANCE:
            if timeframe == TimeUtil.CANDLE_TIMEFRAME_1MINUTES:
                return "1m"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_5MINUTES:
                return "5m"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_15MINUTES:
                return "15m"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_30MINUTES:
                return "30m"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1HOURS:
                return "1h"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_2HOURS:
                return "2h"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_4HOURS:
                return "4h"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1DAY:
                return "1d"
            else:
                raise Exception(f"{timeframe} is not existed in binance.")
        elif exchange == DataUtil.BYBIT:
            if timeframe == TimeUtil.CANDLE_TIMEFRAME_1MINUTES:
                return "1"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_5MINUTES:
                return "5"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_15MINUTES:
                return "15"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_30MINUTES:
                return "30"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1HOURS:
                return "60"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_2HOURS:
                return "120"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_4HOURS:
                return "240"
            elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1DAY:
                return "D"
            else:
                raise Exception(f"{timeframe} is not existed in bybit.")

    @staticmethod
    def str_to_timestamp(target: str, is_kst: bool) -> int:
        if "-" in target:
            formatter = "%Y-%m-%d %H:%M:%S"
        else:
            formatter = "%Y%m%d%H%M%S"

        local_date_time = datetime.strptime(target, formatter)
        if is_kst:
            local_date_time = local_date_time - timedelta(hours=9)

        return int(local_date_time.replace(tzinfo=pytz.utc).timestamp() * 1000)

    @staticmethod
    def timestamp_to_candle_time(timestamp: str, timeframe: str, is_kst: bool) -> str:
        # Convert timestamp to datetime object (UTC)
        timestamp_long = int(timestamp)
        utc_time = datetime.utcfromtimestamp(timestamp_long / 1000)

        # Parse the timeframe to get the unit and amount
        amount = -1
        if timeframe[-1] != 'M':
            amount = int(timeframe[:-1])

        unit = None
        if timeframe[-1] == 'm':
            unit = 'minutes'
        elif timeframe[-1] == 'h':
            unit = 'hours'
        elif timeframe[-1] == 'd':
            unit = 'days'
        elif timeframe[-1] == 'M':
            unit = 'months'
        else:
            raise ValueError("Invalid tick kind")

        # Adjust time to the correct candle time (rounding based on timeframe)
        if unit == 'minutes':
            utc_time = utc_time - timedelta(minutes=utc_time.minute % amount, seconds=utc_time.second,
                                            microseconds=utc_time.microsecond)
        elif unit == 'hours':
            utc_time = utc_time - timedelta(hours=utc_time.hour % amount, minutes=utc_time.minute,
                                            seconds=utc_time.second, microseconds=utc_time.microsecond)
        elif unit == 'days':
            utc_time = utc_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
                days=utc_time.day % amount)
        elif unit == 'months':
            new_month = (utc_time.month - 1) // amount * amount + 1
            if new_month == 13:
                new_month = 1
            utc_time = utc_time.replace(month=new_month, day=1, hour=0, minute=0, second=0, microsecond=0)

        # Convert to Korean Standard Time (KST) if needed
        if is_kst:
            kst_timezone = pytz.timezone('Asia/Seoul')
            utc_time = utc_time.replace(tzinfo=pytz.utc).astimezone(kst_timezone)

        # Return formatted candle time string
        return utc_time.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_current_time_yyyy_mm_dd_hh_mm_ss(is_kst: bool) -> str:
        current_time = datetime.utcnow()

        if is_kst:
            # KST (Korean Standard Time)는 UTC+9
            kst_timezone = pytz.timezone('Asia/Seoul')
            current_time = current_time.replace(tzinfo=pytz.utc).astimezone(kst_timezone)

        return current_time.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def add_times(target: str, timeframe: str, count: int) -> str:
        if target.__contains__("+09:00"):
            target = target.replace("+09:00", "")
        local_date_time = datetime.strptime(target, "%Y-%m-%d %H:%M:%S")

        if timeframe == TimeUtil.CANDLE_TIMEFRAME_1MINUTES:
            local_date_time = local_date_time + timedelta(minutes=count)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_15MINUTES:
            local_date_time = local_date_time + timedelta(minutes=count * 15)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_30MINUTES:
            local_date_time = local_date_time + timedelta(minutes=count * 30)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1HOURS:
            local_date_time = local_date_time + timedelta(hours=count)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_2HOURS:
            local_date_time = local_date_time + timedelta(hours=count * 2)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_4HOURS:
            local_date_time = local_date_time + timedelta(hours=count * 4)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1DAY:
            local_date_time = local_date_time + timedelta(days=count)

        return local_date_time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def minus_times(target: str, timeframe: str, count: int) -> str:
        local_date_time = datetime.strptime(target, "%Y-%m-%d %H:%M:%S")

        if timeframe == TimeUtil.CANDLE_TIMEFRAME_1MINUTES:
            local_date_time = local_date_time - timedelta(minutes=count)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_15MINUTES:
            local_date_time = local_date_time - timedelta(minutes=count * 15)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_30MINUTES:
            local_date_time = local_date_time - timedelta(minutes=count * 30)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1HOURS:
            local_date_time = local_date_time - timedelta(hours=count)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_2HOURS:
            local_date_time = local_date_time - timedelta(hours=count * 2)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_4HOURS:
            local_date_time = local_date_time - timedelta(hours=count * 4)
        elif timeframe == TimeUtil.CANDLE_TIMEFRAME_1DAY:
            local_date_time = local_date_time - timedelta(days=count)

        return local_date_time.strftime("%Y-%m-%d %H:%M:%S")
