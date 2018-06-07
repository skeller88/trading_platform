import tweepy


class Stream(tweepy.Stream):
    """
    Bridge class. Invoke like so:
    stream = Stream(auth=auth, listener=stream_listener)
    """