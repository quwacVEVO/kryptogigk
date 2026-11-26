# LCG - wyniki pomiarów (zakres grupy 2)

Wszystkie liczby w tym pliku są wynikiem uruchomienia `python3 exp_lcg.py`.
Oznaczenia: `c` to przyrost (w notatce `b`), `[a, b]` to przedział `[low, high]`.

## 1. Scenariusz główny

* parametry: `LCG m=65536 a=25173 c=13849 x0=2026`
* K = 200, przedział = [1, 1000] (span = 1000), mapowanie = `mod_reject`
* warunki Hull-Dobella: spełnione
  * NWD(c, m) = 1 - tak (NWD(13849, 65536) = 1)
  * a - 1 podzielne przez każdy dzielnik pierwszy m - tak (dzielniki pierwsze m: [2], a-1 = 25172)
  * m podzielne przez 4 => a - 1 podzielne przez 4 - tak ((a-1) mod 4 = 0)
* okres STANU zmierzony: 65536 (ogon 0); m = 65536
* okres ciągu WARTOŚCI po mapowaniu: 65000 (powtórzenie potwierdzone: True)
* kolizje w K = 200 liczbach: 22 (różnych wartości 178, najczęstsza krotność 3)
* pierwsza kolizja: pozycja 15 (wartość 939)
* najczęściej powtarzane (wartość, krotność): [(60, 3), (445, 3), (787, 3), (112, 2), (173, 2)]
* plik z liczbami: `results/lcg_numbers_main.txt`

## 2. Ciąg K różnych liczb

* warunek wykonalności: K=200 <= b-a+1=1000 - ciąg bez powtórzeń jest możliwy
* K = 200 różnych liczb z [1, 1000] filtrem powtórzeń: `results/lcg_numbers_unique.txt`
* pierwsze 12 wartości: [340, 961, 298, 671, 504, 189, 846, 939, 308, 385, 634, 999]
* ciąg BEZ filtru i bez kolizji: `LCG m=1024 a=5 c=1 x0=7`, K = 200, [1, 1024], mapowanie `mod`
  * warunki Hull-Dobella: spełnione; zmierzony okres stanu: 1024 (ogon 0)
  * kolizje: 0; plik: `results/lcg_numbers_raw_unique.txt`
  * pierwsze 12 wartości: [37, 182, 907, 436, 129, 642, 135, 672, 285, 398, 963, 716]
  * przypadek nasycający ograniczenie K = b-a+1 = 1024: kolizji 0
* przypadek niewykonalny K = 1500: K=1500 > b-a+1=1000 - ciąg K różnych liczb z [1, 1000] jest NIEMOŻLIWY (zasada szufladkowa)
* reakcja implementacji: `ValueError: nie da się wygenerować 1500 różnych liczb z przedziału [1, 1000] o 1000 elementach (warunek K <= b - a + 1)`

## 3. Wpływ parametrów m, a, c, x0

Kolumny "różnych w K=200" i "kolizji" dotyczą przedziału [1, 1000] i mapowania `mod_reject`.
Pomiar okresu przerywany po 200000 krokach - wtedy okres jest nieustalony, a nie "duży".

