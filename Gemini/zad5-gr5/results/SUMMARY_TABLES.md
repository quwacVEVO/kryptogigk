# Zestawienie tabelaryczne wyników eksperymentów — Lab 05, Grupa 5

Środowisko: Python 3.11.2 (Linux x86_64), zegar: `time.perf_counter_ns()`.

## 1. LFSR — Weryfikacja przykładów z notatki (32 bity)

| Przykład | Długość n | Wektor p | Ziarno | Cykl stanu | Maks. 2^n - 1 | Pełny? | Pierwsze 32 bity |
| --- | ---: | --- | --- | ---: | ---: | --- | --- |
| Przykład 1 (n=3) | 3 | `(1, 1, 0)` | `(0, 0, 1)` | 7 | 7 | Tak | `00101110010111001011100101110010` |
| Przykład 2 (n=4, pierwotny) | 4 | `(1, 1, 0, 0)` | `(0, 0, 0, 1)` | 15 | 15 | Tak | `00010011010111100010011010111100` |
| Przykład 3 (n=4, niepierwotny) | 4 | `(1, 1, 1, 1)` | `(1, 0, 0, 1)` | 5 | 15 | Nie | `10010100101001010010100101001010` |
| Przykład 4 (n=6) | 6 | `(1, 1, 0, 1, 1, 0)` | `(0, 0, 1, 0, 0, 1)` | 63 | 63 | Tak | `00100100001110000010111111001010` |

## 2. LFSR — Wpływ długości, odczepów i ziarna (K=200, [1000, 100000])

| Konfiguracja | n | Odczepy | Mapowanie | Cykl stanu | Unikalne | Kolizje | Odsetek kolizji |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| n=8, pierwotny (0,2,3,4), ziarno A | 8 | `(0, 2, 3, 4)` | `mod` | 255 / 255 | 15 | 185 | 92.50% |
| n=8, słabe odczepy (0,4), ziarno A | 8 | `(0, 4)` | `mod` | 12 / 255 | 12 | 188 | 94.00% |
| n=12, pierwotny (0,1,4,6), ziarno A | 12 | `(0, 1, 4, 6)` | `mod` | 4095 / 4095 | 200 | 0 | 0.00% |
| n=12, niepierwotny (0,6), ziarno A | 12 | `(0, 6)` | `mod` | 18 / 4095 | 18 | 182 | 91.00% |
| n=16, pierwotny (0,2,3,5), ziarno A | 16 | `(0, 2, 3, 5)` | `mod` | 65535 / 65535 | 200 | 0 | 0.00% |
| n=16, niepierwotny (0,8), ziarno A | 16 | `(0, 8)` | `mod` | 24 / 65535 | 24 | 176 | 88.00% |
| n=17, pierwotny (0,3), ziarno B (000...001) | 17 | `(0, 3)` | `mod` | 131071 / 131071 | 200 | 0 | 0.00% |
| n=17, pierwotny (0,3), ziarno A (bazowe, mod) | 17 | `(0, 3)` | `mod` | 131071 / 131071 | 200 | 0 | 0.00% |
| n=17, pierwotny (0,3), ziarno A (rejection) | 17 | `(0, 3)` | `rejection` | 131071 / 131071 | 200 | 0 | 0.00% |

## 3. LCG — Porównanie zestawów parametrów m, a, c, x0 (K=200, [1000, 100000])

| Konfiguracja | m | Hull–Dobell | Przedcykl mu | Cykl stanu lambda | Mapowanie | Unikalne | Kolizje | Parzyste |
| --- | ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| Przykładowe (slajd PG: m=15, a=51, c=13) | 15 | Nie | 0 | 5 | `scale` | 5 | 195 | 100.0% |
| Złe parametry z przedcyklem (m=1024, a=12, c=4) | 1024 | Nie | 5 | 1 | `scale` | 5 | 195 | 1.5% |
| Slajd PG (m=134456, a=8121, c=28411, x0=55) | 134456 | Tak | 0 | 134456 | `scale` | 200 | 0 | 57.5% |
| Slajd PG (m=134456, a=8121, c=28411, x0=999) | 134456 | Tak | 0 | 134456 | `scale` | 200 | 0 | 52.5% |
| Microsoft Visual Basic (m=2^24) | 16777216 | Tak | 0 | 16777216 | `scale` | 200 | 0 | 47.5% |
| ANSI C (m=2^31, x0=123456, scale — bazowe) | 2147483648 | Tak | 0 | 2147483648 | `scale` | 200 | 0 | 49.5% |
| ANSI C (m=2^31, x0=123456, mod) | 2147483648 | Tak | 0 | 2147483648 | `mod` | 200 | 0 | 49.5% |
| Borland C/C++ (m=2^32, scale) | 4294967296 | Tak | 0 | 4294967296 | `scale` | 200 | 0 | 50.0% |
| Java java.util.Random (m=2^48, scale) | 281474976710656 | Tak | 0 | 281474976710656 | `scale` | 200 | 0 | 49.5% |

