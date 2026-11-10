#!/usr/bin/env python3
"""Kryptoanaliza szyfru Vigenere'a dla alfabetow alfa26 i alfa37."""

from __future__ import annotations

import logging
import math
from collections import Counter, defaultdict
from pathlib import Path

ALPHABETS = {
    "26": "abcdefghijklmnopqrstuvwxyz",
    "37": "abcdefghijklmnopqrstuvwxyz0123456789 ",
}

ENGLISH = [
    .08167,.01492,.02782,.04253,.12702,.02228,.02015,.06094,.06966,
    .00153,.00772,.04025,.02406,.06749,.07507,.01929,.00095,.05987,
    .06327,.09056,.02758,.00978,.02360,.00150,.01974,.00074
]
POLISH = [
    .0999,.0148,.0444,.0329,.0905,.0031,.0138,.0107,.0829,.0234,
    .0341,.0389,.0291,.0579,.0841,.0310,.00003,.0457,.0494,.0397,
    .0235,.0003,.0455,.0002,.0386,.0657
]

def make_profile(letters: list[float], alphabet: str) -> list[float]:
    if len(alphabet) == 26:
        total = sum(letters)
        return [x / total for x in letters]
    # Spacja jest częsta, cyfry występują rzadziej niż litery.
    digit_frequency = 0.0005
    space_frequency = 0.18
    letter_scale = (1.0 - space_frequency - 10 * digit_frequency) / sum(letters)
    values = [x * letter_scale for x in letters]
    values += [digit_frequency] * 10
    values += [space_frequency]
    return values

def normalize(text: str, alphabet: str) -> str:
    text = text.lower().translate(str.maketrans(
        "ąćęłńóśźż", "acelnoszz"
    ))
    allowed = set(alphabet)
    return "".join(c for c in text if c in allowed)

def indices(text: str, alphabet: str) -> list[int]:
    mapping = {c: i for i, c in enumerate(alphabet)}
    return [mapping[c] for c in text]

def from_indices(values: list[int], alphabet: str) -> str:
    n = len(alphabet)
    return "".join(alphabet[x % n] for x in values)

def encrypt(plain: str, key: str, alphabet: str) -> str:
    p, k = indices(plain, alphabet), indices(key, alphabet)
    if not k:
        raise ValueError("Klucz nie może być pusty.")
    n = len(alphabet)
    return from_indices([(x + k[i % len(k)]) % n for i, x in enumerate(p)], alphabet)

def decrypt(cipher: str, key: str, alphabet: str) -> str:
    c, k = indices(cipher, alphabet), indices(key, alphabet)
    if not k:
        raise ValueError("Klucz nie może być pusty.")
    n = len(alphabet)
    return from_indices([(x - k[i % len(k)]) % n for i, x in enumerate(c)], alphabet)

def ic(text: str) -> float:
    n = len(text)
    if n < 2:
        return 0.0
    counts = Counter(text)
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))

def mean_column_ic(text: str, length: int) -> float:
    columns = [text[i::length] for i in range(length)]
    values = [ic(col) for col in columns if len(col) > 1]
    return sum(values) / len(values) if values else 0.0

def kasiski(text: str, max_length: int) -> Counter:
    votes = Counter()
    for size in (3, 4, 5):
        positions = defaultdict(list)
        for i in range(len(text) - size + 1):
            positions[text[i:i + size]].append(i)
        for places in positions.values():
            for a, b in zip(places, places[1:]):
                distance = b - a
                for divisor in range(2, max_length + 1):
                    if distance % divisor == 0:
                        votes[divisor] += size - 2
    return votes

def length_ranking(text: str, alphabet: str, profiles: dict[str, list[float]],
                   max_length: int) -> list[dict]:
    votes = kasiski(text, max_length)
    max_votes = max(votes.values(), default=1)
    expected_ics = [sum(x*x for x in f) for f in profiles.values()]
    rows = []
    for length in range(1, max_length + 1):
        observed = mean_column_ic(text, length)
        fit = max(math.exp(-abs(observed - target) / .012)
                  for target in expected_ics)
        kasiski_fit = votes[length] / max_votes
        score = .75 * fit + .25 * kasiski_fit - .001 * length
        rows.append({"length": length, "ic": observed,
                     "votes": votes[length], "score": score,
                     "symbols_per_column": len(text) / length})
    return sorted(rows, key=lambda x: x["score"], reverse=True)

def chi_square(column: str, shift: int, alphabet: str,
               frequencies: list[float]) -> float:
    n = len(alphabet)
    counts = [0] * n
    mapping = {c: i for i, c in enumerate(alphabet)}
    for char in column:
        counts[(mapping[char] - shift) % n] += 1
    total = len(column)
    return sum((counts[i] - total * frequencies[i]) ** 2 /
               (total * frequencies[i] + 1e-12) for i in range(n))

