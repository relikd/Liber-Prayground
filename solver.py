#!/usr/bin/env python3
from RuneSolver import VigenereSolver, SequenceSolver
from RuneText import Rune, RuneText
import sys


def load_sequence_file(fname):
    with open(fname, 'r') as f:
        return [int(x) for x in f.readlines()]


PRIMES = load_sequence_file('data/seq_primes_1000.txt')
PRIMES_3301 = load_sequence_file('data/seq_primes_3301.txt')
NOT_PRIMES = load_sequence_file('data/seq_not_primes.txt')
FIBONACCI = load_sequence_file('data/seq_fibonacci.txt')
LUCAS = load_sequence_file('data/seq_lucas_numbers.txt')


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
    slvr.input.load(file='_input.txt')
    slvr.KEY_DATA = []
    slvr.run()


def try_totient_on_unsolved():
    slvr = SequenceSolver()
    slvr.output.QUIET = True
    slvr.output.BREAK_MODE = ''  # disable line breaks
    # for uuu in ['54-55']:
    for uuu in ['0-2', '3-7', '8-14', '15-22', '23-26', '27-32', '33-39', '40-53', '54-55']:
        print()
        print(uuu)
        with open(f'pages/p{uuu}.txt', 'r') as f:
            slvr.input.load(RuneText(f.read()[:110]))
            # alldata = slvr.input.runes_no_whitespace() + [Rune(i=29)]

        def b60(x):
            v = x % 60
            return v if v < 29 else 60 - v
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
            slvr.FN = lambda i, r: Rune(i=(67 * r.index + z) % 29)
            # slvr.FN = lambda i, r: Rune(i=(r.prime ** i + z) % 29)
            slvr.run()


if '-s' in sys.argv:  # print [s]olved
    print_all_solved()
else:
    # play_around()
    try_totient_on_unsolved()
