
class CandleInfo:
    def __init__(self, curs_result):
        """
        candle_info에서 꺼내온 데이터(cursor 결과)를 CandleInfo 객체로 변환

        :param curs_result: 디비 테이블 candle_info에서 꺼내온 데이터
        """
        self.company = curs_result['company']
        self.tick_kind = curs_result['tick_kind']
        self.currency = curs_result['currency']
        self.date = curs_result['date']
        self.open = curs_result['open']
        self.high = curs_result['high']
        self.low = curs_result['low']
        self.close = curs_result['close']
        self.volume = curs_result['volume']