def initial_key(text: str, length: int, alphabet: str,
                frequencies: list[float]) -> list[int]:
    n = len(alphabet)
    key = []
    for offset in range(length):
        column = text[offset::length]
        key.append(min(range(n), key=lambda s:
                       chi_square(column, s, alphabet, frequencies)))
    return key

def reduce_key(key: list[int]) -> list[int]:
    for period in range(1, len(key) + 1):
        if len(key) % period == 0 and all(
            key[i] == key[i % period] for i in range(len(key))
        ):
            return key[:period]
    return key

def language_score(text: str, frequencies: list[float],
                   alphabet: str) -> float:
    if not text:
        return float("-inf")
    mapping = {c: i for i, c in enumerate(alphabet)}
    return sum(math.log(frequencies[mapping[c]] + 1e-12)
               for c in text) / len(text)

def ciphertext_attack(text: str, alphabet: str, profiles: dict[str, list[float]],
                      max_length: int) -> tuple[dict, list[dict], list[dict]]:
    ranking = length_ranking(text, alphabet, profiles, max_length)
    candidates = []
    for row in ranking[:min(12, len(ranking))]:
        tested_length = row["length"]
        for language, frequencies in profiles.items():
            key = initial_key(text, tested_length, alphabet, frequencies)
            key = reduce_key(key)
            plain = decrypt(text, from_indices(key, alphabet), alphabet)
            score = language_score(plain, frequencies, alphabet)
            candidates.append({
                "key_values": key, "key": from_indices(key, alphabet),
                "plaintext": plain, "language": language,
                "length": len(key), "tested_length": tested_length,
                "score": score, "position": None
            })
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[0], candidates, ranking

def crib_attack(text: str, crib: str, alphabet: str, profiles: dict[str, list[float]],
                max_length: int, position: int | None) -> tuple[dict | None, list[dict]]:
    """Odzyskuje kandydatow klucza na podstawie znanego fragmentu.

    Oprocz oceny jezykowej wykorzystuje liczbe powtorzonych ograniczen:
    jesli fragment ma dlugosc q, a badany okres klucza r, to dla r < q
    kolejne znaki fragmentu musza ponownie wskazywac te same symbole klucza.
    Takie zgodnosci sa znacznie silniejszym dowodem niz sama ocena czestosci.
    """
    if len(crib) > len(text):
        raise ValueError("Fragment jest dłuższy niż szyfrogram.")
    offsets = [position] if position is not None else range(len(text) - len(crib) + 1)
    mapping = {c: i for i, c in enumerate(alphabet)}
    n = len(alphabet)
    candidates_by_identity = {}

    for offset in offsets:
        if offset < 0 or offset + len(crib) > len(text):
            continue
        for tested_length in range(1, min(max_length, len(crib)) + 1):
            key = [None] * tested_length
            valid = True
            repeated_checks = 0
            for j, pchar in enumerate(crib):
                shift = (mapping[text[offset + j]] - mapping[pchar]) % n
                slot = (offset + j) % tested_length
                if key[slot] is not None:
                    repeated_checks += 1
                    if key[slot] != shift:
                        valid = False
                        break
                else:
                    key[slot] = shift
            if not valid or any(value is None for value in key):
                continue

            full_key = [int(value) for value in key]
            reduced_key = reduce_key(full_key)
            key_text = from_indices(reduced_key, alphabet)
            plain = decrypt(text, key_text, alphabet)
            identity = (offset, key_text)
            # Przy krótkim lub częściowo uszkodzonym szyfrogramie cały tekst
            # może zdominować ocenę języka. Oceniajmy lokalny kontekst znanego
            # fragmentu, który jest najbardziej wiarygodną częścią odszyfrowania.
            context_start = max(0, offset - 24)
            language_sample = plain[context_start:offset + len(crib)]

            for language, frequencies in profiles.items():
                candidate = {
                    "key_values": reduced_key,
                    "key": key_text,
                    "plaintext": plain,
                    "language": language,
                    "length": len(reduced_key),
                    "tested_length": tested_length,
                    "score": language_score(language_sample, frequencies, alphabet),
                    "language_sample": language_sample,
                    "position": offset,
                    "repeated_checks": repeated_checks,
                }
                old = candidates_by_identity.get(identity)
                # Zachowujemy najdłuższy dowód zgodności dla danego położenia i klucza.
                if old is None or repeated_checks > old["repeated_checks"]:
                    candidates_by_identity[identity] = candidate
                elif repeated_checks == old["repeated_checks"] and candidate["score"] > old["score"]:
                    candidates_by_identity[identity] = candidate

    candidates = list(candidates_by_identity.values())
    # Najpierw liczba niezależnych powtórzeń klucza, dopiero potem ocena językowa.
    candidates.sort(key=lambda item: (item["repeated_checks"], item["score"]), reverse=True)
    return (candidates[0] if candidates else None), candidates

