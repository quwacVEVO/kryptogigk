# Sprawozdanie — Kryptologia, Laboratorium 5: Generatory pseudolosowe i testy pierwszości

**Zespół:** Grupa 5 — Realizacja z wykorzystaniem GenAI (`zad5-gr5`)  
**Harmonogram źródłowy (z `README.md`):**
- Etap 1 (Deadline 1): **26.11.2026, 13:30** — implementacja generatorów LFSR i LCG, pliki wyjściowe, analiza kolizji/cykli, ciągi bez kolizji oraz testy pierwszości.
- Etap 2 (Deadline 2 — oddanie sprawozdania): **30.11.2026, 18:00** — analizy porównawcze, zadania dodatkowe, dokumentacja pracy z GenAI i kompletne sprawozdanie.

> **Uwaga metodyczna dotycząca zakresu Grupy 5:** Niniejszy dokument stanowi kompletny materiał do **własnego sprawozdania Grupy 5** dla jednego, w pełni udokumentowanego i zweryfikowanego przebiegu z użyciem narzędzia GenAI. Nie zastępuje sprawozdania głównego Grupy 4 ani nie zawiera zmyślonych wyników innych modeli czy roboczogodzin członków zespołu — miejsca wymagające uzupełnienia przez zespół (roboczogodziny oraz wyniki porównawcze innych modeli) zostały wyraźnie oznaczone.

---

## 1. Rozpoznanie źródeł i odnotowane rozbieżności

Przed rozpoczęciem implementacji przeanalizowano trzy dokumenty źródłowe: `README.md`, `Kryptologia lab05_zadania-1.pdf` oraz `Kryptologia lab05. Generatory pseudolosowe i testy pierwszości.pdf` (notatka T. Gzelli). Odnotowano następujące istotne rozbieżności i szczegóły techniczne, które rozwiązano jawnie w kodzie:

1. **Oznaczenie przyrostu w LCG (`b` vs `c`):** W notatce wykładowej (slajd 2/14) przyrost oznaczono literą `b` ($S_i = a S_{i-1} + b \bmod m$), natomiast w szczegółowym pliku zadań Grupy 2 oznaczono go literą `c` ($x_{i+1} = (a \cdot x_i + c) \bmod m$), aby uniknąć kolizji oznaczeń z prawą granicą przedziału docelowego $[a, b]$. W kodzie (`zad5-gr5/lcg.py`) przyjęto `c` dla przyrostu oraz `low`, `high` dla granic przedziału $[a, b]$.
2. **Zamieniona kolejność argumentów w pseudokodzie `LCG2` na slajdzie 4/14:** Definicja mówi `FUNCTION LCG2(a, b, mod, seed)`, natomiast wywołanie w przykładzie na tym samym slajdzie podaje `LCG2(134456, 8121, 28411, 55)` (moduł `134456` jako pierwszy argument zamiast trzeciego). W implementacji użyto jednoznacznych argumentów nazwanych `(m, a, c, x0)` i sprawdzono poprawną kolejność `m=134456, a=8121, c=28411, x0=55` ze slajdu 3/14.
3. **Literówka indeksu w wektorze `p` LFSR na slajdzie 6/14:** Zapisano $p = (p_0, \dots, p_{m-1}) \in \mathbb{Z}_2^n$ zamiast $p_{n-1}$. W implementacji długość wektora $p$ jest zawsze równa stopniowi rejestru $n$.
4. **Prosty test pierwszości (wszystkie liczby naturalne vs liczby pierwsze):** Slajd 8/14 przedstawia dzielenie przez wszystkie liczby naturalne $2 \dots \lfloor\sqrt{n}\rfloor$, natomiast szczegółowa treść zadania Grupy 3 wymaga jawnie **dzielenia przez liczby pierwsze do $\lfloor\sqrt{n}\rfloor$**. Jako nadrzędny przyjęto dokument z zadaniami: zaimplementowano dzielenie wyłącznie przez liczby pierwsze wyznaczone sitem Eratostenesa (`trial_division_by_primes`), a niezależną metodę dokładną ($6k \pm 1$, `is_prime_exact_independent`) wykorzystano jako zewnętrzny wzorzec do wyznaczenia rzeczywistego statusu pierwszości.
5. **Prefiks `0b` w pseudokodzie `pot_mod2` (slajd 14/14):** Funkcja Pythona `bin(b)` zwraca łańcuch z prefiksem `"0b"`. W pseudokodzie ze slajdu prefiks ten przypadkowo nie psuje wyniku (dla znaków `'0'` i `'b'` zachodzi $1^2 = 1$), lecz nasza implementacja `mod_pow_binary` korzysta bezpośrednio z operacji bitowych (`e & 1`, `e >>= 1`), unikając narzutu i niejednoznaczności konwersji tekstowej.

