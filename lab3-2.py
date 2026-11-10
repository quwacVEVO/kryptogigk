#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projekt: Szyfr Vigenère'a oraz Szyfr Hilla
Opis: Implementacja szyfrów klasycznych z obsługą alfabetu standardowego (26)
      oraz rozszerzonego (67 znaków). Zawiera pełną obsługę błędów,
      konwencję nawiasową przy deszyfrowaniu oraz automatyczny zestaw testów.
"""

import math
import os
import sys

# ==============================================================================
# DEFINICJE ALFABETÓW
# ==============================================================================

# Alfabet standardowy: 26 wielkich liter angielskich
ALPHABET_STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Znaki specjalne w standardzie ASCII z pominięciem nawiasów kwadratowych '[' i ']'
# (30 znaków)
SPECIAL_CHARS = (
    "!\"#$%&'()*+,-./"   # ASCII 33-47
    ":;<=>?@"           # ASCII 58-64
    "\\^_`"             # ASCII 92, 94, 95, 96 (bez 91 '[' i 93 ']')
    "{|}~"              # ASCII 123-126
)

# Alfabet rozszerzony: 26 liter + 10 cyfr + 1 spacja + 30 znaków specjalnych = 67 znaków.
# 67 jest liczbą pierwszą, co gwarantuje istnienie odwrotności modularnej dla każdego det != 0!
ALPHABET_EXTENDED = (
    ALPHABET_STANDARD +
    "0123456789" +
    " " +
    SPECIAL_CHARS
)


# ==============================================================================
# WALIDACJA I FORMATOWANIE
# ==============================================================================

def validate_and_prepare_text(text: str, is_extended: bool, field_name: str = "Tekst") -> str:
    """
    Sprawdza poprawność znaków i przygotowuje ciąg:
    - Sprawdza zakaz używania nawiasów '[' i ']'.
    - W trybie 26-znakowym akceptuje tylko litery A-Z (odrzuca spacje, cyfry, symbole).
    - W trybie rozszerzonym zamienia małe litery na wielkie i sprawdza obecność w alfabecie 67-znakowym.
    """
    if not text:
        raise ValueError(f"Błąd: {field_name} nie może być pusty!")

    # Bezwzględny zakaz nawiasów kwadratowych
    if "[" in text or "]" in text:
        raise ValueError(
            f"Błąd: {field_name} zawiera niedozwolony znak nawiasu kwadratowego '[' lub ']'. "
            "Nawiasy kwadratowe są zarezerwowane dla formatowania wyjściowego!"
        )

    prepared = []
    alphabet = ALPHABET_EXTENDED if is_extended else ALPHABET_STANDARD

    for idx, ch in enumerate(text):
        upper_ch = ch.upper() if ch.isalpha() else ch

        if not is_extended:
            # W trybie standardowym wymagamy wyłącznie liter A-Z
            if not ('A' <= upper_ch <= 'Z'):
                raise ValueError(
                    f"Błąd: {field_name} zawiera niedozwolony znak '{ch}' na pozycji {idx}. "
                    "W trybie 26-znakowym dozwolone są wyłącznie litery alfabetu angielskiego A-Z "
                    "(brak cyfr, spacji i znaków specjalnych)!"
                )
        else:
            # W trybie rozszerzonym sprawdzamy obecność w ALPHABET_EXTENDED
            if upper_ch not in alphabet:
                raise ValueError(
                    f"Błąd: {field_name} zawiera znak '{ch}' (kod ASCII: {ord(ch)}) na pozycji {idx}, "
                    "który nie należy do dozwolonego alfabetu rozszerzonego!"
                )

        prepared.append(upper_ch)

    return "".join(prepared)


def format_decrypted_output(text: str, is_extended: bool) -> str:
    """
    Formatuje tekst odszyfrowany zgodnie z konwencją:
    - W trybie standardowym: małe litery (np. 'abcd').
    - W trybie rozszerzonym: litery stają się małe, a wszystkie znaki niebędące literami
      (cyfry, spacje, znaki specjalne) zostają ujęte w nawiasy kwadratowe [x].
      Przykład: 'ABCD123_!' -> 'abcd[1][2][3][_][!]'.
    """
    if not is_extended:
        return text.lower()

    output = []
    for ch in text:
        if 'A' <= ch <= 'Z':
            output.append(ch.lower())
        else:
            output.append(f"[{ch}]")
    return "".join(output)


# ==============================================================================
# ALGEBRA DLA SZYFRU HILLA (DOKŁADNE OPERACJE MODULARNE)
# ==============================================================================

def extended_gcd(a: int, b: int):
    """Rozszerzony algorytm Euklidesa: zwraca (gcd, x, y) takie, że a*x + b*y = gcd."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def mod_inverse(a: int, m: int) -> int:
    """Oblicza element odwrotny a^(-1) mod m. Rzuca ValueError jeśli NWD(a, m) != 1."""
    a = a % m
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Liczba {a} nie posiada odwrotności modulo {m} (NWD({a}, {m}) = {gcd} != 1).")
    return (x % m + m) % m


