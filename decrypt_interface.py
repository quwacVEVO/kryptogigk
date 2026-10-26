import sys
import os
import re
from pathlib import Path
from collections import Counter

sys.path.append(str(Path(__file__).resolve().parent))

import kryptolib as kp
import algorytmy_analizy as an


# =====================================================================
# 1. FUNKCJE PODSTAWIEŃ I MANIPULACJI KLUCZEM
# =====================================================================

def apply_substitution(text: str, sub_str: str, temp_key: list) -> tuple[str, bool, str]:    
    if not isinstance(sub_str, str) or len(sub_str) != 2 or not sub_str.isalpha():
        return text, False, "Nieprawidłowy format podstawienia. Użyj dokładnie 2 liter, np. 'Za' lub 'aZ'."

    c_from, c_to = sub_str[0], sub_str[1]

    if c_from.isupper() and c_to.islower():
        cipher_idx = kp.ALFA26.index(c_from)
        if temp_key[cipher_idx] != '_':
            return text, False, f"Litera szyfru '{c_from}' jest już podstawiona jako '{temp_key[cipher_idx]}'."
        if c_to.upper() in temp_key:
            already_used = kp.ALFA26[temp_key.index(c_to.upper())]
            return text, False, f"Litera tekstu jawnego '{c_to.upper()}' została już przypisana do '{already_used}'."
        
        trans_table = str.maketrans({c_from: c_to})
        new_text = text.translate(trans_table)
        temp_key[cipher_idx] = c_to.upper()
        return new_text, True, "OK"
    
    if c_from.islower() and c_to.isupper():
        cipher_idx = kp.ALFA26.index(c_to)
        if temp_key[cipher_idx] != c_from.upper():
            return text, False, f"Konflikt: Litera szyfru '{c_to}' nie była powiązana z literą jawną '{c_from}'."
        
        trans_table = str.maketrans({c_from: c_to})
        new_text = text.translate(trans_table)
        temp_key[cipher_idx] = '_'
        return new_text, True, "OK"

    return text, False, "Nieprawidłowy format wielkości liter. Dla zamiany użyj 'Za', a dla cofnięcia 'aZ'."


def rebuild_text_from_key(current_text: str, temp_key: list) -> tuple[str, list]:
    reverted_text = current_text
    for cipher_idx, plain_char in enumerate(temp_key):
        if plain_char != "_":
            cipher_char = kp.ALFA26[cipher_idx]
            sub_str = f"{plain_char.lower()}{cipher_char}"
            reverted_text, _, _ = apply_substitution(reverted_text, sub_str, temp_key)
    return reverted_text, temp_key


def set_key_from_string(original_text: str, key_str: str, temp_key: list) -> tuple[str, bool]:
    key_str = key_str.strip()
    if len(key_str) != 26:
        print("[BŁĄD] Klucz musi składać się z dokładnie 26 znaków.")
        return original_text, False

    for i in range(26):
        temp_key[i] = '_'

    current_text = original_text
    for cipher_idx, char in enumerate(key_str.upper()):
        if char.isalpha():
            cipher_char = kp.ALFA26[cipher_idx]
            plain_char = char.lower()
            sub_str = f"{cipher_char}{plain_char}"
            current_text, ok, msg = apply_substitution(current_text, sub_str, temp_key)
            if not ok:
                print(f"[OSTRZEŻENIE] Podstawienie {sub_str} pominięte: {msg}")

    return current_text, True


# =====================================================================
# 2. FUNKCJE ANALIZY STATYSTYCZNEJ I RAPORTOWANIA
# =====================================================================

def run_analysis(text: str, mode: str = "ALFA26", top_k_bi: int = 10, top_k_tri: int = 10, hide_guessed: bool = True, temp_key: list = None) -> dict:
    total_len = len(text)
    counts = Counter(text)
    stats = []

    alphabet = kp.ALFA26 if mode == "ALFA26" else kp.ALFA37

    for cipher_idx, char in enumerate(alphabet):
        if hide_guessed:
            if temp_key and cipher_idx < len(temp_key) and temp_key[cipher_idx] != '_':
                continue
            if not temp_key and char.lower() in counts:
                continue

        c = counts.get(char, 0)
        pct = (c / total_len * 100) if total_len > 0 else 0
        stats.append((char, c, pct))

    stats.sort(key=lambda x: (-x[1], x[0]))

    ioc = an.calculate_ioc(text, 26)

    ngrams_bi = [text[i:i+2] for i in range(len(text) - 1) if text[i:i+2].isalpha()]
    total_bi = len(ngrams_bi)
    bigrams = Counter(ngrams_bi).most_common(top_k_bi)

    ngrams_tri = [text[i:i+3] for i in range(len(text) - 2) if text[i:i+3].isalpha()]
    total_tri = len(ngrams_tri)
    trigrams = Counter(ngrams_tri).most_common(top_k_tri)

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
    current_ioc = an.calculate_ioc(text, 26)
    ioc_diffs = {
        lang: abs(current_ioc - target_ioc)
        for lang, target_ioc in an.REF_IOC.items()
    }
    suggested_by_ioc = min(ioc_diffs, key=ioc_diffs.get)

    counts = Counter([ch for ch in text.upper() if ch in kp.ALFA26])
    total = sum(counts.values())
    if total == 0:
        sse_scores = {"polski": 0.0, "angielski": 0.0}
        suggested_by_sse = "polski"
    else:
        text_freqs = {ch: (counts.get(ch, 0) / total) * 100 for ch in kp.ALFA26}
        sse_scores = {}
        for lang, ref_freqs in an.REF_FREQS.items():
            sse = sum((text_freqs[ch] - ref_freqs.get(ch, 0.0)) ** 2 for ch in kp.ALFA26)
            sse_scores[lang] = sse
        suggested_by_sse = min(sse_scores, key=sse_scores.get)

    return current_ioc, suggested_by_ioc, sse_scores, suggested_by_sse


