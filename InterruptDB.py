#!/usr/bin/env python3
import os
from HeuristicSearch import SearchInterrupt
from HeuristicLib import load_indices, Probability

RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'  # used in InterruptToWeb
FILES_SOLVED = ['0_warning', '0_welcome', '0_wisdom', '0_koan_1',
                '0_loss_of_divinity', 'jpg107-167', 'jpg229',
                'p56_an_end', 'p57_parable']
FILES_UNSOLVED = ['p0-2', 'p3-7', 'p8-14', 'p15-22', 'p23-26',
                  'p27-32', 'p33-39', 'p40-53', 'p54-55']
FILES_ALL = FILES_UNSOLVED + FILES_SOLVED


#########################################
#  InterruptDB  :  Perform heuristic search on best possible interrupts.
#########################################

class InterruptDB(object):
    def __init__(self, data, interrupt):
        self.irp = interrupt
        self.iguess = SearchInterrupt(data, interrupt)
        self.irp_count = len(self.iguess.stops)

    def make(self, dbname, name, keylen):
        def fn(x):
            return Probability.target_diff(x, keylen)  # used in db_norm
            # return Probability.IC_w_keylen(x, keylen)  # used in db_high

        if keylen == 0:
            keylen = 1
            score, skips = fn(self.iguess.join()), [[]]  # without interrupts
        else:
            score, skips = self.iguess.sequential(fn, startAt=0, maxdepth=99)
            # score, skips = self.iguess.genetic(fn, topDown=False, maxdepth=4)
        for i, interrupts in enumerate(skips):
            skips[i] = self.iguess.to_occurrence_index(interrupts)

        for nums in skips:
            self.write(
                name, score, self.irp, self.irp_count, keylen, nums, dbname)
        return score, skips

    def make_secondary(self, dbname, name, keylen, threshold):
        scores = []

        def fn(x):
            score = Probability.target_diff(x, keylen)  # used in db_norm
            # score = Probability.IC_w_keylen(x, keylen)  # used in db_high
            if score >= threshold:
                scores.append(score)
                return 1
            return -1

        _, skips = self.iguess.sequential(fn, startAt=0, maxdepth=99)
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

    @staticmethod
    def load(dbname):
        if not os.path.isfile(f'InterruptDB/{dbname}.txt'):
            return {}
        ret = {}
        with open(f'InterruptDB/{dbname}.txt', 'r') as f:
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
    def write(name, score, irp, irpmax, keylen, nums, dbname='db_main'):
        with open(f'InterruptDB/{dbname}.txt', 'a') as f:
            nums = ','.join(map(str, nums))
            f.write(f'{name}|{irpmax}|{score:.5f}|{irp}|{keylen}|{nums}\n')


#########################################
#  InterruptIndices  :  Read chapters and extract indices (cluster by runes)
#########################################

class InterruptIndices(object):
    def __init__(self):
        self.pos = InterruptIndices.read()

    def consider(self, name, irp, limit):
        nums = self.pos[name]['pos'][irp]
        if len(nums) <= limit:
            return self.pos[name]['total']
        return nums[limit]  # number of runes, which is not last index

    def total(self, name):
        return self.pos[name]['total']

    def longest_no_interrupt(self, name, irp, irpmax=0):
        irpmax += 1
        nums = self.pos[name]['pos'][irp] + [self.pos[name]['total']] * irpmax
        ret = [(y - x, x) for x, y in zip(nums, nums[irpmax:])]
        return sorted(ret, reverse=True)

    @staticmethod
    def write(dbname='db_indices'):
        with open(f'InterruptDB/{dbname}.txt', 'w') as f:
            f.write('# file | total runes in file | interrupt | indices\n')
            for name in FILES_ALL:
                fname = f'pages/{name}.txt'
                data = load_indices(fname, 0)
                total = len(data)
                nums = [[] for x in range(29)]
                for idx, rune in enumerate(data):
                    nums[rune].append(idx)
                for irp, pos in enumerate(nums):
                    f.write('{}|{}|{}|{}\n'.format(
                        name, total, irp, ','.join(map(str, pos))))

    @staticmethod
    def read(dbname='db_indices'):
        with open(f'InterruptDB/{dbname}.txt', 'r') as f:
            ret = {}
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                line = line.strip()
                name, total, irp, nums = line.split('|')
                if name not in ret:
                    ret[name] = {'total': int(total),
                                 'pos': [[] for _ in range(29)]}
                pos = ret[name]['pos']
                pos[int(irp)] = list(map(int, nums.split(','))) if nums else []
            return ret


#########################################
#  InterruptToWeb  :  Read interrupt DB and create html graphic / matrix
#########################################

