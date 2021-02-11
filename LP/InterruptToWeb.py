#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from Alphabet import RUNES
from LPath import FILES_ALL, LPath
from InterruptDB import InterruptDB
from InterruptIndices import InterruptIndices


#########################################
#  InterruptToWeb  :  Read interrupt DB and create html graphic / matrix
#########################################

class InterruptToWeb(object):
    def __init__(self, dbname, template='template.html'):
        with open(LPath.results(template), 'r') as f:
            self.template = f.read()
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
                _, num = self.indices.consider(name, i, worst_irpc)
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
        nav = ''
        txt = ''
        for i in range(29):
            has_entries = any(True for x in self.scores.values() if x[i])
            if not has_entries:
                continue
            nav += f'<a href="#tb-i{i}">{RUNES[i]}</a>\n'
            txt += f'<h3 id="tb-i{i}">Interrupt {i}: <b>{RUNES[i]}</b></h3>'
            txt += self.table_interrupt(i, pmin, pmax)
        html = self.template.replace('__NAVIGATION__', nav)
        html = html.replace('__TAB_RELIABLE__', self.table_reliable())
        html = html.replace('__INTERRUPT_TABLES__', txt)
        with open(LPath.results(outfile), 'w') as f:
            f.write(html)


if __name__ == '__main__':
    InterruptToWeb('db_high').make('index_high.html')
    InterruptToWeb('db_norm').make('index_norm.html', pmin=0.40, pmax=0.98)
