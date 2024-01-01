from util.Util import DataUtil, FileUtil, JsonUtil
from repository.entity import CandleInfo
import os

if __name__ == '__main__':
    candle_data_dir_path = DataUtil.CANDLE_DATA_DIR_PATH + "/" + DataUtil.COMPANY_BYBIT

    my_list = []
    # 파일 목록 획득
    file_list = os.listdir(candle_data_dir_path)
    for file in file_list:
        try:
            # 파일 풀 경로를 이용 파일 정보 획득
            file_full_path = candle_data_dir_path + "/" + file

            # tick kind 설정
            tick_kind = DataUtil.CANDLE_TICK_30M

            # json 파일 로드
            candle_data = FileUtil.load_candle_data(file_full_path)

            # 캔들 시간을 오름차순으로 획득
            dates = JsonUtil.get_candle_date_list(candle_data, tick_kind, True)

            under_wick_is_longer = 0
            for date in dates:
                candle_info = CandleInfo(candle_data[tick_kind][date])
                body_length = candle_info.get_body_length()
                under_wick_length = candle_info.get_under_wick()
                if under_wick_length > body_length:
                    under_wick_is_longer = under_wick_is_longer + 1

            my_dict = {file: under_wick_is_longer * 100 / len(dates)}
            my_list.append(my_dict)
        except Exception as e:
            print(f"예외 발생 :{e}")

    sorted_list = sorted(my_list, key=lambda x: list(x.values())[0], reverse=True)
    for data in sorted_list:
        print(data)