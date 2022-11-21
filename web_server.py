from time import time
import os
from os import remove
from flask import Flask, request, send_file, render_template
from muse_handler import harmonize, bach_style
from gpt2_model.sample import make_bach_chorale

app = Flask(__name__)


@app.route("/api/file", methods=['POST'])
def index():
    file = request.files.get('file')
    tmp_filename = f'tmp_{file.filename}_{time()}.mid'
    res_filename = f'res{file.filename}.mid' #restest.mid.mid #res/test.mid
    # res_filename = os.path.join('res', file.filename)
    print(f'res_filename {res_filename}')
    print(f'tmp_filename {tmp_filename}')
    file.save(tmp_filename)

    generatorStyle = request.values.get("generatorStyle")

    generatorStyle = 'chords'
    if generatorStyle == 'chords':
        p = harmonize(tmp_filename)
        p.write('midi', res_filename)
    elif generatorStyle == 'bach':
        res_filename = make_bach_chorale(tmp_filename, res_filename)

    remove(tmp_filename)
    return send_file(res_filename)

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
