#!/usr/bin/env python3
import math
import re
from RuneSolver import VigenereSolver
from RuneText import Rune, RuneText

RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
RCOUNT = len(RUNES)
ORG_INTERRUPT = RUNES.index('ᚠ')
INVERT = False
INV_INTERRUPT = (28 - ORG_INTERRUPT) if INVERT else ORG_INTERRUPT
LOOK_AHEAD = 9  # look ahead
APPEND_REMAINING = False  # should it incl. text past the look ahead?
re_norune = re.compile('[^' + RUNES + ']')


def main():
    # BaselineProbability.translate()
    # BaselineProbability.make('data/p-solved.txt', infile='_solved.txt')
    # BaselineProbability.make('data/p-1gram.txt', 1)
    # for i in range(1, 6):
    #     print(f'generate {i}-gram file')
    #     BaselineProbability.make(
    #         f'data/p-{i}gram.txt', i, infile='data/baseline-rune-words.txt')
    #     BaselineProbability.make(
    #         f'data/p-solved-{i}gram.txt', i, infile='_solved.txt')
    # exit()

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
        # NGramShifter(data).try_all()
        # print(VigenereBreaker(data).guess(8, [4,5,6,7,10,11,14,18,20,21,25]))
        # print(VigenereBreaker(data).guess(13, [2, 3]))
        # continue
        if False:
            # TODO: add some logic for two keys alternation
            bst, kall = test_keylength(data[0::2], kmax=20, wInterrupt=True)
            print('best estimate: keylength: {}, score: {:.4f}'.format(*bst))
            # decrypt_to(kall, fname, '.0')
            bst, kall = test_keylength(data[1::2], kmax=20, wInterrupt=True)
            print('best estimate: keylength: {}, score: {:.4f}'.format(*bst))
            # decrypt_to(kall, fname, '.1')
        else:
            bst, kall = test_keylength(data, kmin=1, kmax=32, start=1, wInterrupt=True)
            print('best estimate: keylength: {}, score: {:.4f}'.format(*bst))
            decrypt_to(kall, fname)


def load_data(fname):
    fname = 'pages/{}.txt'.format(fname)
    print()
    print('loading file:', fname)
    with open(fname, 'r') as f:
        data = RuneText(re_norune.sub('', f.read()))
    data = [(28 - x).index if INVERT else x.index for x in data]
    return data


def decrypt_to(variants, infile, prfx=''):
    slvr = VigenereSolver()
    slvr.input.load(file=f'pages/{infile}.txt')
    slvr.output.QUIET = True
    slvr.output.COLORS = False
    slvr.INTERRUPT = RUNES[ORG_INTERRUPT]
    slvr.KEY_INVERT = INVERT
    for kl, score, intrpts, key_guess in variants:
        outfile = f'out/{infile}.{kl}{prfx}.txt'
        with open(outfile, 'w') as f:
            f.write(f'{kl}, {score:.4f}, {key_guess}, {intrpts}\n')
        slvr.output.file_output = outfile
        slvr.INTERRUPT_POS = intrpts
        slvr.KEY_DATA = key_guess
        slvr.run()


def test_keylength(nums, kmin=1, kmax=32, start=1, wInterrupt=False):
    best_score = 0
    best_kl = 0
    ret = []
    for kl in range(kmin, kmax + 1):
        if wInterrupt:
            score, intrpts = BinTest(nums, kl).test(start=start)
        else:
            score = Probability.IC_w_keylen(nums, kl)
            intrpts = []

        print('{} {:.4f}'.format(kl, score))
        print('  jump:', intrpts)
        key_guess = VigenereBreaker(nums).guess(kl, intrpts)
        print('  key:', key_guess)
        ret.append((kl, score, intrpts, key_guess))

        if score > best_score:
            best_score = score
            best_kl = kl
    return (best_kl, best_score), ret


#########################################
#  BaselineProbability  :  loads and writes ngrams
#########################################

