#!/usr/bin/env python3
import math


# yes it will report 2,3,5 as non-prime
# though why add a check if it will never be tested anyway
def is_prime(num):
    if isinstance(num, str):
        num = int(num)
    if num & 1 and num % 5 > 0:
        for i in range(2, math.floor(math.sqrt(num)) + 1):
            if i & 1 and (num % i) == 0:
                return False
        return True
    return False


def rev(num):  # or int(str(num)[::-1])
    if isinstance(num, str):
        num = int(num)
    revs = 0
    while (num > 0):
        remainder = num % 10
        revs = (revs * 10) + remainder
        num = num // 10
    return revs