class InterruptToWeb(object):
    def __init__(self, dbname, template='InterruptDB/template.html'):
        self.template = template
        self.indices = InterruptIndices()
        self.scores = {}
        db = InterruptDB.load(dbname)
        for k, v in db.items():
            for irpc, score, irp, kl, nums in v:
                if k not in self.scores:
                    self.scores[k] = [[] for _ in range(29)]
                part = self.scores[k][irp]
                while kl >= len(part):
                    part.append((0, 0))  # (score, irpc)
                oldc = part[kl][1]
                if irpc > oldc or (irpc == oldc and score > part[kl][0]):
                    part[kl] = (score, irpc)

    def cls(self, x, low=0, high=1):
        if x <= low:
            return ' class="m0"'
        return f' class="m{int((min(high, x) - low) / (high - low) * 14) + 1}"'

    def table_reliable(self):
        trh = '<tr class="rotate"><th></th>'
        trtotal = '<tr class="small"><th>Total</th>'
        trd = [f'<tr><th>{x}</th>' for x in RUNES]
        del_row = [True] * 29
        for name in FILES_ALL:
            if name not in self.scores:
                continue
            total = self.indices.total(name)
            trh += f'<th><div>{name}</div></th>'
            trtotal += f'<td>{total}</td>'
            for i in range(29):
                scrs = self.scores[name][i][1:]
                if not scrs:
                    trd[i] += '<td>–</td>'
                    continue
                del_row[i] = False
                worst_irpc = min([x[1] for x in scrs])
                if worst_irpc == 0:
                    if max([x[1] for x in scrs]) != 0:
                        trd[i] += '<td>?</td>'
                        continue
                num = self.indices.consider(name, i, worst_irpc)
                trd[i] += f'<td{self.cls(num, 384, 812)}>{num}</td>'

        trh += '</tr>\n'
        trtotal += '</tr>\n'
        for i in range(29):
            trd[i] += '</tr>\n'
            if del_row[i]:
                trd[i] = ''
        return f'<table>{trh}{"".join(trd)}{trtotal}</table>'

    def table_interrupt(self, irp, pmin=1.25, pmax=1.65):
        maxkl = max(len(x[irp]) for x in self.scores.values())
        trh = '<tr class="rotate"><th></th>'
        trbest = '<tr class="small"><th>best</th>'
        trd = [f'<tr><th>{x}</th>' for x in range(maxkl)]
        for name in FILES_ALL:
            maxscore = 0
            bestkl = -1
            try:
                klarr = self.scores[name][irp]
            except KeyError:
                continue
            trh += f'<th><div>{name}</div></th>'
            for kl, (score, _) in enumerate(klarr):
                if score < 0:
                    trd[kl] += f'<td{self.cls(0)}>–</td>'
                else:
                    trd[kl] += f'<td{self.cls(score, pmin, pmax)}>{score:.2f}</td>'
                if score > maxscore:
                    maxscore = score
                    bestkl = kl
            trbest += f'<td>{bestkl}</td>'
        trh += '</tr>\n'
        trbest += '</tr>\n'
        for i in range(29):
            trd[i] += '</tr>\n'
        return f'<table>{trh}{"".join(trd[1:])}{trbest}</table>'

    def make(self, outfile, pmin=1.25, pmax=1.65):
        with open(self.template, 'r') as f:
            html = f.read()
        nav = ''
        txt = ''
        for i in range(29):
            has_entries = any(True for x in self.scores.values() if x[i])
            if not has_entries:
                continue
            nav += f'<a href="#tb-i{i}">{RUNES[i]}</a>\n'
            txt += f'<h3 id="tb-i{i}">Interrupt {i}: <b>{RUNES[i]}</b></h3>'
            txt += self.table_interrupt(i, pmin, pmax)
        html = html.replace('__NAVIGATION__', nav)
        html = html.replace('__TAB_RELIABLE__', self.table_reliable())
        html = html.replace('__INTERRUPT_TABLES__', txt)
        with open(outfile, 'w') as f:
            f.write(html)


#########################################
#  helper functions
#########################################

def create_initial_db(dbname, minkl=1, maxkl=32, max_irp=20, irpset=range(29)):
    oldDB = InterruptDB.load(dbname)
    oldValues = {k: set((a, b, c) for a, _, b, c, _ in v)
                 for k, v in oldDB.items()}
    for irp in irpset:  # interrupt rune index
        # for name in FILES_UNSOLVED:
        for name in FILES_ALL:
            fname = f'pages/{name}.txt'
            data = load_indices(fname, irp, maxinterrupt=max_irp)
            db = InterruptDB(data, irp)
            print('load:', fname, 'interrupt:', irp, 'count:', db.irp_count)
            for keylen in range(minkl, maxkl + 1):  # key length
                if (db.irp_count, irp, keylen) in oldValues.get(name, []):
                    print(f'{keylen}: skipped.')
                    continue
                score, interrupts = db.make(dbname, name, keylen)
                print(f'{keylen}: {score:.4f}, solutions: {len(interrupts)}')


def find_secondary_solutions(db_in, db_out, threshold=0.75, max_irp=20):
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
        fname = f'pages/{name}.txt'
        print('load:', fname, 'interrupt:', irp, 'keylen:', kl)
        data = load_indices(fname, irp, maxinterrupt=max_irp)
        db = InterruptDB(data, irp)
        c = db.make_secondary(db_out, name, kl, threshold)
        print('found', c, 'additional solutions')


if __name__ == '__main__':
    # find_secondary_solutions('db_high', 'db_high_secondary', threshold=1.4)
    # find_secondary_solutions('db_norm', 'db_norm_secondary', threshold=0.55)
    # create_initial_db('db_norm', minkl=1, maxkl=32, max_irp=20)
    # InterruptToWeb('db_high').make('InterruptDB/index_high.html')
    InterruptToWeb('db_norm').make(
        'InterruptDB/index_norm.html', pmin=0.40, pmax=0.98)
