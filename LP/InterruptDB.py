#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
from InterruptSearch import InterruptSearch
from InterruptIndices import InterruptIndices
from Probability import Probability
from RuneText import RuneTextFile
from LPath import FILES_ALL, FILES_UNSOLVED, LPath


#########################################
#  InterruptDB  :  Perform heuristic search on best possible interrupts.
#########################################

class InterruptDB(object):
    def __init__(self, data, interrupt, irp_stops=None):
        self.irp = interrupt
        self.iguess = InterruptSearch(data, irp=interrupt, irp_stops=irp_stops)
        self.irp_count = len(self.iguess.stops)

    def make(self, dbname, name, keylen, fn_score):
        if keylen == 0:  # without interrupts
            score, skips = fn_score(self.iguess.join(), 1), [[]]
        else:
            score, skips = self.iguess.all(keylen, fn_score)
        for i, interrupts in enumerate(skips):
            skips[i] = self.iguess.to_occurrence_index(interrupts)

        for nums in skips:
            self.write(
                name, score, self.irp, self.irp_count, keylen, nums, dbname)
        return score, skips

    def make_secondary(self, dbname, name, keylen, fn_score, threshold):
        scores = []

        def fn(x, kl):
            score = fn_score(x, kl)
            if score >= threshold:
                scores.append(score)
                return 1
            return -1

        _, skips = self.iguess.all(keylen, fn)
        for i, interrupts in enumerate(skips):
            skips[i] = self.iguess.to_occurrence_index(interrupts)
        ret = list(zip(scores, skips))
        bestscore = max(ret)[0]
        # exclude best results, as they are already present in the main db
        filtered = [x for x in ret if x[0] < bestscore]
        for score, nums in filtered:
            self.write(
                name, score, self.irp, self.irp_count, keylen, nums, dbname)
        return len(filtered)

    @staticmethod
    def load(dbname):
        if not os.path.isfile(LPath.db(dbname)):
            return {}
        ret = {}
        with open(LPath.db(dbname), 'r') as f:
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
    def load_scores(dbname):
        scores = {}  # {fname: [irp0_[kl0, kl1, ...], irp1_[...]]}
        for k, v in InterruptDB.load(dbname).items():
            for irpc, score, irp, kl, nums in v:
                if k not in scores:
                    scores[k] = [[] for _ in range(29)]
                part = scores[k][irp]
                while kl >= len(part):
                    part.append((0, 0))  # (score, irp_count)
                oldc = part[kl][1]
                if irpc > oldc or (irpc == oldc and score > part[kl][0]):
                    part[kl] = (score, irpc)
        return scores

    @staticmethod
    def write(name, score, irp, irpmax, keylen, nums, dbname='db_main'):
        with open(LPath.db(dbname), 'a') as f:
            nums = ','.join(map(str, nums))
            f.write(f'{name}|{irpmax}|{score:.5f}|{irp}|{keylen}|{nums}\n')


#########################################
#  helper functions
#########################################

def get_db(fname, irp, max_irp):
    stops, Z = InterruptIndices().consider(fname, irp, max_irp)
    data = RuneTextFile(LPath.page(fname)).index_no_white[:Z]
    return InterruptDB(data, irp, irp_stops=stops)


def create_primary(dbname, fn_score, klset=range(1, 33),
                   max_irp=20, irpset=range(29), files=FILES_ALL):
    oldDB = InterruptDB.load(dbname)
    oldValues = {k: set((a, b, c) for a, _, b, c, _ in v)
                 for k, v in oldDB.items()}
    for irp in irpset:  # interrupt rune index
        for name in files:
            db = get_db(name, irp, max_irp)
            print('load:', name, 'interrupt:', irp, 'count:', db.irp_count)
            for keylen in klset:  # key length
                if (db.irp_count, irp, keylen) in oldValues.get(name, []):
                    print(f'{keylen}: skipped.')
                    continue
                score, interrupts = db.make(dbname, name, keylen, fn_score)
                print(f'{keylen}: {score:.4f}, solutions: {len(interrupts)}')


def create_secondary(db_in, db_out, fn_score, threshold=0.75, max_irp=20):
    oldDB = InterruptDB.load(db_in)
    search_set = set()
    for name, arr in oldDB.items():
        if name not in FILES_UNSOLVED:
            continue
        for irpc, score, irp, kl, nums in arr:
            if score <= threshold or kl > 26 or kl < 3:
                continue
            search_set.add((name, irp, kl))
    print('searching through', len(search_set), 'files.')
    for name, irp, kl in search_set:
        print('load:', name, 'interrupt:', irp, 'keylen:', kl)
        db = get_db(name, irp, max_irp)
        c = db.make_secondary(db_out, name, kl, fn_score, threshold)
        print('found', c, 'additional solutions')


def create_mod_a_db(dbprefix, fn_score, klpairs, max_irp=20, irpset=[0, 28]):
    for mod, upto in klpairs:
        for mo in range(mod):
            # if needed add combined check for all modulo parts
            def xor_split(data, keylen):
                return fn_score(data[mo::mod], keylen)

            create_primary(f'db_{dbprefix}_mod_a_{mod}.{mo}', xor_split,
                           range(1, upto + 1), max_irp, irpset, FILES_UNSOLVED)


def create_mod_b_db(dbprefix, fn_score, klpairs, max_irp=20, irpset=[0, 28]):
    db_i = InterruptIndices()
    for mod, upto in klpairs:
        for mo in range(mod):
            dbname = f'db_{dbprefix}_mod_b_{mod}.{mo}'
            oldDB = {k: set((a, b, c) for a, _, b, c, _ in v)
                     for k, v in InterruptDB.load(dbname).items()}

            for irp in irpset:  # interrupt rune index
                for name in FILES_UNSOLVED:
                    stops, Z = db_i.consider_mod_b(name, irp, max_irp, mod)
                    stops = stops[mo]
                    Z = Z[mo]
                    data = RuneTextFile(LPath.page(name)).index_no_white
                    data = data[mo::mod][:Z]
                    db = InterruptDB(data, irp, irp_stops=stops)
                    print(f'load: {name} interrupt: {irp} count: {len(stops)}')
                    for keylen in range(2, upto + 1):  # key length
                        if (db.irp_count, irp, keylen) in oldDB.get(name, []):
                            print(f'{keylen}: skipped.')
                            continue
                        score, irps = db.make(dbname, name, keylen, fn_score)
                        print(f'{keylen}: {score:.4f}, solutions: {len(irps)}')


if __name__ == '__main__':
    create_primary('db_high', Probability.IC_w_keylen, max_irp=20)
    create_primary('db_norm', Probability.target_diff, max_irp=20)
    create_mod_a_db('high', Probability.IC_w_keylen, [(2, 13), (3, 8)])
    create_mod_a_db('norm', Probability.target_diff, [(2, 13), (3, 8)])
    create_mod_b_db('high', Probability.IC_w_keylen, [(2, 18), (3, 18)])
    create_mod_b_db('norm', Probability.target_diff, [(2, 18), (3, 18)])
    # create_secondary('db_high', 'db_high_secondary',
    #                  Probability.IC_w_keylen, threshold=1.4)
    # create_secondary('db_norm', 'db_norm_secondary',
    #                  Probability.target_diff, threshold=0.55)
