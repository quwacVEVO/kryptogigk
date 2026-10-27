#!/usr/bin/env python3
"""
Narzędzie analizy statystycznej dla ALFA26 i ALFA37 (Grupa 3 - Zadanie 3).
Oblicza częstości 1-znaków z rozróżnieniem wielkości liter,
n-gramów, wskaźnik koincydencji (IoC) oraz tabele referencyjne.
Podstawianie dotyczy wyłącznie wielkich liter w szyfrogramie.
"""

import sys
import os
import csv
import random
import re
import datetime
from collections import Counter
from pathlib import Path
import json


# Dodanie katalogu nadrzędnego do ścieżki systemowej, aby zaimportować kryptolib
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from kryptolib.utils import format_columns
except ImportError:
    # W razie problemów ze ścieżkami – funkcja zastępcza
    def format_columns(text: str, rows: int = 10, column_width: int = 5) -> str:
        text = "".join(text[i:i+column_width] + " " for i in range(0, len(text), column_width))
        row_width = (column_width + 1) * rows
        return "\n".join(text[i:i+row_width] for i in range(0, len(text), row_width))

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFA37 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

LOG_FILE = "krypto_analysis.log"

folder_pl = "Statystyki częstości występowania/Język polski/"
with open(f"{folder_pl}/alfa26_unigramy.json", "r", encoding="utf-8") as f:
    unipl = json.load(f)
with open(f"{folder_pl}/alfa26_bigramy.json", "r", encoding="utf-8") as f:
    bipl = json.load(f)
with open(f"{folder_pl}/alfa26_trigramy.json", "r", encoding="utf-8") as f:
    tripl = json.load(f)

folder_eng = "Statystyki częstości występowania/Język angielski/"
with open(f"{folder_eng}/alfa26_unigramy.json", "r", encoding="utf-8") as f:
    unieng = json.load(f)
with open(f"{folder_eng}/alfa26_bigramy.json", "r", encoding="utf-8") as f:
    bieng = json.load(f)
with open(f"{folder_eng}/alfa26_trigramy.json", "r", encoding="utf-8") as f:
    trieng = json.load(f)

REF_FREQS = {
    "polski": unipl ,
    "angielski": unieng
}


REF_BIGRAMS = {
    "polski": bipl
,
    "angielski": bieng
}

REF_TRIGRAMS = {
    "polski": tripl,
    "angielski": trieng
}

REF_IOC = {
    "polski": 0.0610,
    "angielski": 0.0667
}

