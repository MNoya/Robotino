import time
import re

from datetime import datetime
from random import choice

from channel_ids import FRASES_EPICAS, BOT_TEST
from slack_api import SlackAPI
from db import DB

RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
COMMAND_HELP = [
    '_pyramid `:emoji-code:` <optional-number>_',
    '_epic <optional-text-filter>_'
]
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


class Robotino(object):

    def __init__(self):
        self.slack = SlackAPI()
        self.db = DB()
        self.bot_id = None

    def run(self):
        if self.slack.connect():
            print("Robotino connected and running!")
            self.db.setup()
            self.bot_id = self.slack.get_bot_id()
            while True:
                command, channel = self.parse_bot_commands(self.slack.read())
                try:
                    if command:
                        self.handle_command(command, channel)
                except:
                    self.slack.post_message(channel, ":weird:")
                    self.slack.post_message(channel, "I just crashed horribly :boom:\nTell my family I'm sorry")
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
                print("[user:{}][channel:{}]: {}".format(event['user'], event['channel'], event['text']))
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.bot_id:
                    return message, event["channel"]
                else:
                    self.db.save_message(
                        text=event['text'],
                        user=event['user'],
                        channel=event['channel'],
                        date=datetime.now()
                    )

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
        default_response = "Not sure what you mean.\nTry:\n    {}".format('\n    '.join(COMMAND_HELP))

        if 'pyramid' in command:
            self.handle_pyramid(command, channel)
        elif 'epic' in command:
            self.handle_epic_phrase(command, channel)
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

    def handle_epic_phrase(self, command, channel):
        ignored_words = ['epic', 'phrase', 'frase', 'epica', 'de', 'for', 'of']
        text_filter = []
        for command_part in command.split(" "):
            if command_part.strip() and command_part not in ignored_words:
                text_filter.append(command_part)
        text_filter = " ".join(text_filter)
        messages = self.db.get_messages(FRASES_EPICAS, text_filter)

        if not messages:
            if not text_filter:
                response = "Sorry, I don't have any epic phrase at the moment."
            else:
                response = "Sorry, I don't have any epic phrase for '{}'. Try a wider search.".format(text_filter)
        else:
            random_message = choice(messages)
            text_parts = random_message.text.split('\n')
            if len(text_parts) > 1:
                quoted_text = ""
                for text in text_parts:
                    quoted_text += "> {}\n".format(text)
            else:
                quoted_text = "> {}".format(random_message.text)

            response = "{}\n{}".format(quoted_text, random_message.date.strftime("%-d %b. %Y"))

        print(response)
        self.slack.post_message(channel, text=response)


if __name__ == "__main__":
    Robotino().run()
