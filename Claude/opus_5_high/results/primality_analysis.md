# Testy pierwszości - wyniki pomiarów (zakres grupy 3)

Wszystkie liczby w tym pliku są wynikiem uruchomienia `python3 exp_primality.py`.

## 0. Warunki pomiaru

* Python: 3.14.7 (main, Sep  1 2026, 14:18:09) [Clang 22.1.3 ]
* implementacja: CPython 3.14.7
* system: Linux 7.1.9-arch1-2 (x86_64)
* procesor: AMD Ryzen 5 7520U with Radeon Graphics
* zegar perf_counter: monotoniczny=True, rozdzielczość=1e-09 s
* jednostka wszystkich czasów w tabelach: nanosekundy (ns)
* liczba iteracji: Fermat s = 5, Miller-Rabin s = 5
* ziarno losowania podstaw: `random.Random(12345)`, tworzone od nowa dla każdego testu i scenariusza
* dane wejściowe: `results/lfsr_numbers_main.txt` (K = 200) oraz `results/lcg_numbers_main.txt` (K = 200)
* czasy mierzone dla każdej pozycji pliku (także dla liczb powtórzonych); trafność liczona na zbiorze unikalnych liczb
* przed każdym mierzonym przebiegiem wykonywana jest rozgrzewka (te same testy bez pomiaru, z osobnym generatorem podstaw)
* każdy czas to JEDNO wywołanie funkcji - dla najkrótszych wywołań (rzędu mikrosekundy) szum pomiarowy jest rzędu dziesiątek-setek ns, dlatego istotna jest mediana, a nie pojedyncze maksimum

## 1. Statystyki czasu (ns) - osobno dla każdego testu i źródła

| źródło | test | liczba pomiarów | min | max | średnia | mediana |
|---|---|---|---|---|---|---|
| LFSR | dzielenie | 200 | 250 | 2605 | 369.6 | 320.0 |
| LFSR | Fermat | 200 | 200 | 10069 | 1488.5 | 275.5 |
| LFSR | Miller-Rabin | 200 | 210 | 6332 | 1498.1 | 250.0 |
| LCG | dzielenie | 200 | 270 | 3787 | 393.6 | 335.5 |
| LCG | Fermat | 200 | 200 | 6272 | 1588.0 | 801.5 |
| LCG | Miller-Rabin | 200 | 210 | 6202 | 1618.5 | 796.5 |

Pliki z czasem KAŻDEGO wywołania: `results/primality_calls_lfsr.csv`, `results/primality_calls_lcg.csv`

### 1b. Dlaczego sama mediana jest tu myląca - rozkład dwumodalny

Czas testu zależy przede wszystkim od tego, czy liczba kończy się na warunku
brzegowym (parzysta - jedno dzielenie), czy wymaga pełnego testu. Przy około
połowie liczb parzystych mediana całego zbioru wypada dokładnie na granicy
dwóch skupień, więc reaguje na drobną zmianę proporcji parzystych. Dlatego
poniżej te same pomiary rozbite są na grupy.

| źródło | test | grupa liczb | liczba pomiarów | min ns | max ns | średnia ns | mediana ns |
|---|---|---|---|---|---|---|---|
| LFSR | Fermat | pełny test (nieparzysta >= 5) | 92 | 1192 | 10069 | 2959.3 | 1728.0 |
| LFSR | Fermat | wyjście brzegowe (n < 2, 2, 3 lub parzysta) | 108 | 200 | 460 | 235.7 | 230.0 |
| LFSR | Miller-Rabin | pełny test (nieparzysta >= 5) | 92 | 1363 | 6332 | 2963.2 | 1848.5 |
| LFSR | Miller-Rabin | wyjście brzegowe (n < 2, 2, 3 lub parzysta) | 108 | 210 | 2695 | 250.1 | 221.0 |
| LFSR | dzielenie | pierwsza | 32 | 351 | 2605 | 602.4 | 541.0 |
| LFSR | dzielenie | złożona | 168 | 250 | 1001 | 325.2 | 310.0 |
| LCG | Fermat | pełny test (nieparzysta >= 5) | 100 | 1242 | 6272 | 2933.8 | 1633.0 |
| LCG | Fermat | wyjście brzegowe (n < 2, 2, 3 lub parzysta) | 100 | 200 | 361 | 242.1 | 241.0 |
| LCG | Miller-Rabin | pełny test (nieparzysta >= 5) | 100 | 1312 | 6202 | 3003.0 | 1878.5 |
| LCG | Miller-Rabin | wyjście brzegowe (n < 2, 2, 3 lub parzysta) | 100 | 210 | 281 | 234.1 | 231.0 |
| LCG | dzielenie | pierwsza | 39 | 371 | 621 | 507.4 | 521.0 |
| LCG | dzielenie | złożona | 161 | 270 | 3787 | 366.0 | 321.0 |

