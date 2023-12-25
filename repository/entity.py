
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