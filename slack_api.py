from slackclient import SlackClient
from decouple import config


class SlackAPI(object):
    def __init__(self):
        self.client = SlackClient(config('SLACK_BOT_TOKEN'))

    def connect(self):
        return self.client.rtm_connect(with_team_state=False)

    def read(self):
        return self.client.rtm_read()

    def get_bot_id(self):
        return self.client.api_call("auth.test")["user_id"]

    def get_user_name(self, user_code):
        return self.client.api_call("users.info", user=user_code)['user']['name']

    def get_channel_name(self, channel_code):
        return self.client.api_call("channels.info", channel=channel_code)['channel']['name']

    def post_message(self, channel, text):
        self.client.api_call("chat.postMessage", channel=channel, text=text)
