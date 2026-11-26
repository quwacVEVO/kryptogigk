# Lista kontrolna wymagań — lab05, grupa 5 (GenAI), przebieg Opus 5 / effort high

Statusy: `niezaczęte` / `w toku` / `wykonane i sprawdzone` / `zablokowane`.
**„Wykonane i sprawdzone”** = kod napisany **oraz** uruchomiony, a wynik potwierdzony
testem, wydrukiem lub plikiem wynikowym (kolumna „dowód”). Nigdzie nie oznaczam jako
wykonanego czegoś, co zostało tylko napisane.

Źródła wymagań: `Kryptologia-lab05_zadania-1.pdf` (zakres), `zad5/README.md` (harmonogram,
sposób oddania), `Kryptologia-lab05. Generatory pseudolosowe i testy pierwszości.pdf` (definicje).
Stan na: **25.11.2026, koniec sesji** (po pełnym przebiegu `python3 run_all.py`).

Podsumowanie: **45 pozycji wykonanych i sprawdzonych, 0 w toku, 0 niezaczętych,
3 zablokowane** (wymagają danych od ludzi lub przebiegów innych modeli).

## A. LFSR (zakres grupy 1)

| # | Wymaganie | Status | Dowód |
|---|---|---|---|
| A1 | LFSR w Pythonie: konfigurowalna długość rejestru, odczepy, ziarno | wykonane i sprawdzone | `lfsr.py` (klasa `LFSR`, `from_tap_indices`); CLI `python3 lfsr.py --n … --taps … --seed …`; `test_lfsr.py` |
| A2 | Jednoznaczny opis stanu, numeracji odczepów, kierunku przesuwania, bitu wyjściowego + zgodność z notatką | wykonane i sprawdzone | docstring `lfsr.py` + `README.md` §3; `test_lfsr.TestPrzykladyZNotatki` — 4 przykłady z notatki, okresy 7, 15, 5, 63, pierwszy sprawdzony stan po stanie |
| A3 | Generowanie K liczb z [a,b] i zapis do pliku tekstowego | wykonane i sprawdzone | `results/lfsr_numbers_main.txt` (K=200, [1,1000]) |
| A4 | Opis składania bitów w liczby i mapowania wraz z ograniczeniami | wykonane i sprawdzone | docstring `LFSR.numbers` (tryby `reject`/`mod`, 10 bitów na liczbę, zmienna liczba zużytych bitów); `README.md` §3 |
| A5 | Wykrywanie powtórzeń/kolizji w liczbach + definicja kolizji | wykonane i sprawdzone | `common.collision_report` (definicja w docstringu); wynik: 18 kolizji / 182 różnych — `results/lfsr_analysis.md` §1 |
| A6 | Długość cyklu **stanu** oraz osobno cykl ciągu wartości | wykonane i sprawdzone | okres stanu 65535 (ogon 0), okres wartości 12801 — `results/lfsr_analysis.md` §1; metody `LFSR.period`, `exp_lfsr.measure_value_period` |
| A7 | Rzeczywisty ciąg K liczb bez powtórzeń + pełne parametry | wykonane i sprawdzone | `results/lfsr_numbers_unique.txt` (K=200 filtrem) oraz `results/lfsr_numbers_raw_unique.txt` (K=50, [1,10000], ziarno 0x0002, bez filtru) |
| A8 | Sprawdzenie warunku K ≤ b − a + 1 i reakcja, gdy niespełniony | wykonane i sprawdzone | `lfsr.check_k_fits_interval`; przypadek K=1500 odrzucony wyjątkiem — `results/lfsr_analysis.md` §2, `results/error_handling.md` |
| A9 | Analiza wpływu długości rejestru, odczepów i ziarna + tabele i wnioski | wykonane i sprawdzone | 3 tabele w `results/lfsr_analysis.md` §3–5; wnioski w `REPORT.md` §3 |
| A10 | DODATKOWO: obsługa niepoprawnych parametrów | wykonane i sprawdzone | 13 przypadków LFSR w `results/error_handling.md` §1 (0 nieodrzuconych) |
| A11 | DODATKOWO: obsługa braku pliku i błędnego formatu danych | wykonane i sprawdzone | 6 przypadków w `results/error_handling.md` §2; `common.read_numbers`; `test_common.TestPlikiZLiczbami` |
| A12 | DODATKOWO: porównanie kilku konfiguracji odczepów | wykonane i sprawdzone | 7 konfiguracji, okresy 11–65535 — `results/lfsr_analysis.md` §4 |
| A13 | DODATKOWO: testy poprawności implementacji (przykłady z notatki, ziarno zerowe, przypadki brzegowe) | wykonane i sprawdzone | `test_lfsr.py` — 36 testów, w tym ziarno zerowe, granice przedziału, przedział jednoelementowy, odtwarzalność pliku |

