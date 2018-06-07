from __future__ import absolute_import, print_function

import tweepy


class StreamListener(tweepy.streaming.StreamListener):
    """This is a bridge class in case tweepy is no longer used.
    """