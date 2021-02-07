#!/usr/bin/env python3
from RuneRunner import RuneRunner
from RuneText import Rune, RuneText
from lib import affine_decrypt


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

    def substitute_get(self, pos, keylen, search_term, found_term):
        return found_term.zip_sub(search_term).description(count=True)

    def substitute_supports_keylen(self):
        return False

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
            obj = self.cipher(obj, (index, encrypted_data))
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
#  RunningKeySolver  :  Decrypt runes with key; handles shift, rotation, etc.
#########################################

class RunningKeySolver(RuneSolver):
    def __init__(self):
        super().__init__()
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
        self.k_current_pos = 0
        self.k_len = len(self.KEY_DATA)
        self.k_full_len = self.KEY_OFFSET + self.k_len + self.KEY_POST_PAD
        super().run(data=data)

    def mark_char_at(self, position):
        return self.active_key_pos() != -1

    def active_key_pos(self):
        i = self.k_current_pos - self.KEY_OFFSET
        if i >= 0 and i < self.k_len:
            if self.KEY_DATA[i] != 29:  # placeholder for unknown
                return i
        return -1

    def cipher(self, rune, context):
        r_idx = rune.index
        if self.KEY_INVERT:
            r_idx = 28 - r_idx
        pos = self.active_key_pos()
        if pos == -1:
            self.copy_unmodified(r_idx)
        else:
            i = (pos + self.KEY_SHIFT) % self.k_len
            r_idx = (self.decrypt(r_idx, i) - self.KEY_ROTATE) % 29
        # rotate_key
        if self.k_full_len > 0:  # e.g., for key invert without a key
            self.k_current_pos = (self.k_current_pos + 1) % self.k_full_len
        return Rune(i=r_idx)

    def decrypt(self, rune_index, key_index):  # must subclass
        raise NotImplementedError

    def copy_unmodified(self, rune_index):  # subclass if needed
        pass

    def key__str__(self):
        return self.KEY_DATA  # you should override this

    def key__str__basic_runes(self):
        return RuneText(self.KEY_DATA).description(indexWhitespace=True)

    def __str__(self):
        txt = super().__str__()
        txt += f'\nkey: {self.key__str__()}'
        txt += f'\nkey invert: {self.KEY_INVERT}'
        txt += f'\nkey offset: {self.KEY_OFFSET} runes'
        txt += f'\nkey post pad: {self.KEY_POST_PAD} runes'
        txt += f'\nkey shift: {self.KEY_SHIFT} indices'
        txt += f'\nkey rotate: {self.KEY_ROTATE} indices'
        return txt


#########################################
#  VigenereSolver  :  Decrypt runes with an array of indices
#########################################

class VigenereSolver(RunningKeySolver):
    def decrypt(self, rune_index, key_index):
        return rune_index - self.KEY_DATA[key_index]

    def substitute_supports_keylen(self):
        return True

    def substitute_get(self, pos, keylen, search_term, found_term):
        ret = [Rune(r='⁚')] * keylen
        for i, r in enumerate(found_term.zip_sub(search_term)):
            ret[(pos + i) % keylen] = r
        return RuneText(ret).description(count=True, index=False)

    def key__str__(self):
        return self.key__str__basic_runes()


#########################################
#  AffineSolver  :  Decrypt runes with an array of (s, t) affine keys
#########################################

class AffineSolver(RunningKeySolver):
    def decrypt(self, rune_index, key_index):
        return affine_decrypt(rune_index, self.KEY_DATA[key_index])


#########################################
#  AutokeySolver  :  Decrypts runes by using previously decrypted ones as input
#########################################

class AutokeySolver(RunningKeySolver):
    def run(self, data=None):
        key = self.KEY_DATA[self.KEY_SHIFT:] + self.KEY_DATA[:self.KEY_SHIFT]
        key = [29] * self.KEY_OFFSET + key + [29] * self.KEY_POST_PAD
        self.running_key = key
        super().run(data=data)

    def decrypt(self, rune_index, _):
        rune_index = (rune_index - self.running_key.pop(0)) % 29
        self.running_key.append(rune_index)
        return rune_index

    def copy_unmodified(self, rune_index):
        if self.k_len > 0:
            self.running_key.pop(0)
            self.running_key.append(rune_index)

    def substitute_supports_keylen(self):
        return True

    def substitute_get(self, pos, keylen, search_term, found_term):
        data = self.input.runes_no_whitespace()
        ret = [Rune(r='⁚')] * keylen
        for o in range(len(search_term)):
            plain = search_term[o]
            i = pos + o
            while i >= 0:
                plain = data[i] - plain
                i -= keylen
            ret[i + keylen] = plain
        return RuneText(ret).description(count=True, index=False)

    def key__str__(self):
        return self.key__str__basic_runes()
