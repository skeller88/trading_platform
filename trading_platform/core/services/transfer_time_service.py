import glob

import os

import datetime
import pandas


class TransferTimeService:
    """
    Retrieve time it takes to transfer a currency from one address to another. That time consists of the block time,
    and the number of confirmations needed. The block time is the time is takes for a new block to be added
    to a blockchain. The number of confirmations is the number of confirmed blocks containing a transaction that must
    be added before a transaction is recognized as completed by the exchange.

    Binance requires a min of 30 and max of 60 confirmations for ETH, min of 2 for BTC:
    https://support.binance.com/hc/en-us/articles/115003736451-Deposit-does-not-arrive

    Bittrex requires a min of 36 for ETH, min of 2 for BTC:
    https://bittrex.com/api/v1.1/public/getcurrencies

    Historical Ethereum data is from https://etherscan.io/chart/blocktime

    Historical Bitcoin data is from https://blockchain.info/charts/avg-confirmation-time?timespan=all
    """
    # median transaction times from historical data
    btc_default_transaction_time_min = 11
    eth_default_transaction_time_min = .5

    def __init__(self, source_dir, currencies):
        self.dfs = {}
        self.currencies = currencies
        for currency in currencies:
            files = glob.glob(os.path.join(source_dir, currency.lower() + '*'))
            if len(files) != 1:
                raise Exception('Expected 1 transaction fees file, found {0}'.format(len(files)))

            self.dfs[currency] = pandas.read_csv(files[0], index_col='datetime', parse_dates=True)

    def transfer_completion_datetime_for_currency_and_time(self, currency, transfer_start_datetime):
        """

        Args:
            currency:
            transfer_start_datetime datetime: Starting time of the transfer

        Returns datetime: when the transfer will be complete.

        """
        if currency == 'USDT':
            # https://support.kraken.com/hc/en-us/articles/203325283-How-long-do-cryptocurrency-deposits-take-
            return transfer_start_datetime + datetime.timedelta(minutes=60)
        # Assume with wire transfers, it will take a day. Needless to say, USD pairs probably won't be arbitraged
        elif currency == 'USD':
            return transfer_start_datetime + datetime.timedelta(minutes=24 * 60)
        elif currency not in self.currencies:
            raise Exception('currency {0} not supported'.format(currency))

        df = self.dfs[currency]
        datetime_to_nearest_day = transfer_start_datetime.round('D').timestamp()

        num_confirmations = 40 if currency == 'ETH' else 3

        if datetime_to_nearest_day in df.index:
            transaction_time = df.loc[datetime_to_nearest_day]['transaction_time']
            # ETH transaction times are in seconds, BTC transaction times are in minutes
            # TODO - standardize to minutes
            if currency == 'ETH':
                transaction_time = transaction_time / 60
        else:
            # default transaction times are already standardized to minutes
            transaction_time = self.eth_default_transaction_time_min if currency == 'ETH' else self.btc_default_transaction_time_min

        transaction_time_delta_min = transaction_time * num_confirmations
        return transfer_start_datetime + datetime.timedelta(minutes=transaction_time_delta_min)


            ### ipython work
            # Standardize transaction time files
            # filepath = os.path.join(os.getcwd().replace('notebooks', 'data/transfer_times'), 'btc_transfer_times.csv')
            # df = pd.read_csv(filepath, parse_dates=True)
            # df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
            # df['datetime'] = df['datetime'].apply(lambda x: x.timestamp())
            # df.to_csv(filepath)

            ## Get transaction time statistics for btc for all transaction times that aren't 0. We want to be
            # pessimistic and assume that transaction times will be high
            # df = pd.read_csv(filepath, parse_dates=True)
            # df = df[df['transaction_time'] > 0]
            # print(df.transaction_time.describe())
            # count
            # 1151.000000
            # mean
            # 9.676830
            # std
            # 3.296394
            # min
            # 4.766667
            # 25 % 7.466667
            # 50 % 8.650000
            # 75 % 11.266667
            # max
            # 47.733333

            ## Repeat for eth. Note that transaction times are in seconds for eth, not minutes.
            # df = pd.read_csv(filepath.replace('btc', 'eth'), parse_dates=True)
            # df = df[df['transaction_time'] > 0]
            # df.transaction_time.describe()
            # count
            # 963.000000
            # mean
            # 15.969605
            # std
            # 3.162363
            # min
            # 4.460000
            # 25 % 14.145000
            # 50 % 14.500000
            # 75 % 16.855000
            # max
            # 30.310000
            # Name: transaction_time, dtype: float64