---

## 2. Parametry wspólnego benchmarku i środowisko pomiarowe

Wszystkie eksperymenty wykonano automatycznie skryptem `python3 zad5-gr5/run_experiments.py` w czystej bibliotece standardowej Pythona (bez pakietów zewnętrznych).

- **Środowisko:** Python `3.11.2`, system `Linux x86_64`
- **Zegar pomiarowy:** `time.perf_counter_ns()` (zegar monotoniczny o rozdzielczości nanosekundowej; czas wczytywania plików jest całkowicie oddzielony od pomiaru czasu testów pierwszości).
- **Wspólny scenariusz bazowy (LFSR, LCG i testy pierwszości):**
  - Liczba wygenerowanych wartości: $K = 200$
  - Przedział bazowy: $[a, b] = [1000, 100\,000]$ (rozmiar przedziału $b - a + 1 = 99\,001$)
  - Zapisane pliki wyjściowe: `zad5-gr5/data/lfsr_numbers.txt`, `zad5-gr5/data/lcg_numbers.txt`
  - Liczba iteracji w testach probabilistycznych (Fermat i Miller–Rabin): $s = 10$
  - Ziarno losowania podstaw w testach pierwszości: `rng_seed = 20261126`
- **Definicja kolizji:** Dla wygenerowanego ciągu $y_0, \dots, y_{K-1}$ łączna liczba kolizji wynosi $C = K - |\{y_0, \dots, y_{K-1}\}|$ (liczba nadmiarowych powtórzeń wartości, które wystąpiły już wcześniej). Oddzielnie mierzona jest **długość cyklu stanu** generatora ($\lambda$) oraz długość **części przedcyklicznej** ($\mu$).

---

## 3. Wyniki — Część A: Generator LFSR (zakres Grupy 1)

### 3.1. Definicja i mapowanie bitów

Zastosowano rejestr Fibonacciego przesuwany w lewo (zgodny ze slajdem 6/14):
- Stan rejestru: $S = (S_0, S_1, \dots, S_{n-1}) \in \mathbb{Z}_2^n$.
- Odczepy `taps`: posortowane indeksy $j \in \{0, \dots, n-1\}$, dla których $p_j = 1$.
- Jeden krok: bit wyjściowy to $S_0$, bit sprzężenia to $\text{fb} = \bigoplus_{j \in \text{taps}} S_j$, a nowy stan to $(S_1, \dots, S_{n-1}, \text{fb})$.

**Składanie bitów w liczby z $[a, b]$:** dla rozpiętości $R = b - a + 1$ pobieramy $w = \lceil \log_2 R \rceil$ kolejnych bitów (MSB-first) tworząc słowo $v \in \{0, \dots, 2^w - 1\}$. Zaimplementowano dwa jawne tryby:
1. `mod`: $y = a + (v \bmod R)$. Stały koszt $w$ kroków na liczbę, ale gdy $R$ nie jest potęgą dwójki (tutaj $R = 99\,001$, $2^{17} = 131\,072$), wartości z początku przedziału $[a, a + (2^w \bmod R) - 1]$ mogą występować w pełnym cyklu o 1 raz częściej (lekki bias modulo).
2. `rejection`: odrzucenie słów $v \ge R$ i przyjęcie $y = a + v$ dla $v < R$. Usuwa obciążenie modulo kosztem zmiennej liczby pobieranych słów (średnio $2^{17}/99\,001 \approx 1.32$ słowa na liczbę).

### 3.2. Weryfikacja 4 przykładów z notatki wykładowej (32 bity)

