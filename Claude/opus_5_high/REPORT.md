# Materiał do sprawozdania — grupa 5 (realizacja z wykorzystaniem GenAI)

Zadanie: **„Generatory pseudolosowe i testy pierwszości”**, laboratorium 5.
Zakres wykonany: **grupy 1–3 w całości** (podstawowe + dodatkowe) oraz dokumentacja
procesu pracy z GenAI. Zadania koordynacyjne grupy 4 **nie** były realizowane.

> Wszystkie liczby w tym dokumencie pochodzą z jednego przebiegu `python3 run_all.py`
> z 25.11.2026 (ok. 22:32 czasu lokalnego) i są w całości odtwarzalne. Pełne tabele
> leżą w `results/`; tu są te najważniejsze wraz z interpretacją. Przy ponownym
> uruchomieniu liczby deterministyczne (okresy, kolizje, decyzje testów) będą
> identyczne, a czasy — z natury — nieco inne.

---

## 1. Informacje o przebiegu

| pozycja | wartość |
|---|---|
| model | Claude Opus 5, identyfikator `claude-opus-5`, tryb Claude Code, effort = high |
| skąd wiadomo o wersji | z opisu środowiska uruchomieniowego; nie weryfikowano niezależnie |
| data przebiegu | 25.11.2026 |
| środowisko | CPython 3.14.7, Linux 7.1.9-arch1-2, x86_64, AMD Ryzen 5 7520U |
| zegar pomiarowy | `time.perf_counter_ns`, monotoniczny, rozdzielczość 1 ns |
| zależności zewnętrzne | brak (tylko biblioteka standardowa) |
| wielkość rozwiązania | 14 plików `.py`, 3451 wierszy (z czego 802 wiersze testów) |
| testy poprawności | 117 testów, wynik **OK**, 0 pominiętych |
| kontrola błędów | 28 wymuszonych przypadków błędnych, 0 nieodrzuconych |
| terminy z README | 26.11.2026 13:30 oraz 30.11.2026 18:00 (sprawozdanie na ostatni termin) |

Źródła, które przeczytano przed implementacją: `zad5/README.md` (harmonogram),
`Kryptologia-lab05_zadania-1.pdf` (zakres grup 1–5), `Kryptologia-lab05. Generatory
pseudolosowe i testy pierwszości.pdf` (notatka teoretyczna), konwencje istniejącego
repozytorium (`README.md` w katalogu głównym, układ katalogów `zad2/`).

### Rozbieżności i nieścisłości znalezione w źródłach

1. **Notatka, slajdy 3 i 4** — niespójna kolejność argumentów LCG:
   `lcg(8121, 28411, 134456, 55)` przy sygnaturze `lcg(a,b,mod,seed)` oznacza `m = 134456`,
   ale `LCG2(134456, 8121, 28411, 55)` przy sygnaturze `LCG2(a,b,mod,seed)` oznacza `m = 28411`.
   Rozwiązanie: parametry przekazywane wyłącznie przez nazwy `LCG(m=…, a=…, c=…, x0=…)`.
2. **Kolizja oznaczeń** — notatka oznacza przyrost LCG literą `b`, a treść zadania używa
   `b` jako prawej granicy przedziału `[a, b]`. W kodzie przyrost to `c`, a przedział to
   `low`/`high`; równoważność opisana w docstringu `lcg.py`.
3. **Notatka, slajd 6** — zapis `p = (p_0, …, p_{m−1}) ∈ Z_2^n`: indeks górny powinien być
   `n−1` (wektor odczepów ma długość `n`). Przyjęto długość `n`.
4. **Notatka, slajd 8 vs treść zadania** — notatka dzieli przez wszystkie liczby naturalne
   do `√a`, a zadanie grupy 3 wymaga dzielenia przez **liczby pierwsze**. Zaimplementowano
   wersję z zadania (z własnym sitem Eratostenesa).
5. **Pseudokod `pierwszaMR`** — pętla `WHILE z <> a-1` kończy się ustawieniem `p <- 0`,
   gdy `j = u`, także wtedy, gdy po `u`-tym podniesieniu do kwadratu `z = a-1`. Jest to
   poprawne: `z` jest wtedy równe `t^(a-1) mod a`, a dla liczby pierwszej musi to być 1,
   nie `a-1`. Implementacja jest wierna notatce i przechodzi test zgodności z dokładnym
   dzieleniem dla wszystkich `n ∈ [2, 3000]`.

---

## 2. Metoda

Pełna lista ustaleń (konwencja stanu LFSR, numeracja odczepów, mapowania na `[a,b]`,
definicja kolizji, sposób wykrywania cyklu, zasady pomiaru czasu) jest w
[`README.md`, sekcja 3](README.md). Najważniejsze decyzje metodyczne:

* **Jeden plik parametrów** (`params.py`) jest umową przebiegu — to on, a nie kod,
  definiuje wejścia; dzięki temu inny model można uruchomić na identycznych danych.
* **Okres nigdy nie jest zakładany** — jest mierzony. Gdy pomiar przerwano po limicie
  kroków, w tabeli pisze „nieustalony”, a nie „duży”. Dla LCG osobno sprawdzane są
  warunki Hull–Dobella, co pozwala odróżnić *teorię* od *pomiaru*.
* **Okres stanu i okres ciągu wartości to dwie różne rzeczy** i są raportowane osobno.
* **Podstawą odniesienia** dla pierwszości jest wyłącznie dokładny test dzielenia.
  Testy probabilistyczne nie są nigdzie przedstawiane jako dowód pierwszości.
* **Mierzony jest tylko czas wywołania testu** — bez odczytu pliku i bez budowy sita
  (sito przygotowywane jest wcześniej funkcją `prepare_primes`).
* **Własne potęgowanie binarne**; wbudowane `pow` pojawia się jedynie w testach
  jednostkowych jako niezależna kontrola (5000 losowych przypadków + duże liczby).

---

## 3. LFSR — zakres grupy 1

### Parametry scenariusza głównego