def print_key_mapping(temp_key: list):
    print("\n" + "=" * 65)
    print("                AKTUALNY STAN KLUCZA")
    print("Szyfrogram:  " + " ".join(kp.ALFA26))
    print("Tekst jawny: " + " ".join(temp_key))
    print("=" * 65)


def print_full_report(results, lang_ref_name, temp_key):
    print("\n" + "-" * 75)
    print(f"Tryb alfabetu:               {results['mode']}")
    print(f"Liczba znaków tekstu:        {results['total_len']}")
    print(f"Wskaźnik koincydencji (IoC): {results['ioc']:.5f}")

    # --- 1. TABELA ZNAKÓW ---
    print("-" * 75)
    print(f"1. RANKING NIEODGADNIĘTYCH ZNAKÓW vs REFERENCJA ({lang_ref_name.upper()})")
    print(f"{'Znak':<6} | {'Liczba':<6} | {'Częst.':<8} || {'Ref Znak':<8} | {'Ref Częst.':<10}")
    print("-" * 75)
    
    used_plain_chars = {char.upper() for char in temp_key if char != '_'}
        
    ref_dict = an.REF_FREQS.get(lang_ref_name, an.REF_FREQS["polski"])
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
    ref_bi_raw = an.REF_BIGRAMS.get(lang_ref_name, an.REF_BIGRAMS["polski"])
    if isinstance(ref_bi_raw, dict):
        ref_bi_list = sorted(ref_bi_raw.items(), key=lambda x: x[1], reverse=True)[:10]
    else:
        ref_bi_list = ref_bi_raw[:10]

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
    ref_tri_raw = an.REF_TRIGRAMS.get(lang_ref_name, an.REF_TRIGRAMS["polski"])
    if isinstance(ref_tri_raw, dict):
        ref_tri_list = sorted(ref_tri_raw.items(), key=lambda x: x[1], reverse=True)[:10]
    else:
        ref_tri_list = ref_tri_raw[:10]

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
    while True:
        raw_snippet = text[offset:offset + block_size]
        formatted_snippet = kp.format_columns(raw_snippet, rows=10, column_width=5)
        
        print(f"\n" + "=" * 65)
        print(f"--- PODGLĄD TEKSTU (Pozycje: {offset} - {offset + len(raw_snippet)} z {len(text)}) ---")
        print("=" * 65)
        print(formatted_snippet)
        print("=" * 65)
        
        nav = input("Nawigacja: [n]ext (+500), [p]rev (-500), lub Enter/q aby wyjść do menu: ").lower().strip()
        if nav == 'n':
            if offset + block_size < len(text):
                offset += block_size
            else:
                print("[INFO] Koniec tekstu.")
        elif nav == 'p':
            if offset > 0:
                offset = max(0, offset - block_size)
            else:
                print("[INFO] Początek tekstu.")
        else:
            break
    return offset


def show_longest_guessed_sequence(text: str):
    snippet = ''
    max_snippet = ''

    left_window = ''
    right_window = ''
    
    max_left_window = ''
    max_right_window = ''

    for i in range(len(text)):
        if text[i].islower():
            if len(snippet) == 0:
                dist = min(5, i)
                left_window = text[i - dist:i]
            snippet += text[i]
            
            if i + 1 == len(text) or not text[i + 1].islower():
                dist = min(5, len(text) - (i + 1))
                right_window = text[i + 1:i + 1 + dist]
                
                if len(snippet) > len(max_snippet):
                    max_snippet = snippet
                    max_left_window = left_window
                    max_right_window = right_window
                snippet = ''

    if not max_snippet:
        print("\n[INFO] Brak odgadniętych fragmentów (małych liter) w tekście.")
    else:
        print(f"\n--- Najdłuższy odgadnięty ciąg ({len(max_snippet)} liter) ---")
        print(f"Ciąg: '{max_snippet}'")
        print(f"Kontekst: ...{max_left_window}[{max_snippet}]{max_right_window}...")
    print("-" * 55)
    input("Naciśnij Enter, aby wrócić do menu...")


# =====================================================================
# 3. GŁÓWNA PĘTLA PROGRAMU
# =====================================================================

