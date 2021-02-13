#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from Alphabet import RUNES
from LPath import FILES_ALL, FILES_SOLVED, LPath
from InterruptDB import InterruptDB
from InterruptIndices import InterruptIndices
from RuneText import RuneTextFile
from Probability import Probability

NORM_MIN = 0.40
NORM_MAX = 0.98
HIGH_MIN = 1.25
HIGH_MAX = 1.65


def mark(x, low=0, high=1):
    if x <= low:
        return ' class="m0"'
    return f' class="m{int((min(high, x) - low) / (high - low) * 14) + 1}"'


#########################################
#  InterruptToWeb  :  Read interrupt DB and create html graphic / matrix
#########################################

class InterruptToWeb(object):
    def __init__(self, dbname, template='templates/ioc.html'):
        with open(LPath.results(template), 'r') as f:
            self.template = f.read()
        self.scores = InterruptDB.load_scores(dbname)

    def table_reliable(self):
        db_indices = InterruptIndices()
        trh = '<tr class="rotate"><th></th>'
        trtotal = '<tr class="small"><th>Total</th>'
        trd = [f'<tr><th>{x}</th>' for x in RUNES]
        del_row = [True] * 29
        for name in FILES_ALL:
            if name not in self.scores:
                continue
            total = db_indices.total(name)
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
                _, num = db_indices.consider(name, i, worst_irpc)
                trd[i] += f'<td{mark(num, 384, 812)}>{num}</td>'

        trh += '</tr>\n'
        trtotal += '</tr>\n'
        for i in range(29):
            trd[i] += '</tr>\n'
            if del_row[i]:
                trd[i] = ''
        return f'<table>{trh}{"".join(trd)}{trtotal}</table>'

    def table_interrupt(self, irp, pmin, pmax):
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
                    trd[kl] += f'<td{mark(0)}>–</td>'
                else:
                    trd[kl] += f'<td{mark(score, pmin, pmax)}>{score:.2f}</td>'
                if score > maxscore:
                    maxscore = score
                    bestkl = kl
            trbest += f'<td>{bestkl}</td>'
        trh += '</tr>\n'
        trbest += '</tr>\n'
        for i in range(29):
            trd[i] += '</tr>\n'
        return f'<table>{trh}{"".join(trd[1:])}{trbest}</table>'

    def make(self, outfile, pmin, pmax):
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