| Przykład | $n$ | Wektor $p$ | Ziarno $S$ | Cykl stanu | Maks. $2^n-1$ | Pełny? | Pierwsze 32 bity |
| --- | ---: | --- | --- | ---: | ---: | --- | --- |
| Przykład 1 ($n=3$) | 3 | `(1, 1, 0)` | `(0, 0, 1)` | 7 | 7 | Tak | `00101110010111001011100101110010` |
| Przykład 2 ($n=4$, pierwotny) | 4 | `(1, 1, 0, 0)` | `(0, 0, 0, 1)` | 15 | 15 | Tak | `00010011010111100010011010111100` |
| Przykład 3 ($n=4$, niepierwotny) | 4 | `(1, 1, 1, 1)` | `(1, 0, 0, 1)` | 5 | 15 | Nie | `10010100101001010010100101001010` |
| Przykład 4 ($n=6$) | 6 | `(1, 1, 0, 1, 1, 0)` | `(0, 0, 1, 0, 0, 1)` | 63 | 63 | Tak | `00100100001110000010111111001010` |

### 3.3. Wpływ długości rejestru, odczepów i ziarna ($K = 200$, $[1000, 100\,000]$, $w = 17$)

| Konfiguracja | $n$ | Odczepy | Mapowanie | Cykl stanu | Unikalne | Kolizje | Odsetek kolizji |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| `n=8`, pierwotny `(0,2,3,4)`, ziarno A | 8 | `(0, 2, 3, 4)` | `mod` | 255 / 255 | 15 | 185 | 92.50% |
| `n=8`, słabe odczepy `(0,4)`, ziarno A | 8 | `(0, 4)` | `mod` | 12 / 255 | 12 | 188 | 94.00% |
| `n=12`, pierwotny `(0,1,4,6)`, ziarno A | 12 | `(0, 1, 4, 6)` | `mod` | 4095 / 4095 | 200 | 0 | 0.00% |
| `n=12`, niepierwotny `(0,6)`, ziarno A | 12 | `(0, 6)` | `mod` | 18 / 4095 | 18 | 182 | 91.00% |
| `n=16`, pierwotny `(0,2,3,5)`, ziarno A | 16 | `(0, 2, 3, 5)` | `mod` | 65535 / 65535 | 200 | 0 | 0.00% |
| `n=16`, niepierwotny `(0,8)`, ziarno A | 16 | `(0, 8)` | `mod` | 24 / 65535 | 24 | 176 | 88.00% |
| `n=17`, pierwotny `(0,3)`, ziarno B (`000...001`) | 17 | `(0, 3)` | `mod` | 131071 / 131071 | 200 | 0 | 0.00% |
| `n=17`, pierwotny `(0,3)`, ziarno A (bazowe) | 17 | `(0, 3)` | `mod` | 131071 / 131071 | 200 | 0 | 0.00% |
| `n=17`, pierwotny `(0,3)`, ziarno A | 17 | `(0, 3)` | `rejection` | 131071 / 131071 | 200 | 0 | 0.00% |

### 3.4. Zweryfikowany ciąg bez kolizji (LFSR)

- **Parametry:** $K = 200 \le 99\,001$, $[a, b] = [1000, 100\,000]$, $n = 17$, odczepy `(0, 3)` (wielomian pierwotny $x^{17} + x^3 + 1$), ziarno `10110100110101001`, $w = 17$, mapowanie `rejection` (zapisano w `zad5-gr5/data/lfsr_no_collisions.txt`).
- **Wynik weryfikacji:** `200 / 200` wartości unikalnych (`0` kolizji), cykl stanu $\lambda = 131\,071$ (maksymalny, $\mu = 0$), cykl słów $= 131\,071$ (ponieważ $\gcd(17, 131\,071) = 1$).

### 3.5. Wnioski dla LFSR

1. **Krytyczna rola odczepów (wielomian pierwotny):** Nawet dla $n=16$ niepierwotne odczepy `(0, 8)` redukują cykl stanu z $65\,535$ do zaledwie `24`, dając 88% kolizji.
2. **Zależność między szerokością słowa $w$ a cyklem stanu $\lambda$:** Dla $n=8$ z pierwotnym wielomianem cykl bitowy wynosi $255$, ale przy składaniu słów $w = 17$-bitowych zachodzi $\gcd(17, 255) = 17$, więc cykl słów skraca się aż 17-krotnie do $255/17 = 15$ unikalnych liczb! Aby uniknąć takiej degradacji, należy wybierać $n$ takie, aby $\gcd(w, 2^n - 1) = 1$ (np. $2^{17}-1 = 131\,071$ jest liczbą pierwszą Mersenne’a).
3. **Wpływ ziarna:** Ziarno zerowe natychmiast blokuje rejestr w cyklu długości 1 (stąd domyślnie odrzucane przez walidator). Dla wielomianu pierwotnego dowolne ziarno niezerowe daje dokładnie ten sam maksymalny cykl $2^n - 1$, lecz ziarna o małej wadze Hamminga (np. `000...001`) powodują początkową serię niskich wartości przez pierwsze kroki rozruchu rejestru.

