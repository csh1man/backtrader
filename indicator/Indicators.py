
class Indicator:
    @staticmethod
    def get_body_length(open_price, close_price):
        """캔들에 대한 몸통 길이 획득"""
        return abs(close_price - open_price)

    @staticmethod
    def get_percent(price1, price2):
        """
        price1 대비 price2가 몇퍼센트 차이 나는 지 계산.
        """
        return (price2 - price1) * 100 / price1
