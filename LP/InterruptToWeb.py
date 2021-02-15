#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from Alphabet import RUNES
from LPath import FILES_ALL, FILES_SOLVED, FILES_UNSOLVED, LPath
from InterruptDB import InterruptDB
from InterruptIndices import InterruptIndices
from RuneText import RuneTextFile
from Probability import Probability

NORM_MIN = 0.40
NORM_MAX = 0.98
HIGH_MIN = 1.25
HIGH_MAX = 1.65


class HTML(object):
    @staticmethod
    def attr(attrib):
        txt = ''
        if attrib:
            for k, v in attrib.items():
                txt += f' {k}="{v}"'
        return txt

    @staticmethod
    def mark(x, low=0, high=1):
        if x <= low:
            return ' class="m0"'
        return f' class="m{int((min(high, x) - low) / (high - low) * 14) + 1}"'

    @staticmethod
    def p_warn(content):
        return f'<p class="red">{content}</p>\n'

    @staticmethod
    def dt_dd(title, content, attrib=None):
        return f'<dt>{title}</dt>\n<dd{HTML.attr(attrib)}>\n{content}</dd>\n'

    @staticmethod
    def num_stream(stream, score_min=0, score_max=1):
        dot2 = isinstance(score_min, float) or isinstance(score_max, float)
        txt = ''
        for x in stream:
            txt += '<div'
            if isinstance(x, tuple):
                txt += HTML.attr(x[0])
                x = x[1]
            if not isinstance(x, str):
                txt += HTML.mark(x, score_min, score_max)
            txt += f'>{x:.2f}</div>' if dot2 else f'>{x}</div>'
        return txt + '\n'

    @staticmethod
    def num_table(table, num_ranges, thr=1, thc=1):
        txt = '<table>\n'
        for r, row in enumerate(table):
            attr = ''
            if isinstance(row, tuple):
                attr = HTML.attr(row[0])
                row = row[1]
            txt += f'<tr{attr}>'
            for c, val in enumerate(row):
                td = 'th' if r < thr or c < thc else 'td'
                attr = ''
                if isinstance(val, tuple):
                    attr = HTML.attr(val[0])
                    val = val[1]
                isnum = False
                dot2 = False
                if not isinstance(val, str):
                    for sc_min, sc_max, L, T, R, B in num_ranges:
                        if c >= L and c < R and r >= T and r < B:
                            isnum = True
                            attr += HTML.mark(val, sc_min, sc_max)
                            dot2 = isinstance(sc_min, float) \
                                or isinstance(sc_max, float)
                            break
                if isnum:
                    if val <= 0:
                        txt += f'<{td}>–</{td}>'
                    elif dot2:
                        txt += f'<{td}{attr}>{val:.2f}</{td}>'
                    else:
                        txt += f'<{td}{attr}>{val}</{td}>'
                else:
                    txt += f'<{td}{attr}>{val}</{td}>'
            txt += '</tr>\n'
        return txt + '</table>\n'


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
        tbl = [({'class': 'rotate'}, [''])]
        tbl += [[x] for x in RUNES]
        tbl += [({'class': 'small'}, ['Total'])]
        for name in FILES_ALL:
            if name not in self.scores:
                continue
            tbl[0][1].append(f'<div>{name}</div>')
            tbl[-1][1].append(db_indices.total(name))
            for i in range(29):
                scrs = self.scores[name][i][1:]
                if not scrs:
                    tbl[i + 1].append('–')
                    continue
                worst_irpc = min([x[1] for x in scrs])
                if worst_irpc == 0:
                    if max([x[1] for x in scrs]) != 0:
                        tbl[i + 1].append('?')
                        continue
                _, num = db_indices.consider(name, i, worst_irpc)
                tbl[i + 1].append(num)
        return HTML.num_table(tbl, [(384, 812, 1, 1, 99, len(tbl) - 1)])

    def table_interrupt(self, irp, pmin, pmax):
        maxkl = max(len(x[irp]) for x in self.scores.values())
        tbl = [({'class': 'rotate'}, [''])]
        tbl += [[x] for x in range(1, maxkl)]
        tbl += [({'class': 'small'}, ['best'])]
        for name in FILES_ALL:
            maxscore = 0
            bestkl = -1
            try:
                klarr = self.scores[name][irp]
            except KeyError:
                continue
            tbl[0][1].append(f'<div>{name}</div>')
            for kl, (score, _) in enumerate(klarr):
                if kl == 0:
                    continue
                tbl[kl].append(score)
                if score > maxscore:
                    maxscore = score
                    bestkl = kl
            tbl[-1][1].append(bestkl)
        return HTML.num_table(tbl, [(pmin, pmax, 1, 1, 99, len(tbl) - 1)])

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
        self.db_indices = InterruptIndices()
        self.score = [(InterruptDB.load_scores('db_high'), HIGH_MIN, HIGH_MAX),
                      (InterruptDB.load_scores('db_norm'), NORM_MIN, NORM_MAX)]
        self.db_mod = {
            k: [(mod, mo, InterruptDB.load_scores(f'db_{k}_{mod}.{mo}'))
                for mod in range(2, 4) for mo in range(mod)]
            for k in ['high_mod_a', 'norm_mod_a', 'high_mod_b', 'norm_mod_b']
        }

    def pick_ngrams(self, runes, gramsize, limit=100):
        res = {}
        for i in range(len(runes) - gramsize + 1):
            ngram = ''.join(x.rune for x in runes[i:i + gramsize])
            try:
                res[ngram] += 1
            except KeyError:
                res[ngram] = 1
        res = sorted(res.items(), key=lambda x: -x[1])
        z = ''.join(f'<div><div>{x}:</div> {y}</div>' for x, y in res[:limit])
        if len(res) > limit:
            z += f'+{len(res) - limit}&nbsp;others'
        return HTML.dt_dd(f'{gramsize}-grams:', z, {'class': 'tabwidth'})

    def sec_counts(self, words, runes):
        txt = f'<p><b>Words:</b> {len(words)}</p>\n'
        txt += f'<p><b>Runes:</b> {len(runes)}</p>\n'
        txt += '<dl>\n'
        rcount = [0] * 29
        for r in runes:
            rcount[r.index] += 1
        minmax = [min(rcount), max(rcount)]
        vals = [f'<b>{y}</b>' if y in minmax else str(y) for y in rcount]
        z = ''.join(f'<div><div>{x}:</div> {y}</div>'
                    for x, y in zip(RUNES, vals))
        txt += HTML.dt_dd('1-grams:', z, {'class': 'tabwidth'})
        txt += self.pick_ngrams(runes, 2, limit=100)
        txt += self.pick_ngrams(runes, 3, limit=50)
        txt += self.pick_ngrams(runes, 4, limit=25)
        return txt + '</dl>\n'

    def sec_double_rune(self, indices):
        num_a = []
        num_b = []
        for i, (a, b) in enumerate(zip(indices, indices[1:])):
            x = min(abs(a - b), min(a, b) + 29 - max(a, b))
            num_a.append(({'title': f'offset: {i}, rune: {RUNES[a]}'}, 1)
                         if x == 0 else '.')
            num_b.append(({'title': f'offset: {i}'}, x))
        txt = ''
        txt += HTML.dt_dd('Double Runes:', HTML.num_stream(num_a, 0, 1),
                          {'class': 'ioc-list small one'})
        txt += HTML.dt_dd('Rune Difference:', HTML.num_stream(num_b, 0, 14),
                          {'class': 'ioc-list small two'})
        return '<dl>\n' + txt + '</dl>\n'

    def sec_ioc(self, fname):
        tbl = [['',
                ({'colspan': 2}, 'IoC-<a href="./ioc/high.html">high</a>'),
                ({'colspan': 2}, 'IoC-<a href="./ioc/norm.html">norm</a>'),
                ({'colspan': 2}, 'Runes / keylen')]]
        tbl += [['']]
        tbl += [[x] for x in range(1, 33)]
        tbl += [({'class': 'small'}, ['best'])]
        for scores, pmin, pmax in self.score:
            for irp in [0, 28]:
                maxscore = 0
                bestkl = -1
                try:
                    klarr = scores[fname][irp]
                except KeyError:
                    continue
                tbl[1].append(RUNES[irp])
                for kl, (score, _) in enumerate(klarr):
                    if kl == 0:
                        continue
                    tbl[kl + 1].append(score)
                    if score > maxscore:
                        maxscore = score
                        bestkl = kl
                tbl[-1][1].append(bestkl)

        for irp in [0, 28]:
            try:
                klarr = scores[fname][irp]
            except KeyError:
                continue
            tbl[1].append(RUNES[irp])
            for kl, (_, maxirp) in enumerate(klarr):
                if maxirp > 0:
                    _, num = self.db_indices.consider(fname, irp, maxirp)
                    num /= kl
                    tbl[kl + 1].append(int(num))

        return HTML.num_table(tbl, [
            (HIGH_MIN, HIGH_MAX, 1, 2, 3, len(tbl) - 1),
            (NORM_MIN, NORM_MAX, 3, 2, 5, len(tbl) - 1),
            (28, 100, 5, 2, 7, len(tbl) - 1)
        ], thr=2)

    def sec_ioc_mod(self, fname):
        txt = '<dl>\n'
        for key, minkl, maxkl in [
            ('high_mod_a', 1, 13), ('norm_mod_a', 1, 13),
            ('high_mod_b', 2, 18), ('norm_mod_b', 2, 18)
        ]:
            tbl = [['', 'runes'] + [i for i in range(minkl, maxkl + 1)]]
            type_is_mod_a = key.endswith('a')
            for irp in [0, 28]:
                for mod, off, scores in self.db_mod[key]:
                    try:
                        klarr = scores[fname][irp][minkl:]
                        maxirp = klarr[-1][1]
                    except (KeyError, IndexError):
                        continue
                    if type_is_mod_a:
                        _, num = self.db_indices.consider(fname, irp, maxirp)
                        num = num // mod + (1 if off < num % mod else 0)
                    else:
                        _, num = self.db_indices.consider_mod_b(
                            fname, irp, maxirp, mod)
                        num = num[off]
                    tr = [f'{RUNES[irp]}.{mod}.{off}', num]
                    tr += [score for score, _ in klarr]
                    tbl.append(tr)

            if type_is_mod_a:
                title = 'Interrupt first, then mod'
            else:
                title = 'Mod first, then interrupt'

            if key.startswith('high'):
                title += ' (IoC-<a href="../ioc/high.html">high</a>):'
                tbl = HTML.num_table(tbl, [(HIGH_MIN, HIGH_MAX, 2, 1, 99, 99)])
            else:
                title += ' (IoC-<a href="../ioc/norm.html">norm</a>):'
                tbl = HTML.num_table(tbl, [(NORM_MIN, NORM_MAX, 2, 1, 99, 99)])

            txt += HTML.dt_dd(title, tbl)
        return txt + '</dl>\n'

    def sec_ioc_flow(self, indices):
        txt = '<dl>\n'
        for wsize in [120, 80, 50, 30, 20]:
            nums = HTML.num_stream((({'title': f'offset: {i}'},
                                     Probability(indices[i:i + wsize]).IC())
                                    for i in range(len(indices) - wsize + 1)),
                                   HIGH_MIN - 0.1, HIGH_MAX)
            txt += HTML.dt_dd(f'Window size {wsize}:', nums,
                              {'class': 'ioc-list small four'})
        return txt + '</dl>\n'

    def pick_letters(self, words, idx, desc):
        letters = [x[idx] for x in words]
        ioc = Probability(x.index for x in letters).IC()
        return HTML.dt_dd(f'Pick every {desc} letter (IoC: {ioc:.3f}):',
                          ''.join(f'<div>{x.text}</div>' for x in letters),
                          {'class': 'runelist'})

    def pick_words(self, words, n):
        txt = ''
        for u in range(n):
            if n > 1:
                txt += f'<h4>Start with {u + 1}. word</h4>\n'
            subset = [x for x in words[u::n]]
            ioc = Probability(x.index for y in subset for x in y).IC()
            txt += HTML.dt_dd(f'Words (IoC: {ioc:.3f}):',
                              ''.join(x.text + ' ' for x in subset))
            txt += self.pick_letters(subset, 0, 'first')
            txt += self.pick_letters(subset, -1, 'last')
        return txt

    def sec_concealment(self, words):
        txt = ''
        for n in range(1, 6):
            txt += f'<h3>Pick every {n}. word</h3>\n'
            txt += f'<dl>\n{self.pick_words(words, n)}</dl>\n'
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
            ref = f'<a href="./{fname[7:]}.html">“unsolved” page</a>'
            html = html.replace('__SEC_IOC__', HTML.p_warn(
                f'IoC is disabled on solved pages. Open the {ref} instead.'))
        else:
            html = html.replace('__SEC_IOC__', self.sec_ioc(fname))
        if fname in FILES_UNSOLVED:
            html = html.replace('__SEC_IOC_MOD__', self.sec_ioc_mod(fname))
        else:
            html = html.replace('__SEC_IOC_MOD__', HTML.p_warn(
                'Mod-IoC is disabled on solved pages'))
        html = html.replace('__SEC_IOC_FLOW__', self.sec_ioc_flow(indices))
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
            html = html.replace(
                key, ' '.join(f'<a href="./{x}">{y}</a>' for x, y in links))
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
