from tweepy import OAuthHandler

from trading_platform.twitter.twitter_properties import TwitterProperties


class Auth:
    def __init__(self):
        self.handler = OAuthHandler(TwitterProperties.consumer_key, TwitterProperties.consumer_secret)
        self.handler.set_access_token(TwitterProperties.access_token, TwitterProperties.access_token_secret)