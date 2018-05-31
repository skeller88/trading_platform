"""
Runtime properties.

"ab" = "arbitrage bot"

Ideally a config file like .toml or .yaml would be used, but this works for now.
"""
import os


class Database:
    local_db_password = os.environ.get('LOCAL_DB_PASSWORD', '')
    local_db_username = os.environ.get('LOCAL_DB_USERNAME', '')
    prod_db_password = os.environ.get('PROD_DB_PASSWORD', '')
    prod_db_username = os.environ.get('PROD_DB_USERNAME', '')
    rds_host = os.environ.get('RDS_HOST', '')


class EnvProperties:
    debug = os.environ.get('DEBUG', 'False') == 'True'
    env = os.environ.get('ENV')
    is_prod = env == 'prod'


class S3:
    output_bucket = os.environ.get('OUTPUT_BUCKET', 'arbitrage-bot')


class SNS:
    arbitrage_alerts_topic_arn = os.environ.get('ARBITRAGE_ALERTS_TOPIC_ARN')