| parametr | wartość |
|---|---|
| długość rejestru `n` | 16 |
| odczepy (indeksy `j`, dla których `p_j = 1`) | 0, 2, 3, 5 |
| wektor `p` | `1011010000000000` |
| wielomian charakterystyczny | `x^16 + x^5 + x^3 + x^2 + 1` |
| ziarno | `0xACE1` = 44257 = `1010110011100001` |
| `K` | 200 |
| przedział `[a, b]` | `[1, 1000]`, `span = 1000` |
| mapowanie | `reject`, 10 bitów na liczbę, słowa rozłączne |
| plik wyjściowy | `results/lfsr_numbers_main.txt` |

### Wyniki

| miara | wartość | komentarz |
|---|---|---|
| okres **stanu** | **65535**, ogon 0 | równy maksimum `2^16 − 1`, czyli wielomian jest pierwotny (wynik pomiaru, nie założenia) |
| okres ciągu **wartości** | **12801** | blok 13107 słów, powtórzenie bloku potwierdzone |
| liczba różnych wartości w `K = 200` | 182 | |
| liczba kolizji | **18** | wartość oczekiwana dla losowania równomiernego: 18,65 (odchylenie std. 3,8) |
| pierwsza kolizja | pozycja 39, wartość 692 | |
| największa krotność | 3 | wartości 662 i 710 wystąpiły 3 razy |
| udział jedynek w pełnym okresie | 0,5000076 | dokładnie `2^15/(2^16−1)` — własność m-sekwencji |

Dwa niezależne rachunki kontrolne, które się zgadzają:
* okres słów: `65535 / NWD(10, 65535) = 13107`; przy odrzucaniu przechodzi `1000/1024 = 97,66 %`
  słów, czyli ok. 12 800 — pomiar dał 12801;
* udział jedynek wyszedł dokładnie `2^15/(2^16−1)`, co jest cechą ciągu o okresie maksymalnym.

### Wpływ długości rejestru (osobny wielomian dla każdego `n`, ziarno = 1)

| n | odczepy j | f(x) | okres stanu | 2^n−1 | maksymalny? | udział jedynek | różnych w K=200 | kolizji |
|---|---|---|---|---|---|---|---|---|
| 4 | 0,1 | x^4+x+1 | 15 | 15 | tak | 0,5333 | 3 | 197 |
| 8 | 0,2,3,4 | x^8+x^4+x^3+x^2+1 | 255 | 255 | tak | 0,5020 | 50 | 150 |
| 12 | 0,1,4,6 | x^12+x^6+x^4+x+1 | 4095 | 4095 | tak | 0,5001 | 188 | 12 |
| 16 | 0,2,3,5 | x^16+x^5+x^3+x^2+1 | 65535 | 65535 | tak | 0,5000 | 176 | 24 |
| 20 | 0,3 | x^20+x^3+1 | 1048575 | 1048575 | tak | 0,5000 | 170 | 30 |

**Wniosek.** Przy wielomianie pierwotnym długość rejestru decyduje o tym, czy generator
jest w ogóle użyteczny na danym przedziale. Dla `n = 4` okres bitowy 15 daje tylko
**3 różne liczby** na 200 wylosowanych (197 kolizji) — generator fizycznie nie ma z czego
wziąć więcej wartości. Od `n = 12` liczba kolizji spada do poziomu losowania równomiernego
(12–30 przy oczekiwanych ~19) i dalszy wzrost `n` jej już nie zmniejsza: ograniczeniem
przestaje być generator, a staje się paradoks dnia urodzin dla `K = 200` i `span = 1000`.

### Wpływ konfiguracji odczepów (`n = 16`, ziarno `0xACE1`)

| odczepy j | f(x) | ogon | okres stanu | udział jedynek | okres wartości | różnych w K=200 | kolizji |
|---|---|---|---|---|---|---|---|
| 0,2,3,5 | x^16+x^5+x^3+x^2+1 | 0 | 65535 | 0,5000 | 12801 | 182 | 18 |
| 0,11,13,14 | x^16+x^14+x^13+x^11+1 | 0 | 65535 | 0,5000 | 12801 | 183 | 17 |
| 0,1 | x^16+x+1 | 0 | 255 | 0,5020 | 49 | 47 | 153 |
| 0,2 | x^16+x^2+1 | 0 | 126 | 0,5397 | 61 | 61 | 139 |
| 0 | x^16+1 | 0 | 16 | 0,5000 | 8 | 8 | 192 |
| 1,3 | x^16+x^3+x | **1** | 4599 | 0,4942 | — | 183 | 17 |
| 5 | x^16+x^5 | **3** | 11 | 0,6364 | — | 12 | 188 |

**Wnioski.**
1. Odczepy są **najważniejszym** parametrem LFSR. Te same `n` i ziarno dają okres od 11
   do 65535 — różnica ponad trzy rzędy wielkości — zależnie wyłącznie od wyboru `p`.
2. Dwa różne wielomiany pierwotne dają ten sam okres i praktycznie tę samą jakość
   (18 vs 17 kolizji) — do wyboru jest więc wiele równoważnych konfiguracji.
3. `p_0 = 0` psuje odwracalność odwzorowania stanu: pojawia się **ogon** (1 i 3 kroki),
   czyli stan początkowy nie wraca. Dla takich konfiguracji okresu ciągu wartości nie
   mierzono, bo blok z jednego okresu stanu nie zaczyna się od ziarna (uczciwie: „—”).
4. Uwaga interpretacyjna: konfiguracja `1,3` ma zaledwie 17 kolizji, czyli wynik „dobry”,
   choć okres jest 14× krótszy od maksymalnego, a odwzorowanie wadliwe. **Mała liczba
   kolizji na `K = 200` nie jest dowodem jakości generatora** — przy `K ≪ okres` nie widać
   różnicy. Dlatego w tabelach jest też okres i bilans bitów.

### Wpływ ziarna (`n = 16`, odczepy 0,2,3,5)

| ziarno | okres stanu | ogon | różnych w K=200 | kolizji | pierwsze 5 liczb |
|---|---|---|---|---|---|
| 0x0001 | 65535 | 0 | 176 | 24 | 1, 17, 12, 261, 327 |
| 0x00FF | 65535 | 0 | 185 | 15 | 4, 711, 205, 657, 250 |
| 0xACE1 | 65535 | 0 | 182 | 18 | 692, 543, 278, 478, 96 |
| 0xFFFF | 65535 | 0 | 178 | 22 | 7, 772, 830, 695, 317 |
| 0x8000 | 65535 | 0 | 181 | 19 | 513, 9, 6, 643, 164 |
| 0x3039 | 65535 | 0 | 181 | 19 | 193, 920, 399, 473, 174 |
| 0x0000 | **1** | 0 | 1 | 9 na 10 liczb | 1, 1, 1, 1, 1 (ciąg stale 1) |