def main():
    if "--test" in sys.argv:
        run_tests()
        return

    print("=" * 75)
    print("        ANALIZATOR KRYPTOANALITYCZNY")
    print("=" * 75)

    file_path_str = input("Podaj ścieżkę do pliku szyfrogramu (lub Enter dla tekstu domyślnego): ").strip()
    if file_path_str:
        if not os.path.exists(file_path_str):
            print(f"[BŁĄD] Plik nie istnieje: {file_path_str}")
            return
        original_file_path = Path(file_path_str)
        with open(original_file_path, "r", encoding="utf-8") as f:
            original_text = f.read().strip().upper()
    else:
        original_file_path = Path("szyfrogram_przyklad.txt")
        original_text = "WZZWMW ZWZZWMW ZWKWL XNKLWJ WZZWMW DWKL"
        print(f"[INFO] Załadowano tekst przykładowy ({len(original_text)} znaków).")

    mode_choice = input("Wybierz alfabet [1: ALFA26 (domyślny), 2: ALFA37]: ").strip()
    mode = "ALFA37" if mode_choice == "2" else "ALFA26"

    current_ioc, sug_ioc, sse_scores, sug_sse = get_language_suggestions(original_text)
    
    print("\n" + "-" * 75)
    print(" ANALIZA SUGESTII JĘZYKOWYCH:")
    print(f" 1. Sugestia na podstawie IoC (Index of Coincidence)): {sug_ioc.upper()}")
    print(f"    * IoC tekstu:       {current_ioc:.5f}")
    print(f"    * Ref. polski:      {an.REF_IOC['polski']:.5f}")
    print(f"    * Ref. angielski:   {an.REF_IOC['angielski']:.5f}")
    print(f" 2. Sugestia na podstawie błędów kwadratowych (SSE):  {sug_sse.upper()}")
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

    current_text = original_text
    temp_key = ['_'] * 26
    preview_offset = 0

    while True:
        top_bi_count = 10
        top_tri_count = 10

        results = run_analysis(current_text, mode=mode, top_k_bi=top_bi_count, top_k_tri=top_tri_count, hide_guessed=True, temp_key=temp_key)
        print_full_report(results, lang_ref_name, temp_key)
        print_key_mapping(temp_key)

        print("\n[MENU INTERAKTYWNE]")
        print("  1. Wykonaj podstawienie litery (np. 'Za' -> zamienia szyfr 'Z' na tekst jawny 'a')")
        print("  2. Cofnij pojedyncze podstawienie (np. 'aZ' -> przywraca 'a' do szyfru 'Z')")
        print("  3. Cofnij wszystkie aktywne podstawienia z klucza (rebuild_text_from_key)")
        print("  4. Wpisz pełny klucz 26 znaków z ręki (np. ABC__XYZ...)")
        print("  5. Interaktywny podgląd tekstu (stronami po 500 znaków)")
        print("  6. Pokaż najdłuższy dotychczas odgadnięty ciąg liter")
        print("  7. Zmień język referencyjny tabeli (polski / angielski)")
        print("  8. Zapisz aktualny odszyfrowany tekst do pliku")
        print("  9. Uruchom wbudowane testy (premade tests)")
        print("  0. Wyjście")

        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            sub_input = input("Podaj podstawienie (np. Za): ").strip()
            new_text, success, msg = apply_substitution(current_text, sub_input, temp_key)
            if success:
                current_text = new_text
                print(f"[OK] Wykonano zamianę: {sub_input}")
            else:
                print(f"[BŁĄD] {msg}")

        elif choice == "2":
            sub_input = input("Podaj cofnięcie podstawienia (np. aZ): ").strip()
            new_text, success, msg = apply_substitution(current_text, sub_input, temp_key)
            if success:
                current_text = new_text
                print(f"[OK] Cofnięto zamianę: {sub_input}")
            else:
                print(f"[BŁĄD] {msg}")

        elif choice == "3":
            current_text, temp_key = rebuild_text_from_key(current_text, temp_key)
            print("[OK] Cofnięto wszystkie podstawienia z klucza w tekście.")

        elif choice == "4":
            k_input = input("Wpisz ciąg 26 znaków odpowiadający literom A-Z (użyj '_' dla niewiadomych): ")
            current_text, ok = set_key_from_string(original_text, k_input, temp_key)
            if ok:
                print("[OK] Zaktualizowano klucz i odszyfrowano tekst.")

        elif choice == "5":
            preview_offset = show_interactive_preview(current_text, preview_offset, block_size=500)

        elif choice == "6":
            show_longest_guessed_sequence(current_text)

        elif choice == "7":
            lang_ref_name = "angielski" if lang_ref_name == "polski" else "polski"
            print(f"[OK] Zmieniono język referencyjny na: {lang_ref_name.upper()}")

        elif choice == "8":
            out_txt = original_file_path.parent / "odszyfrowany.txt"
            formatted_text = kp.format_columns(current_text, rows=10, column_width=5)
            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(formatted_text)
            print(f"[OK] Zapisano sformatowany tekst do: {out_txt}")

        elif choice == "9":
            run_tests()
            input("Naciśnij Enter, aby powrócić do menu...")

        elif choice == "0":
            print("Zamykanie programu.")
            break


if __name__ == "__main__":
    main()