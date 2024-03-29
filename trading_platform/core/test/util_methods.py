import json
import logging

from nose.tools import eq_, assert_almost_equal

from trading_platform.exchanges.data.financial_data import FinancialData


def eq_ignore_certain_fields(a, b, fields_to_ignore):
    for k, v in a.__dict__.items():
        if k not in fields_to_ignore:
            eq_(a.__dict__.get(k), b.__dict__.get(k), 'Instance attribute {0}: expected {1}, got {2}'.format(k, v, b.__dict__.get(k)))


def compare_orders(order1, order2):
    numerical_fields = ['amount', 'filled', 'price', 'remaining']
    fields_to_ignore = ['app_create_timestamp', 'exchange_timestamp'] + numerical_fields
    eq_ignore_certain_fields(order1, order2, fields_to_ignore=fields_to_ignore)
    for field in numerical_fields:
        assert_almost_equal(order1.__dict__.get(field), order2.__dict__.get(field),
                            places=FinancialData.five_places)


def compare_dicts(dict1, dict2):
    dict1_json = json.dumps(dict1, sort_keys=True, indent=2)
    dict2_json = json.dumps(dict2, sort_keys=True, indent=2)
    eq_(dict1_json, dict2_json)


def disable_debug_logging():
    """
    When running tests in debug mode, too many log statements are printed out.
    Returns:

    """
    logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('nose').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)