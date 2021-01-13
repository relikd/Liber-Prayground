#!/usr/bin/env python3
from RuneText import RuneText
import lib as LIB
import sys


#########################################
#  RuneWriter  :  handle std output with highlight etc.
#########################################

class RuneWriter(object):
    MARKS = {'_': '\x1b[0m', 'r': '\x1b[31;01m', 'b': '\x1b[30;01m'}

    def __init__(self):
        self.COLORS = True
        self.VERBOSE = '-v' in sys.argv
        self.QUIET = '-q' in sys.argv
        self.BREAK_MODE = None
        self.file_output = None
        self.clear()

    def clear(self):
        self.mark = False
        self.alternate = False
        self._marked = ['_'] * 4
        self.txt = [''] * 4

    def is_empty(self):
        return not self.txt[0]

    def line_break_mode(self):
        if self.BREAK_MODE is not None:  # if set by user
            return self.BREAK_MODE
        return 'l' if self.VERBOSE else 's'  # dynamically adapt to mode

    def write(self, r=None, t=None, n1=None, n2=None):
        m = ('b' if self.alternate else 'r') if self.mark else '_'
        for i, v in enumerate([r, t, n1, n2]):
            if v is None:
                continue
            if self.COLORS and self._marked[i] != m and i != 3:
                self._marked[i] = m
                prfx = self.MARKS[m]
            else:
                prfx = ''
            self.txt[i] += prfx + v

    # def rm(self, r=0, t=0, n1=0, n2=0):
    #     for i, v in enumerate([r, t, n1, n2]):
    #         if v > 0:
    #             self.txt[i] = self.txt[i][:-v]

    def stdout(self):
        def print_f(x=''):
            if self.file_output:
                with open(self.file_output, 'a') as f:
                    f.write(x + '\n')
            else:
                print(x)

        if self.is_empty():
            return
        m = self.mark
        self.mark = False  # flush closing color
        self.write(r='', t='', n1='', n2='')
        self.mark = m

        if not self.QUIET or self.VERBOSE:
            print_f()
        if not self.QUIET:
            print_f(self.txt[0])
        print_f(self.txt[1])
        if self.VERBOSE:
            print_f(self.txt[2])
            print_f(self.txt[3])
        self.clear()


#########################################
#  RuneReader  :  handles parsing of the file and line breaks etc.
#########################################

class RuneReader(object):
    def __init__(self):
        self.data = None
        self.loaded_file = None
        self.words = {x: [] for x in range(20)}  # increase for longer words

    def load(self, data=None, file=None):
        self.loaded_file = None
        if not data:
            with open(file, 'r') as f:
                data = f.read()
                self.loaded_file = file
        self.data = data if isinstance(data, RuneText) else RuneText(data)
        self.generate_word_list()

    def has_data(self):
        if len(self.data) > 0:
            return True
        return False

    def runes_no_whitespace(self):
        return [x for x in self.data if x.kind == 'r']

    def generate_word_list(self):
        for x in self.words.values():
            x.clear()
        res = []
        ai = 0
        ari = 0
        zri = 0
        for zi, x in enumerate(self.data):
            if x.kind == 'l':
                continue
            elif x.kind == 'r':
                res.append(x)
                zri += 1
            else:
                if len(res) > 0:
                    xt = RuneText(res)
                    self.words[len(xt)].append((ai, zi, ari, zri, xt))
                res = []
                ai = zi
                ari = zri

    # count_callback('c|w|l', count, is-first-flag)
    def parse(self, rune_fn, count_fn, whitespace_fn, break_line_on='l'):
        word_sum = 0
        line_sum = 0
        for i, x in enumerate(self.data):
            if x.kind == 'r':
                r = rune_fn(self.data, i, word_sum == 0)
                count_fn('c', r.prime, word_sum == 0)
                word_sum += r.prime
            elif x.kind == 'l' and x.kind != break_line_on:
                continue  # ignore all \n,\r if not forced explicitly
            else:
                if word_sum > 0:
                    count_fn('w', word_sum, line_sum == 0)
                    line_sum += word_sum
                    word_sum = 0
                if x.kind != 'l':  # still ignore \n,\r
                    whitespace_fn(x)
                if x.kind == break_line_on:
                    count_fn('l', line_sum, line_sum == 0)
                    line_sum = 0
        if word_sum > 0:
            count_fn('w', word_sum, line_sum == 0)
            line_sum += word_sum
        if line_sum > 0:
            count_fn('l', line_sum, True)


#########################################
#  RuneRunner  :  Merge RuneWriter and RuneReader and stay in sync
#########################################

class RuneRunner(object):
    def __init__(self):
        self.input = RuneReader()
        self.output = RuneWriter()
        self.marked_chars = []
        self.mark_alternate = []
        self.next_mark = False
        self.fn_cipher = None

    def highlight_words_with_len(self, search_length):
        found = [x for x in self.input.words[search_length]]
        self.marked_chars = set(x for fp in found for x in range(fp[0], fp[1]))
        return found

    def highlight_rune(self, rune, mark_occurrences=[]):
        ip = 0
        tp = 0
        ret = []
        for i, x in enumerate(self.input.data):
            if x.kind == 'r':
                if x.rune == rune:
                    ip += 1
                    ret.append((ip, tp, i, ip in mark_occurrences))
                tp += 1
        self.marked_chars = set(i for _, _, i, _ in ret)
        self.mark_alternate = set(i for _, _, i, f in ret if not f)
        return ret

    def reset_highlight(self):
        self.marked_chars = []
        self.mark_alternate = []

    def start(self, fn_cipher):
        self.fn_cipher = fn_cipher
        self.next_mark = False
        self.input.parse(
            self.rune_callback, self.count_callback, self.whitespace_callback,
            self.output.line_break_mode())

    def rune_callback(self, encrypted_data, index, is_first):
        if self.output.VERBOSE:
            fillup = len(self.output.txt[2]) - len(self.output.txt[1])
            if not is_first:
                fillup += 1  # +1 cause n1 will add a '+'
            if fillup > 0:
                self.output.write(t=' ' * fillup)
        if self.marked_chars:
            x = encrypted_data[index]  # always search on original data
            mt = index in self.marked_chars
            mn = index + 1 in self.marked_chars
            self.output.alternate = index in self.mark_alternate
        else:
            x, mt, mn = self.fn_cipher(encrypted_data, index)
        self.output.mark = mt
        self.output.write(r=x.rune, t=x.text)
        self.next_mark = mn
        return x

    def count_callback(self, typ, num, is_first):
        if typ == 'c':  # char
            if self.output.VERBOSE:
                self.output.write(n1=('' if is_first else '+') + str(num))
            return
        prm = LIB.is_prime(num)
        if typ == 'w':  # word
            tt = ('' if is_first else ' + ') + str(num) + ('*' if prm else '')
            self.output.write(n2=tt)
            if prm and num > 109 and not (self.output.VERBOSE or self.output.QUIET):
                self.output.write(t='__')
        elif typ == 'l':  # line end (ignoring \n if mode is set to 's')
            self.output.mark = False
            # if not is_first:
            sffx = ' = {}'.format(num) + ('*' if prm else '')
            if LIB.is_prime(LIB.rev(num)):
                sffx += '√'
            if self.output.VERBOSE:
                self.output.write(n2=sffx)
            elif not self.output.QUIET:
                self.output.write(t=sffx)
            self.output.stdout()

    def whitespace_callback(self, rune):
        if not self.next_mark:  # dont mark whitespace after selection
            self.output.mark = False
        self.output.write(r=rune.rune, t=rune.text)
        if self.output.VERBOSE:
            self.output.write(n1=' ')
