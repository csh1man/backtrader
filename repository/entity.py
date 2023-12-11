
class CandleInfo:
    def __init__(self, curs_result):
        self.company = curs_result['company']
        self.tick_kind = curs_result['tick_kind']
        self.currency = curs_result['currency']
        self.date = curs_result['date']
        self.open = curs_result['open']
        self.high = curs_result['high']
        self.low = curs_result['low']
        self.close = curs_result['close']
        self.volume = curs_result['volume']
