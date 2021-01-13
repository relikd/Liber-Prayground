#!/usr/bin/env python3
white_rune = {'•': ' ', '⁘': '.', '⁚': ',', '⁖': ';', '⁜': '#'}
white_text = {v: k for k, v in white_rune.items()}
alphabet = [  # Using last value for display. Custom added: V
    (2, 'ᚠ', ['F']), (3, 'ᚢ', ['V', 'U']), (5, 'ᚦ', ['TH']), (7, 'ᚩ', ['O']),
    (11, 'ᚱ', ['R']), (13, 'ᚳ', ['K', 'C']), (17, 'ᚷ', ['G']),
    (19, 'ᚹ', ['W']), (23, 'ᚻ', ['H']), (29, 'ᚾ', ['N']), (31, 'ᛁ', ['I']),
    (37, 'ᛄ', ['J']), (41, 'ᛇ', ['EO']), (43, 'ᛈ', ['P']), (47, 'ᛉ', ['X']),
    (53, 'ᛋ', ['Z', 'S']), (59, 'ᛏ', ['T']), (61, 'ᛒ', ['B']),
    (67, 'ᛖ', ['E']), (71, 'ᛗ', ['M']), (73, 'ᛚ', ['L']),
    (79, 'ᛝ', ['ING', 'NG']), (83, 'ᛟ', ['OE']), (89, 'ᛞ', ['D']),
    (97, 'ᚪ', ['A']), (101, 'ᚫ', ['AE']), (103, 'ᚣ', ['Y']),
    (107, 'ᛡ', ['IO', 'IA']), (109, 'ᛠ', ['EA'])
]
text_map = {t: r for _, r, ta in alphabet for t in ta}
rune_map = {r: t for _, r, ta in alphabet for t in ta}
index_map = [r for _, r, _ in alphabet]  # array already sorted
primes_map = {r: p for p, r, _ in alphabet}
# del alphabet  # used in playground for GP display


#########################################
#  Rune  :  Stores a single rune. Incl. text, prime, index, and kind
#########################################

class Rune(object):
    def __init__(self, r=None, t=None, i=None, p=None):
        self._rune = r
        self._text = t
        self._index = i
        self._prime = p
        self._kind = None  # one of: r n s l w

    def __repr__(self):
        return f'<{self._rune}, {self._text}, {self._index}, {self._prime}>'

    @property
    def rune(self):
        if self._rune is None:
            self._rune = index_map[self._index] if self._index < 29 else '•'
        return self._rune

    @property
    def text(self, sameWhitespace=False):
        if self._text is None:
            if sameWhitespace:
                self._text = rune_map.get(self.rune, ' ')
            else:
                r = self.rune
                self._text = rune_map.get(r, white_rune.get(r, r))
        return self._text

    @property
    def index(self):
        if self._index is None:
            r = self._rune
            self._index = index_map.index(r) if r in index_map else 29
        return self._index

    @property
    def prime(self):
        if self._prime is None:
            self._prime = primes_map.get(self.rune, 0)
        return self._prime

    @property
    def kind(self):
        if self._kind is None:
            x = self.rune
            if x in rune_map:
                self._kind = 'r'  # rune
            elif x == '⁜':
                self._kind = 's'  # paragraph, but treat as sentence
            elif x == '⁘':
                self._kind = 's'  # sentence
            elif x == '\n' or x == '\r':
                self._kind = 'l'  # line end
            elif x in '1234567890':
                self._kind = 'n'  # number
            else:
                self._kind = 'w'  # whitespace (explicitly not n or s)
        return self._kind

    def __add__(self, o):
        if isinstance(o, Rune):
            o = o.index
        if self.index == 29 or o == 29:
            return self
        return Rune(i=(self.index + o) % 29)

    def __sub__(self, o):
        if isinstance(o, Rune):
            o = o.index
        if self.index == 29 or o == 29:
            return self
        return Rune(i=(self.index - o) % 29)

    def __radd__(self, o):
        return self if self.index == 29 else Rune(i=(o + self.index) % 29)

    def __rsub__(self, o):
        return self if self.index == 29 else Rune(i=(o - self.index) % 29)