---

## 4. Wyniki — Część B: Generator LCG (zakres Grupy 2)

### 4.1. Definicja i mapowanie

Równanie: $x_{i+1} = (a \cdot x_i + c) \bmod m$. Zaimplementowano dwa sposoby mapowania stanu $x_i \in \{0, \dots, m-1\}$ na przedział $[a_{\min}, b_{\max}]$ o szerokości $R = b_{\max} - a_{\min} + 1$:
- `scale` (zalecane): $y_i = a_{\min} + \lfloor x_i \cdot R / m \rfloor$ — bazuje na najbardziej znaczących bitach stanu.
- `mod`: $y_i = a_{\min} + (x_i \bmod R)$ — bazuje na najmłodszych bitach; dla $m = 2^k$ i parzystego $R$ (np. $R=16$ na $[0, 15]$) najmłodszy bit ma okres zaledwie 2 (naprzemienność parzysta/nieparzysta `1, 0, 1, 0, ...`), co potwierdzono dodatkowym testem w `run_experiments.py` (`low_bit_demo`).

### 4.2. Analiza wpływu parametrów $m, a, c, x_0$ ($K = 200$, $[1000, 100\,000]$)

| Konfiguracja | $m$ | Hull–Dobell | Przedcykl $\mu$ | Cykl stanu $\lambda$ | Źródło cyklu | Mapowanie | Unikalne | Kolizje | Parzyste |
| --- | ---: | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Przykładowe (slajd PG: `a=51, c=13`) | 15 | Nie | 0 | 5 | pomiar Floyda | `scale` | 5 | 195 | 100.0% |
| Słabe z przedcyklem (`a=12, c=4, x0=7`) | 1024 | Nie | 5 | 1 | pomiar Floyda | `scale` | 5 | 195 | 1.5% |
| Slajd PG (`a=8121, c=28411, x0=55`) | 134456 | Tak | 0 | 134456 | pomiar Floyda | `scale` | 200 | 0 | 57.5% |
| Slajd PG (`a=8121, c=28411, x0=999`) | 134456 | Tak | 0 | 134456 | pomiar Floyda | `scale` | 200 | 0 | 52.5% |
| Microsoft Visual Basic (`m=2^24`) | 16777216 | Tak | 0 | 16777216 | tw. Hulla–Dobella | `scale` | 200 | 0 | 47.5% |
| ANSI C (`m=2^31, x0=123456`, bazowe) | 2147483648 | Tak | 0 | 2147483648 | tw. Hulla–Dobella | `scale` | 200 | 0 | 49.5% |
| ANSI C (`m=2^31, x0=123456`) | 2147483648 | Tak | 0 | 2147483648 | tw. Hulla–Dobella | `mod` | 200 | 0 | 49.5% |
| Borland C/C++ (`m=2^32`) | 4294967296 | Tak | 0 | 4294967296 | tw. Hulla–Dobella | `scale` | 200 | 0 | 50.0% |
| Java `java.util.Random` (`m=2^48`) | 281474976710656 | Tak | 0 | 281474976710656 | tw. Hulla–Dobella | `scale` | 200 | 0 | 49.5% |

### 4.3. Zweryfikowany ciąg bez kolizji (LCG)

- **Parametry:** $K = 200 \le 99\,001$, $[a, b] = [1000, 100\,000]$, $m = 2^{31} = 2\,147\,483\,648$, $a = 1\,103\,515\,245$, $c = 12\,345$, $x_0 = 123\,456$, mapowanie `scale` (zapisano w `zad5-gr5/data/lcg_no_collisions.txt`).
- **Wynik weryfikacji:** `200 / 200` unikalnych liczb (`0` kolizji), spełnione wszystkie 3 warunki twierdzenia Hulla–Dobella (okres stanu $2^{31}$, część przedcykliczna $\mu = 0$).

### 4.4. Wnioski dla LCG

