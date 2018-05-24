import csv
import glob
import os

import pandas
import requests
from bs4 import BeautifulSoup
from pandas.errors import ParserError

from exchanges.src.data import standardizers
from exchanges.src.data.enums import exchange_names, exchange_ids
from exchanges.src.data.financial_data import FinancialData
from exchanges.src import withdrawal_fees_dfs


class WithdrawalFeesService:
    """
    This class only gets withdrawal fees for Binance and Bittrex.
    """
    exchangebit_url = 'https://exchangebit.info'

    @classmethod
    def for_exchange_from_exchangebit(cls, exchange_id, csv_dir):
        """
        Fetches withdrawal fees from a website, parses them, and writes to a csv.
        Args:
            exchange_id:

        Returns:

        """
        exchange_name = exchange_ids.to_name(exchange_id)
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)

        # "wf" short for "withdrawal fee"
        wf_response = requests.get(url='{0}/{1}'.format(cls.exchangebit_url, exchange_name.lower()))
        wf_html = BeautifulSoup(wf_response.text, 'html.parser')

        filename = '{0}_withdrawal_fees.csv'.format(exchange_name.lower())
        with open(os.path.join(csv_dir, filename), 'w') as dest_file:
            writer = csv.DictWriter(dest_file, fieldnames=['currency', 'withdrawal_fee'])
            writer.writeheader()

            for tr in wf_html.find_all('tr'):
                anchor = tr.a
                if anchor is not None:
                    currency = anchor.text

                    writer.writerow({
                        'currency': standardizers.currency(anchor.text),
                        'withdrawal_fee': FinancialData(tr.contents[7].text)
                    })

    @classmethod
    def update_withdrawal_fees_files(cls):
        # csv_dir is both the output and input location of .csv files containing withdrawal fees
        csv_dir = os.getcwd().replace('core/src/services', 'data/withdrawal_fees')
        # Currently exchangebit only supports binance and bittrex
        for exchange_id in [exchange_ids.binance, exchange_ids.bittrex]:
            cls.for_exchange_from_exchangebit(exchange_id, csv_dir)

    @staticmethod
    def for_exchange_from_csv(exchange_id, source_dir):
        """

        Args:
            exchange_id:
            source_dir:

        Returns pandas.DataFrame: withdrawal fees from csv file

        """
        exchange_name = exchange_ids.to_name(exchange_id)
        files = glob.glob(os.path.join(source_dir, exchange_name.lower() + '*'))
        if len(files) != 1:
            raise Exception('Expected 1 withdrawal fees file, found {0}'.format(len(files)))
        try:
            return pandas.read_csv(files[0], index_col='currency', engine='python')
        except ParserError:
            print('c engine')
            try:
                return pandas.read_csv(files[0], index_col='currency', engine='c')
            except ParserError:
                return pandas.read_csv(files[0], index_col='currency', compression='zip')


    @staticmethod
    def by_exchange_ids():
        """
        Get withdrawal fees by exchange id.

        Args:

        Returns dict(id, pandas.DataFrame):

        """
        return {
            exchange_ids.binance: withdrawal_fees_dfs.binance_withdrawal_fees_df,
            exchange_ids.bittrex: withdrawal_fees_dfs.bittrex_withdrawal_fees_df
        }

# Uncomment the line below in order to update the withdrawal fee files
# WithdrawalFeesService.update_withdrawal_fees_files()