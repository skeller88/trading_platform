"""
Saved exchange responses to allow testing of handling of exchange responses without needing to make an
exchange request.
"""
# Binance
binance_fetch_order = {'info': {
    'symbol': 'ETHUSDT',
            'orderId': 54618365,
            'clientOrderId': 'MjPDhqGPu8GYVA0sBQIKWM',
            'price': '9999.00000000',
            'origQty': '0.02000000',
            'executedQty': '0.00000000',
            'status': 'NEW',
            'timeInForce': 'GTC',
            'type': 'LIMIT',
            'side': 'SELL',
            'stopPrice': '0.00000000',
            'icebergQty': '0.00000000',
            'time': 1523323563043,
            'isWorking': True},
   'id': '54618365',
   'timestamp': 1523323563043,
   'datetime': '2018-04-10T01:26:03.430Z',
   'symbol': 'ETH/USDT',
   'type': 'limit',
   'side': 'sell',
   'price': 9999.0,
   'amount': 0.02,
   'cost': 0.0,
   'filled': 0.0,
    'remaining': 0.02,
    'status': 'open',
    'fee': None}

binance_limit_sell_order = {
    'info': {
        'symbol': 'ETHUSDT',
        'orderId': 54617081,
        'clientOrderId': 'A10C8he3g7CfnqKTVn1Zy6',
        'transactTime': 1523323205621,
        'price': '9999.00000000',
        'origQty': '0.02000000',
        'executedQty': '0.00000000',
        'status': 'NEW',
        'timeInForce': 'GTC',
        'type': 'LIMIT',
        'side': 'SELL'},
    'id': '54617081',
    'timestamp': 1523323205621,
    'datetime': '2018-04-10T01:20:06.621Z',
    'symbol': 'ETH/USDT',
    'type': 'limit',
    'side': 'sell',
    'price': 9999.0,
    'amount': 0.02,
    'cost': 0.0,
    'filled': 0.0,
    'remaining': 0.02,
    'status': 'open',
    'fee': None
}

binance_ticker = {'symbol': 'CLOAK/ETH',
                  'timestamp': 1524789472571,
                  'datetime': '2018-04-27T00:37:53.571Z',
                  'high': 0.02352,
                  'low': 0.02,
                  'bid': 0.02115,
                  'bidVolume': 60.86,
                  'ask': 0.021298,
                  'askVolume': 8.71,
                  'vwap': 0.021774,
                  'open': 0.020466,
                  'close': 0.020466,
                  'first': None,
                  'last': 0.021298,
                  'change': 0.000832,
                  'percentage': 4.065,
                  'average': None,
                  'baseVolume': 26229.83,
                  'quoteVolume': 571.12835044,
                  'info': {'symbol': 'CLOAKETH',
                           'priceChange': '0.00083200',
                           'priceChangePercent': '4.065',
                           'weightedAvgPrice': '0.02177400',
                           'prevClosePrice': '0.02046600',
                           'lastPrice': '0.02129800',
                           'lastQty': '17.18000000',
                           'bidPrice': '0.02115000',
                           'bidQty': '60.86000000',
                           'askPrice': '0.02129800',
                           'askQty': '8.71000000',
                           'openPrice': '0.02046600',
                           'highPrice': '0.02352000',
                           'lowPrice': '0.02000000',
                           'volume': '26229.83000000',
                           'quoteVolume': '571.12835044',
                            'openTime': 1524703072571,
                            'closeTime': 1524789472571,
                            'firstId': 23924,
                            'lastId': 26747,
                            'count': 2824}}

# Bittrex
bittrex_create_limit_buy_order = {
    'info': {
        'success': True,
        'message': '',
        'result': {'uuid': 'c9cfdd6f-9d69-421b-8aaf-b45e0ca6ff5c'}},
    'id': 'c9cfdd6f-9d69-421b-8aaf-b45e0ca6ff5c',
    'symbol': 'ETH/USDT',
    'type': 'limit',
    'side': 'buy',
    'status': 'open'
}

bittrex_create_limit_sell_order = {
    'info': {
        'success': True,
        'message': '',
        'result': {'uuid': '206ca7b0-6bec-4af3-be14-5fab6d6328d1'}},
    'id': '206ca7b0-6bec-4af3-be14-5fab6d6328d1',
    'symbol': 'ETH/USDT',
    'type': 'limit',
    'side': 'sell',
    'status': 'open'
}

