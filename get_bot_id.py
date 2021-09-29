from dotenv import load_dotenv
from dotenv.main import dotenv_values
import os
from slackclient import SlackClient


config = dotenv_values(".env")

BOT_NAME = 'Bot_Name'

slack_client = SlackClient(
    config['SLACK_TOKEN']
)


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    print(api_call)
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)
