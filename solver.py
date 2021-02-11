#!/usr/bin/env python3
import LP
import sys
import itertools


def load_sequence_file(fname):
    with open(LP.path.data(fname), 'r') as f:
        return [int(x) for x in f.readlines()]


PRIMES = load_sequence_file('seq_primes_1000')
PRIMES_3301 = load_sequence_file('seq_primes_3301')
NOT_PRIMES = load_sequence_file('seq_not_primes')
FIBONACCI = load_sequence_file('seq_fibonacci')
LUCAS = load_sequence_file('seq_lucas_numbers')
MOEBIUS = load_sequence_file('seq_moebius')


def print_all_solved():
    def plain(slvr, inpt):
        pass

    def invert(slvr, inpt):
        inpt.invert()

    def solution_welcome(slvr, inpt):
        slvr.KEY_DATA = [23, 10, 1, 10, 9, 10, 16, 26]  # DIVINITY
        slvr.INTERRUPT = 'ᚠ'
        slvr.INTERRUPT_POS = [4, 5, 6, 7, 10, 11, 14, 18, 20, 21, 25]

    def solution_koan_1(slvr, inpt):
        slvr.KEY_DATA = [26]  # Y
        inpt.invert()

    def solution_jpg107_167(slvr, inpt):  # FIRFUMFERENFE
        slvr.KEY_DATA = [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18]
        slvr.INTERRUPT = 'ᚠ'
        slvr.INTERRUPT_POS = [2, 3]

    def solution_p56_end(slvr, inpt):
        slvr.FN = lambda i, r: r - (PRIMES[i] - 1)
        slvr.INTERRUPT = 'ᚠ'
        slvr.INTERRUPT_POS = [4]

    def solve(fname, fn_solution, solver=LP.VigenereSolver):
        slvr = solver()
        inpt = LP.RuneTextFile(LP.path.page(fname))
        fn_solution(slvr, inpt)
        print(f'pages/{fname}.txt')
        print()
        io = LP.IOWriter()
        # io.QUIET = True  # or use -v/-q while calling
        io.run(slvr.run(inpt)[0])
        print()

    solve('0_warning', invert)
    solve('0_welcome', solution_welcome)
    solve('0_wisdom', plain)
    solve('0_koan_1', solution_koan_1)
    solve('0_loss_of_divinity', plain)
    solve('jpg107-167', solution_jpg107_167)
    solve('jpg229', plain)
    solve('p56_an_end', solution_p56_end, solver=LP.SequenceSolver)
    solve('p57_parable', plain)


def play_around():
    vowels = [LP.RUNES.index(x) for x in 'ᚢᚩᛁᛇᛖᛟᚪᚫᛡᛠ']
    for uuu in LP.FILES_UNSOLVED:
        inpt = LP.RuneTextFile(LP.path.page(uuu))
        print(uuu)
        print('word count:', sum(1 for _ in inpt.enum_words()))
        a = [1 if x in vowels else 0 for x in inpt.index_no_white]
        b = [a[i:i + 5] for i in range(0, len(a), 5)]
        c = [int(''.join(str(y) for y in x), 2) for x in b]
        # print('-'.join(str(x) for x in c))
        # print(LP.RuneText(c).text)
        # print(''.join('ABCDEFGHIJKLMNOPQRSTUVWXYZ___...'[x] for x in c))


def try_totient_on_unsolved():
    slvr = LP.SequenceSolver()
    # slvr.INTERRUPT = 'ᛝ'
    # slvr.INTERRUPT_POS = [1]
    # for uuu in ['15-22']:
    for uuu in LP.FILES_UNSOLVED:
        print()
        print(uuu)
        inpt = LP.RuneTextFile(LP.path.page(uuu), limit=25).data_clean
        # alldata = [x for x in inpt if x.index != 29] + [LP.Rune(i=29)] * 1

        def ec(r, i):
            p1, p2 = LP.utils.elliptic_curve(i, 149, 263, 3299)
            if p1 is None:
                return r.index
            return r.index + p1 % 29

        for z in range(29):
            # slvr.FN = lambda i, r: r - PRIMES[i] + z
            # slvr.FN = lambda i, r: LP.Rune(i=((r.prime + alldata[i + 1].prime) + z) % 60 // 2)
            # slvr.FN = lambda i, r: LP.Rune(i=(r.prime - PRIMES[FIBONACCI[i]] + z) % 29)
            # slvr.FN = lambda i, r: LP.Rune(i=(r.prime ** i + z) % 29)
            slvr.FN = lambda i, r: LP.Rune(i=(ec(r, i) + z) % 29)
            print(slvr.run(inpt)[0].text)