bittrex_fetch_order_open_status = {
    'info':
        {'AccountId': None,
         'OrderUuid': '309ab197-83e9-49e0-90ac-7c9942ec010b',
         'Exchange': 'BTC-NEO',
         'Type': 'LIMIT_BUY',
         'Quantity': 3.0,
         'QuantityRemaining': 3.0,
         'Limit': 0.00489211,
         'Reserved': 0.01467633,
         'ReserveRemaining': 0.01467633,
         'CommissionReserved': 3.669e-05,
         'CommissionReserveRemaining': 3.669e-05,
         'CommissionPaid': 0.0,
         'Price': 0.0,
         'PricePerUnit': None,
         'Opened': '2018-06-16T23:52:19.11',
         'Closed': None,
         'IsOpen': True,
         'Sentinel': 'e91cc46e-0ac5-4e27-b026-bb305ed76b73',
         'CancelInitiated': False,
         'ImmediateOrCancel': False,
         'IsConditional': False,
         'Condition': 'NONE',
         'ConditionTarget': None},
    'id': '309ab197-83e9-49e0-90ac-7c9942ec010b',
    'timestamp': 1529193139011,
    'datetime': '2018-06-16T23:52:19.110Z',
    'lastTradeTimestamp': None,
    'symbol': 'NEO/BTC',
    'type': 'limit',
    'side': 'buy',
    'price': 0.00489211,
    'cost': 0.01467633,
    'average': None,
    'amount': 3.0,
    'filled': 0.0,
    'remaining': 3.0,
    'status': 'open',
    'fee': {'cost': 0.0,
            'currency': 'BTC'}}

# Same format as open order response except for the following:
bittrex_fetch_order_filled_status = {
    'info': {
        'QuantityRemaining': 0.0,
        'CommissionPaid': 4.381e-05,
        'Price': 0.01752657,
        'PricePerUnit': 0.00584219,
        'Closed': '2018-06-17T00:01:17.51',
        'IsOpen': False,
        'Sentinel': '6b0014d0-084b-4b00-9a91-0c7f42494788'},
    'lastTradeTimestamp': 1529193677051,
    'average': 0.00584219,
    # order amount is filled
    'filled': 3.0,
    # 0 remaining
    'remaining': 0.0,
    'status': 'closed',
    'fee': {'cost': 4.381e-05,
            'currency': 'BTC'}}

# Same format as open order response except for the following:
bittrex_fetch_order_cancelled_status = {
    'info': {
        'Closed': '2018-06-16T23:57:20.787',
        'IsOpen': False,
        'Sentinel': 'fa9b6db0-5ea6-4879-9961-74692e4eaadc',
        'CancelInitiated': True},
    'id': '309ab197-83e9-49e0-90ac-7c9942ec010b',
    'lastTradeTimestamp': 1529193440787,
    'status': 'canceled'}

# List[Dict]. Each Dict is same format as open order response except for the following:
bittrex_closed_orders = [
    {
        # Missing the following fields: AccountId, Reserved, ReserveRemaining, CommissionReserved,
        # CommissionReserveRemaining, CommissionPaid, IsOpen, Sentinel, CancelInitiated
        'info': {
            # Instead of Opened
            'TimeStamp': '2018-05-22T04:07:11.73',
            # Instead of Type
            'OrderType': 'LIMIT_SELL',
            # Instead of ComissionReserved
            'Commission': 0.00023516
        },
        # All of the other top-level fields are the same
    }
]

bittrex_fetch_open_orders = [
    {
        # Missing the following fields: AccountId, Reserved, ReserveRemaining, CommissionReserved,
        # CommissionReserveRemaining, IsOpen, Sentinel, CancelInitiated
        # Unlike fetch_closed_orders, is not missing the CancelInitiated or the CommissionPaid fields
        'info': {
            'Uuid': None,
            }
    }]

bittrex_ticker = {'symbol': 'ZEC/USDT',
                  'timestamp': 1524789534807,
                  'datetime': '2018-04-27T00:38:55.807Z',
                  'high': 304.46499976,
                  'low': 274.00000001,
                  'bid': 301.0,
                  'ask': 303.650305,
                  'vwap': None,
                  'open': None,
                  'close': None,
                  'first': None,
                  'last': 303.0,
                  'change': 0.10583941601803502,
                  'percentage': None,
                  'average': None,
                  'baseVolume': 1272.73998003,
                  'quoteVolume': 366163.62504023,
                  'info': {'MarketName': 'USDT-ZEC',
                           'High': 304.46499976,
                           'Low': 274.00000001,
                           'Volume': 1272.73998003,
                           'Last': 303.0,
                           'BaseVolume': 366163.62504023,
                           'TimeStamp': '2018-04-27T00:38:54.807',
                           'Bid': 301.0,
                           'Ask': 303.650305,
                           'OpenBuyOrders': 328,
                           'OpenSellOrders': 623,
                           'PrevDay': 274.00000001,
                           'Created': '2017-07-14T17:10:10.673'}}