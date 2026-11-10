import os
import sys
import math
from collections import Counter
from typing import Dict, List, Tuple, Optional

FREQ_EN: Dict[str, float] = {
    'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253, 'E': 0.12702,
    'F': 0.02228, 'G': 0.02015, 'H': 0.06094, 'I': 0.06966, 'J': 0.00153,
    'K': 0.00772, 'L': 0.04025, 'M': 0.02406, 'N': 0.06749, 'O': 0.07507,
    'P': 0.01929, 'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
    'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150, 'Y': 0.01974,
    'Z': 0.00074
}

FREQ_PL: Dict[str, float] = {
    'A': 0.09900, 'B': 0.01470, 'C': 0.04360, 'D': 0.03250, 'E': 0.08770,
    'F': 0.00300, 'G': 0.01420, 'H': 0.01080, 'I': 0.08210, 'J': 0.02280,
    'K': 0.03510, 'L': 0.03920, 'M': 0.02800, 'N': 0.05720, 'O': 0.08600,
    'P': 0.03130, 'Q': 0.00005, 'R': 0.04690, 'S': 0.04920, 'T': 0.03980,
    'U': 0.02500, 'V': 0.00040, 'W': 0.04650, 'X': 0.00020, 'Y': 0.03760,
    'Z': 0.07340
}

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFA37 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "


def build_freq_alfa37(base_freq: Dict[str, float]) -> Dict[str, float]:
    freq = {}
    for c in ALFA26:
        freq[c] = base_freq[c] * 0.82
    freq[' '] = 0.160
    for d in "0123456789":
        freq[d] = 0.020 / 10.0
    return freq


def clean_text(raw_text: str, alphabet: str) -> str:
    raw_upper = raw_text.upper()
    return "".join(c for c in raw_upper if c in alphabet)


def index_of_coincidence(text: str, alphabet_len: int = 26) -> float:
    n = len(text)
    if n <= 1:
        return 0.0
    counts = Counter(text)
    num = sum(f * (f - 1) for f in counts.values())
    return num / (n * (n - 1))


def kasiski_examination(text: str, min_len: int = 3, max_len: int = 5) -> Tuple[Dict[str, List[int]], Dict[int, int]]:
    repeats: Dict[str, List[int]] = {}
    n = len(text)

    for length in range(min_len, max_len + 1):
        pos_dict: Dict[str, List[int]] = {}
        for i in range(n - length + 1):
            gram = text[i:i + length]
            pos_dict.setdefault(gram, []).append(i)
        for gram, positions in pos_dict.items():
            if len(positions) > 1:
                repeats[gram] = positions

    factor_counts: Dict[int, int] = {}
    for gram, positions in repeats.items():
        for i in range(len(positions) - 1):
            dist = positions[i + 1] - positions[i]
            for f in range(2, 31):
                if dist % f == 0:
                    factor_counts[f] = factor_counts.get(f, 0) + 1

    return repeats, factor_counts


def average_column_ic(text: str, k: int, alphabet_len: int) -> float:
    total_ic = 0.0
    for i in range(k):
        subseq = text[i::k]
        total_ic += index_of_coincidence(subseq, alphabet_len)
    return total_ic / k