class ChapterToWeb(object):
    def __init__(self, template='templates/pages.html'):
        with open(LPath.results(template), 'r') as f:
            self.template = f.read()
        self.score = [(InterruptDB.load_scores('db_high'), HIGH_MIN, HIGH_MAX),
                      (InterruptDB.load_scores('db_norm'), NORM_MIN, NORM_MAX)]

    def pick_ngrams(self, runes, gramsize, limit=100):
        res = {}
        for i in range(len(runes) - gramsize + 1):
            z = ''.join(x.rune for x in runes[i:i + gramsize])
            try:
                res[z] += 1
            except KeyError:
                res[z] = 1
        res = sorted(res.items(), key=lambda x: -x[1])
        txt = f'<dt>{gramsize}-grams:</dt>\n'
        txt += '<dd class="tabwidth">\n'
        for x, y in res[:limit]:
            txt += f'<div><div>{x}:</div> {y}</div>'
        if len(res) > limit:
            txt += f' + {len(res) - limit} others'
        return txt + '</dd>\n'

    def sec_counts(self, words, runes):
        txt = ''
        txt += f'<p><b>Words:</b> {len(words)}</p>\n'
        txt += f'<p><b>Runes:</b> {len(runes)}</p>\n'
        txt += '<dl>\n'
        rcount = [0] * 29
        for r in runes:
            rcount[r.index] += 1
        minmax = [min(rcount), max(rcount)]
        txt += '<dt>1-grams:</dt>\n'
        txt += '<dd class="tabwidth">\n'
        for x, y in zip(RUNES, rcount):
            txt += f'<div><div>{x}:</div> '
            if y in minmax:
                txt += '<b>'
            txt += str(y)
            if y in minmax:
                txt += '</b>'
            txt += '</div>'
        txt += '</dd>\n'
        txt += self.pick_ngrams(runes, 2, limit=100)
        txt += self.pick_ngrams(runes, 3, limit=50)
        txt += self.pick_ngrams(runes, 4, limit=25)
        txt += '</dl>\n'
        return txt

    def sec_double_rune(self, indices):
        txta = '<dt>Double Runes:</dt>\n<dd class="ioc-list small one">\n'
        txtb = '<dt>Rune Difference:</dt>\n<dd class="ioc-list small two">\n'
        for i, (a, b) in enumerate(zip(indices, indices[1:])):
            x = min(abs(a - b), min(a, b) + 29 - max(a, b))
            y = 1 if x == 0 else 0
            sffx = f' title="offset: {i}, rune: {RUNES[a]}"' if y else ''
            txta += f'<div{mark(y)}{sffx}>{y}</div>'
            txtb += f'<div{mark(x, 0, 14)} title="offset: {i}">{x}</div>'
        txta += '</dd>\n'
        txtb += '</dd>\n'
        return '<dl>' + txta + txtb + '</dl>\n'

    def sec_ioc(self, fname):
        trh1 = '<tr><th></th>'
        trh1 += '<th colspan="2">IoC-<a href="./ioc_high.html">high</a></th>'
        trh1 += '<th colspan="2">IoC-<a href="./ioc_norm.html">norm</a></th>'
        trh1 += '<th colspan="2">Runes / keylen</th>'
        trh2 = '<tr><th></th>'
        trbest = '<tr class="small"><th>best</th>'
        trd = [f'<tr><th>{x}</th>' for x in range(33)]
        scores = None
        for scores, pmin, pmax in self.score:
            for irp in [0, 28]:
                maxscore = 0
                bestkl = -1
                try:
                    klarr = scores[fname][irp]
                except KeyError:
                    continue
                trh2 += f'<th><div>{RUNES[irp]}</div></th>'
                for kl, (score, _) in enumerate(klarr):
                    if score < 0:
                        trd[kl] += f'<td{mark(0)}>–</td>'
                    else:
                        trd[kl] += f'<td{mark(score, pmin, pmax)}>{score:.2f}</td>'
                    if score > maxscore:
                        maxscore = score
                        bestkl = kl
                trbest += f'<td>{bestkl}</td>'

        db_indices = InterruptIndices()
        for irp in [0, 28]:
            try:
                klarr = scores[fname][irp]
            except KeyError:
                continue
            trh2 += f'<th><div>{RUNES[irp]}</div></th>'
            for kl, (_, maxirp) in enumerate(klarr):
                if maxirp > 0:
                    _, num = db_indices.consider(fname, irp, maxirp)
                    num /= kl
                    trd[kl] += f'<td{mark(num, 29, 100)}>{int(num)}</td>'
        trh1 += '</tr>\n'
        trh2 += '</tr>\n'
        trbest += '</tr>\n'
        for i in range(len(trd)):
            trd[i] += '</tr>\n'
        return f'<table>{trh1}{trh2}{"".join(trd[1:])}{trbest}</table>'

    def sec_ioc_flow(self, indices, width):
        txt = f'<dt>Window size {width}:</dt>\n'
        txt += '<dd class="ioc-list small four">\n'
        for i in range(len(indices) - width + 1):
            ioc = Probability(indices[i:i + width]).IC()
            clss = mark(ioc, HIGH_MIN - 0.1, HIGH_MAX)
            txt += f'<div{clss} title="offset: {i}">{ioc:.2f}</div>'
        txt += '</dd>\n'
        return txt

    def pick_letters(self, words, idx, desc):
        letters = []
        for x in words:
            letters.append(x[idx])
        ioc = Probability(x.index for x in letters).IC()
        txt = f'<dt>Pick every {desc} letter (IoC: {ioc:.3f}):</dt>\n'
        txt += '<dd class="runelist">\n'
        for x in letters:
            txt += f'<div>{x.text}</div>'
        txt += '</dd>\n'
        return txt

    def pick_words(self, words, n):
        txt = ''
        for u in range(n):
            if n > 1:
                txt += f'<h4>Start with {u + 1}. word</h4>\n'
            subset = [x for x in words[u:None:n]]
            ioc = Probability(x.index for y in subset for x in y).IC()
            txt += f'<dt>Words (IoC: {ioc:.3f}):</dt>\n'
            txt += '<dd>\n'
            for x in subset:
                txt += str(x.text) + ' '
            txt += '</dd>\n'
            txt += self.pick_letters(subset, 0, 'first')
            txt += self.pick_letters(subset, -1, 'last')
        return txt

    def sec_concealment(self, words):
        txt = ''
        for n in range(1, 6):
            txt += f'<h3>Pick every {n}. word</h3>\n'
            txt += '<dl>\n'
            txt += self.pick_words(words, n)
            txt += '</dl>\n'
        return txt

    def make(self, fname, outfile):
        source = RuneTextFile(LPath.page(fname))
        words = [x[3] for x in source.enum_words()]
        runes = [x for w in words for x in w]
        indices = [x.index for x in runes]
        html = self.template.replace('__FNAME__', fname)
        html = html.replace('__SEC_COUNTS__', self.sec_counts(words, runes))
        html = html.replace('__SEC_DOUBLE__', self.sec_double_rune(indices))
        if fname.startswith('solved_'):
            warn = '<p class="red">IoC is disabled on solved pages. Open the '
            warn += f'<a href="./{fname[7:]}.html">“unsolved” page</a>'
            warn += ' instead.</p>'
            html = html.replace('__SEC_IOC__', warn)
        else:
            html = html.replace('__SEC_IOC__', self.sec_ioc(fname))
        ioc_flow = '<dl>\n'
        for winsize in [120, 80, 50, 30, 20]:
            ioc_flow += self.sec_ioc_flow(indices, winsize)
        ioc_flow += '</dl>\n'
        html = html.replace('__SEC_IOC_FLOW__', ioc_flow)
        html = html.replace('__SEC_CONCEAL__', self.sec_concealment(words))
        with open(LPath.results(outfile), 'w') as f:
            f.write(html)


