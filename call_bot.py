from dotenv import load_dotenv
from dotenv.main import dotenv_values
import os
from slackclient import SlackClient
from twilio.rest import Client
import phonenumbers
import time
import uuid



config = dotenv_values(".env")

BOT_ID = config['BOT_ID']
TWILIO_NUMBER = config['TWILIO_NUMBER']

AT_BOT = "<@" + BOT_ID + ">"
CALL_COMMAND = "call"
TWIMLET = 'https://twimlets.com/echo?Twiml=%3CResponse%3E%0A%20%20%3CDial%3E%3CConference%3E{{name}}%3C%2FConference%3E%3C%2FDial%3E%0A%3C%2FResponse%3E&'


slack_client = SlackClient(
    config['SLACK_TOKEN']
)
twilio_client = Client(config['TWILIO_ACCOUNT_SID'], config['TWILIO_AUTH_TOKEN'])

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + \
               CALL_COMMAND + "* command with numbers, delimited by spaces."
    if command.startswith(CALL_COMMAND):
        response = call_command(command[len(CALL_COMMAND):].strip())
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def call_command(phone_numbers_list_as_string):
    """
        Validates a string of phone numbers, delimited by spaces, then
        dials everyone into a single call if they are all valid.
    """
    # generate random ID for this conference call
    conference_name = str(uuid.uuid4())
    # split phone numbers by spaces
    phone_numbers = phone_numbers_list_as_string.split("\xa0")
    print(phone_numbers)
    # make sure at least 2 phone numbers are specified
    print(len(phone_numbers))
    if len(phone_numbers) > 1:
        print('here')
        # check that phone numbers are in a valid format
       
        are_numbers_valid, response = validate_phone_numbers(phone_numbers)
        if are_numbers_valid:
            # all phone numbers are valid, so dial them together
            for phone_number in phone_numbers:
                real_number = phone_number[-13:-1]
                twilio_client.calls.create(to=real_number,
                                           from_=TWILIO_NUMBER,
                                           url=TWIMLET.replace('{{name}}',
                                           conference_name))
            response = "calling: " + phone_numbers_list_as_string
    else:
        response = "the *call* command requires at least 2 phone numbers"
    return response


def validate_phone_numbers(phone_numbers):
    """
        Uses the python-phonenumbers library to make sure each phone number
        is in a valid format.
    """
    invalid_response = " is not a valid phone number format. Please correct the number and retry. No calls have yet  been dialed."
    print('before for loop')
    for phone_number in phone_numbers:
        print('in for loop')
        try:
            print('inside try catch')
            print((phone_number[-13:-1]))
            validate_phone_number = phonenumbers.parse(phone_number[-13:-1])
            print(validate_phone_number)
            if not phonenumbers.is_valid_number(validate_phone_number):
                return False, phone_number,   invalid_response
        except:
            return False, phone_number,   invalid_response
    return True, None


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is a firehose of data, so
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                
                return output['text'].split(AT_BOT)[1].strip(), output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("CallBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")