## 2. Rzeczywisty status pierwszości i błędne decyzje

Podstawa odniesienia: dokładny test dzielenia przez liczby pierwsze do floor(sqrt(n)).

| źródło | test | liczb unikalnych | pierwszych | złożonych | pseudopierwsze (fałszywie pierwsza) | pseudozłożone (fałszywie złożona) | przykłady pseudopierwszych |
|---|---|---|---|---|---|---|---|
| LFSR | Fermat | 182 | 29 | 153 | 0 | 0 | brak |
| LFSR | Miller-Rabin | 182 | 29 | 153 | 0 | 0 | brak |
| LCG | Fermat | 178 | 36 | 142 | 0 | 0 | brak |
| LCG | Miller-Rabin | 178 | 36 | 142 | 0 | 0 | brak |

Zero pseudozłożonych nie jest przypadkiem: oba testy orzekają "złożona" tylko
na podstawie kontrprzykładu (podstawa świadcząca o złożoności), a dla liczby
pierwszej taki kontrprzykład nie istnieje. Poprawnie zaimplementowany test
Fermata i Millera-Rabina NIE MOŻE odrzucić liczby pierwszej - każde takie
wystąpienie wskazywałoby na błąd implementacji, nie na własność testu.

## 3. Przypadki brzegowe i liczby trudne dla testu Fermata

| n | dzielenie (dokładnie) | Fermat | Miller-Rabin | Fermat zgodny? | M-R zgodny? | uwaga |
|---|---|---|---|---|---|---|
| -7 | złożona | złożona | złożona | tak | tak | poza zakresem pierwszości |
| 0 | złożona | złożona | złożona | tak | tak | poza zakresem pierwszości |
| 1 | złożona | złożona | złożona | tak | tak | poza zakresem pierwszości |
| 2 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 3 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 4 | złożona | złożona | złożona | tak | tak |  |
| 5 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 6 | złożona | złożona | złożona | tak | tak |  |
| 7 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 8 | złożona | złożona | złożona | tak | tak |  |
| 9 | złożona | złożona | złożona | tak | tak |  |
| 25 | złożona | złożona | złożona | tak | tak |  |
| 97 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 341 | złożona | złożona | złożona | tak | tak | najmniejsza pseudopierwsza Fermata dla podstawy 2 |
| 561 | złożona | pierwsza | złożona | BŁĄD | tak | liczba Carmichaela |
| 1105 | złożona | złożona | złożona | tak | tak | liczba Carmichaela |
| 1729 | złożona | złożona | złożona | tak | tak | liczba Carmichaela |
| 2465 | złożona | złożona | złożona | tak | tak | liczba Carmichaela |
| 7919 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 104729 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 1000003 | pierwsza | pierwsza | pierwsza | tak | tak |  |
| 1000001 | złożona | złożona | złożona | tak | tak |  |

## 4. Podstawy mylące testy - przeliczenie wyczerpujące (liczby Carmichaela)

Dla każdej podstawy t z {2, ..., n-2} sprawdzono jedną iterację testu.
Kolumna ostatnia: prawdopodobieństwo, że test Fermata z s = 5 losowymi
podstawami uzna liczbę za pierwszą (iloraz kłamców podniesiony do potęgi s).

| n | liczba podstaw | kłamcy Fermata | % kłamców Fermata | kłamcy M-R | % kłamców M-R | P(Fermat się myli) [%] |
|---|---|---|---|---|---|---|
| 561 | 558 | 318 | 56.99 | 8 | 1.43 | 6.011 |
| 1105 | 1102 | 766 | 69.51 | 28 | 2.54 | 16.227 |
| 1729 | 1726 | 1294 | 74.97 | 160 | 9.27 | 23.685 |
| 2465 | 2462 | 1790 | 72.71 | 68 | 2.76 | 20.315 |
| 2821 | 2818 | 2158 | 76.58 | 268 | 9.51 | 26.336 |
| 6601 | 6598 | 5278 | 79.99 | 328 | 4.97 | 32.756 |
| 8911 | 8908 | 7126 | 80.00 | 1780 | 19.98 | 32.759 |
| 10585 | 10582 | 8062 | 76.19 | 628 | 5.93 | 25.667 |
| 15841 | 15838 | 12958 | 81.82 | 808 | 5.10 | 36.660 |
| 29341 | 29338 | 25918 | 88.34 | 4048 | 13.80 | 53.809 |

## 5. Wpływ liczby iteracji

