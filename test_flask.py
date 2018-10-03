# __author__ = ritvikareddy2
# __date__ = 10/1/18

# import pymessenger

from flask import Flask, request
import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_message():
    if request.method == 'GET' and request.args.get("hub.verify_token") == os.environ['VERIFY_TOKEN']:
        return request.args.get("hub.challenge")
    return "Invalid Token Verification"

# $ export FLASK_APP = hello.py
# $ flask run