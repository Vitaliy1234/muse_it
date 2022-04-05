from music21 import note, stream, converter, chord, midi
from music21.analysis.discrete import DiscreteAnalysisException


HARMONY_RULES = [[1, 2, 3, 4, 5, 6],
                 [0, 2, 4],
                 [0, 3, 4, 5, 6],
                 [0, 1, 4],
                 [0, 2, 5, 6],
                 [0, 1, 2, 3],
                 [0]]


def harmonize(filename):
    """
    Function for harmonize melody
    :param filename:
    :return score: result score with accompany
    """
    score = converter.parse(filename)

    tone = score.analyze('key')
    tones_list = [tone]
    tones_list.extend(tone.alternateInterpretations)

    # iter over tones sorted by relevant
    for key in tones_list:
        acc_p = stream.Part(id='accompany')
        measure_num = 1
        last_step = 0

        key_pitches = key.getChord().pitches

        print('key', key)

        continue_flag = False
        alternative_num = 0
        exit_flag = False
        next_measure = False
        melody_chords = []
        while True:
            measure_chords = []
            used_chords = []
            cur_measure = score.measure(measure_num).pitches
            pitch_ind = 0

            while pitch_ind < len(cur_measure):
                if pitch_ind == len(used_chords):
                    used_chords.append([])
                if measure_num in [1, 8]:
                    cur_measure = append_chord(key.getChord(), 'whole', measure_num)
                    acc_p.append(cur_measure)
                    melody_chords.append(0)
                    measure_num += 1
                    next_measure = True
                    break
                elif measure_num == 4:
                    cur_measure = append_chord(key.getDominant(), 'whole', measure_num)
                    acc_p.append(cur_measure)
                    melody_chords.append(4)
                    measure_num += 1
                    next_measure = True
                    break

                if len(measure_chords) == 2 and measure_chords[1] != measure_chords[0]:
                    pass
                # if current note not in key notes, we return raw score
                # TODO: fix handling notes beyond key
                try:
                    pitch_step = key_pitches.index(cur_measure[pitch_ind])
                except Exception:
                    return score

                pitch_chords = [(pitch_step + i, chord.Chord([key_pitches[(pitch_step + i) % 7],
                                                              get_third(key_pitches, pitch_step + i),
                                                              get_fifth(key_pitches, pitch_step + i)],
                                                             type='quarter')) for i in [0, 2, 4]]
                pitch_chords_num = set([elem[0] for elem in pitch_chords])
                print(measure_num, pitch_chords)
                possible_chords = HARMONY_RULES[melody_chords[measure_num - 2]]
                pitch_chords_num.intersection_update(possible_chords)
                pitch_chords_num.difference_update(used_chords[pitch_ind])

                print(pitch_chords_num)

                if measure_num == 3:
                    pitch_chords_num.discard(4)
                if measure_num == 7:
                    pitch_chords_num.discard(0)

                if not pitch_chords_num:
                    if pitch_ind == 0:
                        return score
                    pitch_ind -= 1
                    continue

                chord_to_add = pitch_chords_num.pop()

                melody_chords.append(chord_to_add)
                used_chords[pitch_ind].append(chord_to_add)
                print(melody_chords, pitch_chords_num)
                pitch_ind += 1
                # exit_flag = True
                # break

            if next_measure:
                try:
                    score.measure(measure_num).analyze('key')
                except Exception:
                    print('jopa')
                    break
                next_measure = False
                continue

            measure_num += 1

            try:
                score.measure(measure_num).analyze('key')
            except Exception:
                break

            if exit_flag:
                break
            continue

            if alternative_num > 5:
                continue_flag = True
                break
            cur_ton = score.measure(measure_num).analyze('key')
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
            acc_p.append(cur_measure)

            try:
                score.measure(measure_num + 1).analyze('key')
            except Exception:
                break

            last_chord = cur_chord
            last_step = step
            measure_num += 1

        if continue_flag:
            continue

        score.insert(0, acc_p)
        break

    return score


def append_chord(key, chord_type, measure_num):
    cur_measure = stream.Measure(number=measure_num)
    cur_measure.append(chord.Chord([(key.root()), key.third, key.fifth], type=chord_type))

    return cur_measure


def get_third(key_pitches, pitch_step):
    return key_pitches[(pitch_step + 2) % 7]


def get_fifth(key_pitches, pitch_step):
    return key_pitches[(pitch_step + 4) % 7]


if __name__ == '__main__':
    res = harmonize('data/test.mid')
    print(type(res))
    res.plot()
    # res.show()