1. **Twierdzenie Hulla–Dobella wyznacza okres maksymalny:** Zestaw `m=15, a=51, c=13` nie spełnia warunku podzielności $a - 1 = 50$ przez dzielnik pierwszy $3 \mid 15$, przez co cykl skraca się do 5 (195 kolizji). Zestaw `m=1024, a=12, c=4` ma $\gcd(m, c) = 4 \ne 1$ i wpada po przedcyklu $\mu = 5$ w punkt stały ($\lambda = 1$).
2. **Wpływ ziarna $x_0$:** Przy spełnionych warunkach Hulla–Dobella zmiana ziarna (`x0=55` vs `x0=999` dla $m=134\,456$) przesuwa wyłącznie punkt startowy na tym samym pełnym cyklu długości $m$.
3. **Jakość mapowania:** Dla $m = 2^k$ należy stosować skalowanie górnych bitów (`scale`), a nie resztę modulo (`mod`), szczególnie gdy szerokość przedziału dzieli się przez potęgę dwójki.

---

## 5. Wyniki — Część C: Testy pierwszości i analiza skuteczności (zakres Grupy 3)

### 5.1. Porównanie na zbiorach z LFSR i LCG ($K = 200$ na zbiór, $[1000, 100\,000]$, $s = 10$, `rng_seed = 20261126`)

Każdy pomiar obejmuje dokładnie jedno wywołanie testu dla jednej liczby ze zbioru (łączna liczba pomiarów: 200 na metodę i zbiór). Dla dzielenia przez liczby pierwsze sito Eratostenesa do $\lfloor\sqrt{\max}\rfloor$ wyznaczono raz na zbiór i podano osobno. Rzeczywisty status pierwszości ustalono niezależną metodą `is_prime_exact_independent` ($6k \pm 1$).

#### Zbiór LFSR (rzeczywistych liczb pierwszych: **14**, złożonych: **186**; budowa sita do 314: `69.021 us`)

| Test | Pomiary | Min [$\mu$s] | Mediana [$\mu$s] | Średnia [$\mu$s] | Max [$\mu$s] | Pseudopierwsze (FP) | Pseudozłożone (FN) | Trafność |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dzielenie przez liczby pierwsze | 200 | 0.410 | 0.471 | 1.555 | 87.432 | 0 | 0 | 100.00% |
| Test Fermata ($s=10$) | 200 | 0.560 | 1.115 | 5.701 | 47.671 | 0 | 0 | 100.00% |
| Test Millera–Rabina ($s=10$) | 200 | 0.550 | 0.885 | 7.601 | 243.356 | 0 | 0 | 100.00% |

#### Zbiór LCG (rzeczywistych liczb pierwszych: **18**, złożonych: **182**; budowa sita do 315: `33.991 us`)

| Test | Pomiary | Min [$\mu$s] | Mediana [$\mu$s] | Średnia [$\mu$s] | Max [$\mu$s] | Pseudopierwsze (FP) | Pseudozłożone (FN) | Trafność |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dzielenie przez liczby pierwsze | 200 | 0.410 | 0.795 | 1.330 | 31.571 | 0 | 0 | 100.00% |
| Test Fermata ($s=10$) | 200 | 0.569 | 4.320 | 6.192 | 52.471 | 0 | 0 | 100.00% |
| Test Millera–Rabina ($s=10$) | 200 | 0.570 | 5.200 | 7.378 | 61.332 | 0 | 0 | 100.00% |

**Uwaga o zerowej liczbie pseudozłożonych (FN = 0):** Poprawnie zaimplementowane testy Fermata oraz Millera–Rabina mają błąd jednostronny (Monte Carlo z zerowym błędem dla liczb pierwszych) — dla każdej liczby pierwszej $p$ Małe Twierdzenie Fermata oraz warunek Millera–Rabina są spełnione dla każdej podstawy $2 \le t \le p - 2$, więc liczba pseudozłożonych wynosi zawsze dokładnie `0`.

**Uwaga o szumie pomiarowym:** Przy pojedynczych wywołaniach rzędu $0.4$–$8\,\mu\text{s}$ pojedyncze wartości maksymalne (np. `243.356 us`) odzwierciedlają wywłaszczenia systemu operacyjnego / alokacje interpretera Pythona, dlatego mediana jest stabilniejszą miarą typowego czasu niż maksimum.

