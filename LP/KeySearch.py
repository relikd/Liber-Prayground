#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from utils import affine_decrypt


#########################################
#  GuessVigenere  :  Shift values around with a given keylength
#########################################

class GuessVigenere(object):
    def __init__(self, nums):
        self.nums = nums

    def guess(self, keylength, score_fn):  # minimize score_fn
        found = []
        avg_score = 0
        for offset in range(keylength):
            bi = -1
            bs = 9999999
            for i in range(29):
                shifted = [(x - i) % 29 for x in self.nums[offset::keylength]]
                score = score_fn(shifted)
                if score < bs:
                    bs = score
                    bi = i
            avg_score += bs
            found.append(bi)
        return avg_score / keylength, found


#########################################
#  GuessAffine  :  Find greatest common affine key
#########################################

class GuessAffine(object):
    def __init__(self, nums):
        self.nums = nums

    def guess(self, keylength, score_fn):  # minimize score_fn
        found = []
        avg_score = 0
        for offset in range(keylength):
            candidate = (None, None)
            best = 9999999
            for s in range(29):
                for t in range(29):
                    shifted = [affine_decrypt(x, (s, t))
                               for x in self.nums[offset::keylength]]
                    score = score_fn(shifted)
                    if score < best:
                        best = score
                        candidate = (s, t)
            avg_score += best
            found.append(candidate)
        return avg_score / keylength, found


#########################################
#  GuessPattern  :  Find a key that is rotated ABC BCA CAB, or ABC CAB BCA
#########################################

class GuessPattern(object):
    def __init__(self, nums):
        self.nums = nums

    @staticmethod
    def pattern(keylen, fn_pattern):
        mask = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:keylen]
        return fn_pattern(mask, keylen)

    def split(self, keylen, mask, offset=0):
        ret = {}
        for _ in range(offset):
            next(mask)
        ret = {k: [] for k in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:keylen]}
        for n, k in zip(self.nums, mask):
            ret[k].append(n)
        return ret.values()

    def zip(self, key_mask, offset=0):
        for _ in range(offset):
            next(key_mask)
        return [(n - k) % 29 for n, k in zip(self.nums, key_mask)]

    @staticmethod
    def guess(parts, score_fn):  # minimize score_fn
        found = []
        avg_score = 0
        for nums in parts:
            best = 9999999
            candidate = 0
            for i in range(29):
                score = score_fn([(x - i) % 29 for x in nums])
                if score < best:
                    best = score
                    candidate = i
            avg_score += best
            found.append(candidate)
        return avg_score / len(parts), found
