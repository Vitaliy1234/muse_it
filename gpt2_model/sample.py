import os
from gpt2_model.helpers import logging
from pathlib import Path

from transformers import GPT2LMHeadModel
from transformers import PreTrainedTokenizerFast

from gpt2_model.helpers.samplinghelpers import *
from gpt2_model.data_preparation import extract_notes, converter

logger = logging.create_logger("sampling")
CUR_FILE_PATH = os.path.dirname(__file__)


def generate_music(priming_sample_custom, model, tokenizer):
    bar_counter = 0

    priming_sample_tokens = priming_sample_custom.split(' ')
    prev_2_bar_idx = priming_sample_tokens.index('BAR_START')

    header = priming_sample_custom[:priming_sample_custom.index('BAR_START')]

    generated_list = []

    for idx, token in enumerate(priming_sample_tokens):
        if token == 'BAR_END':
            bar_counter += 1
        if bar_counter == 2:
            cur_sample = priming_sample_tokens[prev_2_bar_idx:idx + 1]
            cur_sample.append('TRACK_END')
            cur_sample = ' '.join(cur_sample)
            cur_sample = header + cur_sample

            generated_sample = generate(model, tokenizer, cur_sample)
            generated_sample = generated_sample.replace('[PAD]', '').strip()

            generated_list.append(generated_sample)

            bar_counter = 0

            prev_2_bar_idx = idx + 1

    if bar_counter == 1:
        cur_sample = priming_sample_tokens[prev_2_bar_idx:idx + 1]
        cur_sample.append('TRACK_END')
        cur_sample = ' '.join(cur_sample)
        cur_sample = header + cur_sample

        generated_sample = generate(model, tokenizer, cur_sample)
        generated_sample = generated_sample.replace('[PAD]', '').strip()

        generated_list.append(generated_sample)

    return generated_list


def concat_gen_list(generated_list):
    # Concat 2-bars pieces
    from collections import defaultdict

    generated_tracks_dict = defaultdict(str)

    for generated_sample in generated_list:
        generated_tracks = generated_sample.split(' TRACK_END TRACK_START ')

        for track in generated_tracks:
            inst_begin = track.index('INST')
            inst_end = track[track.index('INST'):].index(' ') + track.index('INST')

            inst = track[inst_begin:inst_end]

            if generated_tracks_dict[inst] != '':
                cur_track = track[track.index('BAR_START') - 1:]
            else:
                cur_track = track
            generated_tracks_dict[inst] += cur_track

    for inst in generated_tracks_dict:
        if 'TRACK_START' not in generated_tracks_dict[inst]:
            generated_tracks_dict[inst] = 'TRACK_START ' + generated_tracks_dict[inst]
        if 'TRACK_END' not in generated_tracks_dict[inst]:
            generated_tracks_dict[inst] += ' TRACK_END'

    full_generated_sample = ' '.join(generated_tracks_dict.values())

    return full_generated_sample


def sample(priming_sample_file, result_file):
    """
    Генерация аккомпанемента по данной мелодии
    :param priming_sample_file: файл с исходной мелодией в текстовом виде
    :param result_file: файл, куда надо положить результат генерации в формате midi
    :return: нет возвращаемого значения
    """
    tokenizer_path = os.path.join(CUR_FILE_PATH, "gpt2model_4_bars", "tokenizer.json")
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})

    model_path = os.path.join(CUR_FILE_PATH, "gpt2model_4_bars", "best_model")
    model = GPT2LMHeadModel.from_pretrained(model_path)

    logger.info("Model loaded.")
    with open(priming_sample_file, 'r') as hfile:
        priming_sample = hfile.read()

    # генерируем список двутактовых кусочков мелодии
    generated_list = generate_music(priming_sample, model, tokenizer)
    # соединяем все в единое целое
    full_generation = concat_gen_list(generated_list)
    # преобразовываем текст в midi и сохраняем в файл
    note_seq.note_sequence_to_midi_file(token_sequence_to_note_sequence(full_generation), result_file)


def make_bach_chorale(filename, res_filename):
    logger.info('Start converting midi to text')
    text_repr = extract_notes([filename], converter)
    logger.info('Midi converted to text')

    split_path = os.path.split(filename)

    Path('text_representations').mkdir(exist_ok=True)

    txt_file = f"{split_path[1].split('.')[0]}.txt"
    txt_file = os.path.join('text_representations', txt_file)

    with open(txt_file, 'w') as hfile:
        for piece in text_repr:
            hfile.write(piece + '\n')

    logger.info(f'Text representation of melody was saved in {txt_file}')
    logger.info('Start generation...')

    sample(txt_file, res_filename)
    logger.info(f'Generation finished! Saved in {res_filename}')

    os.remove(txt_file)


if __name__ == '__main__':
    filename = os.path.join('../data', 'v_lesu_elka.mid')

    split_path = os.path.split(filename)

    midi_file = f"{split_path[1].split('.')[0]}.mid"

    Path('generations').mkdir(exist_ok=True)
    midi_file = os.path.join('generations', midi_file)

    make_bach_chorale(filename, midi_file)