def estimate_key_length(text: str, alphabet_len: int, max_k: int = 30) -> List[Tuple[int, float, int]]:
    effective_max_k = min(max_k, max(2, len(text) // 7))
    _, factor_counts = kasiski_examination(text)
    results = []
    for k in range(1, effective_max_k + 1):
        ic = average_column_ic(text, k, alphabet_len)
        kasiski_score = factor_counts.get(k, 0)
        results.append((k, ic, kasiski_score))

    # Sortowanie wg wskaźnika IC z wagą zgodności Kasiskiego
    results.sort(key=lambda x: (x[1] * (1.0 + 0.10 * math.log(1 + x[2]))), reverse=True)
    return results


def select_fundamental_period(rankings: List[Tuple[int, float, int]], ic_threshold: float = 0.055) -> int:
    """Wybiera okres bazowy, eliminując fałszywe cięcia harmoniczne (np. 8 do 4)."""
    top_cand = rankings[0]
    best_k, best_ic, _ = top_cand

    for cand_k, cand_ic, _ in rankings:
        if cand_k < best_k and best_k % cand_k == 0:
            if cand_ic >= 0.90 * best_ic and cand_ic >= ic_threshold:
                best_k = cand_k
                best_ic = cand_ic

    return best_k


def solve_caesar_by_correlation(slice_text: str, alphabet: str, ref_freq: Dict[str, float]) -> Tuple[int, float]:
    m = len(alphabet)
    n = len(slice_text)
    if n == 0:
        return 0, 0.0

    counts = Counter(slice_text)
    best_shift = 0
    best_score = -1.0

    for s in range(m):
        score = 0.0
        for char, prob in ref_freq.items():
            c_idx = (alphabet.index(char) + s) % m
            obs_count = counts.get(alphabet[c_idx], 0)
            score += (obs_count / n) * prob

        if score > best_score:
            best_score = score
            best_shift = s

    return best_shift, best_score


def recover_key(ciphertext: str, key_len: int, alphabet: str, ref_freq: Dict[str, float]) -> Tuple[str, float]:
    key_chars = []
    total_score = 0.0
    for i in range(key_len):
        subseq = ciphertext[i::key_len]
        shift, score = solve_caesar_by_correlation(subseq, alphabet, ref_freq)
        key_chars.append(alphabet[shift])
        total_score += score
    return "".join(key_chars), total_score / key_len


def decrypt_vigenere(ciphertext: str, key: str, alphabet: str) -> str:
    m = len(alphabet)
    k_len = len(key)
    res = []
    for i, c in enumerate(ciphertext):
        c_idx = alphabet.index(c)
        k_idx = alphabet.index(key[i % k_len])
        p_idx = (c_idx - k_idx) % m
        res.append(alphabet[p_idx])
    return "".join(res)


def auto_break(ciphertext: str, alphabet: str) -> Tuple[str, str, str, str, int]:
    m = len(alphabet)
    max_k = min(30, max(2, len(ciphertext) // 7))
    rankings = estimate_key_length(ciphertext, m, max_k)

    best_k = select_fundamental_period(rankings)

    if m == 26:
        profiles = [("Polski", FREQ_PL), ("Angielski", FREQ_EN)]
    else:
        profiles = [("Polski", build_freq_alfa37(FREQ_PL)), ("Angielski", build_freq_alfa37(FREQ_EN))]

    best_lang = ""
    best_key = ""
    max_score = -1.0

    # Testujemy dopasowanie językowe
    for lang_name, freq_dict in profiles:
        cand_key, avg_score = recover_key(ciphertext, best_k, alphabet, freq_dict)
        if avg_score > max_score:
            max_score = avg_score
            best_lang = lang_name
            best_key = cand_key

    decrypted = decrypt_vigenere(ciphertext, best_key, alphabet)
    log_summary = (
        f"Określona długość klucza (okres fundamentalny): {best_k}\n"
        f"Zidentyfikowany język: {best_lang} (korelacja wektorowa: {max_score:.5f})\n"
        f"Odzyskany klucz: {best_key}"
    )
    return best_key, best_lang, decrypted, log_summary, best_k


def attack_known_plaintext(ciphertext: str, crib: str, alphabet: str, assumed_k: Optional[int], ref_freq: Dict[str, float]) -> Tuple[str, int, int]:
    m = len(alphabet)
    crib = clean_text(crib, alphabet)
    crib_len = len(crib)
    c_len = len(ciphertext)

    if crib_len > c_len or crib_len == 0:
        return "", 0, -1

    if assumed_k is not None and assumed_k > 0:
        candidate_k_list = [assumed_k]
    else:
        max_test_k = min(30, max(2, c_len // 2))
        candidate_k_list = list(range(2, max_test_k + 1))

    best_key = ""
    best_k = 0
    best_offset = -1
    best_total_score = -1.0

    for k in candidate_k_list:
        for offset in range(c_len - crib_len + 1):
            sub_c = ciphertext[offset:offset + crib_len]
            derived = [(alphabet.index(sub_c[i]) - alphabet.index(crib[i])) % m for i in range(crib_len)]

            key_map: Dict[int, int] = {}
            consistent = True
            overlaps = 0
            for i, shift in enumerate(derived):
                idx = (offset + i) % k
                if idx in key_map:
                    overlaps += 1
                    if key_map[idx] != shift:
                        consistent = False
                        break
                key_map[idx] = shift

            if not consistent:
                continue

            candidate_key_chars = []
            for i in range(k):
                if i in key_map:
                    candidate_key_chars.append(alphabet[key_map[i]])
                else:
                    subseq = ciphertext[i::k]
                    shift, _ = solve_caesar_by_correlation(subseq, alphabet, ref_freq)
                    candidate_key_chars.append(alphabet[shift])

            cand_key = "".join(candidate_key_chars)
            decrypted_trial = decrypt_vigenere(ciphertext, cand_key, alphabet)

            trial_counts = Counter(decrypted_trial)
            n_trial = len(decrypted_trial)
            lang_score = sum((trial_counts.get(char, 0) / n_trial) * prob for char, prob in ref_freq.items())

            total_score = lang_score + 0.05 * overlaps

            if total_score > best_total_score:
                best_total_score = total_score
                best_key = cand_key
                best_k = k
                best_offset = offset

    return best_key, best_k, best_offset


def generate_logs(ciphertext: str, alphabet: str, chosen_key: str, detected_lang: str) -> str:
    m = len(alphabet)
    repeats, _ = kasiski_examination(ciphertext)
    rankings = estimate_key_length(ciphertext, m, 25)

    lines = []
    lines.append("=== LOG KRYPTOANALIZY SZYFRU VIGENERE'A ===")
    lines.append(f"Moc alfabetu (|Sigma|): {m}")
    lines.append(f"Długość szyfrogramu: {len(ciphertext)} znaków")
    lines.append(f"Indeks Koincydencji całego tekstu: {index_of_coincidence(ciphertext, m):.5f}")
    lines.append("\n--- METODA KASISKIEGO (Wykryte n-gramy o długości >= 4) ---")
    sig_grams = {g: pos for g, pos in repeats.items() if len(g) >= 4}
    for g, pos in list(sig_grams.items())[:10]:
        dists = [pos[i + 1] - pos[i] for i in range(len(pos) - 1)]
        lines.append(f"Wzorzec '{g}': pozycje {pos}, odstępy: {dists}")

    lines.append("\n--- ANALIZA OKRESOWOŚCI PODCIĄGÓW (Top 10) ---")
    lines.append(f"{'Długość (k)':<12}{'Średni IC':<15}{'Zgodność Kasiski':<15}")
    for k, ic, sc in rankings[:10]:
        lines.append(f"{k:<12}{ic:<15.5f}{sc:<15}")

    lines.append("\n--- WYNIK KOŃCOWY ---")
    lines.append(f"Rozpoznany język tekstu: {detected_lang}")
    lines.append(f"Długość klucza bazowego (d): {len(chosen_key)}")
    lines.append(f"Wyznaczony klucz: {chosen_key}")
    return "\n".join(lines)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    output_dir = os.path.join(script_dir, "wyniki")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 68)
    print(" PROGRAM KRYPTOANALIZY SZYFRU VIGENERE'A (ALFA26 / ALFA37)")
    print("=" * 68)
    print(f"Katalog programu: {script_dir}")
    print(f"Katalog wyników:  {output_dir}")

    alphabet = ALFA26
    while True:
        print("\n--- MENU GŁÓWNE ---")
        print("1. Pełna kryptoanaliza automatyczna (Ciphertext-Only)")
        print("2. Kryptoanaliza asystowana (interaktywny wybór długości i języka)")
        print("3. Kryptoanaliza ze znanym fragmentem tekstu (Known-Plaintext)")
        print(f"4. Zmiana alfabetu (aktualny: {'ALFA26' if alphabet == ALFA26 else 'ALFA37'})")
        print("5. Zakończ program")

        choice = input("Wybierz opcję (1-5): ").strip()
        if choice == '5':
            print("Zakończono działanie programu.")
            sys.exit(0)

        if choice == '4':
            print("\n1. ALFA26 (A-Z)")
            print("2. ALFA37 (A-Z, 0-9, spacja)")
            c_alf = input("Wybór (1-2): ").strip()
            alphabet = ALFA37 if c_alf == '2' else ALFA26
            print(f"Ustawiono alfabet o mocy {len(alphabet)}.")
            continue

        if choice not in ['1', '2', '3']:
            print("Niepoprawna opcja.")
            continue

        file_path = input("\nPodaj ścieżkę lub nazwę pliku z szyfrogramem: ").strip()
        if not os.path.isabs(file_path):
            file_path = os.path.join(script_dir, file_path)

        if not os.path.isfile(file_path):
            print(f"Błąd: Plik '{file_path}' nie istnieje.")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        clean_c = clean_text(raw_content, alphabet)
        if len(clean_c) < 10:
            print("Błąd: Za mało poprawnych znaków w pliku do przeprowadzenia analizy.")
            continue

        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        out_decrypted_path = os.path.join(output_dir, f"{base_filename}_odszyfrowany.txt")
        out_key_path = os.path.join(output_dir, f"{base_filename}_klucz.txt")
        out_log_path = os.path.join(output_dir, f"{base_filename}_analiza.log")

        if choice == '1':
            final_key, detected_lang, decrypted, summary, _ = auto_break(clean_c, alphabet)
            print("\n" + summary)

        elif choice == '2':
            rankings = estimate_key_length(clean_c, len(alphabet), 25)
            print("\nProponowane długości klucza wg indeksu koincydencji:")
            for idx, (k, ic, sc) in enumerate(rankings[:5], 1):
                print(f" {idx}. Długość: {k} (Średni IC: {ic:.4f}, punkty Kasiskiego: {sc})")

            def_k = select_fundamental_period(rankings)
            user_k = input(f"Podaj długość klucza [sugerowane: {def_k}]: ").strip()
            chosen_k = int(user_k) if user_k.isdigit() else def_k

            print("\nWybierz język referencyjny:")
            print("1. Polski (domyślny)")
            print("2. Angielski")
            l_choice = input("Wybór (1-2): ").strip()

            if len(alphabet) == 26:
                ref_dict = FREQ_EN if l_choice == '2' else FREQ_PL
            else:
                ref_dict = build_freq_alfa37(FREQ_EN) if l_choice == '2' else build_freq_alfa37(FREQ_PL)

            detected_lang = "Angielski" if l_choice == '2' else "Polski"
            final_key, _ = recover_key(clean_c, chosen_k, alphabet, ref_dict)
            decrypted = decrypt_vigenere(clean_c, final_key, alphabet)
            print(f"\nWyznaczony klucz: {final_key}")

        elif choice == '3':
            crib = input("Podaj znany fragment tekstu jawnego: ").strip()
            user_k = input("Podaj długość klucza (lub naciśnij Enter, aby wykryć automatycznie): ").strip()
            assumed_k = int(user_k) if user_k.isdigit() else None

            # Sprawdzamy dopasowanie zarówno dla profilu angielskiego, jak i polskiego
            best_res = None
            for l_name, r_freq in [("Angielski", FREQ_EN), ("Polski", FREQ_PL)]:
                k_res, k_len, off = attack_known_plaintext(clean_c, crib, alphabet, assumed_k, r_freq)
                if k_res:
                    trial_dec = decrypt_vigenere(clean_c, k_res, alphabet)
                    score = sum((Counter(trial_dec).get(c, 0) / len(trial_dec)) * p for c, p in r_freq.items())
                    if best_res is None or score > best_res[0]:
                        best_res = (score, k_res, k_len, off, l_name)

            if best_res and best_res[1]:
                _, final_key, found_k, best_offset, detected_lang = best_res
                print(f"\n[KPA] Sukces! Wykryte przesunięcie wzorca: offset {best_offset}")
                print(f"[KPA] Zidentyfikowana długość klucza (d): {found_k}")
                print(f"[KPA] Odzyskany klucz: {final_key}")
                decrypted = decrypt_vigenere(clean_c, final_key, alphabet)
            else:
                print("\nBrak dopasowań wzorca. Uruchamiam procedurę statystyczną...")
                final_key, detected_lang, decrypted, summary, _ = auto_break(clean_c, alphabet)
                print(summary)

        with open(out_decrypted_path, 'w', encoding='utf-8') as f:
            f.write(decrypted.lower())

        with open(out_key_path, 'w', encoding='utf-8') as f:
            f.write(final_key)

        log_data = generate_logs(clean_c, alphabet, final_key, detected_lang)
        with open(out_log_path, 'w', encoding='utf-8') as f:
            f.write(log_data)

        print("\nWyniki zostały pomyślnie zapisane:")
        print(f" -> Tekst odszyfrowany: {out_decrypted_path}")
        print(f" -> Odzyskany klucz:    {out_key_path}")
        print(f" -> Dziennik analizy:   {out_log_path}")


if __name__ == "__main__":
    main()