**Wniosek.** Dla wielomianu pierwotnego ziarno **nie ma wpływu na okres** — każde
niezerowe ziarno leży na tym samym cyklu długości 65535 i zmienia tylko fazę. Widać to
w tabeli: okres jest identyczny, a liczba kolizji waha się w przedziale 15–24, czyli
w granicach losowej fluktuacji wokół 18,65. Jedynym wyjątkiem jest **ziarno zerowe**:
stan zeruje się na stałe, ciąg bitów jest stale 0, a wszystkie liczby wynikowe to `a = 1`.
Implementacja domyślnie odrzuca takie ziarno wyjątkiem; tu dopuszczono je jawnie,
żeby pokazać ten przypadek brzegowy.

### Ciąg `K` liczb bez powtórzeń

| wariant | parametry | wynik |
|---|---|---|
| filtr powtórzeń | `n=16`, odczepy 0,2,3,5, ziarno `0xACE1`, `K=200`, `[1,1000]` | 200 różnych liczb, plik `results/lfsr_numbers_unique.txt` |
| bez filtru (dobrane ziarno) | `n=16`, odczepy 0,2,3,5, **ziarno `0x0002`**, `K=50`, `[1,10000]` | 0 kolizji w surowym ciągu, plik `results/lfsr_numbers_raw_unique.txt` |
| przypadek niewykonalny | `K=1500`, `[1,1000]` | odrzucone **przed** generowaniem: `K=1500 > b−a+1=1000` (zasada szufladkowa) |

Warunek `K ≤ b − a + 1` jest sprawdzany jawnie (`check_k_fits_interval`). Dla `K = 200`
i `[1, 1000]` jest spełniony. Pokazano dwa sposoby uzyskania ciągu bez powtórzeń:
(a) **filtr** — pomijanie wartości już użytych; to modyfikacja ciągu wyjściowego, która
zmienia rozkład odstępów, i trzeba o tym mówić wprost; (b) **dobór ziarna** tak, żeby
surowy ciąg był bezkolizyjny — wykonalne tylko przy `K` dostatecznie małym względem
`span` (tu `K = 50` z 10000, znalezione przy drugim sprawdzanym ziarnie).

---

## 4. LCG — zakres grupy 2

### Parametry scenariusza głównego

| parametr | wartość |
|---|---|
| `m` | 65536 = 2^16 |
| `a` (mnożnik) | 25173 |
| `c` (przyrost; w notatce `b`) | 13849 |
| `x0` (ziarno) | 2026 |
| `K`, przedział | 200, `[1, 1000]` |
| mapowanie | `mod_reject`: odrzuć `x ≥ 65000`, zwróć `1 + x mod 1000` |
| plik wyjściowy | `results/lcg_numbers_main.txt` |

`m` wybrano **mniejsze od typowych wartości bibliotecznych celowo**: przy `m = 2^16`
cały okres (65536 kroków) da się zmierzyć w całości, więc raportowany okres jest
pomiarem, a nie deklaracją.

### Wyniki

| miara | wartość | komentarz |
|---|---|---|
| warunki Hull–Dobella | **spełnione** | `NWD(13849, 65536) = 1`; `a−1 = 25172` podzielne przez 2 i przez 4 |
| okres stanu (zmierzony) | **65536**, ogon 0 | zgodnie z warunkami: pełny okres `m` |
| okres ciągu wartości | **65000** | dokładnie `m − (m mod span) = 65536 − 536` — liczba stanów akceptowanych |
| różnych wartości w `K=200` | 178 | |
| kolizji | **22** | oczekiwane 18,65 ± 3,8 — mieści się w granicach fluktuacji |
| pierwsza kolizja | pozycja 15, wartość 939 | |

### Wpływ parametrów `m`, `a`, `c`

| zestaw | m | a | c | Hull–Dobell | ogon | okres (zmierzony) | różnych w K=200 | kolizji |
|---|---|---|---|---|---|---|---|---|
| scenariusz główny | 65536 | 25173 | 13849 | spełnione | 0 | 65536 = m | 178 | 22 |
| notatka (przykład) | 15 | 51 | 13 | niespełnione | 0 | **5** | mapowanie niemożliwe (`m < span`) | — |
| ANSI C | 2^31 | 1103515245 | 12345 | spełnione | ? | nieustalony (> 200 000) | 181 | 19 |
| Borland | 2^32 | 22695477 | 1 | spełnione | ? | nieustalony | 186 | 14 |
| MS Visual C++ | 2^32 | 214013 | 2531011 | spełnione | ? | nieustalony | 181 | 19 |
| MS Visual Basic | 2^24 | 1140671485 | 12820163 | spełnione | ? | nieustalony | 184 | 16 |
| Java | 2^48 | 25214903917 | 11 | spełnione | ? | nieustalony | 188 | 12 |
| pełny okres, małe m | 1024 | 5 | 1 | spełnione | 0 | 1024 = m | 200 | **0** |
| `c = 0` (multiplikatywny) | 65536 | 25173 | 0 | nie dotyczy (`c = 0`) | 0 | **8192** = m/8 | 106 | **94** |
| `a = 1` (licznik) | 65536 | 1 | 13849 | spełnione | 0 | 65536 = m | 200 | **0** |
| `a = 0` (stała) | 65536 | 0 | 13849 | niespełnione | **1** | **1** | 1 | 199 |
| `a = 2, c = 0` | 65536 | 2 | 0 | niespełnione | **15** | **1** | 15 | 185 |
| `m` nie jest potęgą 2 | 1000 | 21 | 3 | spełnione | 0 | 1000 = m | 200 | 0 |

**Wnioski.**
1. **Warunki Hull–Dobella sprawdziły się w każdym mierzalnym przypadku**: gdy były
   spełnione, zmierzony okres był równy `m` (65536, 1024, 1000), i to niezależnie od
   ziarna. Gdy nie były — okres był krótszy (`m = 15`: 5 zamiast 15).
