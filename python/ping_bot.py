from flask import Flask
from threading import Thread

app = Flask("")


@app.route("/")
def home():
    return "Skrt skrt we live."


def run():
    app.run(host="0.0.0.0", port=8080)


def ping_bot():
    t = Thread(target=run)
    t.start()
