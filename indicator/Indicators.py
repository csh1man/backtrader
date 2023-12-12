

class Indicator:
    @staticmethod
    def get_body_length(open_price, close_price):
        return abs(close_price - open_price)