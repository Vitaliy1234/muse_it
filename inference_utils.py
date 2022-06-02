# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import numpy as np
import tensorflow as tf

import path_utils, midi_utils


def generate_pianoroll(generator, conditioned_track, noise_vector=None):
    if noise_vector == None:
        noise_vector = tf.random.truncated_normal((1, 2, 8, 512))
    return generator((conditioned_track, noise_vector), training=False)


def generate_midi(generator, saveto_dir, input_midi_file='./Experiments/data/happy_birthday_easy.mid'):
    conditioned_tracks = midi_utils.get_conditioned_track(midi=input_midi_file)

    result_numpy_piano = []

    for conditioned_track in conditioned_tracks:
        generated_pianoroll = generate_pianoroll(generator, conditioned_track)
        numpy_piano = generated_pianoroll.numpy()
        result_numpy_piano.append(numpy_piano)
    destination_path = path_utils.new_temp_midi_path(saveto_dir=saveto_dir)

    midi_utils.save_pianoroll_as_midi(np.concatenate(result_numpy_piano, axis=1), destination_path=destination_path)
    return destination_path

