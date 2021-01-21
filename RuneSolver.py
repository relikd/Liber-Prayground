#!/usr/bin/env python3
from RuneRunner import RuneRunner
from RuneText import Rune, RuneText
import lib as LIB


#########################################
#  RuneSolver  :  Generic parent class handles interrupts and text highlight
#########################################

class RuneSolver(RuneRunner):
    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        self.INTERRUPT = 'ᚠ'
        self.INTERRUPT_POS = []  # '1' for first occurrence of INTERRUPT

    def highlight_interrupt(self):
        return self.highlight_rune(self.INTERRUPT, self.INTERRUPT_POS)

    def run(self, data=None):
        if data:
            self.input.load(data=data)
        self.interrupt_counter = 0
        self.start(self.cipher_callback)

    def cipher_callback(self, encrypted_data, index):
        obj = encrypted_data[index]
        is_interrupt = obj.rune == self.INTERRUPT
        if is_interrupt:
            self.interrupt_counter += 1
        skip = is_interrupt and self.interrupt_counter in self.INTERRUPT_POS
        mark_this = self.mark_char_at(index)
        if not skip:
            obj = self.cipher(obj, (encrypted_data, index))
        mark_next = self.mark_char_at(index)
        return obj, mark_this, mark_next

    def cipher(self, rune, context):
        raise NotImplementedError  # must subclass

    def mark_char_at(self, position):
        return False

    def __str__(self):
        txt = f'DATA: {len(self.input.data) if self.input.data else 0} bytes'
        if self.input.loaded_file:
            txt += f' (file: {self.input.loaded_file})'
        else:
            txt += f' (manual input)'
        return txt + f'\ninterrupt jumps: {self.INTERRUPT_POS}'


#########################################
#  VigenereSolver  :  Decrypt runes with key; handle key shift, rotation, etc.
#########################################

class VigenereSolver(RuneSolver):
    def __init__(self):
        super().__init__()
        self.current_key_pos = 0
        self.reset()

    def reset(self):
        super().reset()
        self.KEY_DATA = []  # the key material
        self.KEY_INVERT = False  # ABCD -> ZYXW
        self.KEY_SHIFT = 0  # ABCD -> DABC
        self.KEY_ROTATE = 0  # ABCD -> ZABC
        self.KEY_OFFSET = 0  # ABCD -> __ABCD
        self.KEY_POST_PAD = 0  # ABCD -> ABCD__

    def run(self, data=None):
        self.current_key_pos = 0
        super().run(data=data)

    def is_key_active(self, _=None):
        i = self.current_key_pos - self.KEY_OFFSET
        if i >= 0 and i < len(self.KEY_DATA):
            return self.KEY_DATA[i] != 29  # used as placeholder for unknown
        return False

    def mark_char_at(self, position):
        return self.is_key_active(position)

    def rotate_key(self):
        key_size = self.KEY_OFFSET + len(self.KEY_DATA) + self.KEY_POST_PAD
        if key_size > 0:  # mostly for key invert without a key
            self.current_key_pos = (self.current_key_pos + 1) % key_size

    def cipher(self, rune, context):
        r_idx = rune.index
        if self.KEY_INVERT:
            r_idx = 28 - r_idx
        if self.is_key_active():
            key_i = self.current_key_pos
            i = (key_i - self.KEY_OFFSET + self.KEY_SHIFT) % len(self.KEY_DATA)
            r_idx = (r_idx - self.KEY_DATA[i] - self.KEY_ROTATE) % 29
        self.rotate_key()
        return Rune(i=r_idx)

    def __str__(self):
        key = RuneText(self.KEY_DATA).description(indexWhitespace=True)
        txt = super().__str__()
        txt += f'\nkey: {key}'
        txt += f'\nkey invert: {self.KEY_INVERT}'
        txt += f'\nkey shift: {self.KEY_SHIFT} indices'
        txt += f'\nkey offset: {self.KEY_OFFSET} runes'
        txt += f'\nkey post pad: {self.KEY_POST_PAD} runes'
        return txt


#########################################
#  SequenceSolver  :  Decrypt runes with sequential function
#########################################

class SequenceSolver(RuneSolver):
    def __init__(self):
        super().__init__()
        self.seq_index = 0
        self.reset()

    def reset(self):
        super().reset()
        self.FN = None

    def run(self, data=None):
        self.seq_index = 0
        assert(self.FN)
        super().run(data=data)

    def cipher(self, rune, context):
        x = self.FN(self.seq_index, rune)
        self.seq_index += 1
        return x

    def __str__(self):
        return super().__str__() + f'\nf(x): {self.FN}'


#########################################
#  AffineSolver  :  Decrypt runes with an array of (s, t) affine keys
#########################################

class AffineSolver(RuneSolver):
    def __init__(self):
        super().__init__()
        self.current_key_pos = 0
        self.reset()

    def reset(self):
        super().reset()
        self.KEY_DATA = []  # the key material
        self.KEY_INVERT = False  # ABCD -> ZYXW

    def run(self, data=None):
        self.current_key_pos = 0
        super().run(data=data)

    def rotate_key(self):
        self.current_key_pos = (self.current_key_pos + 1) % len(self.KEY_DATA)

    def cipher(self, rune, context):
        r_idx = rune.index
        if self.KEY_INVERT:
            r_idx = 28 - r_idx
        r_idx = LIB.affine_decrypt(r_idx, self.KEY_DATA[self.current_key_pos])
        self.rotate_key()
        return Rune(i=r_idx)

    def __str__(self):
        return super().__str__() + \
            f'\nkey: {self.KEY_DATA}\nkey invert: {self.KEY_INVERT}'
