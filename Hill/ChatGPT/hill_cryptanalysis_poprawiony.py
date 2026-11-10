#!/usr/bin/env python3
"""Kryptoanaliza szyfru Hilla: alfa26/alfa37, ciphertext-only i known-plaintext-fragment."""

import argparse
import itertools
import logging
import math
import random
import sys
import unicodedata
from collections import Counter
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("Brakuje biblioteki numpy. Zainstaluj ją poleceniem: python -m pip install numpy")
    sys.exit(1)

ALPHABETS = {
    "alfa26": "abcdefghijklmnopqrstuvwxyz",
    "alfa37": "abcdefghijklmnopqrstuvwxyz 0123456789",
}
PL_DEFAULT = """
to jest przykladowy tekst w jezyku polskim. ludzie poszukuja informacji, analizuja dane i
sprawdzaja rozne hipotezy. nie zawsze pamietamy wszystkie fakty, a nasze oczekiwania
wplywaja na sposob interpretowania informacji. przykladowo osoby czesto wybieraja
argumenty, ktore potwierdzaja wczesniejsze przekonania. jest to znane zjawisko
psychologiczne. tekst powinien zawierac zwykle slowa, zdania oraz naturalne polskie
polaczenia liter. kiedy analizujemy wiadomosc, mozemy porownac jej statystyki z
czestotliwoscia wystepowania liter i grup liter w jezyku polskim.
"""
EN_DEFAULT = """
this is an example of ordinary english text. people search for information, analyze data,
and test different ideas. our expectations can influence how we interpret facts and
remember events. for example, people often prefer information that confirms earlier
beliefs. this effect is studied in psychology. a natural text contains common words and
common combinations of letters. language statistics can help compare possible messages
and select a more readable result from several candidate decryptions.
"""


# Częstości referencyjne liter w procentach, po sprowadzeniu polskich
# znaków diakrytycznych do liter bazowych używanych w alfa26/alfa37.
# PL: próbka drugiego wydania Korpusu IPI PAN (ok. 25 mln słów).
# EN: standardowa tabela względnych częstości liter publikowana przez Emory University.
LETTER_FREQUENCIES = {
    "pl": dict(zip("abcdefghijklmnopqrstuvwxyz", [
        9.90, 1.47, 4.36, 3.25, 8.77, 0.30, 1.42, 1.08, 8.21, 2.28,
        3.51, 3.92, 2.80, 5.72, 8.60, 3.13, 0.14, 4.69, 4.98, 3.98,
        2.50, 0.04, 4.65, 0.02, 3.76, 6.53
    ])),
    "en": dict(zip("abcdefghijklmnopqrstuvwxyz", [
        8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094,
        6.966, 0.153, 0.772, 4.025, 2.406, 6.749, 7.507, 1.929,
        0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150,
        1.974, 0.074
    ])),
}
LANGUAGE_NAMES = {"pl": "polski", "en": "angielski"}

POLISH_MAP = str.maketrans({
    "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
    "ó": "o", "ś": "s", "ź": "z", "ż": "z",
})


def clean_text(text, alphabet, linebreaks_as_spaces=False):
    if linebreaks_as_spaces and " " in alphabet:
        text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    text = unicodedata.normalize("NFKD", text.lower()).translate(POLISH_MAP)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    allowed = set(alphabet)
    return "".join(ch for ch in text if ch in allowed)


def text_to_numbers(text, alphabet):
    table = {ch: i for i, ch in enumerate(alphabet)}
    return [table[ch] for ch in text]


def numbers_to_text(values, alphabet):
    return "".join(alphabet[int(v)] for v in values)


def prime_factors(value):
    result = []
    d = 2
    while d * d <= value:
        if value % d == 0:
            result.append(d)
            while value % d == 0:
                value //= d
        d += 1
    if value > 1:
        result.append(value)
    return result


def inverse_matrix_mod_prime(matrix, p):
    n = len(matrix)
    a = [[int(matrix[i][j]) % p for j in range(n)] + [int(i == j) for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col] % p), None)
        if pivot is None:
            raise ValueError("Macierz jest osobliwa modulo liczby pierwszej.")
        a[col], a[pivot] = a[pivot], a[col]
        factor = pow(a[col][col], -1, p)
        a[col] = [(x * factor) % p for x in a[col]]
        for row in range(n):
            if row != col:
                factor = a[row][col]
                a[row] = [(a[row][j] - factor * a[col][j]) % p for j in range(2 * n)]
    return [row[n:] for row in a]


def inverse_matrix_mod(matrix, modulus):
    inverses = [inverse_matrix_mod_prime(matrix, p) for p in prime_factors(modulus)]
    n = len(matrix)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            x, current_mod = 0, 1
            for p, inv in zip(prime_factors(modulus), inverses):
                t = ((inv[i][j] - x) * pow(current_mod, -1, p)) % p
                x += current_mod * t
                current_mod *= p
            result[i][j] = x % modulus
    return result