## 4. Testy pierwszości — Statystyki czasów i skuteczności (K=200 na źródło, s=10)

### Zbiór LFSR (liczby pierwsze rzeczywiste: 14, złożone: 186, budowa sita do 314: 69.021 us)

| Test | Pomiary | Min [us] | Mediana [us] | Średnia [us] | Max [us] | Pseudopierwsze (FP) | Pseudozłożone (FN) | Trafność |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dzielenie przez liczby pierwsze | 200 | 0.410 | 0.471 | 1.555 | 87.432 | 0 | 0 | 100.00% |
| Test Fermata (s=10) | 200 | 0.560 | 1.115 | 5.701 | 47.671 | 0 | 0 | 100.00% |
| Test Millera–Rabina (s=10) | 200 | 0.550 | 0.885 | 7.601 | 243.356 | 0 | 0 | 100.00% |

### Zbiór LCG (liczby pierwsze rzeczywiste: 18, złożone: 182, budowa sita do 315: 33.991 us)

| Test | Pomiary | Min [us] | Mediana [us] | Średnia [us] | Max [us] | Pseudopierwsze (FP) | Pseudozłożone (FN) | Trafność |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dzielenie przez liczby pierwsze | 200 | 0.410 | 0.795 | 1.330 | 31.571 | 0 | 0 | 100.00% |
| Test Fermata (s=10) | 200 | 0.569 | 4.320 | 6.192 | 52.471 | 0 | 0 | 100.00% |
| Test Millera–Rabina (s=10) | 200 | 0.570 | 5.200 | 7.378 | 61.332 | 0 | 0 | 100.00% |

## 5. Skalowanie czasów testów pierwszości dla różnych rozmiarów liczb (40 kandydatów/przedział, s=10)

| Przedział | Prawdziwe pierwsze | Sito [us] | Dzielenie średnia [us] | Fermat średnia [us] | Miller–Rabin średnia [us] |
| --- | ---: | ---: | ---: | ---: | ---: |
| [10^3, 10^4] (~4 cyfry) | 15/40 | 17.1 | 1.540 | 18.664 | 21.585 |
| [10^5, 10^6] (~6 cyfr) | 12/40 | 79.9 | 6.360 | 20.088 | 24.140 |
| [10^7, 10^8] (~8 cyfr) | 7/40 | 761.0 | 35.084 | 24.071 | 28.515 |
| [10^9, 10^10] (~10 cyfr) | 7/40 | 7105.5 | 293.899 | 31.616 | 36.367 |
| [10^11, 10^12] (~12 cyfr) | 10/40 | 70279.7 | 1218.479 | 53.044 | 53.519 |

## 6. Wpływ liczby iteracji s (20 liczb Carmichaela + 20 pierwszych + 20 złożonych)

| Iteracje s | Fermat średnia [us] | Fermat FP (Carmichael) | Miller–Rabin średnia [us] | Miller–Rabin FP (Carmichael) | Miller–Rabin FN |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5.220 | 17 (17/20) | 9.786 | 1 (1/20) | 0 |
| 2 | 11.431 | 15 (15/20) | 12.379 | 0 (0/20) | 0 |
| 3 | 13.799 | 11 (11/20) | 14.910 | 0 (0/20) | 0 |
| 5 | 13.837 | 1 (1/20) | 13.184 | 0 (0/20) | 0 |
| 10 | 24.106 | 1 (1/20) | 31.558 | 0 (0/20) | 0 |
| 20 | 45.748 | 1 (1/20) | 37.165 | 0 (0/20) | 0 |
| 40 | 67.245 | 0 (0/20) | 70.343 | 0 (0/20) | 0 |
