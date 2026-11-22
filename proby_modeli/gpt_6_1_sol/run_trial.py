"""Rejestrator niezależnej próby: pełne logi i metadane procesu."""
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

base = Path(__file__).resolve().parent
source = base / 'rozwiazanie.py'
command = [sys.executable, '-u', str(source)]
metadata = {
    'trial_kind': 'new_independent_reproducible_trial',
    'not_recovered_prior_trial': True,
    'model_requested': 'GPT-6.1 Sol',
    'model_call_identifier': 'gpt-6.1-sol',
    'reasoning_effort_requested': 'high',
    'execution_mode': 'independent_agent',
    'model_snapshot': None,
    'model_build': None,
    'actual_internal_model_variant': None,
    'unavailable_model_details_explanation': 'Snapshot/build i rzeczywisty wewnętrzny wariant modelu nie są udostępnione w środowisku; nie zostały odgadnięte.',
    'code_bug_fixes_count': 0,
    'environment_problem_count': 1,
    'environment_problems': [{'description': 'Pierwsze wywołanie mkdir używało nieistniejącego workdir docelowego; proces nie powstał. Ponowiono z istniejącego katalogu nadrzędnego.', 'impact': 'Brak wpływu na źródło i pomiary; nastąpiło przed zapisaniem i uruchomieniem rozwiązania.'}],
    'source_versions': ['source_v1.py'],
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'prompt_sha256': hashlib.sha256((base / 'prompt.txt').read_bytes()).hexdigest(),
    'python_version': sys.version,
    'python_executable': sys.executable,
    'platform': platform.platform(),
    'sympy_version': importlib.metadata.version('sympy'),
    'command': command,
    'cwd': str(base),
    'stdout_file': 'stdout_v1.log',
    'stderr_file': 'stderr_v1.log',
    'timeout_seconds': 120,
    'source_saved_before_execution': True,
}
metadata['utc_start'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
metadata['monotonic_start_ns'] = time.monotonic_ns()
metadata['perf_counter_start_ns'] = time.perf_counter_ns()
with (base / 'metadata.json').open('w') as out:
    json.dump(metadata, out, ensure_ascii=False, indent=2)
with (base / 'stdout_v1.log').open('wb') as stdout, (base / 'stderr_v1.log').open('wb') as stderr:
    proc = subprocess.Popen(command, cwd=base, stdout=stdout, stderr=stderr)
    metadata['pid'] = proc.pid
    try:
        metadata['returncode'] = proc.wait(timeout=metadata['timeout_seconds'])
        metadata['timed_out'] = False
    except subprocess.TimeoutExpired:
        proc.kill()
        metadata['returncode'] = proc.wait()
        metadata['timed_out'] = True
metadata['perf_counter_finish_ns'] = time.perf_counter_ns()
metadata['monotonic_finish_ns'] = time.monotonic_ns()
metadata['utc_finish'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
metadata['wall_seconds_perf'] = (metadata['perf_counter_finish_ns'] - metadata['perf_counter_start_ns']) / 1e9
metadata['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
metadata['stdout_sha256'] = hashlib.sha256((base / 'stdout_v1.log').read_bytes()).hexdigest()
metadata['stderr_sha256'] = hashlib.sha256((base / 'stderr_v1.log').read_bytes()).hexdigest()
with (base / 'metadata.json').open('w') as out:
    json.dump(metadata, out, ensure_ascii=False, indent=2)
print(json.dumps(metadata, ensure_ascii=False, indent=2))
