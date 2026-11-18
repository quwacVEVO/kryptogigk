import time, random
from math import gcd

def rho_pollard(p, g, h):
    start_time = time.perf_counter()

    n = p - 1

    def step(x, u, v):
        if x % 3 == 0:
            x = x * g
            u = u + 1
        elif x % 3 == 1:
            x = x * h
            v = v + 1
        else:
            x = x ** 2
            u = 2 * u
            v = 2 * v

        return x % p, u % n, v % n

    x1, u1, v1 = 1, 0, 0
    x2, u2, v2 = 1, 0, 0

    for _ in range(n):
        x1, u1, v1 = step(x1, u1, v1)

        x2, u2, v2 = step(x2, u2, v2)
        x2, u2, v2 = step(x2, u2, v2)

        if x1 == x2:
            break
    else:
        print('Nie znaleziono kolizji')
        end_time = time.perf_counter()
        total_time = end_time - start_time
        return None, total_time

    r = (v1 - v2) % n
    s = (u2 - u1) % n
    d = gcd(r, n)

    a = None

    if r == 0:
        print('Kolizja trywialna (r = 0)')
        end_time = time.perf_counter()
        total_time = end_time - start_time
        return None, total_time
    elif d == 1:
        a = s * pow(r, -1, n) % n
    else:
        if s % d != 0:
            print('Brak rozwiązania z tej kolizji')
            end_time = time.perf_counter()
            total_time = end_time - start_time
            return None, total_time

        n_d = n // d
        r_d = r // d
        s_d = s // d

        a0 = s_d * pow(r_d, -1, n_d) % n_d

        for k in range(d):
            sol = a0 + k * n_d
            if pow(g, sol, p) == h:
                a = sol
                break

    end_time = time.perf_counter()
    total_time = end_time - start_time

    if a is None or pow(g, a, p) != h:
        print('Wynik nie spełnia g^a = h (mod p)')
        return None, total_time

    return a, total_time


p, g, h = 37781, 3, 24581
N = 100

czas = []
for _ in range(N):
    a, total_time = rho_pollard(p, g, h)
    czas.append(total_time)
print(f'rho: a={a}, g^a = h: {pow(g, a, p) == h}')
print(f'Średni czas z {N} uruchomień Rho-Pollard: {sum(czas) / N:.6f}s')