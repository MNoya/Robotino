import time
import re
import sqlite3

from datetime import datetime

from slackclient import SlackClient
from decouple import config

# instantiate Slack client
slack_client = SlackClient(config('SLACK_BOT_TOKEN'))

# user ID in Slack: value is assigned after the bot starts up
bot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
COMMAND_LIST = ['pyramid `:emoji-code:` <optional-number>']
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
DB_NAME = 'messages.db'


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            if event["channel"] == "frases-epicas":
                store_message(event['text'], event['user'])

            user_id, message = parse_direct_mention(event["text"])
            if user_id == bot_id:
                return message, event["channel"]

    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    default_response = "Not sure what you mean. Try: {}.".format(COMMAND_LIST)

    if 'pyramid' in command:
        handle_pyramid(command, channel)

    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=default_response
        )


def handle_pyramid(command, channel):
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
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=emoji * i
        )


def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        creation_sql = "CREATE TABLE messages(date text, message text, user text)"
        print(creation_sql)
        c.execute(creation_sql)
        conn.commit()
        print("Table created!")
    except:
        pass

    conn.close()


def store_message(message, user):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_now = datetime.now().strftime("%Y-%m-%d")
    print("Saving message for date {}, submitted by {}".format(date_now, user))
    try:
        creation_sql = "INSERT INTO messages('', message, user)".format(date_now)
        print(creation_sql)
        c.execute(creation_sql)
        conn.commit()
        print("Message saved: {}".format(message))
    except:
        pass

    conn.close()


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        setup_database()

        # Read bot's user ID by calling Web API method `auth.test`
        bot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
