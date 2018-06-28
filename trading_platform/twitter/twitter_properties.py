import os

from trading_platform.aws_utils.parameter_store import get_parameter


class TwitterProperties:
    consumer_key = None
    consumer_secret = None
    access_token = None
    access_token_secret = None

    @classmethod
    def set_properties_from_env_variables(cls):
        """
        Invoke this method after all environment variables have been loaded.
        Returns:

        """
        cls.consumer_key = os.environ.get('CONSUMER_KEY')
        cls.consumer_secret = os.environ.get('CONSUMER_SECRET')

        # After the step above, you will be redirected to your app's page.
        # Create an access token under the the "Your access token" section
        cls.access_token = os.environ.get('ACCESS_TOKEN')
        cls.access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

    @classmethod
    def load_properties_from_parameter_store_and_set(cls):
        twitter_credentials = get_parameter('twitter_credentials')
        for name, value in twitter_credentials.items():
            os.environ[name] = value
        cls.set_properties_from_env_variables()
