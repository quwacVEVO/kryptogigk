"""Niezależnie sprawdza kompletność logów i potęgowania po zakończeniu biegu.

Uruchomienie: python sprawdz_logi.py logi/bieg_po_poprawce
Nie powtarza ataków. Sprawdza zapisane wyniki, dane, hashe i liczby rekordów.
"""

from pathlib import Path
from collections import Counter
import hashlib
import json
import sys
from datetime import datetime, timezone


def sha(path):
    """Oblicza SHA-256 pliku bez zmiany jego zawartości."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(folder):
    """Porównuje logi ze znanymi danymi i wykrywa brakujące lub błędne rekordy."""
    root = Path(__file__).resolve().parent
    folder = Path(folder)
    meta = json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'folder': str(folder),
              'checks': {}, 'counts': {}, 'issues': []}
    checks = report['checks']
    checks['run_finished'] = meta['status'] == 'finished'
    checks['source_matches_recorded_hashes'] = all(sha(root/name) == digest for name,digest in meta['source_sha256'].items())
    checks['all_recorded_file_hashes_match'] = all(sha(folder/name) == digest for name,digest in meta.get('data_and_log_sha256', {}).items())
    expect = {'zadania': 48, 'testy_371': 1855, 'testy_losowe': 1280, 'skalowanie': 105}
    all_records = {}
    for suite, expected_count in expect.items():
        records = [json.loads(line) for line in (folder/f'{suite}.jsonl').read_text(encoding='utf-8').splitlines()]
        all_records[suite] = records
        report['counts'][suite] = dict(Counter(r['status'] for r in records))
        checks[f'{suite}_count'] = len(records) == expected_count
        identities = {(r['case_id'], r['method'], r['repeat']) for r in records}
        checks[f'{suite}_unique_runs'] = len(identities) == len(records)
        checks[f'{suite}_values'] = all(
            (r['status'] == 'timeout' and suite == 'skalowanie') or
            (r['status'] == 'ok' and r['verified'] is True and r['a'] == r['expected_a']
             and pow(r['g'], r['a'], r['p']) == r['h'])
            for r in records)
        checks[f'{suite}_isolated_processes_ok'] = all(
            not r.get('isolated_process') or r['returncode'] == 0 for r in records)
        report['counts'][suite+'_ok_after_soft_deadline'] = sum(
            r['status'] == 'ok' and r['elapsed_s'] > r['timeout_s'] for r in records)

    small = json.loads((folder/'dane_testy_371.json').read_text(encoding='utf-8'))
    random_cases = json.loads((folder/'dane_testy_losowe.json').read_text(encoding='utf-8'))
    scale = json.loads((folder/'dane_skalowanie.json').read_text(encoding='utf-8'))
    key = lambda c: (c['p'], c['g'], c['h'])
    report['counts']['random_small_overlap'] = len(set(map(key, small)) & set(map(key, random_cases)))
    checks['256_distinct_random_instances'] = len(set(map(key, random_cases))) == 256
    checks['371_distinct_small_instances'] = len(set(map(key, small))) == 371
    checks['21_distinct_scaling_primes'] = len({c['p'] for c in scale}) == 21
    checks['scaling_bit_lengths'] = Counter(c['p'].bit_length() for c in scale) == {b: 3 for b in (16,20,24,28,32,36,40)}

    # Dodatkowa kontrola pierwszości niezależną biblioteką, jeśli jest dostępna.
    # Samo uruchamianie rozwiązania i głównych testów nie wymaga SymPy.
    try:
        from sympy import isprime
        import sympy
        report['independent_primality_library'] = 'SymPy '+sympy.__version__
        checks['all_dataset_moduli_prime_independent'] = all(isprime(c['p']) for c in small+random_cases+scale)
        checks['safe_primes_independent'] = all(c['p'] == 2*c['q']+1 and isprime(c['p']) and isprime(c['q']) for c in scale)
    except ImportError:
        report['independent_primality_library'] = None
        report['issues'].append('Brak SymPy: pominięto dodatkową kontrolę pierwszości. Główne logi pozostają sprawdzalne.')

    for suite, records in all_records.items():
        for row in records:
            if row.get('isolated_process'):
                raw = json.loads((folder/row['raw_stdout']).read_text(encoding='utf-8'))
                if any(raw.get(k) != row.get(k) for k in ('status','a','p','g','h','elapsed_s','verified')):
                    report['issues'].append(f'Niezgodny surowy log {suite}/{row["case_id"]}/{row["method"]}')
    checks['raw_stdout_agrees'] = not any('Niezgodny' in issue for issue in report['issues'])
    report['all_checks_passed'] = all(checks.values())
    output = folder/'audyt.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['all_checks_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parent/'logi'/'bieg_po_poprawce'))
