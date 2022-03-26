import re
from flask import Flask, request, render_template, send_file
from muse_handler import harmonize
from music21 import note, stream, converter, chord
app = Flask(__name__)


@app.route("/api/file", methods=['POST'])
def index():
    file = request.files.get('file')
    file.save('res/' + file.filename)

    p = harmonize("tmp.mid")
    p.write('midi','res.mid')


    
    #p.plot()
    return send_file('res.mid')



if __name__ == "__main__":
    app.run()
