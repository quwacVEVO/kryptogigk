"""Algorytmy do laboratorium G5. Python 3.8+, tylko biblioteka standardowa.

Kontrakt solverów: p jest pierwsze, g ma dokładny rząd n, a h należy do <g>.
Zwracamy a z przedziału 0 <= a < n, takie że pow(g, a, p) == h.
Rho faktoryzacji i rho logarytmu dyskretnego to różne algorytmy.
"""

from math import gcd, isqrt, prod
from random import Random, SystemRandom
from time import perf_counter


MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
MR_BASES_12 = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
MR_BOUND_12 = 318665857834031151167461
DEFAULT_SEED = 20261112


class SearchTimeout(TimeoutError):
    """Przerwanie po limicie czasu; zachowuje wykonane liczniki w stats."""

    def __init__(self, message, stats=None):
        super().__init__(message)
        self.stats = dict(stats or {})


def _deadline(timeout):
    """Zamienia limit sekund na punkt końcowy zegara monotonicznego."""
    return None if timeout is None else perf_counter() + max(0, timeout)


def _check_time(deadline, stats):
    """Kończy obliczenie, gdy upłynął przydzielony czas."""
    if deadline is not None and perf_counter() >= deadline:
        stats['status'] = 'timeout'
        raise SearchTimeout('Przekroczono limit czasu.', stats)


def _remaining(deadline):
    """Przekazuje podproblemowi pozostałą część wspólnego budżetu czasu."""
    return None if deadline is None else max(0, deadline - perf_counter())


