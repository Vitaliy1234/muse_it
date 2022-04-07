from music21 import note, stream, converter, chord
from music21.analysis.discrete import DiscreteAnalysisException


HARMONY_RULES = [[1, 2, 3, 4, 5, 6],
                 [0, 2, 4],
                 [0, 3, 4, 5, 6],
                 [0, 1, 4],
                 [0, 2, 5, 6],
                 [0, 1, 2, 3],
                 [0]]


def harmonize(filename):
    score = converter.parse(filename)

    tone = score.analyze('key')
    tones_list = [tone]
    tones_list.extend(tone.alternateInterpretations)

    acc_p = stream.Part(id='accompany')
    measure_num = 1

    print('key', tone)

    shift = 0
    history = []
    while True:
        cur_measure = score.measure(measure_num).flat.notesAndRests

        # print('cur_measure', cur_measure)
        if not cur_measure:
            break
        # на случай если затакт
        if isinstance(cur_measure[0], note.Rest):
            shift += 1
            measure_num += 1
            history.append(-1)
            continue

        measure_chords = harmonize_measure(cur_measure, measure_num - shift, tone)
        print('measure_chords', measure_chords)

        if len(measure_chords) > 1:
            chord_to_add = measure_chords.intersection(HARMONY_RULES[history[-1]])

            if not chord_to_add:
                chord_to_add = measure_chords.pop()
            else:
                history.append(chord_to_add.pop())
        else:
            history.append(measure_chords.pop())

        measure_num += 1

    key_pitches = tone.pitches
    measure_num = 1
    for chord_num in history:
        cur_measure = stream.Measure(number=measure_num)
        if chord_num == -1:
            cur_measure.append(note.Rest(type='whole'))
        else:
            cur_measure.append(chord.Chord([key_pitches[chord_num],
                                            get_third(key_pitches, chord_num),
                                            get_fifth(key_pitches, chord_num)],
                                           type='whole'))
        acc_p.append(cur_measure)
        measure_num += 1

    score.insert(acc_p)

    return score


def harmonize_measure(measure, measure_num, key_tone):
    """
    Function for harmonize only ONE measure by ONE chord
    :param measure:
    :param measure_num:
    :param key_tone:
    :return: list of possible chords for the measure
    """
    key_notes = [str(n.name) for n in key_tone.getChord().notes]
    if measure_num in [1, 8] and isinstance(measure[0], note.Note):
        return {0}
    else:
        prev_chords = {0, 1, 2, 3, 4, 5, 6}
        last_chord = 0

        for elem in measure:
            if isinstance(elem, note.Rest):
                continue
            try:
                pitch_step = key_notes.index(str(elem.name))
            except Exception as e:
                continue

            pitch_chords = [((pitch_step + i) % 7, chord.Chord([key_notes[(pitch_step + i) % 7],
                                                                get_third(key_notes, pitch_step + i),
                                                                get_fifth(key_notes, pitch_step + i)],
                                                               )) for i in [-4, -2, 0]]
            pitch_chords_num = set([elem[0] for elem in pitch_chords])
            prev_chords.intersection_update(pitch_chords_num)
            last_chord = pitch_chords_num

        return prev_chords if prev_chords else last_chord


def get_third(key_pitches, pitch_step):
    return key_pitches[(pitch_step + 2) % 7]


def get_fifth(key_pitches, pitch_step):
    return key_pitches[(pitch_step + 4) % 7]


if __name__ == '__main__':
    res = harmonize('data/test.mid')
    res.show()
