from flask import Flask, render_template
import flask
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def assign():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=8080)