def get_matrix_minor(matrix: list, i: int, j: int) -> list:
    """Zwraca podmacierz po usunięciu wiersza i oraz kolumny j."""
    return [row[:j] + row[j + 1:] for row in (matrix[:i] + matrix[i + 1:])]


def matrix_determinant(matrix: list) -> int:
    """Oblicza wyznacznik macierzy kwadratowej całkowitoliczbowo (rozwinięcie Laplace'a)."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    det = 0
    for c in range(n):
        minor = get_matrix_minor(matrix, 0, c)
        sign = (-1) ** c
        det += sign * matrix[0][c] * matrix_determinant(minor)
    return det


def matrix_adjugate(matrix: list) -> list:
    """Oblicza macierz dołączoną adj(A) = C^T (transponowana macierz dopełnień algebraicznych)."""
    n = len(matrix)
    if n == 1:
        return [[1]]

    adj = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            minor = get_matrix_minor(matrix, r, c)
            sign = (-1) ** (r + c)
            cofactor = sign * matrix_determinant(minor)
            # Transpozycja: element (r, c) trafia do adj[c][r]
            adj[c][r] = cofactor
    return adj


def invert_matrix_modulo(matrix: list, mod: int) -> list:
    """
    Oblicza macierz odwrotną K^(-1) mod m za pomocą wzoru:
    K^(-1) = (det(K))^(-1) * adj(K) mod m.
    Działa dla dowolnego pierścienia Z_m (w tym Z_26 i Z_67).
    """
    n = len(matrix)
    det = matrix_determinant(matrix)
    det_mod = det % mod

    gcd, _, _ = extended_gcd(det_mod, mod)
    if gcd != 1:
        raise ValueError(
            f"Macierz klucza jest NIEODWRACALNA modulo {mod}!\n"
            f"Wyznacznik det(K) = {det} (mod {mod} = {det_mod}).\n"
            f"NWD(det, {mod}) = {gcd} != 1. Nie da się stworzyć klucza deszyfrującego."
        )

    det_inv = mod_inverse(det_mod, mod)
    adj = matrix_adjugate(matrix)

    inv_matrix = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            inv_matrix[r][c] = (adj[r][c] * det_inv) % mod

    return inv_matrix


def key_to_matrix(key_text: str, alphabet: str) -> list:
    """
    Konwertuje ciąg znaków klucza na macierz n x n.
    Sprawdza, czy długość klucza tworzy kwadrat liczby całkowitej (n^2).
    """
    length = len(key_text)
    n = math.isqrt(length)
    if n * n != length or n < 2:
        raise ValueError(
            f"Błąd: Długość klucza ({length}) nie tworzy kwadratu liczby całkowitej n x n!\n"
            f"Poprawne długości to np. 4 (macierz 2x2), 9 (3x3), 16 (4x4) itd."
        )

    char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
    matrix = []
    for r in range(n):
        row = [char_to_idx[key_text[r * n + c]] for c in range(n)]
        matrix.append(row)
    return matrix


# ==============================================================================
# IMPLEMENTACJA SZYFRU VIGENÈRE'A
# ==============================================================================

class VigenereCipher:
    @staticmethod
    def encrypt(plaintext: str, key: str, is_extended: bool) -> str:
        alphabet = ALPHABET_EXTENDED if is_extended else ALPHABET_STANDARD
        mod = len(alphabet)
        char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
        idx_to_char = {i: ch for i, ch in enumerate(alphabet)}

        pt = validate_and_prepare_text(plaintext, is_extended, "Tekst jawny")
        k = validate_and_prepare_text(key, is_extended, "Klucz")

        key_len = len(k)
        ciphertext = []
        for i, ch in enumerate(pt):
            p_val = char_to_idx[ch]
            k_val = char_to_idx[k[i % key_len]]
            c_val = (p_val + k_val) % mod
            ciphertext.append(idx_to_char[c_val])

        return "".join(ciphertext)

    @staticmethod
    def decrypt(ciphertext: str, key: str, is_extended: bool) -> str:
        alphabet = ALPHABET_EXTENDED if is_extended else ALPHABET_STANDARD
        mod = len(alphabet)
        char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
        idx_to_char = {i: ch for i, ch in enumerate(alphabet)}

        ct = validate_and_prepare_text(ciphertext, is_extended, "Szyfrogram")
        k = validate_and_prepare_text(key, is_extended, "Klucz")

        key_len = len(k)
        raw_decrypted = []
        for i, ch in enumerate(ct):
            c_val = char_to_idx[ch]
            k_val = char_to_idx[k[i % key_len]]
            p_val = (c_val - k_val) % mod
            raw_decrypted.append(idx_to_char[p_val])

        return format_decrypted_output("".join(raw_decrypted), is_extended)


# ==============================================================================
# IMPLEMENTACJA SZYFRU HILLA
# ==============================================================================

class HillCipher:
    @staticmethod
    def encrypt(plaintext: str, key: str, is_extended: bool) -> tuple:
        """Zwraca (ciphertext, padding_count)."""
        alphabet = ALPHABET_EXTENDED if is_extended else ALPHABET_STANDARD
        mod = len(alphabet)
        char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
        idx_to_char = {i: ch for i, ch in enumerate(alphabet)}

        pt = validate_and_prepare_text(plaintext, is_extended, "Tekst jawny")
        k_clean = validate_and_prepare_text(key, is_extended, "Klucz")

        K = key_to_matrix(k_clean, alphabet)
        n = len(K)

        # Sprawdzenie, czy klucz jest odwracalny (żeby użytkownik nie zaszyfrował czegoś, czego nie da się odszyfrować)
        _ = invert_matrix_modulo(K, mod)

        # Dopełnienie (padding) znakiem 'X' do wielokrotności wymiaru macierzy n
        padding_count = 0
        rem = len(pt) % n
        if rem != 0:
            padding_count = n - rem
            pt += "X" * padding_count

        ciphertext = []
        for b in range(0, len(pt), n):
            block = [char_to_idx[pt[b + i]] for i in range(n)]
            # Mnożenie macierzy przez wektor kolumnowy: C = K * P mod M
            enc_block = []
            for r in range(n):
                val = sum(K[r][c] * block[c] for c in range(n)) % mod
                enc_block.append(idx_to_char[val])
            ciphertext.extend(enc_block)

        return "".join(ciphertext), padding_count

    @staticmethod
    def decrypt(ciphertext: str, key: str, is_extended: bool) -> str:
        alphabet = ALPHABET_EXTENDED if is_extended else ALPHABET_STANDARD
        mod = len(alphabet)
        char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
        idx_to_char = {i: ch for i, ch in enumerate(alphabet)}

        ct = validate_and_prepare_text(ciphertext, is_extended, "Szyfrogram")
        k_clean = validate_and_prepare_text(key, is_extended, "Klucz")

        K = key_to_matrix(k_clean, alphabet)
        n = len(K)

        if len(ct) % n != 0:
            raise ValueError(
                f"Błąd formatu: Długość szyfrogramu ({len(ct)}) nie jest wielokrotnością wymiaru macierzy ({n})! "
                "Szyfrogram jest uszkodzony lub pochodzi z innego szyfru."
            )

        K_inv = invert_matrix_modulo(K, mod)

        raw_decrypted = []
        for b in range(0, len(ct), n):
            block = [char_to_idx[ct[b + i]] for i in range(n)]
            dec_block = []
            for r in range(n):
                val = sum(K_inv[r][c] * block[c] for c in range(n)) % mod
                dec_block.append(idx_to_char[val])
            raw_decrypted.extend(dec_block)

        return format_decrypted_output("".join(raw_decrypted), is_extended)


# ==============================================================================
# BEZPIECZNE OPERACJE NA PLIKACH
# ==============================================================================

def read_file_safely(file_path: str) -> str:
    """Bezpieczne wczytywanie zawartości pliku."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Plik '{file_path}' nie istnieje.")
    if not os.path.isfile(file_path):
        raise IOError(f"Ścieżka '{file_path}' nie jest plikiem.")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback dla innych kodowań
        with open(file_path, "r", encoding="latin-1") as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"Błąd podczas odczytu pliku '{file_path}': {str(e)}")

    if not content:
        raise ValueError(f"Plik '{file_path}' jest całkowicie pusty!")
    return content.strip()


