#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import re  # load_indices
from Alphabet import RUNES
from RuneText import RuneText

re_norune = re.compile('[^' + ''.join(RUNES) + ']')


#########################################
#  load page and convert to indices for faster access
#########################################

def load_indices(fname, interrupt, maxinterrupt=None, minlen=None, limit=None):
    with open(fname, 'r') as f:
        data = RuneText(re_norune.sub('', f.read())).index_no_white[:limit]
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


#########################################
#  find the longest chunk in a list of indices, which does not include an irp
#########################################

def longest_no_interrupt(data, interrupt, irpmax=0):
    def add(i):
        nonlocal ret, prev
        idx = prev.pop(0)
        if idx == 0:
            ret = []
        ret.append((i - idx, idx))

    prev = [0] * (irpmax + 1)
    ret = []
    for i, x in enumerate(data):
        if x == interrupt:
            prev.append(i + 1)
            add(i)
    add(i + 1)
    length, pos = max(ret)
    return pos, length
