#!/usr/bin/env python3
import re
from RuneText import alphabet, RuneText


#########################################
#  NGrams  :  loads and writes ngrams, also: translate english text to runes
#########################################

class NGrams(object):
    @staticmethod
    def translate(infile, outfile, stream=False):  # takes 10s
        with open(infile, 'r') as f:
            src = re.sub('[^A-Z]', '' if stream else ' ', f.read().upper())
            if stream:
                src.replace('\n', '')

        with open(outfile, 'w') as f:
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
    def make(gramsize, infile, outfile):
        allowed_chr = [x[1] for x in alphabet]
        with open(infile, 'r') as f:
            data = re.sub('[^{}]'.format(''.join(allowed_chr)), '', f.read())

        res = {x: 0 for x in allowed_chr} if gramsize == 1 else {}
        for i in range(len(data) - gramsize + 1):
            ngram = data[i:i + gramsize]
            try:
                res[ngram] += 1
            except KeyError:
                res[ngram] = 1

        with open(outfile, 'w') as f:
            for x, y in sorted(res.items(), key=lambda x: -x[1]):
                f.write(f'{x} {y}\n')

    @staticmethod
    def load(ngram=1, prefix=''):
        ret = {}
        with open(f'data/p{prefix}-{ngram}gram.txt', 'r') as f:
            for line in f.readlines():
                r, v = line.split()
                ret[r] = int(v)
        return ret


# NGrams.translate('data/baseline-text.txt', 'data/baseline-rune.txt', False)
# for i in range(1, 6):
#     print(f'generate {i}-gram file')
#     NGrams.make(i, infile='data/baseline-rune-words.txt',
#                 outfile=f'data/p-{i}gram.txt')
#     NGrams.make(i, infile='_solved.txt',
#                 outfile=f'data/p-solved-{i}gram.txt')
#     NGrams.make(i, infile='data/baseline-rune-no-e.txt',
#                 outfile=f'data/p-no-e-{i}gram.txt')
