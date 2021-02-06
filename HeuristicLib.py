#!/usr/bin/env python3
import re
from RuneText import RuneText
from NGrams import NGrams


def normalized_probability(int_prob):
    total = sum(int_prob)
    return [x / total for x in int_prob]  # math.log(x / total, 10)


RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
re_norune = re.compile('[^' + RUNES + ']')
PROB_INT = [0] * 29
for k, v in NGrams.load(1, '').items():  # '-no-e', '-solved'
    PROB_INT[RUNES.index(k)] = v
PROB_NORM = normalized_probability(PROB_INT)
# Target IoC. peace and war: 1.77368517 solved: 1.78021503, no e: 1.82715300
N_total = (sum(PROB_INT) * (sum(PROB_INT) - 1)) / 29
TARGET_IOC = sum(x * (x - 1) for x in PROB_INT) / N_total
# TARGET_IOC = 1.78


#########################################
#  Probability  :  Count runes and do simple frequency analysis
#########################################

class Probability(object):
    def __init__(self, numstream):
        self.prob = [0] * 29
        for r in numstream:
            self.prob[r] += 1
        self.N = len(numstream)

    def IC(self):
        X = sum(x * (x - 1) for x in self.prob)
        return X / ((self.N * (self.N - 1)) / 29)

    def IC_norm(self, target_ioc=TARGET_IOC):
        return abs(self.IC() - target_ioc)

    def similarity(self):
        probs = normalized_probability(self.prob)
        return sum((x - y) ** 2 for x, y in zip(PROB_NORM, probs))

    @staticmethod
    def IC_w_keylen(nums, keylen):
        val = sum(Probability(nums[x::keylen]).IC() for x in range(keylen))
        return val / keylen

    @staticmethod
    def target_diff(nums, keylen, target_ioc=TARGET_IOC):
        val = sum(abs(Probability(nums[x::keylen]).IC() - target_ioc)
                  for x in range(keylen))
        return 1 - (val / keylen)


#########################################
#  load page and convert to indices for faster access
#########################################

def load_indices(fname, interrupt, maxinterrupt=None, minlen=None, limit=None):
    with open(fname, 'r') as f:
        data = RuneText(re_norune.sub('', f.read())).index[:limit]
    if maxinterrupt is not None:
        # incl. everything up to but not including next interrupt
        # e.g., maxinterrupt = 0 will return text until first interrupt
        for i, x in enumerate(data):
            if x != interrupt:
                continue
            if maxinterrupt == 0:
                if minlen and i < minlen:
                    continue
                return data[:i]
            maxinterrupt -= 1
    return data