2. Dla zestawów bibliotecznych (`m ≥ 2^24`) **nie ogłaszam okresu maksymalnego**:
   pomiar przerwano po 200 000 krokach, więc w tabeli jest „nieustalony”. Wiadomo tylko,
   że warunki teoretyczne są spełnione.
3. `c = 0` (generator multiplikatywny) zmniejsza okres z 65536 do 8192 i to natychmiast
   widać w danych: 94 kolizje na 200 liczb zamiast 22.
4. **Zero kolizji nie znaczy „dobry generator”.** `a = 1` daje 0 kolizji na `K = 200`,
   ale ciąg jest arytmetyczny (kolejne liczby różnią się o stałą modulo) — zupełnie
   nielosowy. Kolizje trzeba czytać razem z okresem i strukturą ciągu.
5. Degeneracje widać po **ogonie**: `a = 0` (ogon 1, potem stała), `a = 2, c = 0`
   (ogon 15 — generator wpada w zero i zostaje tam). Tego nie dałoby się zauważyć,
   licząc tylko kolizje liczb wynikowych.

### Wpływ ziarna `x0`

Dla `m = 65536, a = 25173, c = 13849` i ziaren 0, 1, 2026, 12345, 65535 zmierzony
okres wyniósł **za każdym razem 65536 z ogonem 0**, a liczba kolizji 14–24.
To zgadza się z teorią: przy spełnionych warunkach Hull–Dobella okres jest pełny
dla **każdego** ziarna, a ziarno wybiera tylko punkt startu na tym samym cyklu.

### Wpływ sposobu mapowania — najciekawszy wynik tej części

| przedział | span | tryb | okres stanu | okres wartości | różnych w K=200 | kolizji |
|---|---|---|---|---|---|---|
| [1, 1000] | 1000 | mod_reject | 65536 | 65000 | 178 | 22 |
| [1, 1000] | 1000 | mod | 65536 | 65536 | 178 | 22 |
| [1, 1000] | 1000 | scale | 65536 | 65536 | 181 | 19 |
| [1, 1024] | 1024 | mod_reject | 65536 | **1024** | 200 | **0** |
| [1, 1024] | 1024 | mod | 65536 | **1024** | 200 | **0** |
| [1, 1024] | 1024 | scale | 65536 | 65536 | 184 | 16 |

**Wniosek.** Dla `m = 2^16` i `span = 1024 = 2^10` mapowanie przez resztę modulo bierze
dokładnie **10 najmniej znaczących bitów stanu**, a te mają w LCG o module będącym potęgą
dwójki okres zaledwie 1024 — ciąg wartości powtarza się 64 razy szybciej niż stan.
Co gorsza, na `K = 200` objawia się to jako **zero kolizji**, czyli pozornie idealny wynik:
generator przebiega bez powtórzeń początek swojego krótkiego cyklu. Mapowanie `scale`
(bity najstarsze) na tych samych danych daje okres wartości 65536 i 16 kolizji, czyli
zachowanie zgodne z losowaniem równomiernym. **Ten sam generator, ta sama liczba kolizji
bliska zeru — a jakość zupełnie inna; rozstrzyga dopiero okres ciągu wartości.**
Dlatego w tym projekcie okres wartości jest mierzony osobno i raportowany zawsze.

### Ciąg `K` liczb bez powtórzeń

| wariant | parametry | wynik |
|---|---|---|
| filtr powtórzeń | `m=65536, a=25173, c=13849, x0=2026`, `K=200`, `[1,1000]` | 200 różnych liczb, `results/lcg_numbers_unique.txt` |
| bez filtru, konstrukcyjnie | `m=1024, a=5, c=1, x0=7`, `K=200`, `[1,1024]`, mapowanie `mod` | **0 kolizji**, `results/lcg_numbers_raw_unique.txt` |
| nasycenie ograniczenia | te same parametry, `K = 1024 = b−a+1` | **0 kolizji** — cały przedział bez powtórzeń |
| przypadek niewykonalny | `K=1500`, `[1,1000]` | odrzucone przed generowaniem |

Drugi wariant jest skonstruowany, a nie znaleziony metodą prób: warunki Hull–Dobella
dla `m = 1024, a = 5, c = 1` są spełnione (okres 1024 potwierdzony pomiarem), a przy
`span = m` mapowanie `mod` jest bijekcją, więc jeden pełny okres to permutacja przedziału
`[1, 1024]`. Można więc dostać nawet `K = b − a + 1 = 1024` różnych liczb — maksimum
dopuszczone zasadą szufladkową. Cena: taki ciąg jest permutacją całego przedziału,
czyli skrajnie przewidywalny (to ten sam problem, co w akapicie o mapowaniu).

---

## 5. Testy pierwszości — zakres grupy 3

### Co uruchomiono

Trzy testy — dokładne dzielenie przez liczby pierwsze do `⌊√n⌋`, Fermat (`s = 5`),
Miller–Rabin (`s = 5`) — na **wszystkich** `K = 200` liczbach z pliku LFSR i **wszystkich**
200 liczbach z pliku LCG. Wynik i czas **każdego** wywołania (1200 pomiarów) są
w `results/primality_calls_lfsr.csv` i `results/primality_calls_lcg.csv`
z identyfikacją źródła i pozycji w pliku.

### Statystyki czasu (ns, 200 pomiarów na test i źródło)

| źródło | test | min | mediana | średnia | max |
|---|---|---|---|---|---|
| LFSR | dzielenie | 250 | 320 | **370** | 2 605 |
| LFSR | Fermat | 200 | 276 | **1 489** | 10 069 |
| LFSR | Miller–Rabin | 210 | 250 | **1 498** | 6 332 |
| LCG | dzielenie | 270 | 336 | **394** | 3 787 |
| LCG | Fermat | 200 | 802 | **1 588** | 6 272 |
| LCG | Miller–Rabin | 210 | 797 | **1 619** | 6 202 |

