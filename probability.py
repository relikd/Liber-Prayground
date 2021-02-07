#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import LP

INVERT = False
KEY_MAX_SCORE = 0.05
AFF_MAX_SCORE = 0.04
IRP_F_ONLY = True
session_files = []


#########################################
#  Perform heuristic search on the keylength, interrupts, and key
#########################################

def break_cipher(fname, candidates, solver, key_fn):
    def fn_similarity(x):
        return LP.Probability(x).similarity()

    filename = LP.path.page(fname)
    slvr = solver()
    slvr.input.load(file=filename)
    slvr.output.QUIET = True
    slvr.output.COLORS = False
    slvr.KEY_INVERT = INVERT
    key_max_score = KEY_MAX_SCORE
    if key_fn.__name__ == 'GuessAffine':
        key_max_score = AFF_MAX_SCORE
    for irp_count, score, irp, kl, skips in candidates:
        if IRP_F_ONLY and irp != 0:
            continue
        data = LP.load_indices(filename, irp, maxinterrupt=irp_count)
        if INVERT:
            data = [28 - x for x in data]
        iguess = LP.SearchInterrupt(data, (28 - irp) if INVERT else irp)
        print('IoC: {}, interrupt: {}, count: {}, solver: {}'.format(
            score, LP.RUNES[irp], len(iguess.stops), key_fn.__name__))
        testcase = iguess.join(iguess.from_occurrence_index(skips))

        key_score, key = key_fn(testcase).guess(kl, fn_similarity)
        if key_score > key_max_score:
            continue
        prio = (1 - key_score) * max(0, score)
        print(f'  key_score: {prio:.4f}, {key}')
        print('  skip:', skips)
        txtname = f'{fname}_{prio:.4f}.{key_fn.__name__}.{irp}_{kl}'
        if INVERT:
            txtname += '.inv'
        while txtname in session_files:
            txtname += '.'
        session_files.append(txtname)
        outfile = LP.path.tmp(txtname)
        with open(outfile, 'w') as f:
            f.write(
                f'{irp}, {kl}, {score:.4f}, {key_score:.4f}, {key}, {skips}\n')
        slvr.output.file_output = outfile
        slvr.INTERRUPT = LP.RUNES[irp]
        slvr.INTERRUPT_POS = skips
        slvr.KEY_DATA = key
        slvr.run()