### 5.2. Zadanie dodatkowe: Skalowanie czasów dla różnych przedziałów i rozmiarów liczb (40 kandydatów niepodzielnych przez 2, 3, 5 na przedział; $s = 10$)

| Przedział | Prawdziwe pierwsze | Budowa sita [$\mu$s] | Dzielenie — średnia [$\mu$s] | Fermat — średnia [$\mu$s] | Miller–Rabin — średnia [$\mu$s] |
| --- | ---: | ---: | ---: | ---: | ---: |
| $[10^3, 10^4]$ (~4 cyfry) | 15 / 40 | 17.1 | **1.540** | 18.664 | 21.585 |
| $[10^5, 10^6]$ (~6 cyfr) | 12 / 40 | 79.9 | **6.360** | 20.088 | 24.140 |
| $[10^7, 10^8]$ (~8 cyfr) | 7 / 40 | 761.0 | 35.084 | **24.071** | 28.515 |
| $[10^9, 10^{10}]$ (~10 cyfr) | 7 / 40 | 7105.5 | 293.899 | **31.616** | 36.367 |
| $[10^{11}, 10^{12}]$ (~12 cyfr) | 10 / 40 | 70279.7 | 1218.479 | **53.044** | 53.519 |

### 5.3. Zadanie dodatkowe: Wpływ liczby iteracji $s$ oraz pułapka liczb Carmichaela

Zbiór testowy (60 liczb): **20 liczb Carmichaela** (`561, 1105, 1729, ..., 162401`) + **20 liczb pierwszych** + **20 zwykłych liczb złożonych**.

| Iteracje $s$ | Fermat średnia [$\mu$s] | Fermat FP (w tym Carmichael) | Miller–Rabin średnia [$\mu$s] | Miller–Rabin FP (w tym Carmichael) | Miller–Rabin FN |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5.220 | 17 (17 / 20) | 9.786 | 1 (1 / 20) | 0 |
| 2 | 11.431 | 15 (15 / 20) | 12.379 | **0 (0 / 20)** | 0 |
| 3 | 13.799 | 11 (11 / 20) | 14.910 | **0 (0 / 20)** | 0 |
| 5 | 13.837 | 1 (1 / 20) | 13.184 | **0 (0 / 20)** | 0 |
| 10 | 24.106 | 1 (1 / 20) | 31.558 | **0 (0 / 20)** | 0 |
| 20 | 45.748 | 1 (1 / 20) | 37.165 | **0 (0 / 20)** | 0 |
| 40 | 67.245 | 0 (0 / 20) | 70.343 | **0 (0 / 20)** | 0 |

### 5.4. Wskazanie najlepszego testu i uzasadnienie

- **Dla małych liczb ($n \le 10^6$, w tym bazowego przedziału $[1000, 100\,000]$):** najlepszy jest **test dzielenia przez liczby pierwsze** ze współdzielonym sitem — okazał się ok. **4–5× szybszy** (średnia `1.33–1.56 us` vs `7.38–7.60 us` dla Millera–Rabina) i daje **100% deterministycznej pewności**.
- **Dla dużych liczb ($n \ge 10^7$ i w zastosowaniach kryptograficznych):** bezkonkurencyjnie najlepszy jest **test Millera–Rabina** ($s \ge 10$–$20$). Dla liczb 12-cyfrowych jest **~23× szybszy** na pojedynczym wywołaniu niż dzielenie przez liczby pierwsze (i nie wymaga ponad 70 ms na budowę sita), a przy tym wykrywa liczby Carmichaela już od $s = 2$ (0/20 błędów), podczas gdy test Fermata myli się na nich nawet przy $s = 20$.

---

## 6. Dokumentacja procesu pracy z GenAI (zakres Grupy 5)

