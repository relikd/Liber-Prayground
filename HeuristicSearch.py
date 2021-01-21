#!/usr/bin/env python3
import itertools  # product, compress, combinations
import bisect  # bisect_left, insort
import lib as LIB


#########################################
#  GuessVigenere  :  Shift values around with a given keylength
#########################################

class GuessVigenere(object):
    def __init__(self, nums):
        self.nums = nums

    def guess(self, keylength, score_fn):  # minimize score_fn
        found = []
        for offset in range(keylength):
            bi = -1
            bs = 9999999
            for i in range(29):
                shifted = [(x - i) % 29 for x in self.nums[offset::keylength]]
                score = score_fn(shifted)
                if score < bs:
                    bs = score
                    bi = i
            found.append(bi)
        return found


#########################################
#  GuessAffine  :  Find greatest common affine key
#########################################

class GuessAffine(object):
    def __init__(self, nums):
        self.nums = nums

    def guess(self, keylength, score_fn):  # minimize score_fn
        found = []
        for offset in range(keylength):
            candidate = (None, None)
            best = 9999999
            for s in range(29):
                for t in range(29):
                    shifted = [LIB.affine_decrypt(x, (s, t))
                               for x in self.nums[offset::keylength]]
                    score = score_fn(shifted)
                    if score < best:
                        best = score
                        candidate = (s, t)
            found.append(candidate)
        return found


#########################################
#  SearchInterrupt  :  Hill climbing algorithm for interrupt detection
#########################################

class SearchInterrupt(object):
    def __init__(self, arr, interrupt_chr):  # remove all whitespace in arr
        self.single_result = False  # if False, return list of equal likelihood
        self.full = arr
        self.stops = [i for i, n in enumerate(arr) if n == interrupt_chr]

    def to_occurrence_index(self, interrupts):
        return [self.stops.index(x) + 1 for x in interrupts]

    def from_occurrence_index(self, interrupts):
        return [self.stops[x - 1] for x in interrupts]

    def join(self, interrupts=[]):  # rune positions, not occurrence index
        ret = []
        i = -1
        for x in interrupts:
            ret += self.full[i + 1:x]
            i = x
        return ret + self.full[i + 1:]

    # Go over the full string but only look at the first {maxdepth} interrupts.
    # Enumerate all possibilities and choose the one with the highest score.
    # If first interrupt is set, add it to the resulting set. If not, ignore it
    # Every iteration will add a single interrupt only, not the full set.
    def sequential(self, score_fn, startAt=0, maxdepth=9):
        found = [[]]

        def best_in_one(i, depth, prefix=[]):
            best_s = 0
            best_p = []  # [match, match, ...]
            irp = self.stops[i:i + depth]
            for x in itertools.product([False, True], repeat=depth):
                part = list(itertools.compress(irp, x))
                score = score_fn(self.join(prefix + part))
                if score >= best_s:
                    if score > best_s or self.single_result:
                        best_s = score
                        best_p = [part]
                    else:
                        best_p.append(part)
            return best_p, best_s

        def best_in_all(i, depth):
            best_s = 0
            best_p = []  # [(prefix, [match, match, ...]), ...]
            for pre in found:
                parts, score = best_in_one(i, depth, prefix=pre)
                if score >= best_s:
                    if score > best_s or self.single_result:
                        best_s = score
                        best_p = [(pre, parts)]
                    else:
                        best_p.append((pre, parts))
            return best_p, best_s

        # first step: move maxdepth-sized window over data
        i = startAt - 1  # in case loop isnt called
        for i in range(startAt, len(self.stops) - maxdepth):
            print('.', end='')
            parts, _ = best_in_all(i, maxdepth)
            found = []
            search = self.stops[i]
            for prfx, candidates in parts:
                bitSet = False
                bitNotSet = False
                for x in candidates:
                    if len(x) > 0 and x[0] == search:
                        bitSet = True
                    else:
                        bitNotSet = True
                    if bitSet and bitNotSet:
                        break
                if bitSet:
                    found.append(prfx + [search])
                if bitNotSet:
                    found.append(prfx)
        print('.')
        # last step: all permutations for the remaining (< maxdepth) bits
        i += 1
        remaining, score = best_in_all(i, min(maxdepth, len(self.stops) - i))
        found = [x + z for x, y in remaining for z in y]
        return score, found

    # Flip upto {maxdepth} bits anywhere in the full string.
    # Choose the bitset with the highest score and repeat.
    # If no better score found, increment number of testing bits and repeat.
    # Either start with all interrupts set (topDown) or none set.
    def genetic(self, score_fn, topDown=False, maxdepth=3):
        best = 0
        current = self.stops if topDown else []

        def evolve(lvl):
            for x in itertools.combinations(self.stops, lvl + 1):
                tmp = current[:]  # [x for x in current if x not in old]
                for y in x:
                    if y is None:
                        continue
                    elif y in current:
                        tmp.pop(bisect.bisect_left(tmp, y))
                    else:
                        bisect.insort(tmp, y)
                yield tmp, score_fn(self.join(tmp))
            if lvl > 0:
                yield from evolve(lvl - 1)

        best = score_fn(self.join())
        level = -1  # or start directly with maxdepth - 1
        while level < maxdepth:
            print('.', end='')
            update = None
            for interrupts, score in evolve(level):
                if score > best:
                    best = score
                    update = interrupts
            if update:
                current = update
                continue  # did optimize, so retry with same level
            level += 1
        print('.')
        # find equally likely candidates
        if self.single_result:
            return best, [current]
        all_of_them = [x for x, score in evolve(2) if score == best]
        all_of_them.append(current)
        return best, all_of_them


# a = GuessInterrupt([2, 0, 1, 0, 14, 15, 0, 13, 24, 25, 25, 25], 0)
# print(a.sequential(lambda x: (1.2 if len(x) == 11 else 0.1)))
# print(a.sequential(lambda x: (1.1 if len(x) == 10 else 0.1)))
# print(a.sequential(lambda x: (1.3 if len(x) == 9 else 0.1)))
