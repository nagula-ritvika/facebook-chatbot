# __author__ = ritvikareddy
# __date__ = 10/1/18

# import pymessenger
import datetime
import json
import sys

import requests
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/privacy')
def privacy_policy():
    return """<head> <title>Privacy Policy</title> </head> <body> <h2>The Good Reader Privacy Policy</h2> <p 
    style="font-size: 18px">This app 
    is built for educational purposes and does not collect any data or personal information of the user. This app is 
    not intended to be used for any commercial purposes. </p> </body> """, 200


@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Invalid Verification Token", 403
        return request.args["hub.challenge"], 200

    return "Hello World !!", 200


@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"][
                        "id"]
                    message_text = messaging_event["message"]["text"]
                    app.logger.info("Sender id:", sender_id, "Message", message_text)

                    send_message(sender_id, "roger that!")

    return "ok", 200


def send_message(recipient_id, message_text):
    # log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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
        app.logger.info((r.status_code))
        app.logger.err(r.text)


# def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
#     try:
#         if type(msg) is dict:
#             msg = json.dumps(msg)
#         else:
#             msg = msg.format(*args, **kwargs)
#         print(u"{}: {}".format(datetime.now(), msg))
#     except UnicodeEncodeError:
#         pass  # squash logging errors in case of non-ascii text
#     sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)



# $ export FLASK_APP = hello.py
# $ flask run