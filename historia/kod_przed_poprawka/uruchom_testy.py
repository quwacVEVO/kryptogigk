"""Uruchamia zadania, 371 przypadków, 256 losowych instancji i skalowanie.

Polecenie: python uruchom_testy.py --suite all
Każdy bieg tworzy nowy katalog. Log JSONL zawiera osobny zapis KAŻDEGO wyniku.
Wymagania: Python 3.9+, wyłącznie biblioteka standardowa.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import algorytmy as alg

ROOT = Path(__file__).resolve().parent
METHODS = ('brute_force', 'bsgs', 'rho', 'ph_bsgs', 'ph_rho')
SEED_RANDOM = 2026111201
SEED_SCALING = 2026111202
BITS = (16, 20, 24, 28, 32, 36, 40)
TASKS = [
    ('Z1', 37781, 3, 24581, 1234),
    ('Z2', 100000127, 5, 5910514, 70205663),
    ('Z3', 1000000000547, 2, 514634099897, 640639186538),
    ('Z4', 33815155531460793491, 19, 30073559734842340154, 28938741015890190500),
]


def timestamp():
    """Zapisuje czas UTC i odpowiadający mu czas w Warszawie."""
    now = datetime.now(timezone.utc)
    return {'utc': now.isoformat(), 'warsaw': now.astimezone(ZoneInfo('Europe/Warsaw')).isoformat()}


def sha256(path):
    """Suma kontrolna wskazuje dokładną wersję badanego pliku."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    """Zapisuje czytelny JSON z polskimi znakami."""
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_log(path, value):
    """Dopisuje jeden kompletny rekord; flush chroni log długiego obliczenia."""
    with Path(path).open('a', encoding='utf-8') as out:
        out.write(json.dumps(value, ensure_ascii=False) + '\n')
        out.flush()


def generator(p, rng=None):
    """Wybiera generator, sprawdzając każdy pierwszy dzielnik rzędu p-1."""
    if p == 2:
        return 1
    divisors = alg.factorint(p - 1)
    candidates = range(2, p) if rng is None else iter(lambda: rng.randrange(2, p), None)
    for g in candidates:
        if all(pow(g, (p-1)//q, p) != 1 for q in divisors):
            return g
    raise ValueError('Nie znaleziono generatora.')


def random_prime(bits, rng, safe=False):
    """Losuje p o zadanej długości; safe=True wymaga też pierwszości (p-1)/2."""
    while True:
        if safe:
            q = rng.getrandbits(bits-1) | (1 << (bits-2)) | 1
            p = 2*q + 1
            if p.bit_length() == bits and alg.is_prime(q) and alg.is_prime(p):
                return p
        else:
            p = rng.getrandbits(bits) | (1 << (bits-1)) | 1
            if alg.is_prime(p):
                return p


def measure(request):
    """Mierzy sam algorytm, a potem niezależnie sprawdza znaleziony wykładnik."""
    record = dict(request)
    stats = {}
    p, g, h, n = (request[key] for key in ('p', 'g', 'h', 'n'))
    method, seed, timeout = request['method'], request['seed'], request['timeout_s']
    record['start'] = timestamp()
    record['monotonic_start_ns'] = time.monotonic_ns()
    start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
    answer = None
    status = 'ok'
    try:
        if method == 'brute_force':
            answer = alg.brute_force(g, h, p, n, timeout=timeout, stats=stats)
        elif method == 'bsgs':
            answer = alg.bsgs(g, h, p, n, timeout=timeout, stats=stats)
        elif method == 'rho':
            answer = alg.pollard_rho_dlog(g, h, p, n, seed=seed, timeout=timeout, stats=stats)
        else:
            solver = 'bsgs' if method == 'ph_bsgs' else 'rho'
            answer = alg.pohlig_hellman(g, h, p, solver=solver, seed=seed, timeout=timeout, stats=stats)
    except alg.SearchTimeout as error:
        status, record['error'] = 'timeout', str(error)
    except Exception:
        status, record['error'] = 'error', traceback.format_exc()
    record['elapsed_s'] = (time.perf_counter_ns() - start) / 1e9
    record['cpu_s'] = (time.process_time_ns() - cpu_start) / 1e9
    record['monotonic_finish_ns'] = time.monotonic_ns()
    record['finish'] = timestamp()
    record.update(status=status, a=answer, stats=stats)
    record['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Sprawdzenie pow i porównanie ze znanym a nie wchodzą do czasu algorytmu.
    record['pow_result'] = pow(g, answer, p) if answer is not None else None
    record['verified'] = (answer == request['expected_a'] and record['pow_result'] == h
                          and 0 <= answer < n) if answer is not None else None
    if status == 'ok' and not record['verified']:
        record['status'] = 'wrong_result'
    return record


def isolated_measure(request, output_dir):
    """Uruchamia duży pomiar w osobnym procesie; zachowuje stdout, stderr i kod wyjścia."""
    run_id = f"{request['suite']}_{request['case_id']}_{request['method']}_r{request['repeat']}"
    raw = output_dir / 'surowe'
    raw.mkdir(exist_ok=True)
    command = [sys.executable, '-u', str(Path(__file__).resolve()), '--worker']
    env = dict(os.environ, PYTHONHASHSEED='0')
    parent_start = timestamp()
    start = time.perf_counter()
    try:
        result = subprocess.run(command, input=json.dumps(request), capture_output=True,
                                text=True, encoding='utf-8', env=env,
                                timeout=request['timeout_s'] + 15)
        stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        record = json.loads(stdout) if returncode == 0 else {
            **request, 'status': 'worker_error', 'error': stderr,
            'a': None, 'verified': None}
    except subprocess.TimeoutExpired as error:
        stdout, stderr = error.stdout or b'', error.stderr or b''
        stdout = stdout.decode('utf-8') if isinstance(stdout, bytes) else stdout
        stderr = stderr.decode('utf-8') if isinstance(stderr, bytes) else stderr
        returncode = None
        record = {**request, 'status': 'hard_timeout', 'a': None, 'verified': None}
    (raw / f'{run_id}.stdout').write_text(stdout, encoding='utf-8')
    (raw / f'{run_id}.stderr').write_text(stderr, encoding='utf-8')
    record.update(process_start=parent_start, process_finish=timestamp(),
                  process_elapsed_s=time.perf_counter()-start, returncode=returncode,
                  command=command, raw_stdout=f'surowe/{run_id}.stdout',
                  raw_stderr=f'surowe/{run_id}.stderr', isolated_process=True)
    return record


def request_for(suite, case, method, repeat=1, timeout=30):
    """Łączy publiczne dane, oczekiwany wynik testu i odtwarzalne ziarno rho."""
    return {**case, 'suite': suite, 'method': method, 'repeat': repeat,
            'seed': 20261112 + case['index']*1009 + repeat*9176,
            'timeout_s': timeout}


def run_records(suite, cases, methods, output_dir, isolated=False, repeats=1):
    """Zapisuje każdą próbę; timeout w skalowaniu jest odrębny od poprawnego wyniku."""
    destination = output_dir / f'{suite}.jsonl'
    if destination.exists():
        raise FileExistsError(f'{destination} już istnieje. Wybierz nowy katalog --out.')
    counter = {'ok': 0, 'timeout': 0, 'other': 0}
    for case in cases:
        chosen = methods(case) if callable(methods) else methods
        for repeat in range(1, repeats+1):
            # Kolejność cykliczna ogranicza wpływ stałej kolejności na porównanie.
            order = list(chosen)
            shift = (case['index']+repeat-1) % len(order)
            order = order[shift:] + order[:shift]
            for method in order:
                timeout = 2 if suite == 'skalowanie' and method == 'brute_force' else 120 if suite == 'zadania' else 30
                request = request_for(suite, case, method, repeat, timeout)
                result = isolated_measure(request, output_dir) if isolated else measure(request)
                if not isolated:
                    result['isolated_process'] = False
                    result['peak_rss_note'] = 'Maksimum wspólnego procesu; nie porównuj per instancja.'
                append_log(destination, result)
                state = result['status']
                counter[state if state in ('ok', 'timeout') else 'other'] += 1
                if isolated:
                    print(f"{suite}: {case['case_id']} {method} r{repeat} {state} "
                          f"a={result.get('a')} t={result.get('elapsed_s', 0):.6f}s", flush=True)
                elif case['index'] % 50 == 0 and method == order[-1]:
                    print(f"{suite}: ukończono {case['index']+1}/{len(cases)} instancji", flush=True)
                if state != 'ok' and not (suite == 'skalowanie' and state == 'timeout'):
                    print('BŁĄD: pełne dane znajdują się w logu.', flush=True)
    return {'instances': len(cases), 'algorithm_runs': sum(counter.values()), 'statuses': counter}


def make_case(index, case_id, p, g, a):
    """Buduje poprawną instancję z losowego lub zadanego wykładnika."""
    return {'index': index, 'case_id': case_id, 'p': p, 'g': g, 'h': pow(g, a, p),
            'n': p-1, 'bits': p.bit_length(), 'expected_a': a}


def small_cases():
    """Powtarza opisany wcześniej zakres 371 przypadków; nie odtwarza dawnego logu."""
    cases = []
    for p in (2, 3, 17, 97, 257):
        g = generator(p)
        for a in range(p-1):
            cases.append(make_case(len(cases), f'p{p}_a{a}', p, g, a))
    assert len(cases) == 371
    return cases


def random_cases():
    """Losuje 256 różnych instancji 8-20 bitów z pełnym rzędem generatora."""
    rng, cases, seen = random.Random(SEED_RANDOM), [], set()
    while len(cases) < 256:
        bits = rng.randrange(8, 21)
        p = random_prime(bits, rng)
        g, a = generator(p, rng), rng.randrange(p-1)
        if (p, g, a) in seen:
            continue
        seen.add((p, g, a))
        case = make_case(len(cases), f'random_{len(cases)+1:03}', p, g, a)
        case['dataset_seed'] = SEED_RANDOM
        cases.append(case)
    return cases


def scaling_cases():
    """Tworzy po 3 różne bezpieczne liczby pierwsze dla każdej z 7 długości."""
    rng, cases, seen = random.Random(SEED_SCALING), [], set()
    for bits in BITS:
        for repetition in range(1, 4):
            while True:
                p = random_prime(bits, rng, safe=True)
                if p not in seen:
                    seen.add(p)
                    break
            g, a = generator(p, rng), rng.randrange(1, p-1)
            case = make_case(len(cases), f'bits{bits}_{repetition}', p, g, a)
            q = (p-1)//2
            case.update(q=q, p_prime=alg.is_prime(p), q_prime=alg.is_prime(q),
                        safe_prime=(p == 2*q+1 and alg.is_prime(q)), dataset_seed=SEED_SCALING)
            cases.append(case)
    return cases


def test_arithmetic(output_dir):
    """Bada MR na pierwszych i pseudopierwszych oraz rozkłady z powtórzonymi czynnikami."""
    cases = [(1, False), (2, True), (3, True), (4, False), (97, True), (561, False),
             (1105, False), (1729, False), (3215031751, False), (341550071728321, False),
             (3825123056546413051, False), (2**61-1, True), (TASKS[-1][1], True)]
    records = []
    for n, expected in cases:
        start = timestamp()
        result = alg.is_prime(n)
        records.append({'kind': 'miller_rabin', 'n': n, 'expected': expected,
                        'actual': result, 'ok': result == expected, 'start': start, 'finish': timestamp()})
    to_factor = [1, 2**16, 3**12, 101**4, 1009*1013, 65537*1000003] + [p-1 for _, p, _, _, _ in TASKS]
    for n in to_factor:
        start = timestamp()
        factors = alg.factorint(n)
        ok = math.prod(q**e for q,e in factors.items()) == n and all(alg.is_prime(q) for q in factors)
        records.append({'kind': 'factorint', 'n': n, 'factors': factors, 'ok': ok,
                        'start': start, 'finish': timestamp()})
    for record in records:
        append_log(output_dir / 'arytmetyka.jsonl', record)
    return {'cases': len(records), 'all_correct': all(r['ok'] for r in records)}


def main():
    """Wybiera zestawy i zapisuje metadane, dane wejściowe oraz pełne logi."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--suite', choices=('all', 'zadania', 'testy', 'skalowanie'), default='all')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(measure(json.load(sys.stdin)), ensure_ascii=False))
        return
    output_dir = args.out or ROOT / 'uruchomienia' / datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = {'start': timestamp(), 'monotonic_start_ns': time.monotonic_ns(), 'suite': args.suite,
                'python': sys.version, 'platform': platform.platform(), 'command': sys.argv,
                'source_sha256': {name: sha256(ROOT/name) for name in ('algorytmy.py', 'uruchom_testy.py')},
                'seeds': {'random': SEED_RANDOM, 'scaling': SEED_SCALING},
                'scaling': {'bits': BITS, 'different_primes_per_size': 3, 'brute_timeout_s': 2, 'other_timeout_s': 30},
                'task_repetitions': 3, 'status': 'running', 'summaries': {}}
    if (output_dir / 'metadata.json').exists():
        raise FileExistsError('Katalog już ma metadata.json; użyj nowego --out.')
    save_json(output_dir / 'metadata.json', metadata)
    print(f'WYNIKI: {output_dir}', flush=True)
    if args.suite in ('all', 'zadania'):
        cases = []
        for idx, (name,p,g,h,a) in enumerate(TASKS):
            case = make_case(idx, name, p, g, a)
            assert case['h'] == h
            cases.append(case)
        save_json(output_dir / 'dane_zadania.json', cases)
        methods = lambda case: METHODS if case['case_id'] in ('Z1','Z2') else ('bsgs','rho','ph_bsgs','ph_rho') if case['case_id']=='Z3' else ('ph_bsgs','ph_rho')
        metadata['summaries']['zadania'] = run_records('zadania', cases, methods, output_dir, isolated=True, repeats=3)
        save_json(output_dir / 'plan_bsgs_z4.json', {**alg.bsgs_plan(TASKS[-1][1]-1),
                  'status': 'not_run', 'reason': 'Dla Z4 wykonano PH z dwoma solwerami. Pełny BSGS wymaga ogromnej pamięci.'})
    if args.suite in ('all', 'testy'):
        metadata['summaries']['arytmetyka'] = test_arithmetic(output_dir)
        for suite, cases in [('testy_371', small_cases()), ('testy_losowe', random_cases())]:
            save_json(output_dir / f'dane_{suite}.json', cases)
            metadata['summaries'][suite] = run_records(suite, cases, METHODS, output_dir)
    if args.suite in ('all', 'skalowanie'):
        cases = scaling_cases()
        save_json(output_dir / 'dane_skalowanie.json', cases)
        metadata['summaries']['skalowanie'] = run_records('skalowanie', cases, METHODS, output_dir, isolated=True)
    metadata.update(finish=timestamp(), monotonic_finish_ns=time.monotonic_ns(), status='finished')
    metadata['elapsed_s'] = (metadata['monotonic_finish_ns']-metadata['monotonic_start_ns'])/1e9
    metadata['all_required_results_correct'] = all(
        s.get('statuses', {}).get('other', 0) == 0 and
        (name == 'skalowanie' or s.get('statuses', {}).get('timeout', 0) == 0) and
        s.get('all_correct', True)
        for name,s in metadata['summaries'].items())
    save_json(output_dir / 'metadata.json', metadata)
    print(json.dumps(metadata['summaries'], ensure_ascii=False, indent=2), flush=True)
    if not metadata['all_required_results_correct']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
