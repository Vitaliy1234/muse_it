from flask import Flask, request
from muse_handler import harmonize
app = Flask(__name__)


@app.route("/api/file", methods=['POST'])
def index():
    print(request.data)

    result = ''
    return result


if __name__ == "__main__":
    app.run()