### 6.1. Dane sesji i wykorzystanego narzędzia
- **Narzędzie / model w tym przebiegu:** sesja AI Studio Build (wersja modelu nie została jawnie podana przez użytkownika w danych wejściowych — należy dopisać identyfikator modelu z interfejsu przy zestawianiu wielu modeli).
- **Podział pracy:** całość kodu Pythona (`lfsr.py`, `lcg.py`, `primality.py`, `run_experiments.py`, `tests/test_all.py`), uruchomienie testów i eksperymentów oraz szkic sprawozdania powstały w tej sesji przy bezpośredniej weryfikacji w terminalu (Python 3.11.2).
- **Wykryte błędy i poprawki podczas weryfikacji:**
  1. W pierwszym uruchomieniu `tests/test_all.py` test `test_benchmark_statistics_consistency` zgłosił błąd asercji (`AssertionError: 6 != 5`) — model podczas ręcznego wpisywania oczekiwanej liczby pierwszych w 10-elementowej próbce testowej błędnie policzył 5 zamiast 6 (w zbiorze `[2, 3, 4, 17, 561, 1009, 1013, 1729, 2047, 7919]` pierwszych jest 6: `2, 3, 17, 1009, 1013, 7919`). Błąd wykryto automatycznie testem jednostkowym i poprawiono przed uruchomieniem eksperymentów.
  2. Zidentyfikowano potencjalną pułapkę w mapowaniu LFSR (`n=8` przy `w=17` ma $\gcd(17, 255) = 17$) oraz LCG (`mod` psuje parzystość dla $m=2^k$) i udokumentowano je empirycznie w tabelach.
- **Zrealizowane wymagania dodatkowe:** Podjęto i w pełni zrealizowano wymagania dodatkowe Grup 1, 2 i 3 (pełna walidacja parametrów i błędów plików/formatu, porównanie wielu konfiguracji odczepów i parametrów LCG, testy jednostkowe `unittest`, skalowanie czasów po rozmiarze liczb, wpływ liczby iteracji Millera–Rabina oraz test liczb Carmichaela).

### 6.2. Szablon protokołu porównawczego dla innych modeli GenAI (do uzupełnienia po uruchomieniu kolejnych modeli)

Aby rzetelnie zrealizować porównanie różnych modeli GenAI oraz wskazać najlepszy model dla każdego typu zadania, kolejne modele należy uruchomić z tym samym promptem głównym oraz ocenić według wspólnych kryteriów:

| Model / wariant | Zgodność LFSR (testy) | Zgodność LCG (testy) | Zgodność pierwszość (testy) | Liczba błędów przed poprawkami | Czas korekty człowieka [h] | Jakość tabel i wniosków (1–5) |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Przebieg bieżący (uzupełnić nazwę modelu) | 7/7 OK | 4/4 OK | 5/5 OK | 1 (asercja w teście) | *do uzupełnienia* | *do uzupełnienia* |
| Model 2 (*do uzupełnienia*) | — | — | — | — | — | — |
| Model 3 (*do uzupełnienia*) | — | — | — | — | — | — |

### 6.3. Ewidencja czasu pracy członków Grupy 5 (do uzupełnienia przez zespół — w zaokrągleniu do pełnych godzin)

> **Ważne:** Model GenAI nie zmyśla roboczogodzin ludzi. Przed oddaniem sprawozdania (30.11.2026, 18:00) należy wpisać rzeczywisty czas pracy każdego członka zespołu w zaokrągleniu do pełnych godzin oraz sumę.

| Osoba | Podzespół / zadanie | Czas pracy [h] (pełne godziny) | Uwagi (np. weryfikacja, poprawki, uruchomienie innych modeli) |
| --- | --- | ---: | --- |
| *Osoba 1* | Podzespół LFSR + weryfikacja | `[uzupełnić]` | — |
| *Osoba 2* | Podzespół LCG + weryfikacja | `[uzupełnić]` | — |
| *Osoba 3* | Podzespół Testy pierwszości + weryfikacja | `[uzupełnić]` | — |
| *Osoba 4* | Porównanie modeli GenAI + redakcja sprawozdania | `[uzupełnić]` | — |
| **SUMA** | **Łącznie Grupa 5** | **`[uzupełnić]`** | — |

---

## 7. Lista kontrolna wymagań (status końcowy bieżącej sesji)

