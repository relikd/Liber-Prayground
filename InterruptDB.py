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
        if keylen == 0:
            keylen = 1
            score, skips = fn(self.iguess.join()), [[]]  # without interrupts
        else:
            score, skips = self.iguess.sequential(fn, startAt=0, maxdepth=99)
            # score, skips = self.iguess.genetic(fn, topDown=False, maxdepth=4)
        for i, interrupts in enumerate(skips):
            skips[i] = self.iguess.to_occurrence_index(interrupts)
        return score, skips

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


def populate_db(irp_chars=range(1), startkeylen=1, maxkeylen=32, max_irp=20):
    oldDB = InterruptDB.load()
    oldValues = {k: set((a, b, c) for a, _, b, c, _ in v)
                 for k, v in oldDB.items()}
    for name in [
        # '0_warning', '0_welcome', '0_wisdom', '0_koan_1', 'jpg107-167',
        # '0_loss_of_divinity', 'jpg229', 'p56_an_end', 'p57_parable',
        'p0-2', 'p3-7', 'p8-14', 'p15-22', 'p23-26',
        'p27-32', 'p33-39', 'p40-53', 'p54-55'
    ]:
        fname = f'pages/{name}.txt'
        print('load:', fname)
        for irp in irp_chars:  # interrupt rune index
            data = load_indices(fname, irp, maxinterrupt=max_irp)
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


# populate_db(startkeylen=0, maxkeylen=0, max_irp=None)