Dane: 331 unikalnych liczb z obu generatorów (LFSR + LCG, przedział [1, 1000]).

### Miller-Rabin

| s (iteracje) | liczba pomiarów | min ns | max ns | średnia ns | mediana ns | pseudopierwsze | pseudozłożone | które liczby uznane za pierwsze mimo złożoności |
|---|---|---|---|---|---|---|---|---|
| 1 | 331 | 180 | 5941 | 836.4 | 1062.0 | 0 | 0 | brak |
| 2 | 331 | 180 | 2895 | 984.8 | 681.0 | 0 | 0 | brak |
| 3 | 331 | 180 | 9418 | 1191.6 | 561.0 | 0 | 0 | brak |
| 5 | 331 | 180 | 9488 | 1467.8 | 341.0 | 0 | 0 | brak |
| 10 | 331 | 180 | 17774 | 2256.2 | 311.0 | 0 | 0 | brak |
| 20 | 331 | 181 | 30046 | 3873.4 | 661.0 | 0 | 0 | brak |
| 40 | 331 | 180 | 43060 | 6655.0 | 471.0 | 0 | 0 | brak |

### Fermat (dla porównania, te same dane)

| s (iteracje) | liczba pomiarów | min ns | max ns | średnia ns | mediana ns | pseudopierwsze | pseudozłożone | które liczby uznane za pierwsze mimo złożoności |
|---|---|---|---|---|---|---|---|---|
| 1 | 331 | 180 | 1624 | 689.4 | 350.0 | 3 | 0 | 39, 435, 635 |
| 2 | 331 | 180 | 2394 | 834.1 | 300.0 | 0 | 0 | brak |
| 3 | 331 | 180 | 4518 | 1013.4 | 281.0 | 1 | 0 | 561 |
| 5 | 331 | 180 | 10169 | 1319.4 | 781.0 | 0 | 0 | brak |
| 10 | 331 | 180 | 42820 | 2558.1 | 892.0 | 0 | 0 | brak |
| 20 | 331 | 180 | 36919 | 3751.8 | 962.0 | 0 | 0 | brak |
| 40 | 331 | 180 | 46386 | 6739.6 | 831.0 | 0 | 0 | brak |

## 6. Wpływ przedziału i rozmiaru liczb

Dla każdego przedziału: 60 liczb z LFSR (n = 16) + 60 liczb z LCG o m = 2^48
(parametry Java - generator o m = 65536 nie pokrywa szerokich przedziałów;
to świadoma zmiana parametru, odnotowana, żeby nie mylić jej ze scenariuszem głównym).

| przedział | span | test | liczba pomiarów | min ns | max ns | średnia ns | mediana ns |
|---|---|---|---|---|---|---|---|
| [1, 10^3] | 1000 | dzielenie | 120 | 240 | 621 | 366.5 | 340.5 |
| [1, 10^3] | 1000 | Fermat | 120 | 210 | 5941 | 1537.3 | 330.0 |
| [1, 10^3] | 1000 | Miller-Rabin | 120 | 210 | 10269 | 1590.0 | 290.5 |
| [10^3, 10^6] | 999001 | dzielenie | 120 | 251 | 5470 | 719.0 | 311.0 |
| [10^3, 10^6] | 999001 | Fermat | 120 | 201 | 10279 | 1851.0 | 251.0 |
| [10^3, 10^6] | 999001 | Miller-Rabin | 120 | 220 | 10069 | 1906.8 | 270.5 |
| [10^6, 10^9] | 999000001 | dzielenie | 120 | 260 | 129901 | 8339.8 | 350.0 |
| [10^6, 10^9] | 999000001 | Fermat | 120 | 210 | 17743 | 2703.8 | 2725.0 |
| [10^6, 10^9] | 999000001 | Miller-Rabin | 120 | 220 | 17372 | 2823.7 | 2945.5 |
| [10^9, 10^12] | 999000000001 | dzielenie | 120 | 290 | 3031190 | 183149.0 | 476.0 |
| [10^9, 10^12] | 999000000001 | Fermat | 120 | 220 | 64070 | 8461.1 | 8606.0 |
| [10^9, 10^12] | 999000000001 | Miller-Rabin | 120 | 230 | 50324 | 8004.7 | 8731.0 |

Udział liczb pierwszych w każdym przedziale (wg dokładnego dzielenia):

| przedział | liczb | pierwszych | % pierwszych |
|---|---|---|---|
| [1, 10^3] | 120 | 22 | 18.3 |
| [10^3, 10^6] | 120 | 11 | 9.2 |
| [10^6, 10^9] | 120 | 11 | 9.2 |
| [10^9, 10^12] | 120 | 7 | 5.8 |