def matrix_multiply(a, b, modulus):
    n, inner, cols = len(a), len(b), len(b[0])
    return [[sum(a[i][k] * b[k][j] for k in range(inner)) % modulus
             for j in range(cols)] for i in range(n)]


def blocks(values, size):
    return [values[i:i + size] for i in range(0, len(values), size)]


def make_language_table(alphabet, language="pl"):
    modulus = len(alphabet)
    if language == "pl":
        raw = PL_DEFAULT
    elif language == "en":
        raw = EN_DEFAULT
    else:
        raise ValueError("Model językowy musi być polski (pl) albo angielski (en).")

    sample = clean_text(raw, alphabet, linebreaks_as_spaces=True)
    if len(sample) < 4:
        raise ValueError("Wbudowany model językowy jest zbyt krótki.")

    counts = Counter(sample[i:i + 4] for i in range(len(sample) - 3))
    total = sum(counts.values())
    floor = math.log10(0.01 / total)
    table = np.full(modulus ** 4, floor, dtype=np.float32)
    index = {ch: i for i, ch in enumerate(alphabet)}
    for gram, count in counts.items():
        code = (((index[gram[0]] * modulus + index[gram[1]]) * modulus + index[gram[2]])
                * modulus + index[gram[3]])
        table[code] = math.log10(count / total)
    return table, len(sample)


def score_numbers(values, table, modulus):
    if len(values) < 4:
        return float("-inf")
    a = np.asarray(values, dtype=np.int64)
    codes = (((a[:-3] * modulus + a[1:-2]) * modulus + a[2:-1]) * modulus + a[3:])
    return float(table[codes].mean())


