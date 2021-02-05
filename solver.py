#!/usr/bin/env python3
from RuneSolver import VigenereSolver, SequenceSolver
from RuneText import Rune, RuneText
from lib import elliptic_curve
import sys
import itertools


def load_sequence_file(fname):
    with open(fname, 'r') as f:
        return [int(x) for x in f.readlines()]


PRIMES = load_sequence_file('data/seq_primes_1000.txt')
PRIMES_3301 = load_sequence_file('data/seq_primes_3301.txt')
NOT_PRIMES = load_sequence_file('data/seq_not_primes.txt')
FIBONACCI = load_sequence_file('data/seq_fibonacci.txt')
LUCAS = load_sequence_file('data/seq_lucas_numbers.txt')
MOEBIUS = load_sequence_file('data/seq_moebius.txt')


def print_all_solved():
    def plain(slvr):
        slvr.KEY_DATA = []

    def invert(slvr):
        slvr.KEY_DATA = []
        slvr.KEY_INVERT = True

    def solution_welcome(slvr):
        slvr.KEY_DATA = [23, 10, 1, 10, 9, 10, 16, 26]  # DIVINITY
        slvr.INTERRUPT = 'ᚠ'
        slvr.INTERRUPT_POS = [4, 5, 6, 7, 10, 11, 14, 18, 20, 21, 25]

    def solution_koan_1(slvr):
        slvr.KEY_DATA = [26]  # Y
        slvr.KEY_INVERT = True

    def solution_jpg107_167(slvr):  # FIRFUMFERENFE
        slvr.KEY_DATA = [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18]
        slvr.INTERRUPT = 'ᚠ'
        slvr.INTERRUPT_POS = [2, 3]

    def solution_p56_end(slvr):
        slvr.FN = lambda i, r: r - (PRIMES[i] - 1)
        slvr.INTERRUPT = 'ᚠ'
        slvr.INTERRUPT_POS = [4]

    def solve(path, fn_solution, solver=VigenereSolver):
        slvr = solver()
        slvr.output.COLORS = False
        slvr.output.QUIET = True  # or use -v/-q while calling
        slvr.input.load(file=f'pages/{path}.txt')
        fn_solution(slvr)
        print(f'pages/{path}.txt')
        print()
        slvr.run()
        print()

    solve('0_warning', invert)
    solve('0_welcome', solution_welcome)
    solve('0_wisdom', plain)
    solve('0_koan_1', solution_koan_1)
    solve('0_loss_of_divinity', plain)
    solve('jpg107-167', solution_jpg107_167)
    solve('jpg229', plain)
    solve('p56_an_end', solution_p56_end, solver=SequenceSolver)
    solve('p57_parable', plain)


def play_around():
    slvr = VigenereSolver()
    slvr.output.COLORS = False
    slvr.output.QUIET = True
    slvr.KEY_DATA = []
    vowels = 'ᚢᚩᛁᛇᛖᛟᚪᚫᛡᛠ'
    for uuu in ['0-2', '3-7', '8-14', '15-22', '23-26', '27-32', '33-39', '40-53', '54-55']:
        slvr.input.load(file=f'pages/p{uuu}.txt')
        print(uuu)
        print('word count:', sum(len(x) for x in slvr.input.words.values()))
        a = [1 if x.rune in vowels else 0 for x in slvr.input.runes_no_whitespace()]
        b = [a[i:i + 5] for i in range(0, len(a), 5)]
        c = [int(''.join(str(y) for y in x), 2) for x in b]
        # print('-'.join(str(x) for x in c))
        # print(''.join(Rune(i=x).text for x in c))
        # print(''.join('ABCDEFGHIJKLMNOPQRSTUVWXYZ___...'[x] for x in c))
        # slvr.run()


def try_totient_on_unsolved():
    slvr = SequenceSolver()
    slvr.output.QUIET = True
    slvr.output.BREAK_MODE = ''  # disable line breaks
    # slvr.INTERRUPT = 'ᛝ'
    # slvr.INTERRUPT_POS = [1]
    # for uuu in ['15-22']:
    for uuu in ['0-2', '3-7', '8-14', '15-22', '23-26', '27-32', '33-39', '40-53', '54-55']:
        print()
        print(uuu)
        with open(f'pages/p{uuu}.txt', 'r') as f:
            slvr.input.load(RuneText(f.read()[:15]))
            # alldata = slvr.input.runes_no_whitespace() + [Rune(i=29)]

        def b60(x):
            v = x % 60
            return v if v < 29 else 60 - v

        def ec(r, i):
            p1, p2 = elliptic_curve(i, 149, 263, 3299)
            if p1 is None:
                return r.index
            return r.index + p1 % 29
        # for p in PRIMES[:500]:
        #     print(p)
        #     for z in range(29):
        #         def fn(i, x):
        #             return (x + alldata[i - 1].index + z) % 29
        #         if fn(0, alldata[0].index) not in [10, 24]:
        #             continue
        #         slvr.FN = lambda i, r: Rune(i=fn(i, r.index))
        #         slvr.run()
        for z in range(29):
            # slvr.FN = lambda i, r: r - z  # ((i + z) // 3)
            # slvr.FN = lambda i, r: r - PRIMES[i] + z
            # slvr.FN = lambda i, r: Rune(i=b60(r.prime) + z % 29)
            # slvr.FN = lambda i, r: Rune(i=((r.prime + alldata[i + 1].prime) + z) % 60 // 2)
            # slvr.FN = lambda i, r: Rune(i=(3301 * r.index + z) % 29)
            slvr.FN = lambda i, r: Rune(i=(ec(r, i) + z) % 29)
            # slvr.FN = lambda i, r: Rune(i=(r.prime - PRIMES[FIBONACCI[i]] + z) % 29)
            # slvr.FN = lambda i, r: Rune(i=(r.prime ** i + z) % 29)
            slvr.run()


