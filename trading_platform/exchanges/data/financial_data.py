"""
Cheapest coins on https://coinmarketcap.com/ are about 8 satoshis, which requires 9 decimal places. So add a few decimal
places for padding.

Use floats because numpy arrays don't have a decimal data type from what I can tell, which means we'd have to convert
every numeric value in the ticker and arbitrage dataframes to a Decimal. That is a pain and has a performance cost.
Maybe the float64 type but I haven't looked into it.
"""
from decimal import Decimal


class FinancialData:
    # Precision is the total number of digits, scale is the number of digits after the decimal point
    # For tests, the test result is not as precise, usually due to the fact that pandas don't have a decimal datatype.
    # These tests don't have as much precision as "decimal_scale".
    one_place = 1
    two_places = 2
    three_places = 3
    four_places = 4
    five_places = 5
    six_places = 6
    eight_places = 8

    def __new__(cls, number):
        try:
            # Bittrex and Kucoin precision for order numerical data is six places. In order to match an order_id in the
            # database with the metadata of an order returned from the exchange, the app needs to round numerical fields to the
            # sixth place as well.
            converted = round(Decimal(number), cls.five_places)
            return converted
        except Exception as ex:
            # This exception occurs so often, swallow it
            if number is not None:
                print(ex)


zero = FinancialData(0)

one = FinancialData(1.0)

two = FinancialData(2.0)

one_hundred = FinancialData(100.0)