def write_file_safely(file_path: str, data: str):
    """Bezpieczny zapis danych do pliku."""
    try:
        dirname = os.path.dirname(file_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        raise IOError(f"Nie udało się zapisać pliku '{file_path}': {str(e)}")


# ==============================================================================
# ZESTAW TESTÓW AUTOMATYCZNYCH
# ==============================================================================

def run_all_tests():
    """
    Automatyczny zestaw testów badający przypadki poprawne oraz oczekiwane błędy.
    """
    print("\n" + "=" * 70)
    print("                 URUCHAMIANIE TESTÓW AUTOMATYCZNYCH")
    print("=" * 70)

    passed_count = 0
    total_tests = 0

    def test_case(name: str, should_succeed: bool, func, *args):
        nonlocal passed_count, total_tests
        total_tests += 1
        print(f"[{total_tests:02d}] {name:<55}", end=" ")
        try:
            result = func(*args)
            if should_succeed:
                print(" -> \033[92m[ZALICZONY]\033[0m")
                passed_count += 1
                return result
            else:
                print(f" -> \033[91m[BŁĄD: Spodziewano się wyjątku, a funkcja zwróciła wynik!]\033[0m")
                return None
        except Exception as e:
            if not should_succeed:
                print(f" -> \033[92m[ZALICZONY - Prawidłowo przechwycono błąd: {e.__class__.__name__}]\033[0m")
                passed_count += 1
            else:
                print(f" -> \033[91m[BŁĄD: Niespodziewany wyjątek: {str(e)}]\033[0m")
            return None

    # 1. VIGENÈRE - ALFABET STANDARDOWY (26)
    print("\n--- TESTY: VIGENÈRE (ALFABET 26-ZNAKOWY) ---")
    ct_vig26 = test_case("Szyfrowanie poprawne (Vigenère 26)", True,
                         VigenereCipher.encrypt, "KRYPTOLOGIA", "TAJNE", False)
    test_case("Deszyfrowanie poprawne (Vigenère 26)", True,
              VigenereCipher.decrypt, ct_vig26, "TAJNE", False)
    test_case("BŁĄD: Cyfra w tekście jawnym (tryb 26)", False,
              VigenereCipher.encrypt, "KRYPTO123", "TAJNE", False)
    test_case("BŁĄD: Spacja w tekście jawnym (tryb 26)", False,
              VigenereCipher.encrypt, "KRYPTO LOGIA", "TAJNE", False)
    test_case("BŁĄD: Znak specjalny w kluczu (tryb 26)", False,
              VigenereCipher.encrypt, "KRYPTOLOGIA", "TAJ!NE", False)

    # 2. VIGENÈRE - ALFABET ROZSZERZONY (67)
    print("\n--- TESTY: VIGENÈRE (ALFABET ROZSZERZONY 67) ---")
    plain_ext = "TEST 123_!"
    key_ext = "K!1_"
    ct_vig_ext = test_case("Szyfrowanie rozszerzone ze znakami i spacją", True,
                           VigenereCipher.encrypt, plain_ext, key_ext, True)
    dec_vig_ext = test_case("Deszyfrowanie rozszerzone (sprawdzenie nawiasów)", True,
                            VigenereCipher.decrypt, ct_vig_ext, key_ext, True)
    # Weryfikacja konwencji nawiasowej: 'TEST 123_!' -> 'test[ ][1][2][3][_][!]'
    expected_dec = "test[ ][1][2][3][_][!]"
    total_tests += 1
    print(f"[{total_tests:02d}] {'Format nawiasów odszyfrowanego tekstu (Vigenère)':<55}", end=" ")
    if dec_vig_ext == expected_dec:
        print(" -> \033[92m[ZALICZONY]\033[0m")
        passed_count += 1
    else:
        print(f" -> \033[91m[BŁĄD: Oczekiwano '{expected_dec}', otrzymano '{dec_vig_ext}']\033[0m")

    test_case("BŁĄD: Nawias '[' w tekście rozszerzonym", False,
              VigenereCipher.encrypt, "TEST[A]", "KLUCZ", True)
    test_case("BŁĄD: Pusty klucz", False,
              VigenereCipher.encrypt, "TEST", "", True)

    # 3. HILL - ALFABET STANDARDOWY (26)
    print("\n--- TESTY: HILL (ALFABET 26-ZNAKOWY) ---")
    # Klucz "HILL": H=7, I=8, L=11, L=11 -> det = 7*11 - 8*11 = -11 = 15 mod 26. NWD(15, 26) = 1 (odwracalna!)
    key_hill_valid = "HILL"
    ct_hill26, _ = test_case("Szyfrowanie poprawne (Hill 2x2, det odwracalny)", True,
                             HillCipher.encrypt, "ACT", key_hill_valid, False) # Długość 3 -> dopełnienie do 4 (ACTX)
    test_case("Deszyfrowanie poprawne (Hill 2x2)", True,
              HillCipher.decrypt, ct_hill26, key_hill_valid, False)

    # Macierz nieodwracalna: "ABCD" -> A=0, B=1, C=2, D=3 -> det = 0 - 2 = -2 = 24 mod 26. NWD(24, 26) = 2 != 1
    test_case("BŁĄD: Macierz nieodwracalna mod 26 ('ABCD')", False,
              HillCipher.encrypt, "TEST", "ABCD", False)
    test_case("BŁĄD: Długość klucza niebędąca kwadratem ('HELLO')", False,
              HillCipher.encrypt, "TEST", "HELLO", False)
    test_case("BŁĄD: Długość szyfrogramu nieparzysta dla macierzy 2x2", False,
              HillCipher.decrypt, "XYZ", key_hill_valid, False)

    # 4. HILL - ALFABET ROZSZERZONY (67)
    print("\n--- TESTY: HILL (ALFABET ROZSZERZONY 67) ---")
    # "HILL" w mod 67: det = -11 = 56 mod 67. Ponieważ 67 jest pierwsze, 56 jest odwracalne!
    ct_hill_ext, _ = test_case("Szyfrowanie rozszerzone (Hill 2x2 ze spacją i znakiem)", True,
                               HillCipher.encrypt, "OK 1!", key_hill_valid, True)
    dec_hill_ext = test_case("Deszyfrowanie rozszerzone (Hill 2x2)", True,
                             HillCipher.decrypt, ct_hill_ext, key_hill_valid, True)
    test_case("BŁĄD: Macierz zerowa w Hillu ('AAAA')", False,
              HillCipher.encrypt, "TEST", "AAAA", True)

    # 5. TESTY OPERACJI PLIKOWYCH
    print("\n--- TESTY: SYSTEM PLIKÓW ---")
    test_file_in = "temp_test_in.txt"
    test_file_out = "temp_test_out.txt"
    try:
        write_file_safely(test_file_in, "PROBA PLIKU")
        read_content = test_case("Zapis i odczyt z pliku", True, read_file_safely, test_file_in)
        test_case("BŁĄD: Próba odczytu nieistniejącego pliku", False, read_file_safely, "nieistniejacy_plik_xyz.txt")
    finally:
        # Sprzątanie
        for f in (test_file_in, test_file_out):
            if os.path.exists(f):
                os.remove(f)

    print("\n" + "=" * 70)
    print(f"PODSUMOWANIE TESTÓW: ZALICZONO {passed_count}/{total_tests} "
          f"({(passed_count / total_tests) * 100:.1f}%)")
    print("=" * 70 + "\n")


# ==============================================================================
# GENERATOR PLIKÓW PRZYKŁADOWYCH (POMOCNIK DO ĆWICZEŃ)
# ==============================================================================

def create_sample_files():
    """Generuje przykładowe pliki z poprawnymi danymi do natychmiastowych testów."""
    samples = {
        "tekst_26.txt": "TAJNAWIADOMOSCDOPRZESLANIA",
        "klucz_vigenere_26.txt": "KLUCZ",
        "klucz_hill_2x2_26.txt": "HILL",       # 2x2 invertible mod 26
        "klucz_hill_3x3_26.txt": "GYBNQKURP",  # 3x3 invertible mod 26 (Lester Hill 1929)
        "tekst_rozszerzony.txt": "Tajny Raport: 123_!() - Haslo OK",
        "klucz_vigenere_ext.txt": "Sekret#2026",
        "klucz_hill_nieodwracalny.txt": "ABCD" # det mod 26 = 24 (NWD = 2, nieodwracalny)
    }

    folder = "przyklady"
    os.makedirs(folder, exist_ok=True)
    for fname, content in samples.items():
        path = os.path.join(folder, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"\n\033[92m[OK] Utworzono przykładowe pliki w katalogu '{folder}/':\033[0m")
    for fname in samples.keys():
        print(f"  - {folder}/{fname}")
    print()


# ==============================================================================
# INTERAKTYWNE MENU KONSOLOWE (FOOLPROOF)
# ==============================================================================

def get_user_choice(prompt: str, valid_options: list) -> str:
    """Pobiera i waliduje wybór użytkownika z menu."""
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"\033[91mNiepoprawny wybór! Dozwolone opcje: {', '.join(valid_options)}\033[0m")