**Ostrzeżenie metodyczne (ważne dla interpretacji).** Rozkład czasów jest **dwumodalny**:
liczby parzyste (i `n < 2`, 2, 3) kończą się na warunku brzegowym po jednym dzieleniu,
a liczby nieparzyste `≥ 5` wymagają `s` potęgowań modulo. Ponieważ parzystych jest około
połowy, **mediana całego zbioru wypada dokładnie na granicy dwóch skupień** i reaguje na
drobną zmianę proporcji parzystych (dlatego mediana LFSR 276 ns wobec LCG 802 ns przy
niemal identycznych średnich — plik LFSR ma 108 liczb parzystych, plik LCG dokładnie 100).
Dla tych danych **miarą właściwą jest średnia** albo statystyki rozbite na grupy
(tabela 1b w `results/primality_analysis.md`), np. dla LFSR/Fermat: 92 pełne testy
(średnia 2 959 ns) i 108 wyjść brzegowych (średnia 236 ns) — różnica ponad 12×,
a w zestawieniu zbiorczym widać tylko jedną liczbę pośrednią.

### Rzeczywisty status pierwszości i błędne decyzje

Podstawa odniesienia: **dokładny test dzielenia** (niezależna metoda dokładna; rozmiary
liczb w pełni na to pozwalają). Trafność liczona na zbiorze liczb **unikalnych**.

| źródło | liczb unikalnych | pierwszych | złożonych | pseudopierwsze (Fermat) | pseudozłożone (Fermat) | pseudopierwsze (M–R) | pseudozłożone (M–R) |
|---|---|---|---|---|---|---|---|
| LFSR | 182 | 29 | 153 | **0** | **0** | **0** | **0** |
| LCG | 178 | 36 | 142 | **0** | **0** | **0** | **0** |

Dwa komentarze, bez których ta tabela jest myląca:

1. **Zero pseudozłożonych nie jest szczęściem, tylko własnością testów.** Fermat
   i Miller–Rabin orzekają „złożona” wyłącznie na podstawie kontrprzykładu (świadka
   złożoności), a dla liczby pierwszej taki świadek nie istnieje. Poprawnie
   zaimplementowany test **nie może** odrzucić liczby pierwszej — gdyby to się zdarzyło,
   byłby to błąd implementacji, nie własność metody. Potwierdzone testem jednostkowym:
   oba testy akceptują **wszystkie 669 liczb pierwszych do 5000**.
2. **Zero pseudopierwszych wynika z małego przedziału,** a nie z niezawodności Fermata.
   W `[1, 1000]` jest tylko kilka liczb mylących ten test, a `s = 5` losowych podstaw
   prawie zawsze je wykrywa. Dlatego słabość Fermata zbadano osobno — poniżej.

### Liczby mylące testy (przeliczenie wyczerpujące, nie losowe)

Dla każdej liczby Carmichaela sprawdzono **wszystkie** podstawy `t ∈ {2, …, n−2}`:

| n | liczba podstaw | kłamcy Fermata | % | kłamcy Millera–Rabina | % | P(Fermat się myli przy s=5) |
|---|---|---|---|---|---|---|
| 561 | 558 | 318 | 56,99 | 8 | 1,43 | 6,0 % |
| 1105 | 1102 | 766 | 69,51 | 28 | 2,54 | 16,2 % |
| 1729 | 1726 | 1294 | 74,97 | 160 | 9,27 | 23,7 % |
| 2465 | 2462 | 1790 | 72,71 | 68 | 2,76 | 20,3 % |
| 2821 | 2818 | 2158 | 76,58 | 268 | 9,51 | 26,3 % |
| 6601 | 6598 | 5278 | 79,99 | 328 | 4,97 | 32,8 % |
| 8911 | 8908 | 7126 | 80,00 | 1780 | 19,98 | 32,8 % |
| 10585 | 10582 | 8062 | 76,19 | 628 | 5,93 | 25,7 % |
| 15841 | 15838 | 12958 | 81,82 | 808 | 5,10 | 36,7 % |
| 29341 | 29338 | 25918 | 88,34 | 4048 | 13,80 | 53,8 % |

Kontrola poprawności tych rachunków: dla `n = 561 = 3·11·17` kłamcami Fermata są
dokładnie podstawy względnie pierwsze z `n`, a `φ(561) = 2·10·16 = 320`; po odjęciu
podstaw 1 i 560 (poza zakresem losowania) zostaje **318** — tyle samo, ile wyliczył
program. Zgodność z teorią liczbową potwierdza implementację.

**Wniosek.** Dla liczb Carmichaela test Fermata myli się **w 57–88 % pojedynczych
podstaw**, a przy `s = 5` losowych podstawach uznaje je za pierwsze z prawdopodobieństwem
od 6 % (`561`) do 54 % (`29341`). Miller–Rabin na tych samych liczbach ma 1,4–20 %
kłamców, czyli od 4 do 40 razy mniej, **przy identycznym koszcie obliczeniowym**.
W zbiorze brzegowym (tabela 3 w `results/primality_analysis.md`) widać to na konkretnym
przypadku: przy ustalonym ziarnie 12345 Fermat uznał `561` za pierwszą, a Miller–Rabin ją
odrzucił.

### Wpływ liczby iteracji (331 unikalnych liczb z obu generatorów)

| s | Miller–Rabin: średnia [ns] | M–R: pseudopierwsze | Fermat: średnia [ns] | Fermat: pseudopierwsze |
|---|---|---|---|---|
| 1 | 836 | 0 | 689 | **3** (39, 435, 635) |
| 2 | 985 | 0 | 834 | 0 |
| 3 | 1 192 | 0 | 1 013 | **1** (561) |
| 5 | 1 468 | 0 | 1 319 | 0 |
| 10 | 2 256 | 0 | 2 558 | 0 |
| 20 | 3 873 | 0 | 3 752 | 0 |
| 40 | 6 655 | 0 | 6 740 | 0 |

**Wnioski.**
1. Koszt rośnie **liniowo** z `s` (z wyraźnym narzutem stałym: `s = 40` jest ok. 8×,
   a nie 40× droższe od `s = 1`, bo połowa liczb kończy się na warunku brzegowym).
2. Miller–Rabin **nie pomylił się ani raz** na tych danych, nawet przy `s = 1`.
3. Fermat przy `s = 1` uznał za pierwsze 3 liczby złożone (39, 435, 635 — pojedyncze
   podstawy, które je „przepuściły”), a przy `s = 3` liczbę Carmichaela 561.
   Niemonotoniczność (`s = 2` → 0 błędów, `s = 3` → 1 błąd) to **nie błąd pomiaru**,
   tylko konsekwencja tego, że przy każdym `s` losowany jest inny zestaw podstaw.
   Wniosek praktyczny: zwiększanie `s` zmniejsza prawdopodobieństwo błędu
   (ograniczenie `4^-s` dla M–R), ale pojedynczy przebieg nie jest dowodem braku błędów.
