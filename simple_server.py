from flask import Flask

app = Flask(__name__)

@app.route('/')
def index() -> str:
    return '<p>' + 'Hello Flask!' * 100 + '</p>'

app.run(debug=True)