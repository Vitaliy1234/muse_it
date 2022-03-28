from time import time
from os import remove
from flask import Flask, request, send_file
from muse_handler import harmonize
app = Flask(__name__)


@app.route("/api/file", methods=['POST'])
def index():
    file = request.files.get('file')
    tmp_filename = f'tmp_{file.filename}_{time()}.mid'
    res_filename = f'res.mid'
    file.save(tmp_filename)

    p = harmonize(tmp_filename)
    p.write('midi', res_filename)
    remove(tmp_filename)
    return send_file(res_filename)


if __name__ == "__main__":
    app.run()
