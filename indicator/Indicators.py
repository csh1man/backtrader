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