4. W tym scenariuszu wzrost `s` powyżej kilku iteracji **kupuje tylko gwarancję
   teoretyczną** — mierzalnej poprawy trafności nie było, bo liczby są małe i łatwe.

### Wpływ przedziału i rozmiaru liczb (60 liczb z LFSR + 60 z LCG na przedział)

| przedział | dzielenie: średnia | Fermat: średnia | Miller–Rabin: średnia | % pierwszych |
|---|---|---|---|---|
| [1, 10^3] | **367 ns** | 1 537 ns | 1 590 ns | 18,3 |
| [10^3, 10^6] | **719 ns** | 1 851 ns | 1 907 ns | 9,2 |
| [10^6, 10^9] | 8 340 ns | **2 704 ns** | 2 824 ns | 9,2 |
| [10^9, 10^12] | 183 149 ns | 8 461 ns | **8 005 ns** | 5,8 |

**Wnioski.**
1. Czas dzielenia próbnego rośnie jak `√n`: od 367 ns do 183 µs, czyli **500×** na
   przestrzeni dziewięciu rzędów wielkości `n`. Testy probabilistyczne rosną
   logarytmicznie (koszt potęgowania) — tylko **5×** w tym samym zakresie.
2. **Punkt przełamania leży między `10^6` a `10^9`.** Dla `n ≲ 10^6` dokładne dzielenie
   jest szybsze *i* dokładne — probabilistyka nie ma tu czego oferować. Dla `n ≳ 10^9`
   relacja się odwraca i przy `10^12` Miller–Rabin jest już ok. 23× szybszy.
3. Mediany w tych przedziałach pozostają małe (np. 476 ns dla dzielenia przy `10^12`),
   bo większość liczb złożonych ma mały dzielnik i wypada po kilku dzieleniach;
   drogie są tylko liczby pierwsze i liczby o dużych dzielnikach. To kolejny powód,
   żeby patrzeć na średnią i maksimum, a nie na samą medianę.

### Który test jest najlepszy — dla zmierzonego scenariusza

| kryterium | dzielenie przez liczby pierwsze | Fermat (s=5) | Miller–Rabin (s=5) |
|---|---|---|---|
| wiarygodność | **dokładny** (dowód) | brak dowodu, podatny na liczby Carmichaela | brak dowodu, błąd ≤ 4^-s |
| błędne decyzje w scenariuszu głównym | 0 (definicyjnie) | 0 przy s=5; 3 przy s=1 | 0 |
| błędne decyzje na liczbach Carmichaela | 0 | 6–54 % przypadków | 1,4–20 % podstaw |
| koszt dla `[1, 1000]` | **370–394 ns** | 1 489–1 588 ns | 1 498–1 619 ns |
| koszt dla `[10^9, 10^12]` | 183 µs | 8,5 µs | **8,0 µs** |
| skalowanie | `O(√n / ln √n)` | `O(s·log n)` mnożeń modulo | `O(s·log n)` mnożeń modulo |

**Rozstrzygnięcie dla zmierzonego scenariusza** (`K = 200`, `[1, 1000]`, CPython 3.14.7,
`s = 5`): najlepszy jest **dokładny test dzielenia** — jest zarazem najszybszy
(średnio ok. 4× szybszy od obu testów probabilistycznych) i jedyny dający pewność.
Przy liczbach, dla których zadanie laboratoryjne ma sens praktyczny
(czyli dużych, od `~10^9` w górę), najlepszy jest **Miller–Rabin**.

**Fermat jest zdominowany**: ma praktycznie ten sam koszt co Miller–Rabin (tyle samo
potęgowań modulo), a istotnie gorszą wiarygodność. Nie ma scenariusza w tych pomiarach,
w którym warto byłoby wybrać Fermata — poza wartością dydaktyczną.

**Ograniczenia tego rozstrzygnięcia.** Pomiary dotyczą jednej maszyny, jednego procesu
i liczb do `10^12` (tam, gdzie dokładna podstawa odniesienia jest wykonalna). Dla liczb
kryptograficznych (`2^1024` i więcej) dzielenie próbne jest nieużywalne i porównanie
wyglądałoby inaczej; tego nie mierzono i nie ekstrapoluję.

---

## 6. Wymagania dodatkowe — rezultaty

| wymaganie (grupa) | rezultat | dowód |
|---|---|---|
| kontrola błędów: niepoprawne parametry (1, 2) | **wykonane**; 22 przypadki, każdy z komunikatem w języku polskim | `results/error_handling.md`, `demo_errors.py` |
| kontrola błędów: brak pliku, błędny format (1, 2) | **wykonane**; 6 przypadków: brak pliku, katalog, zły wiersz z numerem, liczba rzeczywista, plik bez liczb, plik binarny | `results/error_handling.md` |
| porównanie kilku konfiguracji odczepów (1) | **wykonane**; 7 konfiguracji, okresy 11–65535 | `results/lfsr_analysis.md` §4 |
| porównanie kilku zestawów parametrów (2) | **wykonane**; 13 zestawów (w tym biblioteczne i zdegenerowane) | `results/lcg_analysis.md` §3 |
| testy poprawności implementacji (1, 2, 3) | **wykonane**; 117 testów, w tym 4 przykłady LFSR z notatki, zgodność stanów LCG z równaniem, `pow_mod` vs `pow` na 5000 losowych przypadkach | `python3 -m unittest discover -v` |
| czasy dla różnych przedziałów i rozmiarów (3) | **wykonane**; 4 przedziały od `10^3` do `10^12`, 1440 pomiarów | `results/primality_analysis.md` §6 |
| wpływ liczby iteracji Millera–Rabina (3) | **wykonane**; `s ∈ {1,2,3,5,10,20,40}` dla M–R i Fermata | `results/primality_analysis.md` §5 |
| przypadki brzegowe i liczby mylące Fermata (3) | **wykonane**; tabela 22 liczb + wyczerpujące przeliczenie kłamców dla 10 liczb Carmichaela | `results/primality_analysis.md` §3, §4 |
| wskazanie najlepszego modelu GenAI dla typu zadania (5) | **niewykonalne w jednym przebiegu** — wymaga wyników innych modeli | sekcja 9 |
| liczba błędów wymagających poprawek (5) | **częściowo**: policzone dla tego przebiegu (10 pozycji), nie dla innych modeli | `GENAI_LOG.md` |
| zebranie najciekawszych promptów (5) | **częściowo**: zapisane prompty i korekty z tej sesji | `GENAI_LOG.md` |