def get_existing_file_path(prompt: str) -> str:
    """Pobiera ścieżkę do istniejącego pliku z możliwością rezygnacji."""
    while True:
        path = input(prompt).strip()
        if path.lower() == 'q':
            return ""
        if os.path.isfile(path):
            return path
        print(f"\033[91mPlik '{path}' nie istnieje lub nie jest plikiem! (Wpisz 'q' aby anulować)\033[0m")


def interactive_mode():
    """Główna pętla trybu interaktywnego."""
    while True:
        print("\n" + "=" * 60)
        print("          TRYB SZYFROWANIA / DESZYFROWANIA")
        print("=" * 60)
        print("Wybierz szyfr:")
        print(" [1] Szyfr Vigenère'a")
        print(" [2] Szyfr Hilla")
        print(" [0] Wróć do menu głównego")

        cipher_choice = get_user_choice("\nTwój wybór: ", ["1", "2", "0"])
        if cipher_choice == "0":
            break

        print("\nWybierz operację:")
        print(" [1] Szyfrowanie")
        print(" [2] Deszyfrowanie")
        op_choice = get_user_choice("Twój wybór: ", ["1", "2"])
        is_encrypt = (op_choice == "1")

        print("\nWybierz alfabet:")
        print(" [1] Standardowy 26-znakowy (tylko wielkie litery A-Z)")
        print(" [2] Rozszerzony 67-znakowy (A-Z, 0-9, spacja, znaki specjalne)")
        alpha_choice = get_user_choice("Twój wybór: ", ["1", "2"])
        is_extended = (alpha_choice == "2")

        print("\n--- Podaj ścieżki do plików ---")
        in_path = get_existing_file_path("Ścieżka do pliku wejściowego (tekst do przetworzenia): ")
        if not in_path:
            continue

        key_path = get_existing_file_path("Ścieżka do pliku z kluczem: ")
        if not key_path:
            continue

        out_path = input("Ścieżka do pliku wynikowego (gdzie zapisać rezultat): ").strip()
        while not out_path:
            out_path = input("Ścieżka nie może być pusta! Podaj ścieżkę: ").strip()

        # Wykonanie operacji z pełnym przechwytywaniem błędów
        try:
            input_text = read_file_safely(in_path)
            key_text = read_file_safely(key_path)

            print("\nPrzetwarzanie danych...")
            if cipher_choice == "1":
                # Vigenère
                if is_encrypt:
                    result = VigenereCipher.encrypt(input_text, key_text, is_extended)
                else:
                    result = VigenereCipher.decrypt(input_text, key_text, is_extended)
            else:
                # Hill
                if is_encrypt:
                    result, pad_count = HillCipher.encrypt(input_text, key_text, is_extended)
                    if pad_count > 0:
                        print(f"\033[93m[INFO] Tekst został uzupełniony znakiem 'X' (padding = {pad_count}) "
                              f"do wielokrotności bloku macierzy.\033[0m")
                else:
                    result = HillCipher.decrypt(input_text, key_text, is_extended)

            write_file_safely(out_path, result)

            print("\n" + "-" * 50)
            print("\033[92mSUKCES! Operacja zakończona powodzeniem.\033[0m")
            print(f"Wynik zapisano w pliku: '{out_path}'")
            print(f"Podgląd wyniku (pierwsze 100 znaków):\n{result[:100]}")
            if len(result) > 100:
                print("... [skrócono]")
            print("-" * 50)

        except Exception as err:
            print("\n\033[91m" + "!" * 50)
            print(f"BŁĄD: {str(err)}")
            print("Operacja została przerwana. Żaden plik wyjściowy nie został uszkodzony.")
            print("!" * 50 + "\033[0m")

        input("\nNaciśnij [Enter], aby kontynuować...")


def main():
    while True:
        print("\n" + "=" * 60)
        print("        KRYPTOLOGIA - PROJEKT: VIGENÈRE & HILL")
        print("=" * 60)
        print(" [1] Uruchom program (Szyfrowanie / Deszyfrowanie)")
        print(" [2] Uruchom zestaw testów automatycznych")
        print(" [3] Wygeneruj przykładowe pliki z danymi (katalog 'przyklady/')")
        print(" [0] Zakończ program")

        choice = get_user_choice("\nWybierz opcję: ", ["1", "2", "3", "0"])

        if choice == "1":
            interactive_mode()
        elif choice == "2":
            run_all_tests()
            input("Naciśnij [Enter], aby wrócić do menu...")
        elif choice == "3":
            create_sample_files()
            input("Naciśnij [Enter], aby wrócić do menu...")
        elif choice == "0":
            print("\nKoniec programu. Powodzenia na obronie projektu!")
            sys.exit(0)


if __name__ == "__main__":
    main()