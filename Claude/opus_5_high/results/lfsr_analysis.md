# LFSR - wyniki pomiarów (zakres grupy 1)

Wszystkie liczby w tym pliku są wynikiem uruchomienia `python3 exp_lfsr.py`.
Konwencja stanu, odczepów i mapowania: patrz docstring w `lfsr.py` oraz README.md.

## 1. Scenariusz główny

* parametry: `LFSR n=16 p=1011010000000000 (odczepy j=0,2,3,5) f(x)=x^16 + x^5 + x^3 + x^2 + 1 ziarno=44257 (0b1010110011100001)`
* K = 200, przedział = [1, 1000] (span = 1000), mapowanie = `reject`
* bitów na jedną liczbę (szerokość słowa): 10
* okres STANU: 65535 (ogon 0), teoretyczne maksimum 2^16 - 1 = 65535
* okres ciągu WARTOŚCI (po mapowaniu): 12801 (blok 13107 słów, powtórzenie potwierdzone: True)
* kolizje w K = 200 liczbach: 18 (różnych wartości 182, najczęstsza krotność 3)
* pierwsza kolizja: pozycja 39 (wartość 692)
* najczęściej powtarzane wartości (wartość, krotność): [(662, 3), (710, 3), (122, 2), (139, 2), (146, 2)]
* plik z liczbami: `results/lfsr_numbers_main.txt`

## 2. Ciąg K różnych liczb

* warunek wykonalności: K=200 <= b-a+1=1000 - ciąg bez powtórzeń jest możliwy
* K = 200 różnych liczb z [1, 1000] uzyskane filtrem powtórzeń: plik `results/lfsr_numbers_unique.txt`
* pierwsze 12 wartości: [692, 543, 278, 478, 96, 561, 710, 542, 245, 633, 286, 313]
* ciąg BEZ filtru i bez kolizji: K = 50, [1, 10000], dobrane ziarno 0x0002, plik `results/lfsr_numbers_raw_unique.txt`
* pierwsze 12 wartości: [1, 8198, 9084, 5770, 957, 3987, 9615, 2632, 7780, 9761, 8942, 4109]
* przypadek niewykonalny K = 1500: K=1500 > b-a+1=1000 - ciąg K różnych liczb z [1, 1000] jest NIEMOŻLIWY (zasada szufladkowa)
* reakcja implementacji: `ValueError: nie da się wygenerować 1500 różnych liczb z przedziału [1, 1000] o 1000 elementach (warunek K <= b - a + 1)`

## 3. Wpływ długości rejestru

Dla każdego n użyto osobnego zestawu odczepów (kolumna f(x)); ziarno = 1.

| n | odczepy j | f(x) | ogon | okres stanu | 2^n-1 | maksymalny? | udział jedynek w okresie | różnych w K=200 | kolizji |
|---|---|---|---|---|---|---|---|---|---|
| 4 | 0,1 | x^4 + x + 1 | 0 | 15 | 15 | tak | 0.5333 | 3 | 197 |
| 8 | 0,2,3,4 | x^8 + x^4 + x^3 + x^2 + 1 | 0 | 255 | 255 | tak | 0.502 | 50 | 150 |
| 12 | 0,1,4,6 | x^12 + x^6 + x^4 + x + 1 | 0 | 4095 | 4095 | tak | 0.5001 | 188 | 12 |
| 16 | 0,2,3,5 | x^16 + x^5 + x^3 + x^2 + 1 | 0 | 65535 | 65535 | tak | 0.5 | 176 | 24 |
| 20 | 0,3 | x^20 + x^3 + 1 | 0 | 1048575 | 1048575 | tak | 0.5 | 170 | 30 |

## 4. Wpływ konfiguracji odczepów (n = 16, ziarno = 0xACE1)

| odczepy j | f(x) | ogon | okres stanu | udział jedynek | okres wartości | różnych w K=200 | kolizji | uwaga |
|---|---|---|---|---|---|---|---|---|
| 0,2,3,5 | x^16 + x^5 + x^3 + x^2 + 1 | 0 | 65535 | 0.5 | 12801 | 182 | 18 | wielomian pierwotny (scenariusz główny) |
| 0,11,13,14 | x^16 + x^14 + x^13 + x^11 + 1 | 0 | 65535 | 0.5 | 12801 | 183 | 17 | inny wielomian pierwotny |
| 0,1 | x^16 + x + 1 | 0 | 255 | 0.502 | 49 | 47 | 153 | wielomian niepierwotny - okres 255 zamiast 65535 |
| 0,2 | x^16 + x^2 + 1 | 0 | 126 | 0.5397 | 61 | 61 | 139 | wielomian niepierwotny - bardzo krótki okres |
| 0 | x^16 + 1 | 0 | 16 | 0.5 | 8 | 8 | 192 | x^16 + 1 - czysty obrót bitów |
| 1,3 | x^16 + x^3 + x | 1 | 4599 | 0.4942 | nie zmierzono | 183 | 17 | p_0 = 0 - odwzorowanie nieodwracalne (ogon > 0) |
| 5 | x^16 + x^5 | 3 | 11 | 0.6364 | nie zmierzono | 12 | 188 | p_0 = 0, jeden odczep - silnie zdegenerowany |

## 5. Wpływ ziarna (n = 16, odczepy 0,2,3,5)

| ziarno | ziarno (bity) | ogon | okres stanu | różnych w K=200 | kolizji | pierwsze 5 liczb |
|---|---|---|---|---|---|---|
| 0x0001 | 0000000000000001 | 0 | 65535 | 176 | 24 | [1, 17, 12, 261, 327] |
| 0x00FF | 0000000011111111 | 0 | 65535 | 185 | 15 | [4, 711, 205, 657, 250] |
| 0xACE1 | 1010110011100001 | 0 | 65535 | 182 | 18 | [692, 543, 278, 478, 96] |
| 0xFFFF | 1111111111111111 | 0 | 65535 | 178 | 22 | [7, 772, 830, 695, 317] |
| 0x8000 | 1000000000000000 | 0 | 65535 | 181 | 19 | [513, 9, 6, 643, 164] |
| 0x3039 | 0011000000111001 | 0 | 65535 | 181 | 19 | [193, 920, 399, 473, 174] |
| 0x0000 | 0000000000000000 | 0 | 1 | 1 | 9 | [1, 1, 1, 1, 1] |
