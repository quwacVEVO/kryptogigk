import os
import time
from itertools import count, product
from vigenere import decrypt, ALPHABET

ABC_ALFA26 = ALPHABET
ABC_ALFA37 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

FREQ = {
    "pl": {
        "A": 9.90, "B": 1.47, "C": 4.36, "D": 3.25, "E": 8.77, "F": 0.30,
        "G": 1.42, "H": 1.08, "I": 8.21, "J": 2.28, "K": 3.51, "L": 3.92,
        "M": 2.80, "N": 5.72, "O": 8.60, "P": 3.13, "Q": 0.00, "R": 4.69,
        "S": 4.98, "T": 3.98, "U": 2.50, "V": 0.00, "W": 4.65, "X": 0.00,
        "Y": 3.76, "Z": 6.53,
    },
    "en": {
        "A": 8.167, "B": 1.492, "C": 2.782, "D": 4.253, "E": 12.702, "F": 2.228,
        "G": 2.015, "H": 6.094, "I": 6.966, "J": 0.153, "K": 0.772, "L": 4.025,
        "M": 2.406, "N": 6.749, "O": 7.507, "P": 1.929, "Q": 0.095, "R": 5.987,
        "S": 6.327, "T": 9.056, "U": 2.758, "V": 0.978, "W": 2.360, "X": 0.150,
        "Y": 1.974, "Z": 0.074,
    },
}

FREQ_ALFA26 = {
    "pl": {
        "A": 9.787, "B": 1.478, "C": 4.352, "D": 3.335, "E": 8.464, "F": 0.519,
        "G": 1.686, "H": 1.609, "I": 8.250, "J": 2.022, "K": 3.254, "L": 4.261,
        "M": 2.669, "N": 6.010, "O": 8.467, "P": 3.183, "Q": 0.035, "R": 4.947,
        "S": 5.366, "T": 4.409, "U": 2.359, "V": 0.204, "W": 4.402, "X": 0.087,
        "Y": 3.449, "Z": 5.398,
    },
    "en": {
        "A": 8.173, "B": 1.814, "C": 3.631, "D": 4.012, "E": 11.447, "F": 2.055,
        "G": 2.182, "H": 4.822, "I": 7.298, "J": 0.296, "K": 0.697, "L": 4.241,
        "M": 2.786, "N": 6.894, "O": 7.346, "P": 2.560, "Q": 0.133, "R": 6.849,
        "S": 6.537, "T": 8.370, "U": 2.666, "V": 1.216, "W": 1.954, "X": 0.233,
        "Y": 1.667, "Z": 0.123,
    },
}

FREQ_ALFA37 = {
    "pl": {
        " ": 12.503, "A": 8.096, "B": 1.222, "C": 3.600, "D": 2.758, "E": 7.001,
        "F": 0.429, "G": 1.395, "H": 1.331, "I": 6.824, "J": 1.673, "K": 2.692,
        "L": 3.524, "M": 2.208, "N": 4.971, "O": 7.003, "P": 2.633, "Q": 0.029,
        "R": 4.092, "S": 4.439, "T": 3.647, "U": 1.951, "V": 0.169, "W": 3.642,
        "X": 0.072, "Y": 2.853, "Z": 4.465, "0": 0.809, "1": 0.894, "2": 0.673,
        "3": 0.367, "4": 0.355, "5": 0.332, "6": 0.309, "7": 0.304, "8": 0.316,
        "9": 0.420,
    },
    "en": {
        " ": 14.129, "A": 6.443, "B": 1.430, "C": 2.862, "D": 3.163, "E": 9.024,
        "F": 1.620, "G": 1.720, "H": 3.801, "I": 5.753, "J": 0.234, "K": 0.549,
        "L": 3.343, "M": 2.196, "N": 5.435, "O": 5.791, "P": 2.018, "Q": 0.104,
        "R": 5.400, "S": 5.154, "T": 6.598, "U": 2.101, "V": 0.958, "W": 1.541,
        "X": 0.183, "Y": 1.314, "Z": 0.097, "0": 1.245, "1": 1.346, "2": 1.136,
        "3": 0.534, "4": 0.453, "5": 0.445, "6": 0.430, "7": 0.442, "8": 0.471,
        "9": 0.535,
    },
}

BRUTE_THRESHOLD = 0.2


def chi2(text, lang):
    n = len(text)
    total = 0
    for letter, f in FREQ[lang].items():
        expected = n * max(f, 0.1) / 100
        total += (text.count(letter) - expected) ** 2 / expected
    return total


def ic(text):
    n = len(text)
    return sum(text.count(c) * (text.count(c) - 1) for c in ABC) / (n * (n - 1))


def key_length(ct, max_len=30):
    scores = {k: sum(ic(ct[i::k]) for i in range(k)) / k for k in range(1, max_len + 1)}
    best = max(scores.values())
    return next(k for k, s in scores.items() if s > 0.9 * best), scores


def find_key(ct, k, lang):
    return "".join(
        min(ABC, key=lambda c: chi2(decrypt(ct[i::k], c, alphabet=ABC), lang)) for i in range(k)
    )


def brute_force(ct, lang):
    for length in count(1):
        best_key, best_score = None, float("inf")
        for letters in product(ABC, repeat=length):
            key = "".join(letters)
            score = chi2(decrypt(ct, key, alphabet=ABC), lang)
            if score < best_score:
                best_key, best_score = key, score
        if best_score / len(ct) < BRUTE_THRESHOLD:
            return best_key


if __name__ == "__main__":
    path = input("Nazwa pliku z szyfrogramem: ").strip()
    lang = input("Język tekstu (pl/en): ").strip() or "pl"
    mode = input("Alfabet (1 - alfa26, 2 - alfa37): ").strip()
    method = input("Metoda (1 - statystyczna, 2 - brute force): ").strip()

    if mode == "2":
        FREQ = FREQ_ALFA37
        ABC = ABC_ALFA37
    else:
        FREQ = FREQ_ALFA26
        ABC = ABC_ALFA26

    start_time = time.perf_counter()

    ct = open(f"{lang}/{path}", encoding="utf-8").read().strip()

    if method == "2":
        name = "bruteforce"
        key = brute_force(ct, lang)
    else:
        name = "statystyczna"
        k, scores = key_length(ct)
        print("Średnie IC:", {n: round(s, 4) for n, s in scores.items()})
        print("Długość klucza:", k)
        key = find_key(ct, k, lang)

    folder = os.path.join("test", "decrypted", lang)
    os.makedirs(folder, exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(folder, f"{base}_odszyfrowany_{name}.txt")
    open(out, "w", encoding="utf-8").write(decrypt(ct, key, alphabet=ABC))
    print("Klucz:", key)
    print("Zapisano:", out)
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Czas wykonania: {elapsed_time:.4f} sekund")