def pattern_solver(fname, irp=0):
    with open(LP.path.page(fname), 'r') as f:
        orig = LP.RuneText(f.read())
    # orig = LP.RuneText('ᛄᚹᚻᛗᛋᚪ-ᛋᛁᚫᛇ-ᛋᛠᚾᛞ-ᛇᛞ-ᛞᚾᚣᚹᛗ.ᛞᛈ-ᛝᛚᚳᚾᛗᚾᚣ-ᛖᛝᛖᚦᚣᚢ-ᚱᚻᛁᚠ-ᛟᛝ-ᛚᛖᚫᛋᛚᚳᛋᛇ.ᚣᚾᚻᛄᚾᚳᛡ-ᚷᚳᛝ-ᛈᛝ-ᛡᚷᚦᚷᛖ.ᚻᛠᚣ-ᛄᛞᚹᛒ-ᛇᛄᛝᚩᛟ.ᛗᛠᚣᛋᛖᛚᚠ-ᚾᚫᛁ-ᛄᚹᚻᚻᛚᛈᚹᚠ-ᚫᚩᛡᚫᛟ-ᚷᛠ-ᚪᛡᚠᛄᚱᛏᚢᛈ.ᛏᛈ-ᛇᛞ-ᛟᛗᛇᛒᛄᚳᛈ.ᛉᛟ-ᛒᚻᚱᛄᚣ-ᚾᚱ-ᚾᛡᛈᛈ-ᛚᛉᛗᛞ-ᛟᛝ-ᚷᛁᚱᚩᚹᛗ-ᚠᛇᚣ-ᚣᛝᛒ-ᛁ-ᚠᚾᚹᚢ-ᛠᚾᛈᚠᚻ.ᚫᛋᛄᚪᚻ-ᛒᛖᛋᚻᛠ-ᛄᛗ-ᛟᛡᚹᚪᛡ-ᛄᛋᛖᚢᛗ-ᛏᛖᛉᚪ-ᛞᛟᛉᚾᚠ-ᚱᛡᛒᛚᚩᛈᛝ-ᛋᛄᛚᛗ-ᛞᚱᛗᛗ-ᛒᛈ-ᛁᛉᚱᛄᛝ.ᛋᛇᚪ-ᛗᚠᚻᚣᚹᛉᛞ-ᛡᛁᚷᚪ-ᚩᚱ-ᚪᚾᚹᛇᛋᛞᛄᚷ-ᛡ-ᛖᚫᛄ-ᛞᛟᛁᚻᚹᛝ-ᛠᛈᛏ-ᚪᛗᛗᛚᛚᚪᛞ.ᛁᛠᛈᚷᛞ-ᛗᚣᛄᚳᚹᛚ-ᚻᛋᛟᛗ-ᚣᚫᛝᛚ-ᛠᛁᛝᛝᚪ-ᚳᛗ-ᚢᚫᛋ-ᛉᛠᚱ-ᛇᛡᛄᚻᛗᚾ-ᚻᛗᛝᛚ-ᛇᛞ-ᛟᚢᚣᚪᚷᚱ-ᛡᚷ-ᚷᛠ-ᛚᚻᛒ.ᛡᛒ-ᚩᛁᛄ-ᛗᛟᛉᚩᚣ-ᛞᚩ-ᚳᛗ-ᚾᛗᚩ-ᚷᛠ-ᛚᚱᚠᚷ-ᛁᚫᛗᛉ-ᛁᛠᚹᛚ-ᛖᛝᚾᛟᛗᚾ-ᛄᚾ-ᚾᚳᛚᛝ-ᛡ-ᚷᛞᛗᚱᚻᚩ-ᛗᛞᛠᚫᛞ-ᛞᚱᛗᛗ-ᚣᚪ-ᛗᛉᚢᛞᛇᚹ-ᛟᚱᛏᚱᛟᚢᛉᛗᛚᛈᛉᛝ.ᛏᛖ-ᛗᛋᚣ-ᚹᛁ-ᚹᛝ-ᛋᛇᛄᚳᛁᛋᛝ.ᛄᛚᚹ-ᚷᚠᛝ-ᚫᚷᛚᛡᛁᛡ.ᛖᚠᚣ-ᛉᛝᚻᛄᚾᛈᚠ-ᛉᚣ-ᛚᛄᛞᛝᛞᚪ-ᚩᛈ-ᚻᛟ-ᛖᚻᚱᚹ-ᛚᚷᚳ-ᛒᛈᛏᚻ-ᚠᛋᛠᚣᛋᚠ-ᛏᚷᛈᚪᛒ.')
    # orig = LP.RuneText('ᛇᚦ-ᛒᛏᚣᚳ-ᛇᛚᛉ-ᛄᛚᚦᚪ-ᛋᚱᛉᚦ-ᚦᛄᚻ-ᛉᛗ-ᛏᛞᛋ-ᚣᚾ-ᚣᛟᛇᛈᛟᛚ-ᛈᚹᛚᚪᛗ-ᚪᛉᛁᛇᛝᚢᚱᛉ.ᛞᛄ-ᚻᛠᚪᛚ.ᚠᛚ-ᚩᛋᚾ-ᚫᛞᛋᛁᛞᚹᚾᚪᚪ-ᚱᛟᚻ-ᛚᚠᛚᚳᛟᚱ-ᚣᛏ-ᚹᛏᛝᚣ-ᚳᚩ-ᛄᚷᛟ-ᛖ-ᚫᚻᚦᛠ-ᛒᛠᛁ-ᛁᚩᛡ-ᛗᛉᚠᚷᛁ-ᚣᚣᛋᛇᛗᛠᚹ.ᛇᚪ-ᛇᛉᛡ-ᛄᚾᛇᛁᛇᚫ-ᛋᚱᚹ-ᛝᚣᚦ-ᛠᛁᛄᛚᚢᛄ-ᚻᛇᛚᛟ-ᛒᛠᛒᛚ-ᚩᛈᛈ-ᚢᚻᛚ-ᛡᚾᛚ-ᛒᚦᚱᚠᚦᚫ-ᛞᚳ-ᛄᚳᚷ-ᚹᚫ-ᚱᛉᚣᛖᚱ.ᛒᛝᚹ-ᛟᚳᚫᚹᛈᚢ-ᚱᛋᛒ-ᚷᚦᚳᛏᛏᛠᚹ-ᚱᚣᛞ-ᚣᛠᛄ-ᛋ-qᚪᛚᚾᛖᛄᚪ-ᛇᚻᛖ-ᛏᛠᛈ-ᛝᛉᚾᚳ-ᛋᚾᚹᚦᚾ-ᚣᛞᛝᚣ-ᛠᛠᛡ-ᛉᛁᛚᚢᚩ.ᛗᛉᚦ-ᛒᛝᛇᛠᛟ-ᛁᛟᛏ-ᛠᛏᛄ-ᚫᚳᛉᛝᛖᚠ-ᛇᚠ.ᛄᛄᛝᛟᛡᛟ-ᛠᛖᚫ-ᚦᛏᛠᛗ-ᛁᛏᚩᛒᛡ-ᛝᛟ-ᛉᚠᛇᚷᛗᛠ-ᚠᛖ-ᚳᛖᛖᚾᛠᛁᚪᛟ-ᛉᚣ-ᚢᛁ.ᛒᛏ.ᛒᛠ-ᛠᛁᚢᛗ-ᛞᛟᛋᛠᚷᚠᛇᚫ-ᛏᚪ-ᛇᚦ-ᛒᚪᛟᚩᛗ.ᛟᚳᛇ-ᛞᛞ-ᛋᚱᛁᛋᚦ-ᛇᛒ-ᚳᛒᛟ-ᚳᛟᚳᚷᛇ.ᛗᛉᚦ-ᛞᚦᛉᛈᛚᛈᛚᛁᚢ-ᚳᛞᛡᛝᚻᚷ-ᛞᚪ-ᚳᛟᚳᛁᛟᛞ-')
    data = orig.index
    if False:  # longest uninterrupted text
        pos, lg = LP.InterruptDB.longest_no_interrupt(data, interrupt=0, irpmax=0)
        data = data[pos:pos + lg]
    else:  # from the beginning
        data = data[:170]

    data_i = [i for i, x in enumerate(data) if x == 29]
    data = [x for x in data if x != 29]

    def fn_similarity(x):
        return LP.Probability(x).similarity()

    def fn_pattern_mirror(x, kl):
        for i in range(10000):  # mirrored, 012210012210 or 012101210
            yield from x
            # yield from x[::-1]
            yield from x[::-1][1:-1]

    print(fname)
    gr = LP.GuessPattern(data)
    for kl in range(3, 19):
        # for pattern_shift in range(1):
        #     fn_pattern = fn_pattern_mirror
        for pattern_shift in range(1, kl):
            def fn_pattern_shift(x, kl):  # shift by (more than) one, 012201120
                for i in range(10000):
                    yield from x[(i * pattern_shift) % kl:]
                    yield from x[:(i * pattern_shift) % kl]

            fn_pattern = fn_pattern_shift
            # Find proper pattern
            res = []
            for offset in range(kl):  # up to keylen offset
                mask = LP.GuessPattern.pattern(kl, fn_pattern)
                parts = gr.split(kl, mask, offset)
                score = sum(LP.Probability(x).IC() for x in parts) / kl
                if score > 1.6 and score < 2.1:
                    res.append((score, parts, offset))

            # Find best matching key for pattern
            for score, parts, off in res:
                sc, solution = LP.GuessPattern.guess(parts, fn_similarity)
                if sc < 0.1:
                    fmt = 'kl: {}, pattern-n: {}, IoC: {:.3f}, dist: {:.4f}, offset: {}, key: {}'
                    print(fmt.format(kl, pattern_shift, score, sc, off,
                                     LP.RuneText(solution).text))
                    solved = gr.zip(fn_pattern(solution, kl), off)
                    for i in data_i:
                        solved.insert(i, 29)
                    print(' ', LP.RuneText(solved).text)


#########################################
#  main
#########################################
db = LP.InterruptDB.load('db_norm')
# IOC_MIN_SCORE = 1.4  # for db_high
IOC_MIN_SCORE = 0.55  # for db_norm

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
    pattern_solver(fname)
    # break
    continue
    # NGramShifter().guess(data, 'ᚠ')
    if fname not in db:
        print(fname, 'not in db.')
        continue
    print()
    print(f'loading file: pages/{fname}.txt')
    candidates = [x for x in db[fname] if x[1] >= IOC_MIN_SCORE]
    if not candidates:
        maxscore = max(x[1] for x in db[fname])
        print('No candidates. Highest score is only', maxscore)
        continue
    break_cipher(fname, candidates, LP.AffineSolver, LP.GuessAffine)
    break_cipher(fname, candidates, LP.VigenereSolver, LP.GuessVigenere)
