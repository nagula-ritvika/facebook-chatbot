# __author__ = ritvikareddy2
# __date__ = 10/1/18

# import pymessenger

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def get_message():
    # if request.method:
    #     token_sent = request.args.get("hub.verify_token")
    #     return verify_fb_token(token_sent)
    # else:


    return 2022659526

# $ export FLASK_APP = hello.py
# $ flask run