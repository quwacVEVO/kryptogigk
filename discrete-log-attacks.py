import sympy
import math
import random


def BRUTE(p, g, h):
    x = 1
    for a in range(p - 1):
        if x == h % p:
            return a
        x = x * g % p
    return None


def SHANKS(p, g, h, r=None):
    if r is None:
        r = p - 1
    m = math.ceil(math.sqrt(r))
    
    L1 = {pow(g, m * j, p): j for j in range(m)}
    
    g_inv = pow(g, -1, p)
    for i in range(m):
        y = (h * pow(g_inv, i, p)) % p
        if y in L1:
            return (m * L1[y] + i) % r
            
    return None


def RHO_POLLARD(p, g, h, n=None, max_tries=20):
    if n is None:
        n = p - 1

    def step(x, a, b):
        if x % 3 == 0:
            return x * x % p, 2 * a % n, 2 * b % n
        if x % 3 == 1:
            return x * g % p, (a + 1) % n, b
        return x * h % p, a, (b + 1) % n

    for _ in range(max_tries):
        a, b = random.randrange(n), random.randrange(n)
        x = pow(g, a, p) * pow(h, b, p) % p
        X, A, B = x, a, b
        Y, C, D = x, a, b
        while True:
            X, A, B = step(X, A, B)
            Y, C, D = step(*step(Y, C, D))
            if X == Y:
                break

        # (B - D) * a = C - A  (mod n)
        r, s = (B - D) % n, (C - A) % n
        d = math.gcd(r, n)
        if r == 0 or s % d != 0:
            continue
        a0 = (s // d) * pow(r // d, -1, n // d) % (n // d)
        for k in range(d):
            a = a0 + k * (n // d)
            if pow(g, a, p) == h % p:
                return a
    return None 


def PohligHellmanInternal(p, g, h, n, q, c, METHOD=SHANKS):
    beta = h
    gamma = pow(g, n // q, p)
    a = 0

    for j in range(c):
        delta = pow(beta, n // (q ** (j + 1)), p)
        if q <= 100:
            i = BRUTE(p, gamma, delta) #szukamy i takie, że delta = g^in/q  (mod p)
        else:
            i = METHOD(p, gamma, delta, q)
            
        a_j = i
        beta = (beta * pow(g, -a_j * q**j, p)) % p

        a += a_j * q**j

    return a


def POHLIGHELLMAN(p, g, h, METHOD=SHANKS):
    n = p - 1
    czynniki = sympy.factorint(n)

    moduly = []
    reszty = []

    for q, c in czynniki.items():
        moduly.append(q**c)
        reszty.append(PohligHellmanInternal(p, g, h, n, q, c, METHOD))

    a = int(sympy.ntheory.modular.crt(moduly, reszty)[0])
    return a