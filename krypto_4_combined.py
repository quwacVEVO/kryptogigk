import time
import math

p = 100000127
g = 5
h = 5910514

def pow_mod(x, y, z):
    if y < 0:
        x = pow(x, -1, z)
        y = -y
    num = 1
    x %= z
    while y:
        if y & 1:
            num = num * x % z
        y >>= 1
        x = x * x % z
    return num

def check(p, g, h, val):
    res = pow_mod(g, val, p)
    if res == h:
        return True
    else:
        return False

def bruteforce_attack(p: int, g: int, h: int) -> int: # atak brutalny
    res = 1
    for a in range(0, p):
        if res == h: return a
        res = (res * g) % p
    return res

def shanks_attack(p, g, h): # metoda shanksa
    n = p-1
    m = math.ceil(math.sqrt(n))
    j = range(0, m)
    B = []
    k = 0
    i_r = None
    j_r = None
    g0 = pow_mod(g, -m, p)
    

    for x in j:
        if x==0:
            B.append(1)
        else:
            B.append((B[x-1]*g)%p)

    c = pow_mod(g, -m, p)
    k = h%p

    for i in j:
        for x in j:
            if k == B[x]:
                i_r, j_r = i, x
                break
        if i_r is not None:
            break
        k = (k*c)%p

    if i_r is None:
        return None
    return i_r*m+j_r

def pohlig_hellman_attack(p, g, h): # algorytm pohliga-hellmana
    rzadG = p - 1
    e = 2
    f = rzadG // 2

    c = pow_mod(h, f, p)
    l = pow_mod(g, f, p)

    m = pow_mod(g, e, p)
    n = pow_mod(h, e, p)

    x = m
    a1 = 1
    if x != n:
        for _ in range(0, f - 1):
            a1 = a1 + 1
            x = (x * m) % p
            if x == n:
                break

    k = 0
    while pow_mod(l, a1 + f * k, p) != c:
        k += 1

    wynik = a1 + f * k
    return wynik

def rho_pollards_attack(p, g, h): # algorytm rho pollarda
    a, b, x = [0], [0], [1]
    pair = []
    for i in range(p - 1): 
        if 0 < x[i] <= p // 3:
            a.append((a[i] + 1) % (p - 1))
            b.append(b[i])
            x.append((h * x[i]) % p)
        elif p // 3 < x[i] <= (2 * p) // 3:
            a.append((2 * a[i]) % (p - 1))
            b.append((2 * b[i]) % (p - 1))
            x.append((x[i] ** 2) % p)
        else:
            a.append(a[i])
            b.append((b[i] + 1) % (p - 1))
            x.append((g * x[i]) % p)
        tmp = x[i + 1]
        if tmp in x[:-1]: 
            pair = [i + 1, x.index(tmp)]
            break
    j, k = pair

    A = (a[j] - a[k]) % (p - 1) 
    B = (b[k] - b[j]) % (p - 1)
    d = math.gcd(A, p - 1)
    if d == 1: 
        l = (B * pow_mod(A, -1, p - 1)) % (p - 1)
        return l
    else: 
        mod_red = (p - 1) // d 
        l0 = ((B // d) * pow_mod(A // d, -1, mod_red)) % mod_red
        for m in range(d): 
            l = l0 + m * mod_red 
            if pow_mod(g, l, p) == h: 
                return l

def run_it(p,g,h): # program glowny
    print(f'==============[TESTY]=============')
    start_time = time.perf_counter()
    res_brutal = bruteforce_attack(p, g, h)
    attack_duration = time.perf_counter() - start_time
    if check(p, g, h, res_brutal):
        print(f'SUKCES \nCZAS TRWANIA: {attack_duration:.4f}s')
    else:
        print(f'PORAZKA \nCZAS TRWANIA: {attack_duration:.4f}s')

    print(f'===[ATAK SHANKSA]===')
    start_time = time.perf_counter()
    res_brutal = shanks_attack(p, g, h)
    attack_duration = time.perf_counter() - start_time
    if check(p, g, h, res_brutal):
        print(f'SUKCES\nCZAS TRWANIA: {attack_duration:.4f}s')
    else:
        print(f'PORAZKA \nCZAS TRWANIA: {attack_duration:.4f}s')

    print(f'===[ATAK POHLIGA-HELLMANA]===')
    start_time = time.perf_counter()
    res_brutal = pohlig_hellman_attack(p, g, h)
    attack_duration = time.perf_counter() - start_time
    if check(p, g, h, res_brutal):
        print(f'SUKCES \nCZAS TRWANIA: {attack_duration:.4f}s')
    else:
        print(f'PORAZKA \nCZAS TRWANIA: {attack_duration:.4f}s')

    print(f'===[ATAK RHO-POLLARDA]===')
    start_time = time.perf_counter()
    res_brutal = rho_pollards_attack(p, g, h)
    attack_duration = time.perf_counter() - start_time
    if check(p, g, h, res_brutal):
        print(f'SUKCES \nCZAS TRWANIA: {attack_duration:.4f}s')
    else:
        print(f'PORAZKA \nCZAS TRWANIA: {attack_duration:.4f}s')

    print(f'=============[KONIEC]=============')

run_it(p,g,h)