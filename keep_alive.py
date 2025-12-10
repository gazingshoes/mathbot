from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    # This keeps the web server running on port 8000
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()