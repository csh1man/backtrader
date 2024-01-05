import math
from decimal import Decimal

class Indicator:
    @staticmethod
    def get_body_length(open_price, close_price):
        """캔들에 대한 몸통 길이 획득"""
        return abs(Decimal(str(close_price)) - Decimal(str(open_price)))

    @staticmethod
    def get_percent(price1, price2):
        """
        price1 대비 price2가 몇퍼센트 차이 나는 지 계산.
        """
        return (Decimal(str(price2)) - Decimal(str(price1))) * Decimal("100") / Decimal(str(price1))

    @staticmethod
    def get_diff_percent(close, stop_price):
        """
        종가 대비 손절가격이 몇퍼센트 차이나는지 계산
        """
        return round((Decimal(str(close)) - Decimal(str(stop_price))) * Decimal(str(100)) / Decimal(str(close)))

    @staticmethod
    def get_cut_price(close, atr, params):
        """
        손절가격을 Decimal로 계산하여 반환
        :param close: 종가
        :param atr: atr 값
        :param params: atr_constant가 들어있는 파라미터 dict
        :return: 손절가격
        """
        return Decimal(str(close)) - Decimal(str(atr)) * Decimal(str(params.atr_constant))

    @staticmethod
    def get_position_size(leverage, equity, close, params):
        position_size = Decimal(str(leverage)) * Decimal(str(equity)) * Decimal(str(params.risk_per_trade)) / Decimal("100") / Decimal(str(close))
        # position_size = leverage * Decimal(str(self.broker.getvalue())) * Decimal(
        #     str(self.p.risk_per_trade)) / Decimal("100") / Decimal(str(self.close[0]))
    @staticmethod
    def get_ma_separation(close, ma):
        """
        이동평균선 대비 종가가 어느 정도의 위치에 있는 지 이격도를 계산하는 함수

        :param close: 캔들의 종가
        :param ma: 이동평균선
        :return: 이격도
        """
        return close * 100 / ma

    @staticmethod
    def calculate_max_draw_down(df):
        """
        현재 가격을 최댓값이라 가정하고 현재 가격 이후 중 가장 작은 가격과 차이를 계산하여 리스트화한다.
        그러고 리스트화한 결과 목록 중 가장 큰 값이 mdd가된다.

        :param df:
            index : date
            value : asset
        :return:
            mdd
        """
        max_draw_downs = []

        for index in df.index:
            current_price = df.loc[index, 'asset']
            futures_prices = df.loc[index:, 'asset']
            min_futures_price = futures_prices.min()

            draw_down = (current_price - min_futures_price) / current_price
            max_draw_downs.append(draw_down)

        return max(max_draw_downs) * -1

    @staticmethod
    def get_mdd_dates(date_list, asset_list):
        """
        MDD에 해당하는 최댓값 날짜와 최솟값 날짜를 획득한다.

        :param date_list: asset_list가 저장된 날짜 목록
        :param asset_list: 자산 목록 (순수자산 + low * position_size)
        :return: MDD에 해당 하는 시작날짜, 끝날짜
        """
        print("TEST")



    @staticmethod
    def adjust_price(price, tick_size):
        """
        특정 종목의 최소 가격 변동 단위에 맞게 계산된 가격을 반환

        :param price: 계산한 price
        :param tick_size: 종목의 최소 가격 변동 단위
        :return: tick_size에 맞게 소수점 조정된 가격
        """
        return math.round(price / tick_size) * tick_size

    @staticmethod
    def adjust_quantity(quantity, step_size):
        """
        특정 종목의 최소 수량 변동 단위에 맞게 계산된 수량을 반환

        :param quantity: 계산한 수량
        :param step_size: 종목의 최소 수량 변동 단위
        :return: step_size에 맞게 소수점 조정된 가격
        """
        return math.floor(quantity / step_size) * step_size

    @staticmethod
    def get_percentage(price1, price2):
        """
        price1 대비 price2 차이 퍼센트 획득
        :param price1: 기준 가격
        :param price2: 비교 가격
        :return: 가격간 차이
        """
        return round((price1-price2) * 100 / price1)

    @staticmethod
    def get_leverage(risk_per_trade, diff_percent):
        """
        진입하고자하는 레버리지 값을 획득한다.

        :param risk_per_trade: 리스크 사이즈
        :param diff_percent: 진입가격과 손절가격 간 퍼센트 차이
        :return: 진입할 레버리지
        """
        return round(Decimal("100") / (Decimal(str(risk_per_trade)) * Decimal(diff_percent)))