def is_prime(n, rng=None):
    """Miller-Rabin: deterministyczny do MR_BOUND_12, dalej 32 losowe bazy.

    Do 2^64 stosujemy 7 specjalnych baz; potem 12 pierwszych baz pierwszych.
    Przedziały: github.com/sympy/sympy/blob/master/sympy/ntheory/primetest.py
    Dla większych n True oznacza prawdopodobną pierwszość, nie dowód.
    Jeśli nie podano rng, losowe bazy pochodzą z SystemRandom.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    rng = rng if rng is not None else SystemRandom()
    if n < 2**64:
        bases = MR_BASES_64
    elif n < MR_BOUND_12:
        bases = MR_BASES_12
    else:
        bases = [rng.randrange(2, n-1) for _ in range(32)]
    for base in bases:
        base %= n
        if base == 0:
            continue
        x = pow(base, d, n)
        if x in (1, n-1):
            continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1:
                break
        else:
            return False
    return True


def _rho_factor(n, rng, deadline, stats):
    """Znajduje nietrywialny dzielnik n przez rho Pollarda z cyklem Brenta."""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    while True:
        _check_time(deadline, stats)
        y, c = rng.randrange(1, n), rng.randrange(1, n)
        divisor, block_length = 1, 1
        stats['factor_restarts'] = stats.get('factor_restarts', 0) + 1
        while divisor == 1:
            x = y
            previous_count = stats.get('factor_iterations', 0)
            for j in range(block_length):
                if j & 2047 == 0:
                    stats['factor_iterations'] = previous_count+j
                    _check_time(deadline, stats)
                y = (y*y+c) % n
            stats['factor_iterations'] = previous_count+block_length
            offset = 0
            while offset < block_length and divisor == 1:
                previous_y = y
                product = 1
                size = min(128, block_length-offset)
                for _ in range(size):
                    y = (y*y+c) % n
                    product = product*abs(x-y) % n
                stats['factor_iterations'] = stats.get('factor_iterations', 0) + size
                divisor = gcd(product, n)
                offset += size
                _check_time(deadline, stats)
            block_length *= 2
        if divisor == n:
            # Iloczyn objął zbyt wiele zderzeń. Badamy je pojedynczo.
            while True:
                previous_y = (previous_y*previous_y+c) % n
                divisor = gcd(abs(x-previous_y), n)
                stats['factor_iterations'] = stats.get('factor_iterations', 0) + 1
                _check_time(deadline, stats)
                if divisor > 1:
                    break
        if divisor != n:
            return divisor


def _factorint(n, rng, deadline, stats):
    """Rozbija złożone liczby przez rho, kończąc gałęzie testem MR."""
    if n < 1:
        raise ValueError('Faktoryzacja wymaga n >= 1.')
    factors, stack = {}, [n]
    while stack:
        _check_time(deadline, stats)
        value = stack.pop()
        if value == 1:
            continue
        stats['miller_rabin_calls'] = stats.get('miller_rabin_calls', 0) + 1
        if is_prime(value, rng):
            factors[value] = factors.get(value, 0) + 1
        else:
            divisor = _rho_factor(value, rng, deadline, stats)
            stack.extend((divisor, value//divisor))
    return dict(sorted(factors.items()))


def factorint(n, rng=None):
    """Rozkłada n metodą Miller-Rabin + rho Pollarda; bez dzielenia próbnego.

    Wyjątek stanowi szybkie sprawdzenie podzielności przez 2 i 3.
    Przykład: factorint(20) zwraca {2: 2, 5: 1}.
    """
    rng = rng if rng is not None else Random(DEFAULT_SEED)
    return _factorint(n, rng, None, {})


def brute_force(g, h, p, n, *, timeout=None, stats=None):
    """Sprawdza wykładniki po kolei, obliczając następną potęgę mnożeniem."""
    if n < 1:
        raise ValueError('Rząd n musi być dodatni.')
    stats = stats if stats is not None else {}
    stats.update(method='brute_force', iterations=0, status='running')
    deadline = _deadline(timeout)
    _check_time(deadline, stats)
    value, g, h = 1, g % p, h % p
    for a in range(n):
        if a & 4095 == 0:
            stats['iterations'] = a
            _check_time(deadline, stats)
        if value == h:
            stats.update(iterations=a+1, multiplications=a, status='ok')
            return a
        value = value*g % p
    stats.update(iterations=n, status='not_found')
    raise ValueError('Brak rozwiązania w podanym zakresie.')


def bsgs_plan(n):
    """Wylicza wielkość tablicy z n; 128 B/wpis to jawne przybliżenie RAM.

    Funkcja nie nakłada limitu tablicy. Decyzję o dostępnych zasobach
    podejmuje kod wywołujący. Rzeczywisty rozmiar zależy od implementacji Pythona.
    """
    if n < 1:
        raise ValueError('Rząd n musi być dodatni.')
    m = isqrt(n-1)+1
    return {'n': n, 'm': m, 'entries': m, 'estimated_bytes': 128*m,
            'assumed_bytes_per_entry': 128, 'giant_steps_max': (n+m-1)//m}


def bsgs(g, h, p, n, *, timeout=None, stats=None):
    """Shanks: tablica g^j i dopasowanie h*g^(-i*m), gdzie m=ceil(sqrt(n))."""
    stats = stats if stats is not None else {}
    plan = bsgs_plan(n)
    stats.update(method='bsgs', status='running', baby_steps=0, giant_steps=0,
                 iterations=0, **plan)
    deadline = _deadline(timeout)
    _check_time(deadline, stats)
    m, table, value = plan['m'], {}, 1
    g, h = g % p, h % p
    for j in range(m):
        if j & 4095 == 0:
            stats.update(baby_steps=j, iterations=j)
            _check_time(deadline, stats)
        table.setdefault(value, j)
        value = value*g % p
    stats.update(baby_steps=m, iterations=m)
    step, value = pow(pow(g, m, p), -1, p), h
    for i in range(plan['giant_steps_max']):
        if i & 4095 == 0:
            stats.update(giant_steps=i, iterations=m+i)
            _check_time(deadline, stats)
        if value in table:
            a = i*m+table[value]
            if a < n and pow(g, a, p) == h:
                stats.update(giant_steps=i+1, iterations=m+i+1, status='ok')
                return a
        value = value*step % p
    stats.update(giant_steps=plan['giant_steps_max'], status='not_found')
    raise ValueError('Brak rozwiązania w podanym zakresie.')


def pollard_rho_dlog(g, h, p, n, *, seed=DEFAULT_SEED, timeout=None, stats=None):
    """Rho logarytmu dyskretnego: 16 gałęzi losowego spaceru i cykl Brenta.

    Stan spełnia x = g^a*h^b (mod p). Zderzenie daje kongruencję liniową.
    Gdy n jest złożone, obsługujemy gcd i weryfikujemy kandydatów. Nie używamy
    BSGS ani PH. Restart zmienia spacer; seed umożliwia odtworzenie przebiegu.
    """
    if n < 1:
        raise ValueError('Rząd n musi być dodatni.')
    stats = stats if stats is not None else {}
    stats.update(method='pollard_rho_dlog', seed=seed, iterations=0, restarts=0,
                 collisions=0, candidate_checks=0, discarded_collisions=0,
                 status='running', partitions=16)
    deadline = _deadline(timeout)
    _check_time(deadline, stats)
    g, h = g % p, h % p
    if h == 1:
        stats.update(status='ok', trivial_case='h=1')
        return 0
    if n <= 2:
        # Dla grupy rzędu 1 lub 2 nie potrzeba losowego spaceru.
        if n == 2 and h == g:
            stats.update(status='ok', trivial_case='n=2')
            return 1
        raise ValueError('h nie należy do podanej grupy.')

    rng = Random(seed)
    total_steps = 0
    walk_budget = 8*(isqrt(n)+1)
    # Przy bardzo licznej rodzinie kandydatów lepiej zmienić spacer.
    candidate_budget = max(32, min(4096, isqrt(n)+1))
    for attempt in range(128):
        stats['restarts'] = attempt
        _check_time(deadline, stats)
        multipliers, add_a, add_b = [], [], []
        for _ in range(16):
            while True:
                da, db = rng.randrange(n), rng.randrange(n)
                multiplier = pow(g, da, p)*pow(h, db, p) % p
                if multiplier != 1:
                    break
            multipliers.append(multiplier)
            add_a.append(da)
            add_b.append(db)
        a, b = rng.randrange(n), rng.randrange(n)
        x = pow(g, a, p)*pow(h, b, p) % p
        old_x, old_a, old_b = x, a, b
        power, length = 1, 0

        for walk_step in range(walk_budget):
            if walk_step & 2047 == 0:
                stats['iterations'] = total_steps
                _check_time(deadline, stats)
            if power == length:
                old_x, old_a, old_b = x, a, b
                power *= 2
                length = 0
            # Mieszamy bity x, by wybór gałęzi nie zależał tylko od parzystości.
            branch = (x ^ (x >> 16)) & 15
            x = x*multipliers[branch] % p
            a += add_a[branch]
            if a >= n:
                a -= n
            b += add_b[branch]
            if b >= n:
                b -= n
            length += 1
            total_steps += 1
            if x != old_x:
                continue

            stats['collisions'] += 1
            # (b-old_b)*log_g(h) = old_a-a (mod n).
            coefficient, rhs = (b-old_b) % n, (old_a-a) % n
            divisor = gcd(coefficient, n)
            stats['last_collision_gcd'] = divisor
            if coefficient == 0 or rhs % divisor or divisor > candidate_budget:
                stats['discarded_collisions'] += 1
                break
            reduced_n = n//divisor
            first = (rhs//divisor)*pow(coefficient//divisor, -1, reduced_n) % reduced_n
            for k in range(divisor):
                candidate = first+k*reduced_n
                stats['candidate_checks'] += 1
                if pow(g, candidate, p) == h:
                    stats.update(iterations=total_steps, status='ok')
                    return candidate
                if k & 63 == 0:
                    stats['iterations'] = total_steps
                    _check_time(deadline, stats)
            stats['discarded_collisions'] += 1
            break
    stats.update(iterations=total_steps, status='failed')
    raise ValueError('Rho nie znalazło wyniku po 128 restartach.')


def _crt(residues, moduli):
    """Łączy reszty dla parami względnie pierwszych modułów."""
    modulus = prod(moduli)
    answer = 0
    for residue, part in zip(residues, moduli):
        other = modulus//part
        answer += residue*other*pow(other, -1, part)
    return answer % modulus


def pohlig_hellman(g, h, p, *, solver='bsgs', seed=DEFAULT_SEED, timeout=None, stats=None):
    """Pełny PH: faktoryzacja MR+rho, cyfry modulo q^e, a na końcu CRT.

    Wybór solver='rho' zastępuje BSGS rzeczywistym rho DLP dla każdej
    nietrywialnej podgrupy. Tylko q=2 i h=1 mają rozwiązanie bez spaceru.
    """
    if solver not in ('bsgs', 'rho'):
        raise ValueError("solver musi być 'bsgs' albo 'rho'.")
    stats = stats if stats is not None else {}
    stats.update(method='pohlig_hellman', solver=solver, seed=seed,
                 status='running', subproblems=[], iterations=0)
    deadline = _deadline(timeout)
    _check_time(deadline, stats)
    n, g, h = p-1, g % p, h % p
    factors = _factorint(n, Random(seed), deadline, stats)
    stats['factors'] = factors
    if any(pow(g, n//q, p) == 1 for q in factors):
        raise ValueError('PH wymaga generatora pełnej grupy rzędu p-1.')
    residues, moduli = [], []
    subgroup_index = 0
    for q, exponent in factors.items():
        residue, q_power = 0, 1
        base = pow(g, n//q, p)
        for digit_index in range(exponent):
            _check_time(deadline, stats)
            shifted = h*pow(g, -residue, p) % p
            target = pow(shifted, n//(q_power*q), p)
            detail = {'q': q, 'digit_index': digit_index, 'base': base, 'target': target}
            stats['subproblems'].append(detail)
            try:
                if solver == 'bsgs':
                    digit = bsgs(base, target, p, q, timeout=_remaining(deadline), stats=detail)
                else:
                    digit = pollard_rho_dlog(base, target, p, q,
                        seed=seed+subgroup_index, timeout=_remaining(deadline), stats=detail)
            except SearchTimeout:
                stats['status'] = 'timeout'
                stats['iterations'] = sum(item.get('iterations', 0) for item in stats['subproblems'])
                raise SearchTimeout('Limit czasu podczas podproblemu PH.', stats)
            detail['digit'] = digit
            subgroup_index += 1
            residue += digit*q_power
            q_power *= q
        residues.append(residue)
        moduli.append(q_power)
    answer = _crt(residues, moduli)
    if pow(g, answer, p) != h:
        raise ValueError('Niepoprawny wynik PH.')
    stats.update(status='ok', residues=residues, moduli=moduli,
                 iterations=sum(item.get('iterations', 0) for item in stats['subproblems']))
    return answer
