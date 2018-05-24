ERROR_PREFIX = 'ERROR - {0}'
EXCHANGE_SUFFIX = ' - {0}'

BALANCE_ERR = ERROR_PREFIX.format('fetching balance') + EXCHANGE_SUFFIX
CANCEL_ORDER_ERR = ERROR_PREFIX.format('cancelling order') + EXCHANGE_SUFFIX
CREATE_ORDER_ERR = ERROR_PREFIX.format('placing order') + EXCHANGE_SUFFIX
LIMIT_BUY_ORDER_ERR = ERROR_PREFIX.format('creating limit buy order') + EXCHANGE_SUFFIX
LIMIT_SELL_ORDER_ERR = ERROR_PREFIX.format('creating limit sell order') + EXCHANGE_SUFFIX
OPEN_ORDERS_ERR = ERROR_PREFIX.format('fetching open orders') + EXCHANGE_SUFFIX
TICKER_ERR = ERROR_PREFIX.format('fetching tickers') + EXCHANGE_SUFFIX

BALANCE_ATTEMPT = 'fetching balance' + EXCHANGE_SUFFIX
CANCEL_ORDER_ATTEMPT = 'cancelling order' + EXCHANGE_SUFFIX
CREATE_ORDER_ATTEMPT = 'placing order' + EXCHANGE_SUFFIX
LIMIT_BUY_ORDER_ATTEMPT = 'creating limit buy order' + EXCHANGE_SUFFIX
LIMIT_SELL_ORDER_ATTEMPT = 'creating limit sell order' + EXCHANGE_SUFFIX
OPEN_ORDERS_ATTEMPT = 'fetching open orders' + EXCHANGE_SUFFIX
TICKER_ATTEMPT = 'fetching tickers' + EXCHANGE_SUFFIX