| zestaw | m | a | c | x0 | Hull-Dobell | ogon | okres stanu (zmierzony) | okres = m? | różnych w K=200 | kolizji | pierwsze 5 liczb |
|---|---|---|---|---|---|---|---|---|---|---|---|
| scenariusz główny | 65536 | 25173 | 13849 | 2026 | spełnione | 0 | 65536 | tak | 178 | 22 | [340, 961, 298, 671, 504] |
| notatka, przykład | 15 | 51 | 13 | 1 | niespełnione (a - 1 podzielne przez każdy dzielnik pierwszy m) | 0 | 5 | nie | m < span, mapowanie mod_reject niemożliwe | - | - |
| ANSI C | 2147483648 | 1103515245 | 12345 | 2026 | spełnione | ? | > 200000 (pomiar przerwany) | nie ustalono | 181 | 19 | [148, 9, 626, 239, 456] |
| Borland C/C++ | 4294967296 | 22695477 | 1 | 2026 | spełnione | ? | > 200000 (pomiar przerwany) | nie ustalono | 186 | 14 | [444, 265, 946, 591, 584] |
| Microsoft Visual C++ | 4294967296 | 214013 | 2531011 | 2026 | spełnione | ? | > 200000 (pomiar przerwany) | nie ustalono | 181 | 19 | [350, 173, 776, 247, 754] |
| Microsoft Visual Basic | 16777216 | 1140671485 | 12820163 | 2026 | spełnione | ? | > 200000 (pomiar przerwany) | nie ustalono | 184 | 16 | [422, 365, 352, 15, 18] |
| Java | 281474976710656 | 25214903917 | 11 | 2026 | spełnione | ? | > 200000 (pomiar przerwany) | nie ustalono | 188 | 12 | [854, 429, 64, 119, 874] |
| pełny okres, małe m | 1024 | 5 | 1 | 7 | spełnione | 0 | 1024 | tak | 200 | 0 | [37, 182, 907, 436, 129] |
| c = 0 (multiplikatywny) | 65536 | 25173 | 0 | 2026 | niespełnione (NWD(c, m) = 1; c > 0 (warunki Hull-Dobella dotyczą c > 0)) | 0 | 8192 | nie | 106 | 94 | [491, 755, 75, 491, 579] |
| a = 1 (licznik modulo m) | 65536 | 1 | 13849 | 2026 | spełnione | 0 | 65536 | tak | 200 | 0 | [876, 725, 574, 423, 736] |
| a = 0 (stała) | 65536 | 0 | 13849 | 2026 | niespełnione (a - 1 podzielne przez każdy dzielnik pierwszy m; m podzielne przez 4 => a - 1 podzielne przez 4) | 1 | 1 | nie | 1 | 199 | [850, 850, 850, 850, 850] |
| a = 2, c = 0 (zbiega do 0) | 65536 | 2 | 0 | 2026 | niespełnione (NWD(c, m) = 1; a - 1 podzielne przez każdy dzielnik pierwszy m; m podzielne przez 4 => a - 1 podzielne przez 4; c > 0 (warunki Hull-Dobella dotyczą c > 0)) | 15 | 1 | nie | 15 | 185 | [53, 105, 209, 417, 833] |
| m nie jest potęgą 2 | 1000 | 21 | 3 | 7 | spełnione | 0 | 1000 | tak | 200 | 0 | [151, 154, 217, 540, 323] |

## 4. Wpływ ziarna x0 (m = 65536, a = 25173, c = 13849)

| x0 | ogon | okres stanu | różnych w K=200 | kolizji | pierwsze 5 liczb |
|---|---|---|---|---|---|
| 0 | 0 | 65536 | 181 | 19 | [850, 743, 224, 181, 926] |
| 1 | 0 | 65536 | 186 | 14 | [23, 88, 197, 6, 883] |
| 2026 | 0 | 65536 | 178 | 22 | [340, 961, 298, 671, 504] |
| 12345 | 0 | 65536 | 176 | 24 | [823, 32, 181, 630, 203] |
| 65535 | 0 | 65536 | 183 | 17 | [213, 398, 251, 892, 969] |

## 5. Wpływ sposobu mapowania na przedział

Ten sam generator (scenariusz główny), różne przedziały i tryby mapowania.

| przedział | span | tryb | okres stanu | okres wartości | różnych w K=200 | kolizji | min | max |
|---|---|---|---|---|---|---|---|---|
| [1, 1000] | 1000 | mod_reject | 65536 | 65000 | 178 | 22 | 6 | 999 |
| [1, 1000] | 1000 | mod | 65536 | 65536 | 178 | 22 | 6 | 999 |
| [1, 1000] | 1000 | scale | 65536 | 65536 | 181 | 19 | 2 | 999 |
| [1, 1024] | 1024 | mod_reject | 65536 | 1024 | 200 | 0 | 3 | 1023 |
| [1, 1024] | 1024 | mod | 65536 | 1024 | 200 | 0 | 3 | 1023 |
| [1, 1024] | 1024 | scale | 65536 | 65536 | 184 | 16 | 2 | 1023 |
