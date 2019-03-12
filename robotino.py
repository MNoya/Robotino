import time
import re

from channel_ids import FRASES_EPICAS
from db import setup_database, store_message
from slack_api import SlackAPI

RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
COMMAND_LIST = ['pyramid `:emoji-code:` <optional-number>']
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


class Robotino(object):

    def __init__(self):
        self.slack = SlackAPI()
        self.bot_id = None

    def run(self):
        if self.slack.connect():
            print("Starter Bot connected and running!")
            setup_database()

            self.bot_id = self.slack.get_bot_id()
            while True:
                command, channel = self.parse_bot_commands(self.slack.read())
                if command:
                    self.handle_command(command, channel)
                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")

    def parse_bot_commands(self, slack_events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                print(event['user'], event['channel'], event['text'])
                if event["channel"] == FRASES_EPICAS:
                    store_message(event['text'], self.slack.get_user_name(event['user']))

                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.bot_id:
                    return message, event["channel"]

        return None, None

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def handle_command(self, command, channel):
        """
            Executes bot command if the command is known
        """
        default_response = "Not sure what you mean. Try: {}.".format(COMMAND_LIST)

        if 'pyramid' in command:
            self.handle_pyramid(command, channel)
        else:
            self.slack.post_message(channel, default_response)

    def handle_pyramid(self, command, channel):
        command_args = command.split(' ')
        emoji = ":party_parrot:"
        for arg in command_args:
            if arg.startswith(":"):
                emoji = arg.strip()
        number = 5
        for arg in command_args:
            try:
                number = int(arg)
            except:
                continue

        iterations = list(range(1, number + 1)) + list(reversed(range(1, number)))
        print("Creating emoji loop: pyramid {} {}".format(emoji, iterations))
        for i in iterations:
            self.slack.post_message(channel, text=emoji * i)


if __name__ == "__main__":
    Robotino().run()
