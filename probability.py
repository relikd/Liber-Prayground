#!/usr/bin/env python3
from RuneSolver import VigenereSolver, AffineSolver
from HeuristicSearch import GuessVigenere, GuessAffine, SearchInterrupt
from HeuristicLib import load_indices, Probability
from InterruptDB import InterruptDB
# from FailedAttempts import NGramShifter

RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
INVERT = False
MIN_SCORE = 1.4
session_files = []


#########################################
#  Perform heuristic search on the keylength, interrupts, and key
#########################################

def break_cipher(fname, candidates, solver, key_fn):
    def fn_similarity(x):
        return Probability(x).similarity()

    filename = f'pages/{fname}.txt'
    slvr = solver()
    slvr.input.load(file=filename)
    slvr.output.QUIET = True
    slvr.output.COLORS = False
    slvr.KEY_INVERT = INVERT
    for irp_count, score, irp, kl, skips in candidates:
        data = load_indices(filename, irp, maxinterrupt=irp_count)
        if INVERT:
            data = [28 - x for x in data]
        iguess = SearchInterrupt(data, (28 - irp) if INVERT else irp)
        print('score: {}, interrupt: {}, count: {}, solver: {}'.format(
            score, RUNES[irp], len(iguess.stops), key_fn.__name__))
        testcase = iguess.join(iguess.from_occurrence_index(skips))

        key = key_fn(testcase).guess(kl, fn_similarity)
        print('  skip:', skips)
        print('  key:', key)
        txtname = f'{key_fn.__name__}.{score:.3f}_{fname}_{kl}.{irp}'
        if INVERT:
            txtname += '.inv'
        while txtname in session_files:
            txtname += '.'
        session_files.append(txtname)
        outfile = f'out/{txtname}.txt'
        with open(outfile, 'w') as f:
            f.write(f'{kl}, {score:.4f}, {key}, {skips}\n')
        slvr.output.file_output = outfile
        slvr.INTERRUPT = RUNES[irp]
        slvr.INTERRUPT_POS = skips
        slvr.KEY_DATA = key
        slvr.run()


#########################################
#  main
#########################################
# db = InterruptDB.load('InterruptDB/db_secondary.txt')
db = InterruptDB.load()

for fname in [
    'p0-2',  # ???
    'p3-7',  # ???
    'p8-14',  # ???
    'p15-22',  # ???
    'p23-26',  # ???
    'p27-32',  # ???
    'p33-39',  # ???
    'p40-53',  # ???
    'p54-55',  # ???
    # '0_warning',  # invert
    # '0_welcome',  # V8
    # '0_wisdom',  # plain
    # '0_koan_1',  # invert + shift
    # '0_loss_of_divinity',  # plain
    # 'jpg107-167',  # V13
    # 'jpg229',  # plain
    # 'p56_an_end',  # totient
    # 'p57_parable',  # plain
]:
    # NGramShifter().guess(data, 'ᚠ')
    if fname not in db:
        print(fname, 'not in db.')
        continue
    print()
    print(f'loading file: pages/{fname}.txt')
    candidates = [x for x in db[fname] if x[1] >= MIN_SCORE]
    if not candidates:
        maxscore = max(x[1] for x in db[fname])
        print('No candidates. Highest score is only', maxscore)
        continue
    break_cipher(fname, candidates, AffineSolver, GuessAffine)
    break_cipher(fname, candidates, VigenereSolver, GuessVigenere)
