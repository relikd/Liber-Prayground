#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from IOReader import load_indices
from LPath import FILES_ALL, LPath


#########################################
#  InterruptIndices  :  Read chapters and extract indices (cluster by runes)
#########################################

class InterruptIndices(object):
    def __init__(self):
        self.pos = InterruptIndices.load()

    def consider(self, name, irp, limit):
        nums = self.pos[name]['pos'][irp]
        total = self.pos[name]['total'] if len(nums) <= limit else nums[limit]
        return nums[:limit], total

    def total(self, name):
        return self.pos[name]['total']

    def longest_no_interrupt(self, name, irp, irpmax=0):
        irpmax += 1
        nums = self.pos[name]['pos'][irp] + [self.pos[name]['total']] * irpmax
        ret = [(y - x, x) for x, y in zip(nums, nums[irpmax:])]
        return sorted(ret, reverse=True)

    @staticmethod
    def write(dbname='db_indices'):
        with open(LPath.db(dbname), 'w') as f:
            f.write('# file | total runes in file | interrupt | indices\n')
            for name in FILES_ALL:
                data = load_indices(LPath.page(name), 0)
                total = len(data)
                nums = [[] for x in range(29)]
                for idx, rune in enumerate(data):
                    nums[rune].append(idx)
                for irp, pos in enumerate(nums):
                    f.write('{}|{}|{}|{}\n'.format(
                        name, total, irp, ','.join(map(str, pos))))

    @staticmethod
    def load(dbname='db_indices'):
        with open(LPath.db(dbname), 'r') as f:
            ret = {}
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                line = line.strip()
                name, total, irp, nums = line.split('|')
                if name not in ret:
                    ret[name] = {'total': int(total),
                                 'pos': [[] for _ in range(29)]}
                pos = ret[name]['pos']
                pos[int(irp)] = list(map(int, nums.split(','))) if nums else []
            return ret


if __name__ == '__main__':
    # InterruptIndices.write()
    for name, val in InterruptIndices.load().items():
        print(name, 'total:', val['total'])
        print(' ', [len(x) for x in val['pos']])