def setup_log(path: Path) -> logging.Logger:
    logger = logging.getLogger("vigenere37")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    return logger

def main() -> None:
    print("Kryptoanaliza szyfru Vigenere'a")
    filename = input("Nazwa pliku z szyfrogramem: ").strip().strip('"')
    path = Path(filename)
    if not path.is_file():
        print("Nie znaleziono pliku.")
        return
    alphabet_choice = input("Alfabet: 26 czy 37? [26/37]: ").strip() or "26"
    if alphabet_choice not in ALPHABETS:
        print("Nieprawidłowy alfabet.")
        return
    alphabet = ALPHABETS[alphabet_choice]
    raw = path.read_text(encoding="utf-8-sig")
    cipher = normalize(raw, alphabet)
    if len(cipher) < 10:
        print("Szyfrogram jest zbyt krótki.")
        return
    profiles = {
        "angielski": make_profile(ENGLISH, alphabet),
        "polski": make_profile(POLISH, alphabet)
    }
    log_path = path.with_name(path.stem + "_log.txt")
    logger = setup_log(log_path)
    logger.info("Plik: %s; alfabet: alfa%s; długość: %d",
                path, alphabet_choice, len(cipher))
    print(f"Wczytano {len(cipher)} symboli.")
    print("1. Atak bez tekstu jawnego")
    print("2. Znany fragment i znana pozycja")
    print("3. Znany fragment i nieznana pozycja")
    choice = input("Wybór [1-3]: ").strip()
    max_length = min(60, max(1, len(cipher)//2))
    answer = input(f"Maksymalna długość klucza [{min(30,max_length)}]: ").strip()
    if answer:
        max_length = min(max_length, max(1, int(answer)))
    if choice == "1":
        best, candidates, ranking = ciphertext_attack(
            cipher, alphabet, profiles, max_length)
        print("Najlepsze długości:", [(x["length"], round(x["score"],4))
              for x in ranking[:8]])
        logger.info("Ranking długości: %s", ranking[:15])
    elif choice in {"2", "3"}:
        crib = normalize(input("Znany fragment tekstu jawnego: "), alphabet)
        if not crib:
            print("Pusty fragment.")
            return
        position = None
        if choice == "2":
            position = int(input("Pozycja fragmentu (indeks od 0): "))
        best, candidates = crib_attack(
            cipher, crib, alphabet, profiles, max_length, position)
        if best is None:
            print("Nie znaleziono zgodnego klucza. Fragment powinien obejmować co najmniej jeden pełny okres klucza.")
            return
        baseline, _, ranking = ciphertext_attack(
            cipher, alphabet, profiles, max_length)
        best["baseline"] = baseline
        print("Znaleziono kandydatów (położenie i klucz):", len(candidates))
        print("Najlepsze położenie fragmentu (indeks od 0):", best["position"])
        print("Odzyskany klucz:", repr(best["key"]))
        print("Długość odzyskanego klucza:", best["length"])
        print("Liczba zgodnych powtórzeń klucza:", best["repeated_checks"])
        if best["repeated_checks"] >= 4:
            print("Siła dopasowania fragmentu: mocna")
        elif best["repeated_checks"] >= 2:
            print("Siła dopasowania fragmentu: umiarkowana")
        else:
            print("Siła dopasowania fragmentu: słaba — wynik wymaga dodatkowej weryfikacji")
        print("Klucz z ataku statystycznego (wynik porównawczy):", repr(baseline["key"]))
        print("Zgodność kluczy:", best["key"] == baseline["key"])
        print("Uwaga: ranking ataku z fragmentem opiera się najpierw na liczbie zgodnych powtórzeń klucza. Ocena częstości językowych jest tylko kryterium pomocniczym.")
        logger.info("Atak z fragmentem: %s", best)
        logger.info("Najlepsi kandydaci z fragmentu: %s", candidates[:10])
        logger.info("Atak statystyczny: %s", baseline)
    else:
        print("Nieprawidłowy wybór.")
        return
    plain_path = path.with_name(path.stem + "_odszyfrowany.txt")
    key_path = path.with_name(path.stem + "_klucz.txt")
    plain_path.write_text(best["plaintext"] + "\n", encoding="utf-8")
    key_path.write_text(
        f"Klucz: {best['key']!r}\nDługość: {best['length']}\n"
        f"Język: {best['language']}\nMetoda: {choice}\n",
        encoding="utf-8")
    logger.info("Wynik: klucz=%r; długość=%d; język=%s; ocena=%.6f",
                best["key"], best["length"], best["language"], best["score"])
    logger.info("Zapisano: %s oraz %s", plain_path, key_path)
    print("Język:", best["language"])
    print("Klucz:", repr(best["key"]))
    print("Początek tekstu:", repr(best["plaintext"][:160]))
    print("Zapisano:", plain_path, key_path, log_path)

if __name__ == "__main__":
    main()
