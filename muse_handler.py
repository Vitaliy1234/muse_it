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
    s = converter.parse(filename)

    ton = s.analyze('key')
    tons_list = [ton]
    tons_list.extend(ton.alternateInterpretations)
    # print(tons_list)

    tonic = ton.getChord(type='whole').pitches[0]
    dom = ton.getChord(type='whole').pitches[4]
    subdom = ton.getChord(type='whole').pitches[3]
    parall_tonic = ton.getChord(type='whole').pitches[5]
    parall_dom = ton.getChord(type='whole').pitches[2]
    parall_subdom = ton.getChord(type='whole').pitches[1]

    for key in tons_list:
        acc_p = stream.Part(id='accompany')
        measure_num = 1
        last_step = 0
        last_chord = key

        print('key', key)

        continue_flag = False
        # step = key.getChord().pitches.index(last_chord.getChord().pitches[0])
        #
        # if step not in HARMONY_RULES[last_step]:
        #     continue

        # measure_num += 1
        exit_flag = False
        alternative_num = 0

        while True:
            if alternative_num > 5:
                continue_flag = True
                break
            cur_ton = s.measure(measure_num).analyze('key')
            chords = [cur_ton]
            chords.extend(cur_ton.alternateInterpretations)
            cur_chord = chords[alternative_num]

            if cur_chord.getChord().pitches[0] not in key.getChord().pitches:
                alternative_num += 1
                continue

            step = key.getChord().pitches.index(cur_chord.getChord().pitches[0])

            if step not in HARMONY_RULES[last_step]:
                alternative_num += 1
                continue

            alternative_num = 0
            # print(last_chord, last_step)
            print(cur_chord, cur_chord.correlationCoefficient, last_step)

            # tonic = cur_chord.getChord(type='whole').pitches[0]
            # dom = cur_chord.getChord(type='whole').pitches[4]
            # subdom = cur_chord.getChord(type='whole').pitches[3]
            # parall_tonic = cur_chord.getChord(type='whole').pitches[5]
            # parall_dom = cur_chord.getChord(type='whole').pitches[2]
            # parall_subdom = cur_chord.getChord(type='whole').pitches[1]

            cur_measure = stream.Measure(number=measure_num)
            cur_measure.append(chord.Chord([(cur_chord.getChord().root()), cur_chord.getChord().third, cur_chord.getChord().fifth], type='whole'))
            # cur_measure.append(note.Note(cur_chord.getChord().third, type='whole'))
            # cur_measure.append(note.Note(cur_chord.getChord().fifth, type='whole'))
            acc_p.append(cur_measure)

            try:
                s.measure(measure_num + 1).analyze('key')
            except Exception:
                break

            last_chord = cur_chord
            last_step = step
            measure_num += 1

        if continue_flag:
            continue

        s.insert(0, acc_p)
        break

    return s


if __name__ == '__main__':
    res = harmonize('data/test.mid')
    res.show()
