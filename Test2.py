import math
from decimal import Decimal


def round_customized(n):
    return math.floor(n + Decimal("0.5"))

if __name__ == '__main__':
    diff_percent = Decimal("4")
    risk_per_trade = Decimal("10")

    leverage = Decimal("2.5")
    leverage = round_customized(leverage)
    print(leverage)
