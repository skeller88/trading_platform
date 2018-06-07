from trading_platform.twitter.auth import Auth
from trading_platform.twitter.stream_listener import StreamListener


class Stream:
    def __init__(self, auth: Auth, stream_listener: StreamListener):
        self.stream = Stream(auth, stream_listener)