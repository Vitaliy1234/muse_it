from flask import Flask
from muse_handler import harmonize
app = Flask(__name__)


@app.route("/&lt;username&gt;", methods=['GET'])
def index(username):
    return "Hello, %s!" % username


if __name__ == "__main__":
    app.run()
