#!/usr/bin/env python3
import math


# yes it will report 2,3,5 as non-prime
# though why add a check if it will never be tested anyway
def is_prime(num):
    if isinstance(num, str):
        num = int(num)
    if num in [2, 3, 5]:
        return True
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


def power(x, y, p):
    res = 1
    x %= p
    while (y > 0):
        if (y & 1):
            res = (res * x) % p
        y = y >> 1
        x = (x * x) % p
    return res


def sqrtNormal(n, p):
    n %= p
    for x in range(2, p):
        if ((x * x) % p == n):
            return x
    return None


# Assumption: p is of the form 3*i + 4 where i >= 1
def sqrtFast(n, p):
    if (p % 4 != 3):
        # raise ValueError('Invalid Input')
        return sqrtNormal(n, p)
    # Try "+(n ^ ((p + 1)/4))"
    n = n % p
    x = power(n, (p + 1) // 4, p)
    if ((x * x) % p == n):
        return x
    # Try "-(n ^ ((p + 1)/4))"
    x = p - x
    if ((x * x) % p == n):
        return x
    return None


def elliptic_curve(x, a, b, r):
    y2 = (x ** 3 + a * x + b) % r
    y = sqrtFast(y2, r) if y2 > 0 else 0
    if y is None:
        return None, None
    return y, -y % r
