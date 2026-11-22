# Laboratorium 5, grupa 5 - generatory pseudolosowe i testy pierwszości

Kompletna, odtwarzalna realizacja zakresu grup 1-3 z użyciem GenAI. Projekt korzysta wyłącznie ze standardowej biblioteki Pythona.

## Szybkie uruchomienie

Wymagany Python 3.10 lub nowszy. Polecenia należy wykonać w katalogu `zad5-gr5`:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 run_experiments.py
PYTHONPATH=src python3 verify_results.py
```

Ostatni zweryfikowany przebieg wykonano w Pythonie 3.12.14 na Linuksie. Testy: 27/27 zaliczonych. Weryfikator wyników zakończył się komunikatem `OK`.

## Struktura

- `src/lab05/generators.py` - LFSR, LCG, cykle, kolizje i warunki Hulla-Dobella;
- `src/lab05/primality.py` - dokładne dzielenie przez liczby pierwsze, własne potęgowanie binarne, Fermat i Miller-Rabin;
- `src/lab05/io_utils.py` - zapis i kontrolowany odczyt plików tekstowych;
- `src/lab05/experiment.py` - parametry, benchmarki i generowanie tabel;
- `tests/` - testy jednostkowe, przypadki brzegowe i liczba Carmichaela 561;
- `data/` - po 200 rzeczywiście wygenerowanych liczb LFSR i LCG;
- `results/` - surowe pomiary, zestawienia i metadane środowiska;
- `verify_results.py` - niezależne przeliczenie kluczowych statystyk zapisanych w CSV;
- `CHECKLIST.md` - stan każdego wymagania i dowód wykonania;
- `SPRAWOZDANIE_MATERIAL.md` - gotowy materiał merytoryczny do własnego sprawozdania grupy 5;
- `GENAI_PROCESS.md` - jawna dokumentacja użycia GenAI i poprawek.

## Jednoznaczne definicje

### LFSR

Stan ma postać `(S_i, ..., S_(i+n-1))`, najstarszy bit znajduje się po lewej. Odczepy są indeksami 0-based. Bitem wyjściowym jest `state[0]`. Bit sprzężenia to XOR bitów o podanych indeksach; rejestr przesuwa się w lewo, a nowy bit trafia na prawy koniec. Jest to bezpośrednia realizacja rekurencji z notatki:

`S_(i+n) = sum(p_j * S_(i+j)) mod 2`.

Kolejne bity są składane od najstarszego do najmłodszego. Mapowanie do `[a,b]` używa rejection samplingu, aby uniknąć obciążenia prostego modulo. Powrót pełnego stanu w trakcie samych odrzuceń kończy się jawnym błędem zamiast zapętlenia.

### LCG

Implementowane równanie to `x_(i+1) = (a*x_i + c) mod m`. W notatce przyrost nazywa się `b`; w kodzie użyto `c`, aby nie pomylić go z górną granicą przedziału `[a,b]`. Zwracany jest stan po wykonaniu rekurencji. Mapowanie do przedziału także używa rejection samplingu i wymaga `b-a+1 <= m`.

### Kolizje i cykle

- `duplicate_occurrences = K - liczba różnych wartości`;
- `repeated_values` - liczba różnych wartości występujących więcej niż raz;
- `colliding_pairs = sum(c_v*(c_v-1)/2)`;
- okres generatora jest okresem pełnego stanu, nie ciągu po mapowaniu.

## Scenariusz główny

- `K=200`, `[10000,59999]`, więc `K <= b-a+1`;
- LFSR: `n=16`, odczepy `(0,2,3,5)`, ziarno `0000000000000001`;
- LCG: `m=65536`, `a=5`, `c=1`, `x0=20226`;
- Fermat: 5 iteracji; Miller-Rabin: 5 iteracji;
- ziarno eksperymentów probabilistycznych: `20261122`;
- każda pozycja wejściowa jest mierzona, także gdyby wystąpiły duplikaty;
- czas samego wywołania testu mierzy `time.perf_counter_ns`.

W głównym przebiegu oba ciągi miały po 200 różnych liczb. Okres stanu LFSR wyniósł 65535, a LCG 65536.

## Pliki wynikowe

- `generator_summary.csv` - kolizje i okresy;
- `parameter_analysis.csv` - wpływ długości, odczepów, ziaren i parametrów LCG;
- `primality_measurements.csv` - 1200 pojedynczych pomiarów;
- `primality_summary.csv` - minimum, maksimum, średnia i mediana osobno dla każdej metody i źródła;
- `error_summary.csv` - błędne uznania za pierwszą i błędne odrzucenia;
- `range_comparison.csv` - porównanie dla liczb 3-, 5- i 7-cyfrowych;
- `mr_iterations.csv` - wpływ 1, 3, 5 i 10 iteracji Millera-Rabina;
- `run_metadata.json` - środowisko, parametry i polityka pomiarów;
- `REPORT_RESULTS.md` - automatycznie wygenerowane tabele i interpretacja.

## Ograniczenia

Pojedynczy przebieg na współdzielonym środowisku nie jest stabilnym mikrobenchmarkiem; szczególnie minimum i mediana krótkich wywołań podlegają szumowi. Testy Fermata i Millera-Rabina są probabilistyczne. Ranking różnych modeli GenAI oraz rzeczywiste roboczogodziny zespołu wymagają danych od ludzi i innych niezależnych przebiegów.
