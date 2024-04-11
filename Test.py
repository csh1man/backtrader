from decimal import Decimal, ROUND_HALF_UP


if __name__ == '__main__':
    tick_size = Decimal('0.0001')
    price = Decimal('3.12000000000000000000000000000000000000000012')

    print(price.quantize(tick_size, rounding=ROUND_HALF_UP))