def find_oeis(irp=0, invert=False, offset=0, allow_fails=1, min_match=2):
    def trim_orig_oeis(minlen=15, trim=40):
        # download and unzip: https://oeis.org/stripped.gz
        with open(LP.path.db('oeis_orig'), 'r') as f_in:
            with open(LP.path.db('oeis'), 'w') as f_out:
                for line in f_in.readlines():
                    if line[0] == '#':
                        continue
                    name, *vals = line.split(',')
                    vals = [str(int(x) % 29) for x in vals if x.strip()][:trim]
                    if len(vals) < minlen:
                        continue
                    f_out.write(name + ',' + ','.join(vals) + '\n')

    # trim_orig_oeis()  # create db if not present already
    with open(LP.path.db('oeis'), 'r') as f:
        seqs = []
        for line in f.readlines():
            vals = line.split(',')
            seqs.append((vals[0], list(map(int, vals[1:]))))

    words = [set()] * 13
    words[1] = set(x for x in LP.RUNES)
    for i in range(2, 13):  # since 12 is the longest word
        with open(LP.path.data(f'dictionary_{i}'), 'r') as f:
            words[i] = set(x.strip() for x in f.readlines())

    for uuu, wlen in {
        'p0-2': [8, 5, 4, 3, 3, 11, 5, 4, 3, 3],
        'p3-7': [2, 11, 3, 4, 7, 7, 7, 4, 6],
        'p8-14': [4, 8, 3, 2, 3, 9, 4, 3, 4, 2, 2],
        'p15-22': [4, 5, 4, 2, 5, 4, 5, 6, 5, 6, 3, 3],
        'p23-26': [2, 6, 3, 4, 8, 3, 3, 7, 5, 5],
        'p27-32': [3, 12, 4, 7, 2, 3, 3, 2, 1, 3, 4],
        'p33-39': [2, 8, 2, 9, 6, 3, 3, 5, 3, 2],
        'p40-53': [3, 5, 5, 4, 3, 5, 4, 2, 12, 3, 3, 2],
        'p54-55': [1, 8, 8, 3, 6, 2, 5, 3, 2, 3, 5, 7],
        # 'p56_an_end': [2, 3, 5, 2, 4, 3, 4, 6, 1, 4, 3, 6, 2],
    }.items():
        splits = [(0, 0, 0)]
        for x in wlen:
            splits.append((splits[-1][1], splits[-1][1] + x))
        splits = splits[1:]
        print()
        print(uuu)
        data = LP.RuneTextFile(LP.path.page(uuu), limit=120).index_no_white
        if invert:
            data = [28 - x for x in data]
        irps = [i for i, x in enumerate(data[:splits[-1][1]]) if x == irp]
        irps.reverse()  # insert -1 starting with the last

        min_len = sum(wlen[:2])  # must match at least n words
        data_len = len(data)
        for oeis, vals in seqs:  # 390k
            vals = vals[offset:]
            if len(vals) < min_len:
                continue
            cases = [x for x in irps if x < len(vals)]
            for i in range(len(cases) + 1):
                for comb in itertools.combinations(cases, i):  # 2^3
                    res = vals[:]
                    for z in comb:
                        res.insert(z, -1)  # insert interrupts
                    shortest = min(data_len, len(res))

                    for s in range(29):
                        failed = 0
                        full = []
                        clen = 0
                        for a, b in splits:
                            if b > shortest:
                                break
                            nums = [x if y == -1 else (x - y - s) % 29
                                    for x, y in zip(data[a:b], res[a:b])]
                            word = ''.join(LP.RUNES[x] for x in nums)
                            if word in words[len(nums)]:
                                clen += len(nums)
                            else:
                                failed += 1
                                if failed > allow_fails:
                                    break
                            full.append(LP.RuneText(nums).text)

                        if failed > allow_fails or clen < min_match:
                            continue  # too many failed
                        print(oeis.split()[0], 'shift:', s, 'irps:', comb)
                        print(' ', ' '.join(full))


if '-s' in sys.argv:  # print [s]olved
    print_all_solved()
else:
    play_around()
    # try_totient_on_unsolved()
    # for i in range(0, 4):
    #     print('offset:', i)
    #     find_oeis(irp=0, invert=False, offset=i, allow_fails=1, min_match=10)
