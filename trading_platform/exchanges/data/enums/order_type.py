class OrderType:
    limit = 0
    market = 1

    @staticmethod
    def from_exchange_data(order_type_str):
        order_type_str = order_type_str.lower()
        if order_type_str == 'market':
            return OrderType.market
        else:
            return OrderType.limit