---

## 7. Co faktycznie uruchomiono i z jakim wynikiem

| komenda | wynik |
|---|---|
| `python3 -m unittest discover -v` | 117 testów, **OK**, 0 pominiętych, czas ok. 2,2 s |
| `python3 exp_lfsr.py` | pliki `lfsr_numbers_*.txt`, `lfsr_analysis.md`, `lfsr_variants.csv` |
| `python3 exp_lcg.py` | pliki `lcg_numbers_*.txt`, `lcg_analysis.md`, `lcg_variants.csv` |
| `python3 exp_primality.py` | `primality_calls_{lfsr,lcg}.csv` (1200 pomiarów), `primality_analysis.md`, `environment.txt` |
| `python3 demo_errors.py` | `error_handling.md`: 28 przypadków, **0 nieodrzuconych** |
| `python3 run_all.py` | cały przebieg w 10,6 s; `summary.md` + `benchmark.json` |
| `python3 lfsr.py --n 4 --taps 0,1 --seed 0001 --count 10 --low 1 --high 8` | sprawdzenie CLI; ciąg o okresie 5 wartości, zgodny z okresem bitowym 15 |
| `python3 primality.py 561 1105 7919 104729` | sprawdzenie CLI testów |

Kontrole zgodności, które przeszły:
* cztery przykłady LFSR z notatki (`p=(1,1,0)` itd.) — zmierzone okresy 7, 15, 5, 63;
  dla pierwszego dodatkowo porównano **cały przebieg stanów i bitów** z rachunkiem ręcznym;
* `pow_mod(5, 100, 22) = 1` — zgodne z przykładem z notatki (slajd 13);
* `pow_mod` vs wbudowane `pow`: 5000 losowych trójek + liczby rzędu `2^61`;
* `trial_division_is_prime` vs sito Eratostenesa dla **wszystkich** `n ∈ [0, 20000]`;
* `π(10^6) = 78498` — znana wartość, zgodna z własnym sitem;
* Miller–Rabin z `s = 20` zgodny z dokładnym dzieleniem dla wszystkich `n ∈ [2, 3000]`;
* liczba kłamców Fermata dla 561 równa `φ(561) − 2 = 318`;
* pliki z liczbami odtworzone z `params.py` są **identyczne** z zapisanymi na dysku
  (test odtwarzalności w `test_lfsr.py` i `test_lcg.py`);
* **kontrolny przebieg w czystym katalogu** (kopia samego kodu, bez `results/`) dał
  **identyczne sumy SHA-256 wszystkich sześciu plików z liczbami** oraz identyczne
  wyniki deterministyczne (okresy, ogony, kolizje, liczba pseudopierwszych dla każdego
  `s`); pliki `lfsr_analysis.md` i `lcg_analysis.md` wyszły bajt w bajt takie same.
  Różni się jedynie `error_handling.md`, bo zawiera ścieżki katalogu tymczasowego,
  który system nazywa losowo. W czystym katalogu testy raportują 115 wykonanych
  i 2 pominięte (testy odtwarzalności nie mają jeszcze plików do porównania, bo
  wykonują się przed eksperymentami) — w przebiegu wzorcowym pliki już istniały,
  więc wykonało się wszystkie 117.

---

## 8. Problemy, błędy i jak zostały rozwiązane

Pełny dziennik: [`GENAI_LOG.md`](GENAI_LOG.md). Najważniejsze:

1. **Mediana jako pułapka.** Pierwsze wyniki pokazywały medianę Fermata 556 ns dla LFSR
   i 1738 ns dla LCG przy niemal równych średnich. Przyczyna: rozkład dwumodalny
   i mediana wypadająca na granicy skupień (108 vs 100 liczb parzystych). Rozwiązanie:
   dodana tabela statystyk rozbitych na grupy i jawne ostrzeżenie w raporcie.
2. **Brak rozgrzewki zaburzał badanie wpływu `s`.** Pierwszy mierzony scenariusz
   (`s = 1`) wychodził wolniejszy od późniejszych, co sugerowałoby nonsens („więcej
   iteracji = szybciej”). Dodany przebieg rozgrzewkowy przed każdym pomiarem,
   z osobnym generatorem podstaw, żeby nie zmieniać losowanych podstaw.
3. **Przedział `[1, 1000]` jest za mały, by pokazać słabość Fermata.** Scenariusz główny
   dał 0 pseudopierwszych, co mogłoby sugerować, że Fermat jest wiarygodny. Dodano
   wyczerpujące przeliczenie kłamców dla liczb Carmichaela i badanie `s = 1…40`.
4. **Mapowanie `mod_reject` nie działa, gdy `m < span`.** Wyszło przy próbie użycia
   przykładu z notatki (`m = 15`) do przedziału `[1, 1000]`. Zamiast cichego błędu
   dodany komunikat wyjaśniający i tryb `scale`; przypadek trafił do tabeli i do testów.
5. **Pozostałości po refaktoryzacji** (martwa funkcja pomocnicza w `exp_lcg.py`,
   warunek `if False`) — usunięte po przeglądzie własnego kodu.
6. **Niespójność dokumentacji** — pierwsza wersja `common.py` miała docstringi bez
   polskich znaków diakrytycznych; przepisana dla spójności z resztą projektu.

Rzeczy, które okazały się **łatwe**: sama implementacja LFSR, LCG i trzech testów
(definicje z notatki są jednoznaczne), budowa tabel, testy jednostkowe.
Rzeczy **problematyczne**: uczciwy pomiar czasu wywołań rzędu 0,3 µs, rozdzielenie
okresu stanu od okresu wartości, oraz dobór scenariuszy pokazujących rzeczywiste
różnice między testami, a nie przypadkowe zera w tabelach.

---

## 9. Czego nie udało się zrobić i co wymaga ludzi lub innych modeli

