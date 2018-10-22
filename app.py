# __author__ = ritvikareddy
# __date__ = 10/1/18

import json
import logging
import os
import random
import re
import requests
import sys
import xmltodict

from datetime import datetime
from flask import Flask, request
from xml.etree import ElementTree

PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
GOODREADS_KEY = os.environ["GOODREADS_API_KEY"]

app = Flask(__name__)

@app.route('/')
def hello():
    log("someone hit the base endpoint")
    return "Hello World!", 200


@app.route('/privacy')
def privacy_policy():
    log("someone hit the privacy policy endpoint")

    return """<head> <title>Privacy Policy</title> </head> <body> <h2>The Good Reader Privacy Policy</h2> <p 
    style="font-size: 18px">This app 
    is built for educational purposes and does not collect any data or personal information of the user. This app is 
    not intended to be used for any commercial purposes. </p> </body> """, 200


@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            log("Invalid verification token")
            return "Invalid Verification Token", 403
        log("Returned verification token")
        return request.args["hub.challenge"], 200
    log("No verification token received")
    return "Hello World !!", 200


@app.route('/', methods=['POST'])
def receive_message():

    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"][
                        "id"]
                    message_text = messaging_event["message"]["text"]

                    for word in message_text.split():
                        if word.lower() in GREETING_INPUTS:
                            send_message(sender_id, random.choice(GREETING_RESPONSES))
                            return "ok", 200

                    if re.search('^#', message_text) is None:
                        send_message(sender_id, ERROR_MSG)
                        return "ok", 200

                    if '#author' in message_text:
                        get_author_details(sender_id, message_text)
                        return "ok", 200

                    log("Received a message from sender id {} saying {}".format(sender_id, str(message_text)))

    return "ok", 200


def send_message(recipient_id, message_text):
    log("sending message to {}: {}".format(recipient_id,message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


GREETING_INPUTS = ['hi', 'hey', 'hello', 'ssup', 'sup', "what's up", 'heyy', 'greetings', 'there']
GREETING_RESPONSES = ['Hi there!', 'Hello', 'Hi', 'Happy to help you!', 'Hey there!', 'Hey']
ERROR_MSG = 'I am sorry, I cannot seem to understand what you are saying'


def get_author_details(sender_id, message_text):

    author_name = message_text.split('#author')[-1]
    response = requests.get('https://www.goodreads.com/api/author_url/'+author_name+'?key='+GOODREADS_KEY)
    response_dict = xmltodict.parse(response.content)
    reply_text = 'Did you mean '+response_dict['GoodreadsResponse']['author']['name']+'?. Here is the link - ' + \
                 response_dict['GoodreadsResponse']['author']['link']

    send_message(sender_id, reply_text)


def log(msg):
    try:
        print(u"{}: {}".format(datetime.now(), str(msg)))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run()
