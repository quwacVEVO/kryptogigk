# Instrukcja uruchomienia — `zad5-gr5` (Kryptologia Lab 05, Grupa 5)

## Wymagania
- Python 3.10+ (zweryfikowano na Python 3.11.2, wyłącznie biblioteka standardowa — brak zależności zewnętrznych).

## Struktura katalogu `zad5-gr5/`
- `lfsr.py` — generator LFSR, mapowanie `mod`/`rejection`, analiza kolizji, wykrywanie cyklu stanu i słów, zapis/odczyt z pliku z kontrolą błędów.
- `lcg.py` — generator LCG, weryfikacja twierdzenia Hulla–Dobella, wykrywanie przedcyklu $\mu$ i cyklu $\lambda$ metodą Floyda, mapowanie `scale`/`mod`, zapis/odczyt z pliku.
- `primality.py` — własne szybkie potęgowanie binarne `mod_pow_binary`, test dzielenia przez liczby pierwsze do $\lfloor\sqrt{n}\rfloor$, niezależny wzorzec dokładny ($6k\pm 1$), test Fermata, test Millera–Rabina, benchmark z `time.perf_counter_ns()`.
- `run_experiments.py` — główny skrypt odtwarzający wszystkie zbiory danych, pliki CSV, tabele Markdown oraz plik JSON wyników.
- `tests/test_all.py` — 16 testów jednostkowych (`unittest`) pokrywających przypadki znane z notatki, przypadki brzegowe, błędy I/O, liczby Carmichaela i spójność statystyk.
- `data/` — wygenerowane pliki tekstowe (`lfsr_numbers.txt`, `lfsr_no_collisions.txt`, `lcg_numbers.txt`, `lcg_no_collisions.txt`).
- `results/` — wyniki szczegółowe (`primality_lfsr_results.csv`, `primality_lcg_results.csv`, `experiment_results.json`, `SUMMARY_TABLES.md`).
- `SPRAWOZDANIE_GRUPA5.md` — kompletny materiał do sprawozdania Grupy 5.

## Komendy uruchomienia i weryfikacji

```bash
# 1. Uruchomienie testów poprawności (16 testów jednostkowych)
python3 -m unittest discover -s zad5-gr5/tests -v

# 2. Odtworzenie wszystkich plików danych, CSV i tabel porównawczych
python3 zad5-gr5/run_experiments.py
```
