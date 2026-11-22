# Lista kontrolna wymagań

Statusy: `niezaczęte / w toku / wykonane i sprawdzone / zablokowane`.

## LFSR

| Wymaganie | Status | Dowód |
|---|---|---|
| Konfigurowalna długość, odczepy i ziarno | wykonane i sprawdzone | `src/lab05/generators.py`, testy parametrów |
| Jawna reprezentacja, numeracja, przesuwanie i bit wyjściowy | wykonane i sprawdzone | `README.md`, docstring klasy `LFSR` |
| Zgodność z rekurencją i przykładem notatki | wykonane i sprawdzone | test ciągu `0010111`, okres 7 |
| Generowanie K liczb z `[a,b]` | wykonane i sprawdzone | `data/lfsr_numbers.txt`, 200 liczb w `[10000,59999]` |
| Zapis do pliku tekstowego | wykonane i sprawdzone | round-trip w `tests/test_io.py` |
| Jawne składanie bitów i mapowanie | wykonane i sprawdzone | MSB-first + rejection sampling, `README.md` |
| Powtórzenia/kolizje wynikowych liczb | wykonane i sprawdzone | `generator_summary.csv` i trzy definicje kolizji |
| Długość cyklu pełnego stanu | wykonane i sprawdzone | okres 65535, ponownie sprawdzany przez `verify_results.py` |
| Rzeczywisty ciąg bez kolizji i komplet parametrów | wykonane i sprawdzone | K=200, `[10000,59999]`, 200 wartości unikalnych |
| Sprawdzenie `K <= b-a+1` | wykonane i sprawdzone | `verify_results.py` |
| Wpływ długości, odczepów i ziarna | wykonane i sprawdzone | 7 konfiguracji w `parameter_analysis.csv` |
| Ziarno zerowe i przypadki brzegowe | wykonane i sprawdzone | okres 1; test jednostkowy |
| Kontrola błędnych parametrów | wykonane i sprawdzone | testy pustych/duplikowanych odczepów, bitów i długości |
| Brak pliku i błędny format wejścia | wykonane i sprawdzone | `tests/test_io.py` |
| Brak zawieszenia przy niemożliwym rejection samplingu | wykonane i sprawdzone | wykrycie powrotu stanu i test regresji |

## LCG

| Wymaganie | Status | Dowód |
|---|---|---|
| Implementacja `x_(i+1)=(a*x_i+c) mod m` | wykonane i sprawdzone | `src/lab05/generators.py`, test znanych stanów |
| Wyjaśnienie `b` z notatki a `c` w kodzie | wykonane i sprawdzone | `README.md`, docstring `LCG` |
| Generowanie K liczb z `[a,b]` i zapis | wykonane i sprawdzone | `data/lcg_numbers.txt`, round-trip |
| Jawne mapowanie bez obciążenia modulo | wykonane i sprawdzone | rejection sampling; wymagane `b-a+1 <= m` |
| Kolizje wartości i cykl stanu/przedcykl | wykonane i sprawdzone | `generator_summary.csv`, `parameter_analysis.csv` |
| Rzeczywisty ciąg bez kolizji i komplet parametrów | wykonane i sprawdzone | K=200, `[10000,59999]`, 200 wartości unikalnych |
| Wpływ `m,a,c,x0` | wykonane i sprawdzone | 5 konfiguracji w `parameter_analysis.csv` |
| Pełny okres bez gołosłownego twierdzenia | wykonane i sprawdzone | warunki Hulla-Dobella + pomiar okresu 65536 |
| Błędne parametry, brak pliku, format | wykonane i sprawdzone | testy jednostkowe i I/O |
| Brak zawieszenia przy niemożliwym mapowaniu | wykonane i sprawdzone | wykrycie powrotu stanu i test regresji |

## Pierwszość

| Wymaganie | Status | Dowód |
|---|---|---|
| Dokładne dzielenie przez liczby pierwsze do `floor(sqrt(n))` | wykonane i sprawdzone | sito + `prime_division_test` |
| Własne szybkie potęgowanie binarne | wykonane i sprawdzone | 500 porównań z referencyjnym `pow` |
| Fermat z losowymi podstawami | wykonane i sprawdzone | stałe ziarno, 5 iteracji |
| Miller-Rabin z konfigurowalną liczbą iteracji | wykonane i sprawdzone | 1, 3, 5 i 10 iteracji |
| `0,1,2,3`, parzyste, pierwsze i złożone | wykonane i sprawdzone | `tests/test_primality.py` |
| Trudny przypadek Fermata | wykonane i sprawdzone | 561 przechodzi Fermata dla podstawy 2, MR odrzuca |
| Każdy test na danych LFSR i LCG | wykonane i sprawdzone | 1200 wierszy w `primality_measurements.csv` |
| Wynik i czas każdego wywołania | wykonane i sprawdzone | `result`, `truth`, `elapsed_ns` w surowym CSV |
| Min, max, średnia, mediana, N i jednostka | wykonane i sprawdzone | `primality_summary.csv`, `perf_counter_ns` |
| Niezależny dokładny status i błędy obu kategorii | wykonane i sprawdzone | `error_summary.csv`, weryfikacja ponownym dokładnym testem |
| Porównanie szybkości, wiarygodności i wybór | wykonane i sprawdzone | `REPORT_RESULTS.md`, `SPRAWOZDANIE_MATERIAL.md` |
| Różne zakresy/rozmiary liczb | wykonane i sprawdzone | 3-, 5- i 7-cyfrowe w `range_comparison.csv` |
| Wpływ iteracji MR | wykonane i sprawdzone | `mr_iterations.csv` |
| Zgodność statystyk z surowymi wynikami | wykonane i sprawdzone | `verify_results.py` zakończony `OK` |

## Grupa 5

| Wymaganie | Status | Dowód |
|---|---|---|
| Realizacja zakresu grup 1-3 z GenAI | wykonane i sprawdzone | kompletny projekt i wyniki |
| Podział LFSR/LCG/pierwszość | wykonane i sprawdzone | moduły, testy i tabele |
| Format współpracy i weryfikacji | wykonane i sprawdzone | `GENAI_PROCESS.md`, testy, weryfikator |
| Model/wersja, prompty, poprawki, zakres AI/człowieka | wykonane i sprawdzone w dostępnym zakresie | nieznana dokładna wersja oznaczona jako nieujawniona |
| Materiał do własnego sprawozdania | wykonane i sprawdzone | `SPRAWOZDANIE_MATERIAL.md` |
| Próba wszystkich wymagań dodatkowych | wykonane i sprawdzone | obsługa błędów, warianty parametrów, zakresy, iteracje, testy |
| Terminy z README | wykonane i sprawdzone | 26.11.2026 13:30; 30.11.2026 18:00; sprawozdanie na drugi termin |
| Rzeczywiste roboczogodziny członków | zablokowane | zespół musi wpisać własne czasy; nie wolno ich wymyślać |
| Porównanie kilku modeli na identycznych warunkach | zablokowane | dostępny jest jeden przebieg |
| Ostateczny najlepszy model i przekrojowa liczba błędów | zablokowane | wymaga wyników innych modeli |
| Sprawozdanie główne grupy 4 | niezaczęte - poza zakresem | grupa 5 przygotowuje tylko własne sprawozdanie |

## Końcowa kontrola wykonana

- `PYTHONPATH=src python3 -m unittest discover -s tests -v` - 27/27 testów `OK`;
- `PYTHONPATH=src python3 run_experiments.py` - wygenerowano wszystkie dane i tabele;
- `PYTHONPATH=src python3 verify_results.py` - spójność danych, cykli, statusów i statystyk `OK`.