def log_action(message: str):
    """Zapisuje akcję użytkownika/systemu do pliku logu."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def calculate_ioc(text: str, alphabet_len: int = 26) -> float:
    upper_text = text.upper()
    n = len(upper_text)
    if n <= 1:
        return 0.0
    counts = Counter(upper_text)
    sum_fi = sum(f * (f - 1) for f in counts.values())
    return sum_fi / (n * (n - 1))

def analyze_ngrams(text: str, n: int = 2, top_k: int = 10):
    ngrams = [text[i:i+n] for i in range(len(text) - n + 1)]
    counts = Counter(ngrams)
    total = len(ngrams)
    return counts.most_common(top_k), total

def run_analysis(text: str, mode: str = "ALFA26", top_k_bi: int = 10, top_k_tri: int = 10, hide_guessed: bool = True):
    alphabet = ALFA26 if mode == "ALFA26" else ALFA37
    total_len = len(text)

    counts = Counter(text)
    stats = []
    
    # Filtrowanie odgadniętych liter ze statystyk tekstu (małe litery są ukrywane z lewej tabeli)
    for char, c in counts.items():
        if hide_guessed and char.islower():
            continue
        if c > 0:
            pct = (c / total_len * 100) if total_len > 0 else 0
            stats.append((char, c, pct))

    stats.sort(key=lambda x: x[1], reverse=True)
    
    ioc = calculate_ioc(text, len(alphabet))
    bigrams, total_bi = analyze_ngrams(text, 2, top_k_bi)
    trigrams, total_tri = analyze_ngrams(text, 3, top_k_tri)

    return {
        "mode": mode,
        "total_len": total_len,
        "ioc": ioc,
        "char_stats": stats,
        "bigrams": bigrams,
        "total_bi": total_bi,
        "trigrams": trigrams,
        "total_tri": total_tri
    }

def get_language_suggestions(text: str) -> tuple[float, str, dict, str]:
    """
    Oblicza osobno sugestię języka na podstawie IoC oraz błędów kwadratowych (SSE).
    """
    current_ioc = calculate_ioc(text, 26)
    ioc_diffs = {
        lang: abs(current_ioc - target_ioc)
        for lang, target_ioc in REF_IOC.items()
    }
    suggested_by_ioc = min(ioc_diffs, key=ioc_diffs.get)

    counts = Counter([ch for ch in text.upper() if ch in ALFA26])
    total = sum(counts.values())
    if total == 0:
        sse_scores = {"polski": 0.0, "angielski": 0.0}
        suggested_by_sse = "polski"
    else:
        text_freqs = {ch: (counts.get(ch, 0) / total) * 100 for ch in ALFA26}
        sse_scores = {}
        for lang, ref_freqs in REF_FREQS.items():
            sse = sum((text_freqs[ch] - ref_freqs.get(ch, 0.0)) ** 2 for ch in ALFA26)
            sse_scores[lang] = sse
        suggested_by_sse = min(sse_scores, key=sse_scores.get)

    return current_ioc, suggested_by_ioc, sse_scores, suggested_by_sse

def rebuild_text_from_history(original_text: str, mapping: dict) -> str:
    """Odtwarza tekst na podstawie oryginalnego tekstu oraz pełnej mapy zamian."""
    res = []
    for ch in original_text:
        if ch in mapping and mapping[ch] != '_':
            res.append(mapping[ch].lower())
        else:
            res.append(ch)
    return "".join(res)

def get_mapping_from_logs(substitutions_log: list) -> dict:
    """Buduje słownik zamian (Wielka litera szyfru -> Mała litera jawna)."""
    mapping = {ch: '_' for ch in ALFA26}
    for sub in substitutions_log:
        parts = sub.split("->")
        if len(parts) == 2:
            src, tgt = parts[0].strip().upper(), parts[1].strip().lower()
            mapping[src] = tgt
    return mapping

def apply_substitution(text: str, sub_str: str, substitutions_log: list) -> tuple[str, bool, str]:
    if "->" not in sub_str:
        return text, False, "Niepoprawny format. Użyj np. A->B"
    
    parts = sub_str.split("->")
    if len(parts) != 2:
        return text, False, "Błąd składni zamiany."
    
    c1, c2_upper = parts[0].strip().upper(), parts[1].strip().upper()
    if len(c1) != 1 or len(c2_upper) != 1 or not c1.isalpha() or not c2_upper.isalpha():
        return text, False, "Podawaj pojedyncze litery (np. A->B)!"

    c2_lower = c2_upper.lower()

    current_mapping = get_mapping_from_logs(substitutions_log)
    if current_mapping.get(c1, '_') != '_':
        return text, False, f"Litera szyfrogramu {c1} jest już podstawiona pod '{current_mapping[c1].upper()}'."
    if c2_lower in current_mapping.values():
        used_by = [k for k, v in current_mapping.items() if v == c2_lower]
        return text, False, f"Litera tekstu jawnego '{c2_upper}' została już użyta dla {used_by[0]}."

    trans_table = str.maketrans({c1: c2_lower})
    new_text = text.translate(trans_table)
    return new_text, True, "OK"

def print_key_mapping(substitutions_log):
    mapping = get_mapping_from_logs(substitutions_log)
    
    plaintext_to_cipher = {}
    for cipher_char, plain_char in mapping.items():
        if plain_char != '_':
            plaintext_to_cipher[plain_char.upper()] = cipher_char

    cipher_row = [plaintext_to_cipher.get(ch, '_') for ch in ALFA26]

    print("\n--- AKTUALNY KLUCZ PODSTAWIANIA ---")
    print("Tekst jawny: " + " ".join(list(ALFA26)))
    print("Szyfrogram:  " + " ".join(cipher_row))
    print("-" * 55)
    return mapping

def print_full_report(results, lang_ref_name, substitutions_log):
    print("\n" + "-" * 75)
    print(f"Tryb alfabetu:    {results['mode']}")
    print(f"Liczba znaków:    {results['total_len']}")
    print(f"Wskaźnik koincydencji (IoC): {results['ioc']:.5f}")

    # --- 1. TABELA ZNAKÓW ---
    print("-" * 75)
    print(f"1. RANKING NIEODGADNIĘTYCH ZNAKÓW vs REFERENCJA ({lang_ref_name.upper()})")
    print(f"{'Znak':<6} | {'Liczba':<6} | {'Częst.':<8} || {'Ref Znak':<8} | {'Ref Częst.':<10}")
    print("-" * 75)
    
    used_plain_chars = {v.upper() for v in get_mapping_from_logs(substitutions_log).values() if v != '_'}

    ref_dict = REF_FREQS.get(lang_ref_name, REF_FREQS["polski"])
    ref_sorted = sorted(ref_dict.items(), key=lambda x: x[1], reverse=True)
    
    ref_sorted_filtered = [(ch, val) for ch, val in ref_sorted if ch not in used_plain_chars]
    
    max_rows_char = max(len(results['char_stats']), len(ref_sorted_filtered))
    for i in range(max_rows_char):
        if i < len(results['char_stats']):
            ch, count, pct = results['char_stats'][i]
            d_ch = repr(ch) if ch == ' ' else f"'{ch}'"
            left_str = f"{d_ch:<6} | {count:<6} | {pct:5.2f}%"
        else:
            left_str = f"{'':<6} | {'':<6} | {'':<8}"
            
        if i < len(ref_sorted_filtered) and results['mode'] == "ALFA26":
            ref_ch, ref_val = ref_sorted_filtered[i]
            ref_disp = f"'{ref_ch}'"
            right_str = f"  {ref_disp:<8} | {ref_val:5.2f}%"
        else:
            right_str = f"  {'':<8} | {'':<10}"
        print(f"{left_str} ||{right_str}")

    # --- 2. TABELA BIGRAMÓW ---
    ref_bi_list = REF_BIGRAMS.get(lang_ref_name, REF_BIGRAMS["polski"])
    print("-" * 75)
    print(f"2. NAJCZĘSTSZE DWUZNAKI (Top {len(ref_bi_list)}): TEKST vs REFERENCJA")
    print(f"{'Bigram':<8} | {'Liczba':<6} | {'Częst.':<8} || {'Ref Bigram':<10} | {'Ref Orient.':<10}")
    print("-" * 75)

    text_bi_processed = []
    for bg, count in results['bigrams']:
        pct = (count / results['total_bi'] * 100) if results['total_bi'] > 0 else 0
        text_bi_processed.append((bg, count, pct))

    for i in range(len(ref_bi_list)):
        if i < len(text_bi_processed):
            bg, count, pct = text_bi_processed[i]
            left_str = f"'{bg}':    | {count:<6} | {pct:5.2f}%"
        else:
            left_str = f"{'':<8} | {'':<6} | {'':<8}"

        r_bg, r_val = ref_bi_list[i]
        right_str = f"  '{r_bg}':       | ~{r_val:4.1f}%"
        print(f"{left_str} ||{right_str}")

    # --- 3. TABELA TRIGRAMÓW ---
    ref_tri_list = REF_TRIGRAMS.get(lang_ref_name, REF_TRIGRAMS["polski"])
    print("-" * 75)
    print(f"3. NAJCZĘSTSZE TRÓJZNAKI (Top {len(ref_tri_list)}): TEKST vs REFERENCJA")
    print(f"{'Trigram':<9} | {'Liczba':<6} | {'Częst.':<8} || {'Ref Trigram':<11} | {'Ref Orient.':<10}")
    print("-" * 75)

    text_tri_processed = []
    for tg, count in results['trigrams']:
        pct = (count / results['total_tri'] * 100) if results['total_tri'] > 0 else 0
        text_tri_processed.append((tg, count, pct))

    for i in range(len(ref_tri_list)):
        if i < len(text_tri_processed):
            tg, count, pct = text_tri_processed[i]
            left_str = f"'{tg}':     | {count:<6} | {pct:5.2f}%"
        else:
            left_str = f"{'':<9} | {'':<6} | {'':<8}"

        r_tg, r_val = ref_tri_list[i]
        right_str = f"  '{r_tg}':       | ~{r_val:4.1f}%"
        print(f"{left_str} ||{right_str}")

    print("-" * 75)

def show_interactive_preview(text: str, offset: int = 0, block_size: int = 500) -> int:
    """
    Dedykowana pętla podglądu pozwalająca wygodnie nawigować [n]ext / [p]rev.
    Zwraca aktualny offset po wyjściu.
    """
    while True:
        raw_snippet = text[offset:offset + block_size]
        # 100 kolumn x 5 znaków wystarczy na zmieszczenie 500 znaków na ekranie
        formatted_snippet = format_columns(raw_snippet, rows=100, column_width=5)
        
        print(f"\n" + "=" * 65)
        print(f"--- PODGLĄD TEKSTU (Zakres: {offset} - {offset + len(raw_snippet)} z {len(text)}) ---")
        print("=" * 65)
        print(formatted_snippet)
        print("=" * 65)
        
        nav = input("Nawigacja: [n]ext (+500), [p]rev (-500), lub Enter/q aby wrócić do menu: ").lower().strip()
        if nav == 'n':
            if offset + block_size < len(text):
                offset += block_size
            else:
                print("[INFO] Osiągnięto koniec tekstu!")
        elif nav == 'p':
            if offset > 0:
                offset = max(0, offset - block_size)
            else:
                print("[INFO] Jesteś na początku tekstu!")
        else:
            break
    return offset

def show_context_for_char(text: str, char: str, window: int = 10):
    char = char.upper()
    idx = text.find(char)
    if idx == -1:
        print(f"\n[INFO] Nie znaleziono litery '{char}' w tekście lub została już odgadnięta.")
    else:
        start = max(0, idx - window)
        end = min(len(text), idx + window + 1)
        snippet = text[start:end]
        print(f"\n--- Kontekst dla pierwszej litery '{char}' (pozycja {idx}) ---")
        print(f"...{snippet}...")
    
    print("-" * 55)
    input("Naciśnij Enter, aby wrócić do menu...")

def show_longest_guessed_sequence(text: str, window: int = 5):
    matches = list(re.finditer(r'[a-z]+', text))
    if not matches:
        print("\n[INFO] Brak odgadniętych fragmentów (małych liter) w tekście.")
    else:
        longest = max(matches, key=lambda m: m.end() - m.start())
        start = max(0, longest.start() - window)
        end = min(len(text), longest.end() + window)
        snippet = text[start:end]
        
        print(f"\n--- Najdłuższy odgadnięty ciąg ({longest.end() - longest.start()} liter) ---")
        print(f"Ciąg: '{longest.group()}'")
        print(f"Kontekst: ...{snippet}...")

    print("-" * 55)
    input("Naciśnij Enter, aby wrócić do menu...")

def set_key_from_string(key_str: str, substitutions_log: list, original_text: str):
    key_str = key_str.strip()
    if len(key_str) != 26:
        print("[BŁĄD] Klucz musi zawierać dokładnie 26 znaków!")
        return original_text, False

    substitutions_log.clear()
    for i, cipher_char in enumerate(key_str):
        if cipher_char != '_':
            plain_char = ALFA26[i]
            substitutions_log.append(f"{cipher_char.upper()}->{plain_char.upper()}")
    
    mapping = get_mapping_from_logs(substitutions_log)
    new_text = rebuild_text_from_history(original_text, mapping)
    log_action(f"Ustawiono klucz z ciągu: {key_str}")
    return new_text, True

def auto_match_by_frequency(current_text: str, lang_ref_name: str, substitutions_log: list, original_text: str):
    counts = Counter([ch for ch in current_text if ch.isupper() and ch in ALFA26])
    if not counts:
        print("[INFO] Brak wielkich liter do automatycznego dopasowania.")
        return current_text
    
    most_common_cipher = counts.most_common(1)[0][0]
    ref_dict = REF_FREQS.get(lang_ref_name, REF_FREQS["polski"])
    
    used_targets = set(get_mapping_from_logs(substitutions_log).values())
    ref_sorted = sorted(ref_dict.items(), key=lambda x: x[1], reverse=True)
    
    target_ref = None
    for r_char, _ in ref_sorted:
        if r_char.lower() not in used_targets:
            target_ref = r_char.upper()
            break
            
    if target_ref:
        sub_str = f"{most_common_cipher}->{target_ref}"
        new_text, success, msg = apply_substitution(current_text, sub_str, substitutions_log)
        if success:
            substitutions_log.append(sub_str)
            log_action(f"Auto-dopasowanie wg częstości: {sub_str}")
            print(f"[OK] Wykonano auto-dopasowanie: {sub_str}")
            return new_text
        else:
            print(f"[BŁĄD] {msg}")
    return current_text

def remove_arbitrary_substitution(substitutions_log: list, original_text: str):
    if not substitutions_log:
        print("[INFO] Brak zamian do cofnięcia.")
        return original_text
    
    print("\nHistoria obecnych zamian:")
    for idx, sub in enumerate(substitutions_log):
        print(f" {idx + 1}. {sub}")
    
    choice = input("Podaj numer zamiany do usunięcia (lub Enter, aby anulować): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(substitutions_log):
            removed = substitutions_log.pop(idx)
            log_action(f"Cofnięto wybraną zamianę: {removed}")
            print(f"[OK] Usunięto zamianę: {removed}")
            mapping = get_mapping_from_logs(substitutions_log)
            return rebuild_text_from_history(original_text, mapping)
    print("[INFO] Nie usunięto żadnej zamiany.")
    return rebuild_text_from_history(original_text, get_mapping_from_logs(substitutions_log))

def main():
    print("=" * 75)
    print("        ANALIZATOR KRYPTOANALITYCZNY (GRUPA 3 - ZADANIE 3)")
    print("=" * 75)

    file_path_str = input("Podaj ścieżkę do pliku szyfrogramu: ").strip()
    if not os.path.exists(file_path_str):
        print(f"[BŁĄD] Plik nie istnieje: {file_path_str}")
        return

    original_file_path = Path(file_path_str)

    with open(original_file_path, "r", encoding="utf-8") as f:
        original_text = f.read().strip().upper()

    log_action(f"Wczytano plik szyfrogramu: {original_file_path}")

    mode_choice = input("Wybierz alfabet [1: ALFA26 (domyślny), 2: ALFA37]: ").strip()
    mode = "ALFA37" if mode_choice == "2" else "ALFA26"

    current_ioc, sug_ioc, sse_scores, sug_sse = get_language_suggestions(original_text)
    
    print("\n" + "-" * 75)
    print(" ANALIZA SUGESTII JĘZYKOWYCH:")
    print(f" 1. Sugestia na podstawie IoC (Wskaźnik Koincydencji): {sug_ioc.upper()}")
    print(f"    * IoC tekstu:       {current_ioc:.5f}")
    print(f"    * Ref. polski:      {REF_IOC['polski']:.5f}")
    print(f"    * Ref. angielski:   {REF_IOC['angielski']:.5f}")
    print(f" 2. Sugestia na podstawie błędów kwadratowych (SSE): {sug_sse.upper()}")
    print(f"    * Błąd kwadratowy dla polskiego:       {sse_scores['polski']:.2f}")
    print(f"    * Błąd kwadratowy dla angielskiego:    {sse_scores['angielski']:.2f}")
    print("-" * 75)

    default_lang = sug_sse
    lang_choice = input(f"Wybierz język referencyjny [1: polski, 2: angielski] (domyślnie: {default_lang}): ").strip()
    
    if lang_choice == "1":
        lang_ref_name = "polski"
    elif lang_choice == "2":
        lang_ref_name = "angielski"
    else:
        lang_ref_name = default_lang

    substitutions_log = []
    current_text = original_text
    preview_offset = 0

    while True:
        top_bi_count = len(REF_BIGRAMS[lang_ref_name])
        top_tri_count = len(REF_TRIGRAMS[lang_ref_name])

        results = run_analysis(current_text, mode=mode, top_k_bi=top_bi_count, top_k_tri=top_tri_count, hide_guessed=True)
        print_full_report(results, lang_ref_name, substitutions_log)
        current_mapping = print_key_mapping(substitutions_log)

        print("\n[MENU INTERAKTYWNE]")
        print("  1. Wykonaj podstawienie znaków (np. A->B, gdzie B to odgadnięta litera)")
        print("  2. Cofnij dowolne dopasowanie")
        print("  3. Resetuj do oryginalnego tekstu")
        print("  4. Podgląd tekstu (interaktywny podgląd stronami po 500 znaków)")
        print("  5. Pokaż okolicę wybranej litery (10 przed/po)")
        print("  6. Pokaż najdłuższy odgadnięty ciąg znaków")
        print("  7. Wpisz pełny klucz podstawienia z ręki (np. ___B____C...)")
        print("  8. Automatyczne dopasowanie najczęstszych liter")
        print("  9. Losowe podstawienie")
        print(" 10. Eksportuj statystyki do CSV / Zapisz sformatowany szyfrogram")
        print("  0. Wyjście")
        
        if substitutions_log:
            print(f"  * Zastosowane zamiany: {', '.join(substitutions_log)}")

        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            sub_input = input("Podaj zamianę (np. A->B): ").strip().upper()
            new_text, success, msg = apply_substitution(current_text, sub_input, substitutions_log)
            if success:
                current_text = new_text
                substitutions_log.append(sub_input)
                log_action(f"Wykonano podstawienie: {sub_input}")
                print(f"[OK] Wykonano zamianę: {sub_input}")
            else:
                print(f"[BŁĄD] {msg}")

        elif choice == "2":
            current_text = remove_arbitrary_substitution(substitutions_log, original_text)

        elif choice == "3":
            substitutions_log.clear()
            current_text = original_text
            log_action("Zresetowano tekst do stanu początkowego")
            print("[OK] Przywrócono tekst oryginalny.")

        elif choice == "4":
            preview_offset = show_interactive_preview(current_text, preview_offset, block_size=500)

        elif choice == "5":
            char_to_find = input("Podaj literę szyfrogramu do podglądu otoczenia: ").strip()
            if char_to_find:
                show_context_for_char(current_text, char_to_find)

        elif choice == "6":
            show_longest_guessed_sequence(current_text)

        elif choice == "7":
            k_input = input("Wpisz ciąg 26 znaków klucza odpowiadający A-Z tekstu jawnego (użyj '_' dla niewiadomych): ")
            current_text, ok = set_key_from_string(k_input, substitutions_log, original_text)

        elif choice == "8":
            current_text = auto_match_by_frequency(current_text, lang_ref_name, substitutions_log, original_text)

        elif choice == "9":
            used_sources = set(get_mapping_from_logs(substitutions_log).keys())
            used_targets = set(get_mapping_from_logs(substitutions_log).values())

            avail_src = [c for c in ALFA26 if c not in used_sources]
            avail_tgt = [c.lower() for c in ALFA26 if c.lower() not in used_targets]

            if avail_src and avail_tgt:
                c1, c2 = random.choice(avail_src), random.choice(avail_tgt)
                sub_str = f"{c1}->{c2.upper()}"
                new_text, success, _ = apply_substitution(current_text, sub_str, substitutions_log)
                if success:
                    current_text = new_text
                    substitutions_log.append(sub_str)
                    log_action(f"Losowe podstawienie: {sub_str}")
                    print(f"[OK] Losowe podstawienie: {sub_str}")

        elif choice == "10":
            out_txt = original_file_path.parent / "odszyfrowany.txt"
            formatted_text = format_columns(current_text, rows=100, column_width=5)
            
            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(formatted_text)
            print(f"[OK] Zapisano sformatowany tekst do: {out_txt}")

        elif choice == "0":
            log_action("Zakończono sesję")
            print("Zamykanie programu.")
            break

if __name__ == "__main__":
    main()