#!/usr/bin/env python3
try:
    from PIL import Image, ImageDraw
    IMG_OUT = True
except ModuleNotFoundError:
    IMG_OUT = False


def power(x, y, p):
    res = 1
    x %= p
    while (y > 0):
        if (y & 1):
            res = (res * x) % p
        y = y >> 1
        x = (x * x) % p
    return res


# Assumption: p is of the form 3*i + 4 where i >= 1
def sqrtFast(n, p):
    if (p % 4 != 3):
        raise ValueError('Invalid Input')
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


def sqrtNormal(n, p):
    n %= p
    for x in range(2, p):
        if ((x * x) % p == n):
            return x
    return None


def elliptic_curve(a, b, r):
    print(f'generate curve: a={a}, b={b}, r={r}')
    if IMG_OUT:
        image1 = Image.new('RGB', (r, r))
        draw1 = ImageDraw.Draw(image1)
        draw1.rectangle((0, 0, r, r), fill='white')
        image2 = Image.new('RGB', (r, r))
        draw2 = ImageDraw.Draw(image2)
        draw2.rectangle((0, 0, r, r), fill='white')

    sqrtFn = sqrtNormal if (r % 4 != 3) else sqrtFast
    txt = ''
    for x in range(r):
        y2 = (x ** 3 + a * x + b) % r
        u2 = sqrtFn(y2, r) if y2 > 0 else 0
        if u2 is not None:
            z1 = r - 1 - u2
            z2 = r - 1 - (-u2 % r)
            print(x, y2, -y2 % r)
            txt += f'{x} {y2} {-y2 % r}\n'
            if IMG_OUT:
                draw1.rectangle((x, z1, x, z1), fill='black')
                draw1.rectangle((x, z2, x, z2), fill='black')
                draw2.rectangle((x - 2, z1 - 2, x + 2, z1 + 2), fill='black')
                draw2.rectangle((x - 2, z2 - 2, x + 2, z2 + 2), fill='black')

    with open(f'ec-a{a}-b{b}-r{r}.txt', 'w') as f:
        f.write(txt)
    if IMG_OUT:
        print('writing image output')
        image1.save(f'ec-a{a}-b{b}-r{r}-pp.png', 'PNG')
        image2.save(f'ec-a{a}-b{b}-r{r}-lg.png', 'PNG')
    print()


elliptic_curve(a=149, b=263, r=3299)
