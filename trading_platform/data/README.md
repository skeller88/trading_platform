# TODO - add explanations of what all the files and directories are


## `arbitrage_finder`- tickers logged by the arbitrage_finder lambda

`derived` - data is grouped by exchange, by pair, and by day.

`windows/ticker` - tickers grouped by day (tickers are logged to S3 every minute). 
Created by src/analytics/fetch_s3_ticker_objects.py. 

## `kaiko` - historical data purchased from kaiko

## `transaction_times` - historical transaction time data for ETH and BTC

## `withdrawal_fees` - current withdrawal fees on Binance and Bittrex