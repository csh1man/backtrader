
class CurrencyInfo:
    def __init__(self, curs_result):
        """
        디비에 저장된 코인 종목 별로 가격 및 수량 사이즈 단위 획득.
        :param curs_result: DB cursor Result
        """
        self.company = curs_result['company']
        self.currency = curs_result['currency']
        self.tick_size = float(curs_result['tick_size'])
        self. step_size = float(curs_result['step_size'])


class CandleInfo:
    def __init__(self, json_data):
        self.open = float(json_data['open'])
        self.high = float(json_data['high'])
        self.low = float(json_data['low'])
        self.close = float(json_data['close'])
        self.volume = float(json_data['volume'])

    def is_bullish(self):
        if self.close > self.open:
            return True
        else:
            return False

    def get_under_wick(self):
        if self.is_bullish():
            return self.open - self.low
        else:
            return self.close - self.low

    def get_body_length(self):
        return abs(self.close - self.open)