#########################################
#  RuneText  :  Stores multiple Rune objects. Allows arithmetic operations
#########################################

class RuneText(object):
    def __init__(self, anything):
        if not anything:
            self._data = []
        elif isinstance(anything, list):
            if len(anything) > 0 and isinstance(anything[0], Rune):
                self._data = anything
            else:
                self._data = [Rune(i=x) for x in anything]
        else:
            txt = anything.strip()
            if not txt:
                self._data = []
            elif txt[0] in rune_map or txt[0] in white_rune:
                self._data = [Rune(r=x) for x in txt]
            else:
                try:
                    self._data = [
                        Rune(i=int(x)) for x in txt.strip('[]').split(',')
                    ]
                except ValueError:
                    self._data = self.from_text(txt)

        self._data_len = len(self._data)

    def __len__(self):
        return self._data_len

    def trim(self, maxlen):
        if self._data_len > maxlen:
            self._data = self._data[:maxlen]
            self._data_len = maxlen

    @classmethod
    def from_text(self, text):
        res = []
        text = text.strip().upper().replace('QU', 'CW')
        tlen = len(text)
        skip = 0
        for i in range(tlen):
            if skip:
                skip -= 1
                continue
            char = text[i]
            rune = None
            wspace = white_text.get(char, None)
            if wspace is not None:
                rune = wspace
            elif char in '\"\'\n\r\t1234567890':
                rune = char
            else:
                if char in 'TINEOA' and i + 1 < tlen:
                    bichar = char + text[i + 1]
                    rune = text_map.get(bichar, None)
                    if rune is not None:
                        char = bichar
                        skip = 1
                    elif char == 'I' and i + 2 < tlen:
                        trichar = bichar + text[i + 2]
                        rune = text_map.get(trichar, None)
                        if rune:
                            char = trichar
                            skip = 2
                if not rune:
                    rune = text_map.get(char, None)
            if not rune:
                raise ValueError(f'Unkn0n char: {i} "{char}"')
            res.append(Rune(r=rune, t=char))
        return res

    def as_dict(self):
        ret = {'r': '', 't': '', 'i': [], 'p': []}
        for x in self._data:
            ret['r'] += x.rune
            ret['t'] += x.text
            ret['i'].append(x.index)
            ret['p'].append(x.prime)
        return ret

    def description(self, count=False, index=True, indexWhitespace=False):
        if len(self) == 0:
            return None
        fmt = '{0} ({1}) – {2} ({3})' if count else '{0} – {2}'
        d = self.as_dict()
        if index:
            fmt += ' – {4}'
            if not indexWhitespace:
                d['i'] = [x for x in d['i'] if x != 29]
        return fmt.format(d['r'], len(d['r']), d['t'], len(d['t']), d['i'])

    def __getitem__(self, key):
        if isinstance(key, str):
            return [getattr(x, key) for x in self._data]
        else:
            return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __add__(self, other):
        if isinstance(other, RuneText):
            if len(self) != len(other):
                raise IndexError('RuneText length mismatch')
            return RuneText([x + y for x, y in zip(self._data, other._data)])
        else:
            return RuneText([x + other for x in self._data])

    def __sub__(self, other):
        if isinstance(other, RuneText):
            if len(self) != len(other):
                raise IndexError('RuneText length mismatch')
            return RuneText([x - y for x, y in zip(self._data, other._data)])
        else:
            return RuneText([x - other for x in self._data])

    def __radd__(self, other):
        return RuneText([other + x for x in self._data])

    def __rsub__(self, other):
        return RuneText([other - x for x in self._data])

    def __repr__(self):
        return f'RuneText<{len(self._data)}>'