| Sekcja | Wymaganie | Status | Dowód wykonania |
| --- | --- | --- | --- |
| **LFSR** | Implementacja konfigurowalnego LFSR (długość, odczepy, ziarno) | **wykonane i sprawdzone** | `zad5-gr5/lfsr.py`, `tests/test_all.py` (7 testów OK) |
| **LFSR** | Generowanie $K$ liczb z $[a, b]$ i zapis do pliku | **wykonane i sprawdzone** | `zad5-gr5/data/lfsr_numbers.txt` ($K=200$) |
| **LFSR** | Wykrywanie powtórzeń, kolizji i długości cyklu | **wykonane i sprawdzone** | `analyze_collisions`, `detect_state_cycle`, `detect_output_word_cycle` |
| **LFSR** | Ciąg $K$ liczb bez kolizji z parametrami i warunkiem $K \le b-a+1$ | **wykonane i sprawdzone** | `zad5-gr5/data/lfsr_no_collisions.txt` (200/200 unikalnych) |
| **LFSR** | Analiza wpływu długości, odczepów, ziarna + tabele | **wykonane i sprawdzone** | Tabela 3.3, `results/SUMMARY_TABLES.md` |
| **LFSR (dod.)** | Kontrola błędów parametrów/pliku/formatu, porównanie odczepów, testy | **wykonane i sprawdzone** | `TestLFSR` w `tests/test_all.py` |
| **LCG** | Implementacja $x_{i+1} = (a x_i + c) \bmod m$ | **wykonane i sprawdzone** | `zad5-gr5/lcg.py`, wyjaśnienie `b` vs `c` |
| **LCG** | Generowanie $K$ liczb z $[a, b]$ i zapis do pliku | **wykonane i sprawdzone** | `zad5-gr5/data/lcg_numbers.txt` ($K=200$) |
| **LCG** | Kolizje, cykl stanu $\lambda$ i przedcykl $\mu$ | **wykonane i sprawdzone** | `detect_state_cycle` (Floyd) + `check_hull_dobell` |
| **LCG** | Ciąg $K$ liczb bez kolizji z parametrami | **wykonane i sprawdzone** | `zad5-gr5/data/lcg_no_collisions.txt` (200/200 unikalnych) |
| **LCG** | Analiza wpływu $m, a, c, x_0$ + tabele | **wykonane i sprawdzone** | Tabela 4.2, `results/SUMMARY_TABLES.md` |
| **LCG (dod.)** | Kontrola błędów parametrów/pliku/formatu, porównanie zestawów, testy | **wykonane i sprawdzone** | `TestLCG` w `tests/test_all.py` |
| **Pierwszość** | Dzielenie przez liczby pierwsze do $\lfloor\sqrt{n}\rfloor$ | **wykonane i sprawdzone** | `trial_division_by_primes` w `zad5-gr5/primality.py` |
| **Pierwszość** | Własne szybkie potęgowanie binarne modulo $n$ | **wykonane i sprawdzone** | `mod_pow_binary`, testowane vs `pow()` |
| **Pierwszość** | Test Fermata i test Millera–Rabina z ustalonym $s$ i ziarnem | **wykonane i sprawdzone** | `fermat_test`, `miller_rabin_test` ($s=10$, `seed=20261126`) |
| **Pierwszość** | Uruchomienie na zbiorach LFSR i LCG + zapis wyników i czasów | **wykonane i sprawdzone** | `results/primality_lfsr_results.csv`, `primality_lcg_results.csv` |
| **Pierwszość** | Statystyki czasów (min, max, średnia, mediana) + status rzeczywisty (FP/FN) | **wykonane i sprawdzone** | Tabele w sekcji 5.1, `is_prime_exact_independent` |
| **Pierwszość** | Porównanie testów i wskazanie najlepszego | **wykonane i sprawdzone** | Sekcja 5.4 (osobno małe vs duże liczby) |
| **Pierwszość (dod.)** | Skalowanie dla różnych $[a, b]$, wpływ iteracji MR, liczby Carmichaela, testy | **wykonane i sprawdzone** | Tabele 5.2 i 5.3, `TestPrimality` (5 testów OK) |
| **Grupa 5** | Podział na podzespoły i spójne uruchomienie | **wykonane i sprawdzone** | `zad5-gr5/` + `run_experiments.py` |
| **Grupa 5** | Dokumentacja procesu GenAI, błędów i poprawek | **wykonane i sprawdzone** | Sekcja 6.1 (jawnie opisany wykryty błąd asercji) |
| **Grupa 5** | Porównanie różnych modeli GenAI i ranking modeli | **zablokowane (wymaga innych modeli)** | Przygotowany szablon i identyczny benchmark (sekcja 6.2) |
| **Grupa 5** | Roboczogodziny członków zespołu (zaokrąglone do pełnych godzin) | **zablokowane (wymaga danych od zespołu)** | Tabela do uzupełnienia w sekcji 6.3 |
