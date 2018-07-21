"""
Runtime properties.

"ab" = "arbitrage bot"

Ideally a config file like .toml or .yaml would be used, but this works for now.
"""
import os


class AwsProperties:
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_access_key_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

    @classmethod
    def set_properties_from_env_variables(cls):
        cls.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        cls.aws_access_key_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')


class DatabaseProperties:
    local_db_password = os.environ.get('LOCAL_DB_PASSWORD', '')
    local_db_username = os.environ.get('LOCAL_DB_USERNAME', '')
    prod_db_password = os.environ.get('PROD_DB_PASSWORD', '')
    prod_db_username = os.environ.get('PROD_DB_USERNAME', '')
    rds_host = os.environ.get('RDS_HOST', '')

    @classmethod
    def set_properties_from_env_variables(cls):
        """
        Sometimes the environment variables that this class inspects have not been set when this class is evaluated.
        In those situations, call this method after environment variables have been set.

        Returns:

        """
        cls.local_db_password = os.environ.get('LOCAL_DB_PASSWORD', '')
        cls.local_db_username = os.environ.get('LOCAL_DB_USERNAME', '')
        cls.prod_db_password = os.environ.get('PROD_DB_PASSWORD', '')
        cls.prod_db_username = os.environ.get('PROD_DB_USERNAME', '')
        cls.rds_host = os.environ.get('RDS_HOST', '')


class EnvProperties:
    debug = os.environ.get('DEBUG', 'False') == 'True'
    env = os.environ.get('ENV')
    is_prod = env == 'prod'


class OrderExecutionProperties:
    # How many times to check the status of an order after placing it to see if status has changed
    num_order_status_checks = os.environ.get('NUM_ORDER_STATUS_CHECKS', 20)
    # How much time to sleep between order status checks
    sleep_time_sec_between_order_checks = os.environ.get('SLEEP_TIME_SEC_BETWEEN_ORDER_CHECKS', 2)


class S3:
    output_bucket = os.environ.get('OUTPUT_BUCKET')