def find_oeis(irp=0, invert=False, offset=0):
    def trim_orig_oeis(minlen=15, trim=40):
        # download and unzip: https://oeis.org/stripped.gz
        with open('data/oeis_orig.txt', 'r') as f_in:
            with open('data/oeis.txt', 'w') as f_out:
                for line in f_in.readlines():
                    if line[0] == '#':
                        continue
                    name, *vals = line.split(',')
                    vals = [str(int(x) % 29) for x in vals if x.strip()][:trim]
                    if len(vals) < minlen:
                        continue
                    f_out.write(name + ',' + ','.join(vals) + '\n')

    # trim_orig_oeis()  # create db if not present already
    with open('data/oeis.txt', 'r') as f:
        seqs = []
        for line in f.readlines():
            name, *vals = line.split(',')
            vals = [int(x) for x in vals]
            seqs.append([name] + vals)

    RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
    words = [set()] * 13
    words[1] = set(x for x in RUNES)
    for i in range(2, 13):  # since 12 is the longest word
        with open(f'data/dictionary_{i}.txt', 'r') as f:
            words[i] = set(x.strip() for x in f.readlines())

    for uuu, wlen in {
        '0-2': [8, 5, 4, 3, 3, 11, 5, 4, 3, 3],
        '3-7': [2, 11, 3, 4, 7, 7, 7, 4, 6],
        '8-14': [4, 8, 3, 2, 3, 9, 4, 3, 4, 2, 2],
        '15-22': [4, 5, 4, 2, 5, 4, 5, 6, 5, 6, 3, 3],
        '23-26': [2, 6, 3, 4, 8, 3, 3, 7, 5, 5],
        '27-32': [3, 12, 4, 7, 2, 3, 3, 2, 1, 3, 4],
        '33-39': [2, 8, 2, 9, 6, 3, 3, 5, 3, 2],
        '40-53': [3, 5, 5, 4, 3, 5, 4, 2, 12, 3, 3, 2],
        '54-55': [1, 8, 8, 3, 6, 2, 5, 3, 2, 3, 5, 7],
        # '56_an_end': [2, 3, 5, 2, 4, 3, 4, 6, 1, 4, 3, 6, 2],
    }.items():
        minwords = sum(wlen[:2])  # must match at least n words
        splits = [(0, 0, 0)]
        for x in wlen:
            splits.append((splits[-1][1], splits[-1][1] + x))
        splits = splits[1:]
        print()
        print(uuu)
        with open(f'pages/p{uuu}.txt', 'r') as f:
            data = RuneText(f.read()[:120]).index_no_whitespace
            irps = [i for i, x in enumerate(data[:splits[-1][1]]) if x == irp]
            irps.reverse()
            if invert:
                data = [28 - x for x in data]

        for oeis, *v in seqs:  # 390k
            v = v[offset:]
            if len(v) < minwords:
                continue
            cases = [x for x in irps if x < len(v)]
            for i in range(len(cases) + 1):
                for comb in itertools.combinations(cases, i):  # 2^3
                    res = v[:]
                    for z in comb:
                        res.insert(z, -1)  # insert interrupts
                    for s in range(29):
                        who = ''.join(RUNES[x if y == -1 else (x - y - s) % 29]
                                      for x, y in zip(data, res))
                        active = [x for x in splits if x[1] <= len(who)]
                        bag = [who[x:y] for x, y in active]
                        if all(w in words[len(w)] for w in bag):
                            print(oeis.split()[0], 'shift:', s, 'irps:', comb)
                            print(' ', ' '.join(RuneText(w).text for w in bag))


if '-s' in sys.argv:  # print [s]olved
    print_all_solved()
else:
    play_around()
    # try_totient_on_unsolved()
    # for i in range(0, 4):
    #     print('offset:', i)
    #     find_oeis(irp=0, invert=False, offset=i)
