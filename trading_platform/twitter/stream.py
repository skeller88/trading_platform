import os
from typing import Type

import tweepy
from tweepy import OAuthHandler
import sys; sys.path.append(os.getcwd())
from trading_platform.twitter.stream_listener import StreamListener
from trading_platform.twitter.twitter_properties import TwitterProperties


class Stream(tweepy.Stream):
    """
    Bridge class. Invoke like so:
    stream = Stream(auth=auth, listener=stream_listener)
    """
    @classmethod
    def for_listener(cls, stream_listener: Type[StreamListener]) -> 'Stream':
        auth = OAuthHandler(TwitterProperties.consumer_key, TwitterProperties.consumer_secret)
        auth.set_access_token(TwitterProperties.access_token, TwitterProperties.access_token_secret)
        api = tweepy.API(auth)
        return cls(auth=api.auth, listener=stream_listener)