class BaselineProbability(object):
    @staticmethod
    def translate():  # takes 10s
        with open('data/baseline-text.txt', 'r') as f:
            src = re.sub('[^A-Z]', ' ', f.read().upper())
            # src.replace('\n', '')

        with open('data/baseline-rune.txt', 'w') as f:
            flag = False
            for r in RuneText.from_text(src):
                if r.kind != 'r':
                    if not flag:
                        f.write('\n')
                        flag = True
                    continue
                f.write(r.rune)
                flag = False

    @staticmethod
    def make(outfile, gramsize=1, infile='data/baseline-rune.txt'):
        res = {x: 0 for x in RUNES}
        for x in range(gramsize - 1):
            res = {x + y: 0 for x in RUNES for y in res.keys()}
        with open(infile, 'r') as f:
            data = re_norune.sub('', f.read())
        for i in range(len(data) - (gramsize - 1)):
            ngram = data[i:i + gramsize]
            res[ngram] += 1
        with open(outfile, 'w') as f:
            for x, y in sorted(res.items(), key=lambda x: -x[1]):
                if y != 0:
                    f.write(f'{x} {y}\n')

    @staticmethod
    def load_ngram(gram=2):
        ret = {}
        with open(f'data/p-{gram}gram.txt', 'r') as f:
            for line in f.readlines():
                r, v = line.split()
                ret[r] = int(v)
        return ret

    @staticmethod
    def load():
        with open('data/p-1gram.txt', 'r') as f:
            lines = f.readlines()
        ret = [0] * RCOUNT
        for line in lines:
            r, v = line.split()
            ret[RUNES.index(r)] = int(v)
        return ret


#########################################
#  Probability  :  Count runes and simple frequency analysis
#########################################

class Probability(object):
    def __init__(self, arr):
        self.prob = Probability.count(arr)
        self.N = len(arr)

    def IC(self):
        X = sum([x * (x - 1) for x in self.prob])
        return X / ((self.N * (self.N - 1)) / 29)

    def friedman(self):
        return (K_p - K_r) / (self.IC() - K_r)

    def similarity(self):
        probs = Probability.to_log(self.prob)
        return sum((PROB_BASELINE[i] - probs[i]) ** 2 for i in range(RCOUNT))

    @staticmethod
    def count(nums):
        res = [0] * RCOUNT
        for r in nums:
            res[r] += 1
        return res

    @staticmethod
    def to_log(int_prob):
        total = sum(int_prob)
        for i, v in enumerate(int_prob):
            int_prob[i] = v / total
            # int_prob[i] = math.log(v / total, 10)
        return int_prob

    @staticmethod
    def IC_w_keylen(nums, keylen):
        val = sum(Probability(nums[x::keylen]).IC() for x in range(keylen))
        return val / keylen


#########################################
#  BinTest  :  Split text into Vigenere columns and apply frequency anlysis
#########################################

class BinTest(object):
    def __init__(self, nums, keylength):
        self.keylength = keylength
        self.intrpts = [-1]
        self.parts = []
        for i, n in enumerate(nums):
            if n != INV_INTERRUPT:
                continue
            self.parts.append(nums[self.intrpts[-1] + 1:i])  # drop ᚠ
            self.intrpts.append(i)
        self.parts.append(nums[self.intrpts[-1] + 1:])  # remainder
        self.previous = self.parts[0]

    def permutations(self, index, maxdepth=LOOK_AHEAD):
        ret = [self.previous]
        i = maxdepth
        for part in self.parts[index:]:
            tmp = []
            for x in ret:
                tmp.append(x + [INV_INTERRUPT] + part)
                tmp.append(x + part)  # + INV_INTERRUPT
                # TODO: properly append INV_INTERRUPT
                # ommitting a rune will slightly favor the shorter text
                # however, adding it at the end will shift all remaining runes
            ret = tmp
            i -= 1
            if i <= 0:
                if APPEND_REMAINING:
                    remainder = []
                    for z in self.parts[index + maxdepth:]:
                        remainder.extend([INV_INTERRUPT] + z)
                    for u in range(len(ret)):
                        ret[u].extend(remainder)
                break
        return ret

    def best_permutation(self, start, maxdepth=LOOK_AHEAD, oneShot=False):
        # TODO: better algorithm to select interrupts
        permutations = self.permutations(start, maxdepth=maxdepth)
        best_i = 0
        best_score = 0
        # try all permutations for the next x interrupts
        for p_i, p in enumerate(permutations):
            score = Probability.IC_w_keylen(p, self.keylength)
            if score > best_score:
                best_score = score
                best_i = p_i
        if oneShot:
            # permutations without interrupt are appended first
            # since we only care about the first char, i >= len/2 is sufficient
            is_interrupt = best_i >= len(permutations) / 2
            return best_score, is_interrupt
        else:
            found = []
            mi = int(math.log(len(permutations), 2))
            for i in range(mi):
                if best_i & (1 << (mi - i)):
                    found.append(i + start - 1)
            return best_score, found

    def join_parts(self, end=None):
        ret = []
        for part in self.parts[:end]:
            ret.append(INV_INTERRUPT)
            ret.extend(part)
        return ret[1:]

    def test(self, start=1):
        if start > 1:
            if start >= len(self.parts):
                start = len(self.parts) - 1
            self.previous = self.join_parts(self.intrpts[start])
        # # enum all possible permutation. But only once
        # return self.best_permutation(start=start, maxdepth=12, oneShot=True)
        # # calculate IoC without interrupts
        # return Probability.IC_w_keylen(self.join_parts(), self.keylength), []
        if start >= len(self.intrpts):
            return Probability.IC_w_keylen(self.previous, self.keylength), []

        found = []
        best = 0
        for i in range(start, len(self.intrpts)):
            score, is_interrupt = self.best_permutation(i)
            if score > best:
                best = score
            if is_interrupt:
                found.append(i)
            else:
                self.previous += [INV_INTERRUPT]
            self.previous.extend(self.parts[i])
        return best, found