## B. LCG (zakres grupy 2)

| # | Wymaganie | Status | Dowód |
|---|---|---|---|
| B1 | LCG `x_{i+1} = (a·x_i + c) mod m` z konfigurowalnymi m, a, c, x0 | wykonane i sprawdzone | `lcg.py` (klasa `LCG`), CLI; `test_lcg.TestZgodnoscZRownaniem` (100 kolejnych stanów zgodnych z wzorem) |
| B2 | Objaśnienie oznaczeń (`c` = `b` z notatki vs prawa granica `[a,b]`) | wykonane i sprawdzone | docstring `lcg.py`; `README.md` §3; `REPORT.md` §1 pkt 2 |
| B3 | Generowanie K liczb z [a,b] + zapis do pliku | wykonane i sprawdzone | `results/lcg_numbers_main.txt` (K=200, [1,1000]) |
| B4 | Jawny opis mapowania stanu do przedziału | wykonane i sprawdzone | docstring `LCG.numbers` (3 tryby: `mod_reject`, `mod`, `scale`); `README.md` §3 |
| B5 | Wykrywanie powtórzeń/kolizji wynikowych liczb | wykonane i sprawdzone | 22 kolizje / 178 różnych — `results/lcg_analysis.md` §1 |
| B6 | Długość cyklu stanu + część przedcykliczna, odróżnione od powtórzeń po mapowaniu | wykonane i sprawdzone | okres stanu 65536 (ogon 0) vs okres wartości 65000 — `results/lcg_analysis.md` §1; ogony 1 i 15 dla zdegenerowanych zestawów — §3 |
| B7 | Ciąg K liczb bez powtórzeń + kompletne parametry, warunek K ≤ b−a+1 | wykonane i sprawdzone | `results/lcg_numbers_unique.txt`; `results/lcg_numbers_raw_unique.txt` (m=1024, a=5, c=1 — 0 kolizji bez filtru, także dla K=1024 = b−a+1) |
| B8 | Wpływ m, a, c, x0 — tabele i wnioski; bez ogłaszania okresu maksymalnego bez sprawdzenia | wykonane i sprawdzone | 13 zestawów + tabela ziaren + tabela mapowań — `results/lcg_analysis.md` §3–5; warunki Hull–Dobella liczone osobno (`lcg.hull_dobell`), okres nieustalony oznaczony jawnie |
| B9 | DODATKOWO: błędne parametry, brak pliku, błędny format | wykonane i sprawdzone | 9 przypadków LCG + 6 plikowych w `results/error_handling.md` |
| B10 | DODATKOWO: porównanie kilku zestawów parametrów | wykonane i sprawdzone | `results/lcg_analysis.md` §3 (w tym ANSI C, Borland, MSVC, VB, Java, przykład z notatki, 4 zdegenerowane) |
| B11 | DODATKOWO: testy poprawności (zgodność stanów z równaniem) | wykonane i sprawdzone | `test_lcg.py` — 29 testów, w tym zgodność warunków Hull–Dobella ze zmierzonym okresem i odtwarzalność pliku |

## C. Testy pierwszości (zakres grupy 3)

