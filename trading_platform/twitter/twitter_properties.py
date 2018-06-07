import os


class TwitterProperties:
    consumer_key = os.environ.get('CONSUMER_KEY')
    consumer_secret = os.environ.get('CONSUMER_SECRET')

    # After the step above, you will be redirected to your app's page.
    # Create an access token under the the "Your access token" section
    access_token = os.environ.get('ACCESS_TOKEN')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')