class IndexToWeb(object):
    def __init__(self, template='templates/index.html'):
        with open(LPath.results(template), 'r') as f:
            self.template = f.read()

    def make(self, the_links, outfile='index.html'):
        html = self.template
        for key, links in the_links.items():
            txt = ''
            for x, y in links:
                txt += f' <a href="./{x}">{y}</a> '
            html = html.replace(key, txt)
        with open(LPath.results(outfile), 'w') as f:
            f.write(html)


if __name__ == '__main__':
    links = {
        '__A_IOC__': [('ioc/high.html', 'Highest (bluntly)'),
                      ('ioc/norm.html', 'Normal english (1.7767)')],
        '__A_CHAPTER__': [(f'pages/{x}.html', x) for x in FILES_ALL],
        '__A_SOLVED__': [(f'pages/solved_{x}.html', x)
                         for x in FILES_SOLVED]
    }
    InterruptToWeb('db_high').make('ioc/high.html', HIGH_MIN, HIGH_MAX)
    InterruptToWeb('db_norm').make('ioc/norm.html', NORM_MIN, NORM_MAX)
    ctw = ChapterToWeb()
    for x, y in links['__A_CHAPTER__']:
        ctw.make(y, x)
    for x, y in links['__A_SOLVED__']:
        ctw.make('solved_' + y, x)
    IndexToWeb().make(links)
