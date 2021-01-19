#!/usr/bin/env python3
import re
from RuneSolver import VigenereSolver
from RuneText import RuneText
from NGrams import NGrams
from HeuristicSearch import GuessVigenere, SearchInterrupt
# from FailedAttempts import NGramShifter

RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
RCOUNT = len(RUNES)
ORG_INTERRUPT = 'ᚠ'
INV_INTERRUPT = RUNES.index(ORG_INTERRUPT)
INVERT = False
if INVERT:
    INV_INTERRUPT = 28 - INV_INTERRUPT
re_norune = re.compile('[^' + RUNES + ']')


def load_data(fname):
    fname = 'pages/{}.txt'.format(fname)
    print()
    print('loading file:', fname)
    with open(fname, 'r') as f:
        data = RuneText(re_norune.sub('', f.read()))['index']
    if INVERT:
        data = [28 - x for x in data]
    return data


#########################################
#  Probability  :  Count runes and simple frequency analysis
#########################################

class Probability(object):
    def __init__(self, numstream):
        self.prob = [0] * RCOUNT
        for r in numstream:
            self.prob[r] += 1
        self.N = len(numstream)

    def IC(self):
        X = sum(x * (x - 1) for x in self.prob)
        return X / ((self.N * (self.N - 1)) / 29)

    def friedman(self):
        return (K_p - K_r) / (self.IC() - K_r)

    def similarity(self):
        probs = Probability.normalized(self.prob)
        return sum((x - y) ** 2 for x, y in zip(PROB_NORM, probs))

    @staticmethod
    def normalized(int_prob):
        total = sum(int_prob)
        return [x / total for x in int_prob]  # math.log(x / total, 10)

    @staticmethod
    def IC_w_keylen(nums, keylen):
        val = sum(Probability(nums[x::keylen]).IC() for x in range(keylen))
        return val / keylen


#########################################
#  Perform heuristic search on the keylength, interrupts, and key
#########################################

def enum_keylengths(nums, fn_interrupt, fn_keyguess, kmin=1, kmax=32):
    best_s = 0
    best_kl = 0
    iguess = SearchInterrupt(nums, INV_INTERRUPT)
    print('interrupt:', ORG_INTERRUPT, 'count:', len(iguess.stops))
    for kl in range(kmin, kmax + 1):
        score, intrpts = fn_interrupt(kl, iguess)
        print('{} {:.4f}'.format(kl, score))
        key_guess = []
        for i, skips in enumerate(intrpts):
            key = fn_keyguess(kl, iguess.join(skips))
            yield kl, score, i, skips, key
            key_guess.append(key)
            intrpts[i] = iguess.to_occurrence_index(skips)
        print('  skip:', intrpts)
        print('  key:', key_guess)
        if score > best_s:
            best_s = score
            best_kl = kl
    print(f'best estimate: keylength: {best_kl}, score: {best_s:.4f}')


def fn_break_vigenere(fname, data):
    def fn_similarity(x):
        return Probability(x).similarity()

    def fn_irp(kl, iguess):
        def fn_IoC(x):
            return Probability.IC_w_keylen(x, kl)
        return iguess.sequential(fn_IoC, startAt=0, maxdepth=9)
        # return iguess.genetic(fn_IoC, topDown=False, maxdepth=4)
        # return fn_IoC(iguess.join()), [[]]  # without interrupts

    def fn_key(kl, data):
        return GuessVigenere(data).guess(kl, fn_similarity)

    slvr = VigenereSolver()
    slvr.input.load(file=f'pages/{fname}.txt')
    slvr.output.QUIET = True
    slvr.output.COLORS = False
    slvr.INTERRUPT = ORG_INTERRUPT
    slvr.KEY_INVERT = INVERT
    for kl, score, i, skips, key in enum_keylengths(data, fn_irp, fn_key,
                                                    kmin=1, kmax=32):
        outfile = f'out/{fname}.{score:.3f}.{kl}.{i}.txt'
        with open(outfile, 'w') as f:
            f.write(f'{kl}, {score:.4f}, {key}, {skips}\n')
        slvr.output.file_output = outfile
        slvr.INTERRUPT_POS = skips
        slvr.KEY_DATA = key
        slvr.run()


#########################################
#  main
#########################################

PROB_INT = [0] * RCOUNT
for k, v in NGrams.load().items():
    PROB_INT[RUNES.index(k)] = v
PROB_NORM = Probability.normalized(PROB_INT)
K_r = 1 / 29   # 0.034482758620689655
K_p = sum(x ** 2 for x in PROB_INT)  # 0.06116195419412538

for fname in [
    # '0_welcome',  # V8
    # 'jpg107-167',  # V13
    # '0_warning',  # invert
    # '0_wisdom',  # plain
    # 'p0-2',  # ???
    # 'p3-7',  # ???
    # 'p8-14',  # ??? -> kl 11? or 12?
    # 'p15-22',  # ???
    # 'p23-26',  # ???
    # 'p27-32',  # ???
    # 'p33-39',  # ???
    # 'p40-53',  # ???
    'p54-55',  # ???
]:
    data = load_data(fname)
    # NGramShifter().guess(data, RUNES[INV_INTERRUPT])
    fn_break_vigenere(fname, data)
