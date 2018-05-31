class AlertService:
    def __init__(self, client):
        """

        Args:
            client: sends the alert
        """
        self.client = client

    def send_alert(self, topic_arn, message):
        """
        Args:
            message str:

        Returns:

        """
        # try:
        self.client.publish(TopicArn=topic_arn, Message=message)
        # except Exception:
        #     print('Exception when sending alert. Swallowing for now so the app doesn\'t crash.')
        #     traceback.print_stack()