1. **Porównanie różnych modeli GenAI i wskazanie najlepszego dla każdego typu zadania.**
   Ten folder to **jeden przebieg jednego modelu**. Rankingu nie da się zrobić
   samodzielnie i nie jest udawany. Potrzebne: co najmniej dwa dalsze przebiegi
   (np. innego dostawcy i innego rozmiaru modelu) na **tym samym `params.py`**,
   na tej samej maszynie, z tym samym `run_all.py`; porównanie przez
   `results/benchmark.json` i sumy SHA-256 plików z liczbami.
2. **Łączna liczba błędów modeli i wybór najciekawszych promptów przekrojowo** —
   wymaga dzienników (`GENAI_LOG.md`) z pozostałych przebiegów.
3. **Roboczogodziny członków grupy.** Nie zostały mi podane i **nie wymyślam ich**.
   Tabela do uzupełnienia jest w sekcji 10. Jedyna liczba, którą mogę podać uczciwie:
   wall-clock sesji modelu od pierwszego utworzonego pliku do zapisania tego raportu
   to ok. **50 minut** (25.11.2026, ok. 22:00–22:50; pierwszy utworzony plik ma znacznik
   22:12, z czego pierwsze kilkanaście minut to lektura źródeł); **nie jest to
   roboczogodzina człowieka** i nie powinno być tak raportowane.
4. **Rzeczywisty status pierwszości dla liczb większych niż `~10^12`.** Dokładne
   dzielenie przestaje być wykonalne w rozsądnym czasie, a innej metody dokładnej
   (np. BPSW, deterministyczny M–R z ustalonym zbiorem podstaw) nie implementowano —
   wykracza poza zakres laboratorium. Dlatego badanie rozmiarów kończy się na `10^12`.
5. **Okresy generatorów bibliotecznych** (`m ≥ 2^24`) nie zostały zmierzone — pomiar
   przerwano po 200 000 krokach. Wiadomo tylko, że warunki Hull–Dobella są spełnione.
   Pełny pomiar wymagałby przejścia `2^31`–`2^48` kroków.
6. **Jakość statystyczna generatorów** została oceniona tylko prostymi miarami
   (kolizje, bilans bitów, okres wartości). Testy serii, pokrycia czy chi-kwadrat
   nie były wymagane i nie zostały zrobione.

---

## 10. Zakres pracy AI i człowieka

| element | wykonawca | uwagi |
|---|---|---|
| lektura PDF-ów i README, rozpoznanie stanu repozytorium | model | pliki udostępnione przez człowieka |
| projekt struktury plików i `params.py` | model | |
| implementacja `lfsr.py`, `lcg.py`, `primality.py`, `common.py` | model | konwencje spisane w docstringach |
| skrypty eksperymentów, tabele, `run_all.py`, `demo_errors.py` | model | |
| 117 testów jednostkowych | model | |
| uruchomienie i weryfikacja wyników | model | wszystkie liczby w raporcie z faktycznych uruchomień |
| wykrycie i poprawa błędów metodycznych (mediana, rozgrzewka, mapowanie) | model | lista w `GENAI_LOG.md` |
| decyzja o katalogu roboczym i o niemodyfikowaniu gałęzi git | **człowiek** | pytanie zadane przed implementacją, dwie odpowiedzi |
| udostępnienie treści zadania i prompt główny | **człowiek** | `PROMPT_GLOWNY_LAB05_GRUPA5.md` |
| przegląd merytoryczny, commit, PR, oddanie pracy | **człowiek** | do wykonania |
| roboczogodziny i sprawozdanie końcowe grupy | **człowiek** | tabela poniżej |

### Roboczogodziny — do uzupełnienia przez członków grupy

Zgodnie z README czas realizacji należy podać **w zaokrągleniu do pełnych godzin**.
Nie wypełniam tych pól, bo nie mam danych.

| osoba | zadanie | godziny (pełne) |
|---|---|---|
| … | przygotowanie promptu i materiałów | … |
| … | nadzór nad przebiegiem GenAI, decyzje organizacyjne | … |
| … | weryfikacja kodu i wyników | … |
| … | redakcja sprawozdania grupy 5 | … |
| **suma** | | **…** |

---

## 11. Samoocena tego przebiegu

**Co zostało zrobione:** cały zakres grup 1–3 (podstawowy i dodatkowy) z pomiarami,
tabelami, 117 testami i odtwarzalnym punktem wejścia; dokumentacja procesu GenAI;
format wyników przygotowany pod późniejsze porównanie modeli.

**Ile błędów wykryto w trakcie sesji:** 10 pozycji w `GENAI_LOG.md`, z czego
3 metodyczne (mediana w rozkładzie dwumodalnym, brak rozgrzewki pomiaru, za mały
przedział do oceny Fermata), 3 implementacyjne/porządkowe (martwy kod, mylący warunek,
niespójne docstringi), 2 dotyczące walidacji (`mod_reject` przy `m < span`, czytelność
parsowania odczepów w CLI), 1 w teście (błędna oczekiwana treść komunikatu),
1 w interpretacji źródeł (różnica między notatką a treścią zadania przy dzieleniu próbnym).
Żaden z nich nie przeszedł do wersji końcowej.

**Ryzyka, które pozostają:**
* czasy zależą od maszyny i stanu procesu — porównania między modelami mają sens tylko
  przy identycznym środowisku i jednym sposobie uruchomienia;
* wnioski o „najlepszym teście” są ważne wyłącznie dla zmierzonego zakresu (`n ≤ 10^12`,
  CPython, `s = 5`);
* dobór wielomianów LFSR i zestawów LCG opiera się na znanych wartościach z literatury,
  ale **każdy okres w tabelach jest zmierzony**, więc błąd w doborze ujawniłby się
  natychmiast jako okres niemaksymalny;
* testy jednostkowe sprawdzają implementację względem definicji z notatki i wartości
  znanych teoretycznie; nie zastępują recenzji człowieka.

**Czego brakuje do pełnego zakresu grupy 5:** co najmniej dwóch dalszych przebiegów
innych modeli na tym samym `params.py`, zestawienia ich błędów oraz decyzji grupy,
który model wybrać dla LFSR, LCG i testów pierwszości. Format do tego jest gotowy
(`results/benchmark.json`, sumy SHA-256, identyczne wejścia).
