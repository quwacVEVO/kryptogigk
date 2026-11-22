"""Uruchomienie w osobnym procesie z pełnymi logami i metadanymi."""

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic_ns, perf_counter_ns


KATALOG = Path(__file__).resolve().parent
KOD = KATALOG / "rozwiazanie.py"
KOMENDA = [sys.executable, str(KOD)]


def teraz():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def main():
    poczatek_utc = teraz()
    poczatek_monotonic_ns = monotonic_ns()
    poczatek_perf_ns = perf_counter_ns()
    with (KATALOG / "stdout.txt").open("wb") as stdout, (KATALOG / "stderr.txt").open("wb") as stderr:
        try:
            proces = subprocess.run(KOMENDA, cwd=KATALOG, stdout=stdout, stderr=stderr, timeout=180)
            returncode = proces.returncode
            timeout = False
        except subprocess.TimeoutExpired:
            returncode = None
            timeout = True
    koniec_perf_ns = perf_counter_ns()
    koniec_monotonic_ns = monotonic_ns()
    koniec_utc = teraz()
    metadane = {
        "model_id_requested": "gpt-6-sol",
        "model_display_name": "GPT-6 Sol",
        "model_snapshot_build": None,
        "model_snapshot_build_note": "Snapshot/build nie jest udostępniony temu agentowi.",
        "actual_internal_variant": None,
        "actual_internal_variant_note": "Rzeczywisty wewnętrzny wariant nie jest udostępniony temu agentowi.",
        "execution_mode": "niezależny agent",
        "reasoning_effort_requested": "high",
        "independent_reproducible_attempt": True,
        "source_version": 1,
        "code_error_corrections": 0,
        "environment_issues": 0,
        "python_version": platform.python_version(),
        "python_full_version": sys.version,
        "command_argv": KOMENDA,
        "command_display": " ".join(KOMENDA),
        "working_directory": str(KATALOG),
        "source_file": KOD.name,
        "source_sha256": hashlib.sha256(KOD.read_bytes()).hexdigest(),
        "started_utc": poczatek_utc,
        "finished_utc": koniec_utc,
        "started_monotonic_ns": poczatek_monotonic_ns,
        "finished_monotonic_ns": koniec_monotonic_ns,
        "elapsed_monotonic_ns": koniec_monotonic_ns - poczatek_monotonic_ns,
        "started_perf_counter_ns": poczatek_perf_ns,
        "finished_perf_counter_ns": koniec_perf_ns,
        "elapsed_perf_counter_ns": koniec_perf_ns - poczatek_perf_ns,
        "returncode": returncode,
        "timeout": timeout,
        "stdout_file": "stdout.txt",
        "stderr_file": "stderr.txt",
    }
    (KATALOG / "metadata.json").write_text(json.dumps(metadane, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"returncode": returncode, "timeout": timeout, "metadata": str(KATALOG / "metadata.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
