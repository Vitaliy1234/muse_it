from time import time
from os import remove
from flask import Flask, request, send_file

from muse_handler import harmonize, bach_style
from gpt2_model.sample import make_bach_chorale
app = Flask(__name__)


@app.route("/api/file", methods=['POST'])
def index():
    file = request.files.get('file')
    tmp_filename = f'tmp_{file.filename}_{time()}.mid'
    res_filename = f'res{file.filename}.mid'
    file.save(tmp_filename)

    generatorStyle = request.values.get("generatorStyle")

    if generatorStyle == 'chords':
        p = harmonize(tmp_filename)
        p.write('midi', res_filename)
    elif generatorStyle == 'bach':
        res_filename = make_bach_chorale(tmp_filename, res_filename)

    remove(tmp_filename)
    return send_file(res_filename)


if __name__ == "__main__":
    app.run()
