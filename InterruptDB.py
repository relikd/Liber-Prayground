#!/usr/bin/env python3
import os
from HeuristicSearch import SearchInterrupt
from HeuristicLib import load_indices, Probability


class InterruptDB(object):
    DB_NAME = 'data/interruptDB.txt'

    def __init__(self, data, interrupt):
        self.iguess = SearchInterrupt(data, interrupt)
        self.stop_count = len(self.iguess.stops)

    def make(self, keylen):
        def fn(x):
            return Probability.IC_w_keylen(x, keylen)
        score, intrpts = self.iguess.sequential(fn, startAt=0, maxdepth=99)
        # score, intrpts = self.iguess.genetic(fn, topDown=False, maxdepth=4)
        # score, intrpts = fn(self.iguess.join()), [[]]  # without interrupts
        for i, skips in enumerate(intrpts):
            intrpts[i] = self.iguess.to_occurrence_index(skips)
        return score, intrpts

    @staticmethod
    def load():
        if not os.path.isfile(InterruptDB.DB_NAME):
            return {}
        ret = {}
        with open(InterruptDB.DB_NAME, 'r') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                line = line.rstrip()
                name, irpc, score, irp, kl, nums = [x for x in line.split('|')]
                val = [int(irpc), float(score), int(irp), int(kl)]
                val.append([int(x) for x in nums.split(',')] if nums else [])
                try:
                    ret[name].append(val)
                except KeyError:
                    ret[name] = [val]
        return ret

    @staticmethod
    def write(fname, score, irpchr, irpmax, keylen, nums):
        nums = ','.join(map(str, nums))
        with open(InterruptDB.DB_NAME, 'a') as f:
            t = f'{fname}|{irpmax}|{score:.5f}|{irpchr}|{keylen}|{nums}\n'
            f.write(t)


def populate_db(irp_chars=range(1), startkeylen=1, maxkeylen=32):
    oldDB = InterruptDB.load()
    oldValues = {k: set((a, b, c) for a, _, b, c, _ in v)
                 for k, v in oldDB.items()}
    for name in [
        # '0_welcome', 'jpg107-167', '0_warning', '0_wisdom',
        'p0-2', 'p3-7', 'p8-14', 'p15-22', 'p23-26',
        'p27-32', 'p33-39', 'p40-53', 'p54-55'
    ]:
        fname = f'pages/{name}.txt'
        print('load:', fname)
        for irp in irp_chars:  # interrupt rune index
            data = load_indices(fname, irp, maxinterrupt=20)
            db = InterruptDB(data, irp)
            irp_count = db.stop_count
            print('analyze interrupt:', irp, 'count:', irp_count)
            for keylen in range(startkeylen, maxkeylen + 1):
                if (irp_count, irp, keylen) in oldValues.get(name, []):
                    print(f'{keylen}: skipped.')
                    continue
                score, interrupts = db.make(keylen)
                print(f'{keylen}: {score:.4f}, solutions: {len(interrupts)}')
                for x in interrupts:
                    InterruptDB.write(name, score, irp, irp_count, keylen, x)
