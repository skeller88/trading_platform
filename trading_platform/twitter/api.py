import tweepy


class Api(tweepy.API):
    @classmethod
    def instance(cls) -> 'Api':
        auth = OAuthHandler(TwitterProperties.consumer_key, TwitterProperties.consumer_secret)
        auth.set_access_token(TwitterProperties.access_token, TwitterProperties.access_token_secret)
        return cls(auth)