def generate_2x2_candidates(modulus, limit=None, seed=2026):
    if limit is None:
        candidates = []
        vals = np.arange(modulus, dtype=np.int16)
        for a, b, c in itertools.product(range(modulus), repeat=3):
            det = (a * vals - b * c) % modulus
            ds = vals[np.gcd(det, modulus) == 1]
            if len(ds):
                part = np.empty((len(ds), 4), dtype=np.int16)
                part[:, 0] = a
                part[:, 1] = b
                part[:, 2] = c
                part[:, 3] = ds
                candidates.append(part)
        return np.concatenate(candidates, axis=0)

    rng = np.random.default_rng(seed)
    found = []
    while sum(len(x) for x in found) < limit:
        batch = rng.integers(0, modulus, size=(max(5000, limit // 4), 4), dtype=np.int16)
        det = (batch[:, 0] * batch[:, 3] - batch[:, 1] * batch[:, 2]) % modulus
        good = batch[np.gcd(det, modulus) == 1]
        if len(good):
            found.append(good)
    return np.concatenate(found, axis=0)[:limit]


def score_2x2_candidates(cipher_values, candidates, table, modulus, chunk_size=256, top_n=80):
    values = np.asarray(cipher_values, dtype=np.int64)
    x, y = values[0::2], values[1::2]
    best = []
    for start in range(0, len(candidates), chunk_size):
        mats = candidates[start:start + chunk_size].astype(np.int64)
        a, b, c, d = (mats[:, i, None] for i in range(4))
        p0 = (a * x[None, :] + b * y[None, :]) % modulus
        p1 = (c * x[None, :] + d * y[None, :]) % modulus
        plain = np.empty((len(mats), 2 * len(x)), dtype=np.int64)
        plain[:, 0::2], plain[:, 1::2] = p0, p1
        codes = (((plain[:, :-3] * modulus + plain[:, 1:-2]) * modulus
                  + plain[:, 2:-1]) * modulus + plain[:, 3:])
        scores = table[codes].mean(axis=1)
        take = min(top_n, len(scores))
        ix = np.argpartition(scores, -take)[-take:]
        best.extend((float(scores[i]), tuple(map(int, mats[i]))) for i in ix)
        if len(best) > top_n * 4:
            best = sorted(best, reverse=True)[:top_n]
    return sorted(best, reverse=True)[:top_n]


def decrypt_values(cipher_values, matrix, size, modulus):
    arr = np.asarray(cipher_values, dtype=np.int64).reshape(-1, size)
    dec_matrix = np.asarray(matrix, dtype=np.int64)
    plain = (arr @ dec_matrix.T) % modulus
    return plain.reshape(-1).tolist()


def is_invertible(matrix, modulus):
    try:
        inverse_matrix_mod(matrix, modulus)
        return True
    except ValueError:
        return False


def random_invertible_matrix(size, modulus, rng):
    while True:
        matrix = [[rng.randrange(modulus) for _ in range(size)] for _ in range(size)]
        if is_invertible(matrix, modulus):
            return matrix


def anneal_size(cipher_values, size, modulus, table, restarts, iterations, seed):
    rng = random.Random(seed + size * 101 + modulus)
    sample = cipher_values[:min(len(cipher_values), 2400 - (2400 % size))]
    if len(sample) % size:
        sample = sample[:len(sample) - len(sample) % size]
    best_matrix, best_score = None, float("-inf")

    for _ in range(restarts):
        current = random_invertible_matrix(size, modulus, rng)
        current_plain = decrypt_values(sample, current, size, modulus)
        current_score = score_numbers(current_plain, table, modulus)
        for step in range(iterations):
            candidate = [row[:] for row in current]
            if rng.random() < 0.12:
                row = rng.randrange(size)
                candidate[row] = [rng.randrange(modulus) for _ in range(size)]
            else:
                row, col = rng.randrange(size), rng.randrange(size)
                candidate[row][col] = rng.randrange(modulus)
            if not is_invertible(candidate, modulus):
                continue
            candidate_plain = decrypt_values(sample, candidate, size, modulus)
            candidate_score = score_numbers(candidate_plain, table, modulus)
            temperature = 0.35 * (1 - step / max(1, iterations)) + 0.015
            if (candidate_score > current_score or
                    rng.random() < math.exp(min(0.0, (candidate_score - current_score) / temperature))):
                current, current_score = candidate, candidate_score
            if current_score > best_score:
                best_matrix, best_score = [row[:] for row in current], current_score
    return best_matrix, best_score


def ciphertext_only(cipher_values, modulus, table, max_size, restarts, iterations, logger, top_n=80):
    candidates_by_size = []
    for size in range(2, max_size + 1):
        if len(cipher_values) % size:
            logger.info("Pominięto rozmiar %d: długość szyfrogramu nie jest podzielna przez %d.", size, size)
            continue
        logger.info("Testowanie macierzy %dx%d.", size, size)
        if size == 2:
            candidates = generate_2x2_candidates(modulus, limit=None)
            search_values = cipher_values[:min(len(cipher_values), 3000 if modulus == 26 else 900)]
            search_values = search_values[:len(search_values) - len(search_values) % 2]
            ranked = score_2x2_candidates(search_values, candidates, table, modulus, top_n=top_n)
            for _, flat in ranked[:top_n]:
                dec_matrix = [[flat[0], flat[1]], [flat[2], flat[3]]]
                full_plain = decrypt_values(cipher_values, dec_matrix, 2, modulus)
                score = score_numbers(full_plain, table, modulus)
                candidates_by_size.append((score - 0.015 * size * size, score, size, dec_matrix))
        else:
            dec_matrix, _ = anneal_size(cipher_values, size, modulus, table, restarts, iterations, seed=2026)
            if dec_matrix is not None:
                full_plain = decrypt_values(cipher_values, dec_matrix, size, modulus)
                score = score_numbers(full_plain, table, modulus)
                candidates_by_size.append((score - 0.015 * size * size, score, size, dec_matrix))

    if not candidates_by_size:
        raise ValueError("Nie znaleziono rozmiaru macierzy zgodnego z długością szyfrogramu.")
    candidates_by_size.sort(reverse=True, key=lambda item: item[0])
    return candidates_by_size[0], candidates_by_size



def prepare_fragment_phase(fragment_values, size, modulus, phase, max_trials=256):
    """Przygotowuje pełne bloki tekstu jawnego dla danego wyrównania."""
    block_count = (len(fragment_values) - phase) // size
    if block_count < size:
        return None

    p_blocks = [
        fragment_values[phase + i * size:phase + (i + 1) * size]
        for i in range(block_count)
    ]
    total_combinations = math.comb(block_count, size)
    limit = min(4096, total_combinations)
    index_sets = list(itertools.islice(
        itertools.combinations(range(block_count), size), limit
    ))
    if total_combinations > limit:
        seen = set(index_sets)
        rng = random.Random(2026 + phase * 17 + size * 101 + modulus)
        target_trials = min(max_trials, total_combinations)
        while len(index_sets) < target_trials:
            sample = tuple(sorted(rng.sample(range(block_count), size)))
            if sample not in seen:
                seen.add(sample)
                index_sets.append(sample)

    for indices in index_sets:
        p_matrix = [[p_blocks[k][row] for k in indices] for row in range(size)]
        try:
            p_inverse = inverse_matrix_mod(p_matrix, modulus)
        except ValueError:
            continue
        return {
            "p_blocks": p_blocks,
            "indices": indices,
            "p_inverse": p_inverse,
            "block_count": block_count,
            "phase": phase,
        }
    return None


def recover_key_at_fragment_offset(cipher_values, start, size, modulus, phase_data):
    """Wyznacza i weryfikuje klucz z pełnych bloków fragmentu dla rozmiarów >= 3."""
    first_block = start + phase_data["phase"]
    indices = phase_data["indices"]
    c_matrix = [
        [cipher_values[first_block + k * size + row] for k in indices]
        for row in range(size)
    ]
    key = matrix_multiply(c_matrix, phase_data["p_inverse"], modulus)

    for block_index, p_block in enumerate(phase_data["p_blocks"]):
        block_start = first_block + block_index * size
        c_block = cipher_values[block_start:block_start + size]
        expected = [
            sum(key[row][col] * p_block[col] for col in range(size)) % modulus
            for row in range(size)
        ]
        if expected != c_block:
            return None
    return key, phase_data["block_count"]


def prepare_2x2_row_map(fragment_values, modulus, phase):
    """Tworzy odwzorowanie rzędu klucza na wartości szyfrogramu dla krótkich cribów."""
    block_count = (len(fragment_values) - phase) // 2
    if block_count < 2:
        return None
    p_blocks = [
        fragment_values[phase + i * 2:phase + (i + 1) * 2]
        for i in range(block_count)
    ]
    row_map = {}
    for a, b in itertools.product(range(modulus), repeat=2):
        signature = tuple((a * block[0] + b * block[1]) % modulus for block in p_blocks)
        row_map.setdefault(signature, []).append((a, b))
    return {"p_blocks": p_blocks, "row_map": row_map, "block_count": block_count, "phase": phase}


def fragment_matches_at(cipher_values, start, fragment_values, dec_matrix, size, modulus):
    """Sprawdza cały crib, łącznie ze znakami na granicach niepełnych bloków."""
    first_block = (start // size) * size
    end_block = min(len(cipher_values), ((start + len(fragment_values) + size - 1) // size) * size)
    cipher_segment = cipher_values[first_block:end_block]
    plain_segment = decrypt_values(cipher_segment, dec_matrix, size, modulus)
    offset = start - first_block
    return plain_segment[offset:offset + len(fragment_values)] == fragment_values


def candidate_language_scores(plain_values, language_tables, modulus):
    return {
        language: score_numbers(plain_values, table, modulus)
        for language, table in language_tables.items()
    }


def known_plaintext_fragment_attack(fragment_values, cipher_values, modulus, alphabet,
                                    max_size, language_choice, logger, restarts=3, iterations=700):
    """Szuka znanego słowa/fragmentu; najpierw rozwiązuje równania, potem używa cribu do filtrowania."""
    if not fragment_values:
        raise ValueError("Podany fragment tekstu jawnego jest pusty po normalizacji.")
    if len(fragment_values) > len(cipher_values):
        raise ValueError("Znany fragment jest dłuższy niż cały szyfrogram.")
    if len(fragment_values) < 3:
        raise ValueError("Fragment jest za krótki. Podaj co najmniej 3 znaki; najlepiej całe słowo lub kilka słów.")

    languages = ["pl", "en"] if language_choice == "auto" else [language_choice]
    language_tables = {}
    for language in languages:
        language_tables[language], _ = make_language_table(alphabet, language)

    found = {}
    inverse_cache = {}
    for size in range(2, max_size + 1):
        if len(cipher_values) % size:
            logger.info("Pominięto rozmiar %d: długość szyfrogramu nie jest podzielna przez %d.", size, size)
            continue

        logger.info("Szukanie znanego fragmentu dla macierzy %dx%d (mod %d).", size, size, modulus)
        phase_data = {}
        for phase in range(size):
            block_count = (len(fragment_values) - phase) // size
            if size == 2 and block_count <= 128:
                phase_data[phase] = prepare_2x2_row_map(fragment_values, modulus, phase)
            else:
                phase_data[phase] = prepare_fragment_phase(fragment_values, size, modulus, phase)

        usable_phases = [phase for phase, data in phase_data.items() if data is not None]
        if not usable_phases:
            logger.info(
                "Fragment nie zawiera %d pełnych bloków potrzebnych do bezpośredniego wyznaczenia klucza %dx%d.",
                size, size, size
            )
            continue

        max_start = len(cipher_values) - len(fragment_values)
        for start in range(max_start + 1):
            phase = (-start) % size
            prepared = phase_data[phase]
            if prepared is None:
                continue
            first_block = start + phase

            if size == 2 and "row_map" in prepared:
                row_map = prepared["row_map"]
                signatures = [
                    tuple(cipher_values[first_block + k * 2 + row]
                          for k in range(prepared["block_count"]))
                    for row in range(2)
                ]
                row_options = [row_map.get(signature, []) for signature in signatures]
                if not row_options[0] or not row_options[1]:
                    continue
                key_candidates = (
                    [[row0[0], row0[1]], [row1[0], row1[1]]]
                    for row0, row1 in itertools.product(*row_options)
                )
            else:
                result = recover_key_at_fragment_offset(cipher_values, start, size, modulus, prepared)
                if result is None:
                    continue
                key, _ = result
                key_candidates = [key]

            for key in key_candidates:
                key_id = (size, tuple(tuple(row) for row in key))
                if key_id not in inverse_cache:
                    try:
                        inverse_cache[key_id] = inverse_matrix_mod(key, modulus)
                    except ValueError:
                        inverse_cache[key_id] = None
                dec = inverse_cache[key_id]
                if dec is None:
                    continue
                if not fragment_matches_at(cipher_values, start, fragment_values, dec, size, modulus):
                    continue
                if key_id in found:
                    if start + 1 not in found[key_id]["offsets"]:
                        found[key_id]["offsets"].append(start + 1)
                    continue

                full_plain = decrypt_values(cipher_values, dec, size, modulus)
                full_scores = candidate_language_scores(full_plain, language_tables, modulus)
                selected_language = max(full_scores, key=full_scores.get)
                score = full_scores[selected_language]
                found[key_id] = {
                    "size": size,
                    "key": key,
                    "dec": dec,
                    "plain_values": full_plain,
                    "language": selected_language,
                    "score": score,
                    "adjusted": score - 0.015 * size * size,
                    "offsets": [start + 1],
                    "matched_blocks": prepared["block_count"],
                    "method": "direct-crib",
                }

    # Krótkie słowo może nie zawierać wystarczającej liczby pełnych bloków.
    # Wtedy używamy go jako filtra dla najlepszych kandydatów ze statystycznego ataku.
    if not found:
        logger.info(
            "Nie udało się wyznaczyć klucza wyłącznie z bloków znanego fragmentu. "
            "Uruchamiam wyszukiwanie statystyczne i sprawdzę, czy słowo występuje w odszyfrowaniu."
        )
        for language, table in language_tables.items():
            _, candidates = ciphertext_only(
                cipher_values, modulus, table, max_size, restarts, iterations, logger, top_n=400
            )
            for _, score, size, dec in candidates:
                plain_values = decrypt_values(cipher_values, dec, size, modulus)
                plain_text = numbers_to_text(plain_values, alphabet)
                plain_fragment = numbers_to_text(fragment_values, alphabet)
                position = plain_text.find(plain_fragment)
                if position < 0:
                    continue
                key = inverse_matrix_mod(dec, modulus)
                key_id = (size, tuple(tuple(row) for row in key))
                existing = found.get(key_id)
                adjusted = score - 0.015 * size * size
                if existing is None or adjusted > existing["adjusted"]:
                    found[key_id] = {
                        "size": size,
                        "key": key,
                        "dec": dec,
                        "plain_values": plain_values,
                        "language": language,
                        "score": score,
                        "adjusted": adjusted,
                        "offsets": [position + 1],
                        "matched_blocks": 0,
                        "method": "crib-filtered-statistical",
                    }

    if not found:
        raise ValueError(
            "Nie znaleziono odszyfrowania zawierającego podany fragment. Sprawdź alfabet i pisownię "
            "po normalizacji. Jeżeli podane jest tylko krótkie słowo (np. 3-4 litery), program musi "
            "najpierw znaleźć właściwy klucz metodą statystyczną, a następnie użyć słowa jako filtra. "
            "W takim przypadku zwiększ --restarts i --iterations albo podaj dłuższy fragment, "
            "najlepiej 8-15 znaków lub kilka słów."
        )

    candidates = sorted(found.values(), key=lambda item: item["adjusted"], reverse=True)
    for candidate in candidates[:5]:
        logger.info(
            "Kandydat %dx%d: język %s, ocena %.6f, pozycje fragmentu %s, metoda %s.",
            candidate["size"], candidate["size"], LANGUAGE_NAMES[candidate["language"]],
            candidate["score"], ", ".join(map(str, candidate["offsets"][:10])), candidate["method"]
        )
    if len(candidates) > 1 and abs(candidates[0]["adjusted"] - candidates[1]["adjusted"]) < 0.001:
        logger.warning("Znaleziono kilku podobnie ocenionych kandydatów; wynik może być niejednoznaczny.")

    best = candidates[0]
    details = (
        "Pozycja początku znanego fragmentu w odszyfrowanej wiadomości (liczenie od 1): "
        + ", ".join(map(str, best["offsets"])) + "\n"
        + f"Liczba pełnych bloków fragmentu wykorzystanych do odzyskania klucza: {best['matched_blocks']}\n"
        + f"Sposób odzyskania: {best['method']}\n"
        + "Położenie fragmentu zostało wyszukane automatycznie.\n"
    )
    return best, details, len(candidates)

def format_matrix(matrix):
    return "\n".join("[" + "  ".join(f"{x:2d}" for x in row) + "]" for row in matrix)


def display_symbol(symbol):
    return "[SPACJA]" if symbol == " " else symbol


def display_ngram(gram):
    return gram.replace(" ", "[SP]")


def normalize_reference_frequencies(language):
    values = LETTER_FREQUENCIES[language]
    total = sum(values.values())
    return {letter: value * 100.0 / total for letter, value in values.items()}


def format_letter_comparison(text, language):
    counts = Counter(ch for ch in text if ch in "abcdefghijklmnopqrstuvwxyz")
    total = sum(counts.values())
    lines = [
        "LITERY - PORÓWNANIE POSORTOWANYCH ROZKŁADÓW",
        f"Język odniesienia: {LANGUAGE_NAMES[language]}",
        "Pozycja | Tekst: litera | Tekst: procent | Język: litera | Język: procent",
        "Rankingi tekstu i języka są sortowane niezależnie, od największej częstości."
    ]
    if total == 0:
        lines.append("(brak liter A-Z do porównania)")
        return "\n".join(lines)

    reference = normalize_reference_frequencies(language)
    observed = {letter: counts[letter] / total * 100.0 for letter in "abcdefghijklmnopqrstuvwxyz"}
    text_order = sorted(observed, key=lambda letter: (-observed[letter], letter))
    language_order = sorted(reference, key=lambda letter: (-reference[letter], letter))
    for rank, (text_letter, language_letter) in enumerate(zip(text_order, language_order), start=1):
        lines.append(
            f"{rank:>3} | {text_letter} | {observed[text_letter]:.3f}% | "
            f"{language_letter} | {reference[language_letter]:.3f}%"
        )
    lines.append(f"Łączna liczba liter użyta do obliczenia procentów tekstu: {total}")
    lines.append("Liczby wystąpień poszczególnych liter są również dostępne w sekcji unigramów.")
    return "\n".join(lines)


def format_ngram_section(text, n, title):
    counts = Counter(text[i:i + n] for i in range(max(0, len(text) - n + 1)))
    total = max(0, len(text) - n + 1)
    lines = [title, "Wzorzec | Liczba wystąpień | Udział"]
    if not counts:
        lines.append("(brak danych)")
        return "\n".join(lines)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    if n in (2, 3):
        ordered = ordered[:5]
    for gram, count in ordered:
        percentage = count / total * 100 if total else 0.0
        label = display_symbol(gram) if n == 1 else display_ngram(gram)
        lines.append(f"{label} | {count} | {percentage:.4f}%")
    if n in (2, 3):
        lines.append("Pokazano 5 najczęstszych n-gramów.")
    return "\n".join(lines)


def create_statistics_report(cipher_text, plain_text, alphabet_name, language):
    alphabet = ALPHABETS[alphabet_name]
    sections = [
        "STATYSTYKI CZĘSTOTLIWOŚCI - SZYFR HILLA",
        f"Alfabet: {alphabet_name} (moduł {len(alphabet)})",
        f"Język odniesienia: {LANGUAGE_NAMES[language]}",
        "Częstości językowe dotyczą liter A-Z. W alfa37 spacje i cyfry są "
        "uwzględniane w unigramach i n-gramach, ale nie w porównaniu częstości liter.",
        "N-gramy liczone są z nakładaniem. W bigramach i trigramach pokazano "
        "wyłącznie 5 najczęstszych wzorców. [SP] oznacza spację.",
        "Tabela liter pokazuje dwa niezależne rankingi: badany tekst i język referencyjny, każdy od najczęstszej litery.",
        "Porównanie szyfrogramu z językiem jest poglądowe: szyfrowanie zmienia rozkład liter."
    ]
    for title, text in (("SZYFROGRAM", cipher_text), ("TEKST ODSZYFROWANY", plain_text)):
        sections.extend([
            "\n" + "=" * 72,
            title,
            "=" * 72,
            f"Liczba symboli: {len(text)}",
            f"Liczba liter A-Z: {sum(ch in 'abcdefghijklmnopqrstuvwxyz' for ch in text)}",
            f"Liczba spacji i cyfr: {sum(ch == ' ' or ch.isdigit() for ch in text)}",
            format_letter_comparison(text, language),
            "",
            format_ngram_section(text, 1, "UNIGRAMY - WSZYSTKIE WYSTĘPUJĄCE SYMBOLE"),
            "",
            format_ngram_section(text, 2, "BIGRAMY - 5 NAJCZĘSTSZYCH"),
            "",
            format_ngram_section(text, 3, "TRIGRAMY - 5 NAJCZĘSTSZYCH"),
        ])
    sections.extend([
        "\nŹRÓDŁA CZĘSTOŚCI REFERENCYJNYCH",
        "Polski: próbka drugiego wydania Korpusu IPI PAN (ok. 25 mln słów); "
        "polskie znaki diakrytyczne są sumowane z literami bazowymi, zgodnie z normalizacją programu.",
        "https://ckziumragowo.pl/szkolne-artykuly/2020/Cz%C4%99sto%C5%9B%C4%87-wyst%C4%99powania-liter-w-j%C4%99zyku-polskim",
        "Angielski: tabela względnych częstości liter - Emory University.",
        "https://math.oxford.emory.edu/site/math125/englishLetterFreqs/",
        "Wartości referencyjne są przybliżonym punktem odniesienia; rzeczywiste częstości zależą od rodzaju i tematyki tekstu."
    ])
    return "\n".join(sections) + "\n"


def write_statistics(output_dir, cipher_text, plain_text, alphabet_name, language):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = create_statistics_report(cipher_text, plain_text, alphabet_name, language)
    (output_dir / "statystyki.txt").write_text(report, encoding="utf-8")
    return report


def write_outputs(output_dir, plain_text, key_matrix, dec_matrix, size, alphabet_name,
                  method, score=None, details=""):

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "odszyfrowana_wiadomosc.txt").write_text(plain_text.lower(), encoding="utf-8")
    key_text = (
        f"Alfabet: {alphabet_name} (mod {len(ALPHABETS[alphabet_name])})\n"
        f"Rozmiar macierzy: {size}x{size}\n"
        f"Metoda: {method}\n"
        + (f"Ocena statystyczna: {score:.6f}\n" if score is not None else "")
        + ("\n" + details if details else "")
        + "\nKlucz szyfrujący K:\n" + format_matrix(key_matrix)
        + "\n\nMacierz deszyfrująca K^(-1):\n" + format_matrix(dec_matrix) + "\n"
    )
    (output_dir / "klucz.txt").write_text(key_text, encoding="utf-8")


def setup_logger(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("hill")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(output_dir / "log.txt", mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger


def read_plaintext_from_console(subject="znany fragment"):
    print(f"Wpisz {subject} w jednej linii i naciśnij Enter.")
    return input()


def choose_plaintext_source(subject="znanego fragmentu"):
    print(f"Sposób podania {subject}:")
    print("1 - wpisz słowo lub fragment w jednej linii i naciśnij Enter")
    print("2 - wklej tekst wielowierszowy (zakończ słowem KONIEC w osobnym wierszu)")
    print("3 - podaj ścieżkę do pliku tekstowego")
    choice = input("Wybierz [1/2/3]: ").strip()
    if choice == "1":
        return None, read_plaintext_from_console("znany fragment")
    if choice == "2":
        return None, read_multiline_fragment_from_console()
    if choice == "3":
        path = input("Ścieżka do pliku ze znanym fragmentem: ").strip().strip('"')
        return path, None
    raise ValueError("Nieprawidłowy wybór sposobu podania fragmentu.")


def read_multiline_fragment_from_console():
    print("Wklej tekst. Aby zakończyć, wpisz KONIEC w osobnym wierszu:")
    lines = []
    while True:
        line = sys.stdin.readline()
        if line == "":
            break
        if line.rstrip("\r\n").strip().upper() == "KONIEC":
            break
        lines.append(line)
    return "".join(lines).rstrip("\r\n")


def interactive_args(base_args=None):
    print("Kryptoanaliza szyfru Hilla")
    print("1 - sam szyfrogram (atak statystyczny, bez tekstu wzorcowego)")
    print("2 - znany fragment tekstu jawnego (automatyczne szukanie i weryfikacja)")
    choice = input("Wybierz tryb [1/2]: ").strip()
    modes = {"1": "ciphertext", "2": "known-fragment"}
    if choice not in modes:
        raise ValueError("Nieprawidłowy wybór trybu.")
    mode = modes[choice]
    cipher = input("Ścieżka do pliku z szyfrogramem: ").strip().strip('"')
    default_alphabet = getattr(base_args, "alphabet", "alfa26")
    alphabet = input(f"Alfabet [alfa26/alfa37] (domyślnie {default_alphabet}): ").strip().lower() or default_alphabet
    plain = None
    plain_text = None
    if mode == "known-fragment":
        plain, plain_text = choose_plaintext_source("znanego fragmentu")
    return argparse.Namespace(
        ciphertext=cipher, alphabet=alphabet, mode=mode, plaintext=plain,
        plaintext_text=plain_text,
        language=getattr(base_args, "language", "auto"),
        max_size=getattr(base_args, "max_size", 5),
        restarts=getattr(base_args, "restarts", 3),
        iterations=getattr(base_args, "iterations", 700),
        output=getattr(base_args, "output", ".")
    )


def main():
    parser = argparse.ArgumentParser(description="Kryptoanaliza szyfru Hilla: alfa26/alfa37, atak na szyfrogram lub ze znanym fragmentem.")
    parser.add_argument("-c", "--ciphertext", help="Plik z szyfrogramem.")
    parser.add_argument("-a", "--alphabet", choices=ALPHABETS, default="alfa26")
    parser.add_argument("-m", "--mode", choices=["ciphertext", "known-fragment"],
                        default="ciphertext")
    plain_group = parser.add_mutually_exclusive_group()
    plain_group.add_argument("-p", "--plaintext",
                             help="Plik zawierający znany fragment tekstu jawnego (tryb known-fragment).")
    plain_group.add_argument("--plaintext-text",
                             help="Znany fragment tekstu jawnego przekazany jako argument.")
    parser.add_argument("--language", choices=["auto", "pl", "en"], default="auto",
                        help="Język modelu statystycznego; domyślnie auto (porównanie polskiego i angielskiego).")
    parser.add_argument("--max-size", type=int, default=5, help="Maksymalny testowany rozmiar macierzy.")
    parser.add_argument("--restarts", type=int, default=3, help="Liczba startów dla rozmiarów >= 3.")
    parser.add_argument("--iterations", type=int, default=700, help="Liczba iteracji na start dla rozmiarów >= 3.")
    parser.add_argument("-o", "--output", default=".", help="Folder plików wynikowych.")
    args = parser.parse_args()
    if not args.ciphertext:
        args = interactive_args(args)
    elif args.mode == "known-fragment" and not args.plaintext and not args.plaintext_text:
        args.plaintext, args.plaintext_text = choose_plaintext_source("znanego fragmentu")

    logger = setup_logger(args.output)
    try:
        if args.alphabet not in ALPHABETS:
            raise ValueError("Nieznany alfabet. Wybierz alfa26 lub alfa37.")
        if args.max_size < 2 or args.max_size > 8:
            raise ValueError("Maksymalny rozmiar macierzy musi należeć do zakresu 2-8.")
        alphabet = ALPHABETS[args.alphabet]
        modulus = len(alphabet)
        cipher_raw = Path(args.ciphertext).read_text(encoding="utf-8", errors="replace")
        cipher = clean_text(cipher_raw, alphabet)
        if len(cipher) < 8:
            raise ValueError("Szyfrogram po oczyszczeniu jest zbyt krótki.")
        cipher_values = text_to_numbers(cipher, alphabet)
        logger.info("Plik szyfrogramu: %s", args.ciphertext)
        logger.info("Alfabet: %s, moduł: %d, liczba symboli: %d", args.alphabet, modulus, len(cipher))

        if args.mode == "known-fragment":
            if args.plaintext_text is not None:
                fragment_raw = args.plaintext_text
                logger.info("Znany fragment tekstu jawnego podano bezpośrednio.")
            elif args.plaintext:
                fragment_raw = Path(args.plaintext).read_text(encoding="utf-8", errors="replace")
                logger.info("Plik ze znanym fragmentem tekstu jawnego: %s", args.plaintext)
            else:
                raise ValueError("W trybie known-fragment podaj fragment w konsoli albo przez --plaintext.")
            fragment = clean_text(fragment_raw, alphabet, linebreaks_as_spaces=True)
            best, details, candidate_count = known_plaintext_fragment_attack(
                text_to_numbers(fragment, alphabet), cipher_values, modulus, alphabet,
                args.max_size, args.language, logger, args.restarts, args.iterations
            )
            size = best["size"]
            key, dec = best["key"], best["dec"]
            text = numbers_to_text(best["plain_values"], alphabet)
            detected_language = best["language"]
            write_outputs(args.output, text, key, dec, size, args.alphabet,
                          "known-plaintext-fragment", best["score"], details)
            logger.info(
                "Odzyskano klucz na podstawie znanego fragmentu: macierz %dx%d; "
                "język odniesienia: %s; liczba różnych kandydatów: %d.",
                size, size, LANGUAGE_NAMES[detected_language], candidate_count
            )
        else:
            languages = ["pl", "en"] if args.language == "auto" else [args.language]
            language_results = []
            for language in languages:
                table, model_len = make_language_table(alphabet, language)
                logger.info("Ocena kandydatów z wbudowanym modelem języka: %s (%d znaków).",
                            "polski" if language == "pl" else "angielski", model_len)
                best_for_language, candidates_for_language = ciphertext_only(
                    cipher_values, modulus, table, args.max_size, args.restarts, args.iterations, logger
                )
                language_results.append((best_for_language, candidates_for_language, language))

            best, all_candidates, detected_language = max(
                language_results, key=lambda item: item[0][0]
            )
            _, score, size, dec = best
            key = inverse_matrix_mod(dec, modulus)
            decrypted = decrypt_values(cipher_values, dec, size, modulus)
            text = numbers_to_text(decrypted, alphabet)
            write_outputs(args.output, text, key, dec, size, args.alphabet,
                          f"ciphertext-only (atak statystyczny, model: {detected_language})", score)
            logger.info("Najlepszy model językowy: %s.",
                        "polski" if detected_language == "pl" else "angielski")
            logger.info("Najlepszy kandydat: rozmiar %dx%d, wynik %.6f.", size, size, score)
            for adjusted, candidate_score, candidate_size, _ in all_candidates[:5]:
                logger.info("Kandydat %dx%d: wynik %.6f (z korektą %.6f).",
                            candidate_size, candidate_size, candidate_score, adjusted)
            logger.warning("To wynik heurystyczny. Sprawdź, czy odszyfrowany tekst jest czytelny.")

        statistics_report = write_statistics(args.output, cipher, text, args.alphabet, detected_language)
        logger.info("Zapisano: odszyfrowana_wiadomosc.txt, klucz.txt oraz statystyki.txt.")
        logger.info("Log zapisano w: %s", Path(args.output) / "log.txt")
        print("\n" + statistics_report)
        print("Zakończono. Wyniki zapisano w folderze:", Path(args.output).resolve())
    except Exception as exc:
        logger.exception("Błąd: %s", exc)
        print("BŁĄD:", exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
