import csv
import os
import pandas
import re
import requests
import shutil
from bs4 import BeautifulSoup
from typing import Dict, Match
from typing.re import Pattern

from trading_platform.exchanges.data import standardizers
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData


class WithdrawalFeesService:
    """
    Fetches withdrawal fees via web scraping.
    """
    exchangebit_url= 'https://exchangebit.info'
    anythingcrypto_url = 'https://anythingcrypto.com/exchange-withdrawal-fees'
    currency_regex: Pattern = re.compile('\((.+)\)')
    withdrawal_fee_regex: Pattern = re.compile('([0-9]+\.[0-9]+)')

    withdrawal_fees_dir = os.path.dirname(__file__).replace('exchanges', 'withdrawal_fees')

    @classmethod
    def for_exchange_from_anythingcrypto(cls, exchange_id, withdrawal_fees_dir):
        """
        Supports the following exchanges:
        - Binance
        - Bittrex
        - Coinbase
        - Kraken
        - Kucoin
        - Poloniex

        Not supported:
        - Bitflyer
        - Gdax
        - Gemini
        Args:
            exchange_id:
            withdrawal_fees_dir:

        Returns:

        """
        exchange_name = exchange_ids.to_name(exchange_id)
        if not os.path.exists(withdrawal_fees_dir):
            os.makedirs(withdrawal_fees_dir)

        # "wf" short for "withdrawal fee"
        wf_response = requests.get(url='{0}/{1}'.format(cls.anythingcrypto_url, exchange_name.lower()))
        wf_html = BeautifulSoup(wf_response.text, 'html.parser')

        filename = '{0}_withdrawal_fees.csv'.format(exchange_id)
        with open(os.path.join(withdrawal_fees_dir, filename), 'w+') as dest_file:
            writer = csv.DictWriter(dest_file, fieldnames=['currency', 'withdrawal_fee'])
            writer.writeheader()

            rows_to_skip = 3
            skipped = 0

            for tr in wf_html.find_all('tr'):
                if skipped < rows_to_skip:
                    skipped += 1
                    continue

                groups: Match = cls.currency_regex.search(tr.contents[0].text)
                if groups is None:
                    continue

                currency = standardizers.currency(groups.group(1))
                groups: Match = cls.withdrawal_fee_regex.search(tr.contents[1].span.text)
                if groups is None:
                    continue

                withdrawal_fee = FinancialData(groups.group(0))

                writer.writerow({
                    'currency': currency,
                    'withdrawal_fee': withdrawal_fee
                })

    @classmethod
    def for_exchange_from_exchangebit(cls, exchange_id, withdrawal_fees_dir):
        """
        Fetches withdrawal fees from a website, parses them, and writes to a csv.
        Args:
            exchange_id:

        Returns:

        """
        exchange_name = exchange_ids.to_name(exchange_id)
        if not os.path.exists(withdrawal_fees_dir):
            os.makedirs(withdrawal_fees_dir)

        # "wf" short for "withdrawal fee"
        wf_response = requests.get(url='{0}/{1}'.format(cls.exchangebit_url, exchange_name.lower()))
        wf_html = BeautifulSoup(wf_response.text, 'html.parser')

        filename = '{0}_withdrawal_fees.csv'.format(exchange_id)
        with open(os.path.join(withdrawal_fees_dir, filename), 'w+') as dest_file:
            writer = csv.DictWriter(dest_file, fieldnames=['currency', 'withdrawal_fee'])
            writer.writeheader()
            tbody = wf_html.find('tbody')
            for tr in tbody.find_all('tr'):
                anchor = tr.a
                if anchor is not None:
                    writer.writerow({
                        'currency': standardizers.currency(anchor.text),
                        'withdrawal_fee': FinancialData(tr.contents[7].text)
                    })

    @classmethod
    def update_withdrawal_fees_files(cls):
        for exchange_id in exchange_ids.all_ids:
            if exchange_id in [exchange_ids.binance, exchange_ids.bittrex]:
                cls.for_exchange_from_exchangebit(exchange_id=exchange_id, withdrawal_fees_dir=cls.withdrawal_fees_dir)
            else:
                cls.for_exchange_from_anythingcrypto(exchange_id=exchange_id, withdrawal_fees_dir=cls.withdrawal_fees_dir)

        # Gdax is now called coinbase pro, but ccxt uses the name Gdax.
        shutil.copy(os.path.join(cls.withdrawal_fees_dir, '{0}_withdrawal_fees.csv'.format(exchange_ids.coinbase)),
                    os.path.join(cls.withdrawal_fees_dir, '{0}_withdrawal_fees.csv'.format(exchange_ids.gdax)))

    @staticmethod
    def get_by_exchange_ids() -> Dict[int, pandas.DataFrame]:
        """
        Get withdrawal fees by exchange id.
        """
        withdrawal_fees_dir = os.path.dirname(__file__).replace('exchanges', 'withdrawal_fees')

        def withdrawal_df_for_exchange(exchange_id: int):
            filepath = os.path.join(withdrawal_fees_dir, '{0}_withdrawal_fees.csv'.format(exchange_id))
            if os.path.exists(filepath):
                return pandas.read_csv(filepath, index_col='currency')

            return pandas.DataFrame()

        return {exchange_id: withdrawal_df_for_exchange(exchange_id) for exchange_id in exchange_ids.all_ids}
