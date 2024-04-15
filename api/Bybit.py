
class Bybit:
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange_info = None

    def get_futures_exchange_info(self):
        print('futures exchange_info')