| # | Wymaganie | Status | Dowód |
|---|---|---|---|
| C1 | Dokładny test dzielenia przez **liczby pierwsze** do ⌊√n⌋ | wykonane i sprawdzone | `primality.trial_division_is_prime` + własne sito; zgodność z sitem dla wszystkich n ∈ [0, 20000] i `π(10^6) = 78498` — `test_primality.TestSitoIDzielenieProbne` |
| C2 | Własne szybkie potęgowanie binarne modulo n, użyte w testach | wykonane i sprawdzone | `primality.pow_mod` (wg `pot_mod2`); `pow_mod(5,100,22)=1` jak w notatce; zgodność z wbudowanym `pow` na 5000 losowych przypadkach |
| C3 | Test Fermata z losowanymi podstawami z {2,…,n−2} | wykonane i sprawdzone | `primality.fermat_is_probably_prime`; `test_primality` (m.in. akceptuje wszystkie 669 liczb pierwszych < 5000) |
| C4 | Test Millera–Rabina z konfigurowalną, ustaloną liczbą iteracji | wykonane i sprawdzone | `primality.miller_rabin_is_probably_prime`, `s = 5` w `params.py`; zgodny z dokładnym testem dla wszystkich n ∈ [2, 3000] przy s = 20 |
| C5 | Obsługa n < 2, 2, 3, liczb parzystych, zakresu podstaw | wykonane i sprawdzone | `primality._trivial_case`; `test_primality.TestPrzypadkiBrzegoweTestow`; tabela brzegowa w `results/primality_analysis.md` §3 |
| C6 | Udokumentowane ziarno losowania (odtwarzalność) | wykonane i sprawdzone | `params.RNG_SEED = 12345`, nowy `random.Random` dla każdego testu i scenariusza — opis w `results/primality_analysis.md` §0; test odtwarzalności decyzji |
| C7 | Każdy test na liczbach z LFSR **i** LCG: wynik + czas każdego wywołania, z identyfikacją źródła | wykonane i sprawdzone | `results/primality_calls_lfsr.csv` i `…_lcg.csv` — 1200 wierszy (źródło, pozycja, n, test, wynik, czas_ns) |
| C8 | Statystyki czasu osobno dla każdego testu: min, max, średnia, mediana + liczba pomiarów i jednostki | wykonane i sprawdzone | `results/primality_analysis.md` §1 (+ §1b: rozbicie na grupy wobec rozkładu dwumodalnego) |
| C9 | Rzeczywisty status pierwszości wybranego zbioru **niezależną metodą dokładną** | wykonane i sprawdzone | podstawa: dokładne dzielenie; zbiór: 182 unikalne liczby z LFSR i 178 z LCG — `results/primality_analysis.md` §2 |
| C10 | Liczba pseudopierwszych i pseudozłożonych | wykonane i sprawdzone | 0 i 0 przy s = 5 (z wyjaśnieniem); Fermat przy s = 1 → 3 pseudopierwsze (39, 435, 635), przy s = 3 → 561 — §2 i §5 |
| C11 | Porównanie szybkości, wiarygodności i liczby błędnych decyzji + najlepszy test dla zmierzonego scenariusza | wykonane i sprawdzone | `REPORT.md` §5 (tabela porównawcza + rozstrzygnięcie z ograniczeniami) |
| C12 | DODATKOWO: czasy w różnych przedziałach i dla różnych rozmiarów liczb | wykonane i sprawdzone | 4 przedziały (10^3…10^12), 1440 pomiarów — `results/primality_analysis.md` §6 |
| C13 | DODATKOWO: wpływ liczby iteracji Millera–Rabina | wykonane i sprawdzone | `s ∈ {1,2,3,5,10,20,40}` dla M–R i (dla porównania) Fermata — §5 |
| C14 | DODATKOWO: testy poprawności metod, przypadki brzegowe, liczby mylące Fermata | wykonane i sprawdzone | `test_primality.py` — 33 testy; wyczerpujące przeliczenie kłamców dla 10 liczb Carmichaela (kontrola: 318 = φ(561) − 2) — §4 |