#########################################
#  VigenereBreaker  :  Given a fixed keylength, shift values around
#########################################

class VigenereBreaker(object):
    def __init__(self, nums):
        self.nums = nums

    def guess(self, keylength, interrupts=[]):
        intup = 0
        ii = 0
        bins = [[] for _ in range(keylength)]
        for i, n in enumerate(self.nums):
            if n == INV_INTERRUPT:
                intup += 1
                if intup in interrupts:
                    continue
            bins[ii % keylength].append(n)
            ii += 1
        found = []
        for data in bins:
            shifted = [[] for _ in range(29)]
            for x in data:
                for i in range(29):
                    shifted[i].append((x - i) % 29)
            bi = -1
            bs = 9999999
            for i, test in enumerate(shifted):
                score = Probability(test).similarity()
                if score < bs:
                    bs = score
                    bi = i
            found.append(bi)
        return found


#########################################
#  NGramShifter  :  Shift fixed with runes around
#########################################

class NGramShifter(object):
    def __init__(self, data):
        self.data = data
        self.variants = [''.join(RUNES[(y - x) % 29] for y in data)
                         for x in range(29)]

    def try_all(self, gramsize=3):
        for i in range(gramsize):
            print('offset:', i)
            NGramShifter(self.data[i:]).guess(gramsize)
            print()

    def guess(self, keylength, interrupts=[]):
        prob = BaselineProbability.load_ngram(keylength)
        maxlen = len(self.data) - len(self.data) % keylength
        res = [[] for _ in range(maxlen // keylength)]
        for v, data in enumerate(self.variants):
            for i in range(0, maxlen, keylength):
                gram = data[i:i + keylength]
                try:
                    value = prob[gram]
                except KeyError:
                    value = 0
                res[i // keylength].append((v, value))
        for arr in res:
            arr.sort(key=lambda x: -x[1])
        fillup = ' ' * (2 * keylength + 1)
        interrupts = [i for i, x in enumerate(self.data) if x == INV_INTERRUPT]
        for i in range(29):
            txt = ''
            for u, x in enumerate(res):
                u *= keylength
                tt = ''
                if x[i][1] > 0:
                    for o in range(u, u + keylength):
                        if o in interrupts:
                            tt += '|'  # mark with preceding
                        tt += Rune(r=self.variants[x[i][0]][o]).text
                txt += tt + fillup[len(tt):]
            txt = txt.rstrip()
            if txt:
                print(txt)


#########################################
#  main
#########################################

PROB_BASELINE = Probability.to_log(BaselineProbability.load())
K_r = 1 / 29   # 0.034482758620689655
K_p = sum([x ** 2 for x in PROB_BASELINE])  # 0.06116195419412538

if __name__ == '__main__':
    main()