## D. Zakres grupy 5 (GenAI)

| # | Wymaganie | Status | Dowód |
|---|---|---|---|
| D1 | Podział wyników na LFSR / LCG / pierwszość + jedna odtwarzalna całość | wykonane i sprawdzone | osobne moduły i pliki wynikowe; `run_all.py` scala wszystko w jeden przebieg (10,6 s) |
| D2 | Format odpowiedzi, weryfikacji i dokumentowania procesu | wykonane i sprawdzone | `GENAI_LOG.md` §3 (7 zasad, m.in. rozdzielenie pomiaru od interpretacji i weryfikacja trójstronna) |
| D3 | Zapis modelu i wersji, promptów/korekt, co powstało z pomocą modelu | wykonane i sprawdzone | `GENAI_LOG.md` §1, §2, §5 (bez dopisywania nieodbytych rozmów; brak danych o tokenach odnotowany jako brak) |
| D4 | Zauważone błędy modelu i poprawki | wykonane i sprawdzone | `GENAI_LOG.md` §4 — 10 pozycji z kolumną „jak wykryto” |
| D5 | Wyniki w formie umożliwiającej porównanie modeli na tych samych wejściach/kryteriach/środowisku | wykonane i sprawdzone | `params.py` jako umowa wejść, `results/benchmark.json` (parametry, wyniki deterministyczne, czasy, środowisko) + sumy SHA-256 plików z liczbami; instrukcja w `README.md` §4 i `GENAI_LOG.md` §6 |
| D6 | Ograniczona samoocena przebiegu | wykonane i sprawdzone | `REPORT.md` §11 (co zrobiono, 10 błędów, pozostałe ryzyka, czego brakuje) |
| D7 | Materiał do sprawozdania grupy 5 | wykonane i sprawdzone | `REPORT.md` (11 sekcji: metoda, parametry, tabele, wyniki, interpretacja, problemy, czego nie zrobiono, zakres AI/człowieka) |
| D8 | Rzeczywisty nakład pracy człowieka (pełne godziny) | **zablokowane** | brak danych; nie wymyślam roboczogodzin. Tabela do uzupełnienia: `REPORT.md` §10. Podany jedynie wall-clock sesji modelu, jawnie oznaczony jako **nie** roboczogodzina człowieka |
| D9 | Porównanie różnych modeli GenAI i wskazanie najlepszego dla każdego typu zadania | **zablokowane** | wymaga ≥ 2 dalszych przebiegów na tym samym `params.py`; format i instrukcja gotowe (`README.md` §4) |
| D10 | Łączna liczba błędów między modelami i przekrojowe rekomendacje | **zablokowane** | wymaga dzienników `GENAI_LOG.md` z pozostałych przebiegów |

## Kontrole wykonane przed zakończeniem pracy

Zgodnie z wymaganiem „wróć do listy po implementacji każdego generatora, po testach
pierwszości i przed zakończeniem”:

| moment | co sprawdzono | wynik |
|---|---|---|
| po LFSR | przykłady z notatki, okres maksymalny, ziarno zerowe, granice przedziału, odtwarzalność pliku | OK; dodany pomiar okresu ciągu wartości jako osobnej miary |
| po LCG | zgodność stanów z równaniem, Hull–Dobell vs okres zmierzony, ogony zestawów zdegenerowanych | OK; dodany tryb `scale` i komunikat dla `m < span` |
| po testach pierwszości | `pow_mod` vs `pow`, dzielenie vs sito do 20000, M–R vs dokładny test do 3000, liczby brzegowe i Carmichaela | OK; dodane rozbicie czasów na grupy i rozgrzewka pomiaru |
| przed zakończeniem | pełny `run_all.py` (117 testów + 3 części + 28 przypadków błędnych), przegląd wszystkich plików `results/`, uzupełnienie tej listy | OK; 0 niezaliczonych testów, 0 nieodrzuconych błędów |
