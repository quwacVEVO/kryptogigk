# lab05 — Generatory pseudolosowe i testy pierwszości (grupa 5, realizacja z GenAI)

Przebieg wykonany modelem **Claude Opus 5** (`claude-opus-5`, Claude Code, effort = high)
w dniu **25.11.2026**. Folder zawiera kompletne rozwiązanie zakresu **grup 1–3**
(LFSR, LCG, testy pierwszości) wraz z wymaganiami dodatkowymi oraz materiał
do sprawozdania grupy 5.

* przebieg pracy z modelem i wykryte błędy: [`GENAI_LOG.md`](GENAI_LOG.md)
* materiał do sprawozdania: [`REPORT.md`](REPORT.md)
* lista kontrolna wymagań ze statusami: [`CHECKLIST.md`](CHECKLIST.md)
* wszystkie liczby, tabele i pliki wynikowe: [`results/`](results)

Konwencja katalogów jest taka jak w `zad2/` — jeden folder na model, żeby można było
dołożyć przebiegi innych modeli na **tych samych wejściach** (patrz „Porównanie modeli”).

---

## 1. Wymagania i uruchomienie

Potrzebny jest wyłącznie **Python 3.8+** i biblioteka standardowa (sprawdzone na CPython 3.14.7,
Linux x86_64). Żadnych zależności zewnętrznych, żadnych pakietów kryptograficznych.

```bash
cd zad5/opus_5_high

python3 run_all.py              # pełny, odtwarzalny przebieg: testy + 3 części + kontrola błędów
```

`run_all.py` jest **wzorcowym sposobem uruchomienia** — wszystkie pliki w `results/`
pochodzą z jednego jego wywołania. Poszczególne etapy można uruchomić osobno:

```bash
python3 -m unittest discover -v  # 117 testów poprawności
python3 exp_lfsr.py              # LFSR: liczby, kolizje, okresy, tabele wpływu parametrów
python3 exp_lcg.py               # LCG: to samo dla generatora kongruencyjnego
python3 exp_primality.py         # testy pierwszości na liczbach z obu generatorów (wymaga plików z dwóch poprzednich)
python3 demo_errors.py           # 28 wymuszonych błędów: parametry, brak pliku, zły format
```

Generatory mają też interfejs wiersza poleceń (zadanie: „zapisanie liczb do pliku tekstowego”):

```bash
python3 lfsr.py  --n 16 --taps 0,2,3,5 --seed 0xACE1 --count 200 --low 1 --high 1000 --out /tmp/lfsr.txt
python3 lfsr.py  --n 16 --taps 1011010000000000 --seed 1010110011100001 --count 10 --low 1 --high 100
python3 lcg.py   --m 65536 --a 25173 --c 13849 --x0 2026 --count 200 --low 1 --high 1000 --out /tmp/lcg.txt
python3 lcg.py   --m 65536 --a 25173 --c 13849 --x0 2026 --count 200 --low 1 --high 1000 --unique
python3 primality.py 561 1105 7919 104729 --rounds 5 --seed 12345
```

Uwaga o pierwszym uruchomieniu w **czystym** katalogu (bez `results/`): testy
poprawności wykonują się przed eksperymentami, więc dwa testy odtwarzalności
(porównanie zapisanych plików z liczbami z ponownym wygenerowaniem) zostaną
**pominięte** — zamiast 117 wykonanych testów będzie 115 wykonanych i 2 pominięte.
Przy każdym kolejnym przebiegu wykonują się wszystkie 117.

Uwaga o pomiarach: czasy w `results/` pochodzą z `run_all.py`, gdzie proces jest już
„rozgrzany” przez testy. Uruchomienie samego `exp_primality.py` w świeżym procesie daje
czasy systematycznie wyższe (dla najkrótszych wywołań nawet ok. 2×). To nie błąd, tylko
własność pomiaru bardzo krótkich wywołań — dlatego porównania między testami należy
czytać **w obrębie jednego przebiegu**.

---

## 2. Struktura plików

| plik | zawartość |
|---|---|
| `params.py` | **wszystkie** parametry eksperymentów w jednym miejscu (umowa przebiegu) |
| `common.py` | zapis/odczyt plików z liczbami, kolizje, wykrywanie cyklu, statystyki, pomiar czasu |
| `lfsr.py` | klasa `LFSR` + mapowanie bitów na `[a,b]` + CLI |
| `lcg.py` | klasa `LCG`, warunki Hull–Dobella, mapowania + CLI |
| `primality.py` | sito, dzielenie próbne, `pow_mod`, Fermat, Miller–Rabin + CLI |
| `exp_lfsr.py`, `exp_lcg.py`, `exp_primality.py` | eksperymenty i tabele (bez interpretacji) |
| `demo_errors.py` | wymuszenie i udokumentowanie wszystkich obsługiwanych błędów |
| `run_all.py` | jedno wejście: testy → LFSR → LCG → pierwszość → błędy → `summary.md` + `benchmark.json` |
| `test_common.py`, `test_lfsr.py`, `test_lcg.py`, `test_primality.py` | 117 testów poprawności |
| `results/*.md` | tabele i zmierzone fakty (generowane) |
| `results/*.txt` | ciągi K liczb z nagłówkiem opisującym parametry |
| `results/primality_calls_*.csv` | wynik i czas **każdego** wywołania każdego testu |
| `results/benchmark.json` | maszynowy skrót przebiegu + sumy SHA-256 plików z liczbami |

---

## 3. Ustalenia i parametry

Wszystko poniżej jest zapisane w `params.py` i powtarzalne.

### Scenariusz główny
* `K = 200` liczb, przedział `[a, b] = [1, 1000]` (1000 wartości, więc `K ≤ b − a + 1`).
* Format pliku: jedna liczba w wierszu, wiersze `#` to nagłówek z parametrami generatora.
  Odczyt pomija komentarze i puste wiersze.

### LFSR
* Definicja z notatki: `S = (S_0, …, S_{n−1})`, `S_{i+n} = Σ_{j=0}^{n−1} p_j·S_{i+j} mod 2`.
* **Stan**: lista `n` bitów; **bit wyjściowy** = `state[0]`; **przesuwanie w lewo**,
  nowy bit sprzężenia dopisywany z prawej.
* **Odczepy**: `p = (p_0, …, p_{n−1})`, `p_j` mnoży `state[j]` — indeks liczony od bitu
  wyjściowego. Wielomian charakterystyczny: `f(x) = x^n + Σ p_j x^j`.
* Parametry główne: `n = 16`, odczepy `j ∈ {0,2,3,5}` (`f(x) = x^16+x^5+x^3+x^2+1`),
  ziarno `0xACE1`. Okres nie jest zakładany — jest **mierzony** (`LFSR.period()`).
* **Mapowanie na `[a,b]`**: `span = b − a + 1`, `width = ⌈log2(span)⌉` bitów na liczbę,
  bity składane od najstarszego, słowa **rozłączne**. Tryb `reject` (domyślny) odrzuca
  słowa `≥ span` (rozkład równomierny, zmienna liczba zużytych bitów); tryb `mod`
  zostawiony do porównania (obciążenie modulo przy `span` niebędącym potęgą dwójki).
* Ziarno zerowe jest odrzucane wyjątkiem; można je dopuścić jawnie
  (`allow_zero_seed=True`) do zbadania przypadku brzegowego.

### LCG
* `x_{i+1} = (a·x_i + c) mod m`; `c` to przyrost (w notatce oznaczony `b`).
  **`c` ≠ prawa granica przedziału `[a,b]`** — w kodzie przedział to `low`/`high`.
* Parametry główne: `m = 65536`, `a = 25173`, `c = 13849`, `x0 = 2026` — dobrane tak,
  żeby cały okres dał się **zmierzyć** (65536 kroków), a warunki Hull–Dobella sprawdzić.
* **Mapowanie**: `mod_reject` (domyślne) odrzuca stany `x ≥ m − (m mod span)` i zwraca
  `low + x mod span`; `mod` — bez odrzucania; `scale` — `low + ⌊x·span/m⌋` (bity starsze).
* Dla przedziałów szerszych niż `m` tryb `mod_reject` zgłasza błąd; w scenariuszach
  dużych liczb użyto osobnego LCG o `m = 2^48` (parametry Java), co jest jawnie odnotowane.

### Definicje przyjęte w analizie
* **Kolizja** — pozycja ciągu, której wartość wystąpiła już wcześniej;
  `liczba kolizji = K − liczba różnych wartości` (wartość o krotności `k` wnosi `k−1`).
* **Okres stanu** — wykrywany słownikiem „stan → numer kroku”; wynik to para
  (długość ogona, długość cyklu). Ogon > 0 oznacza część przedcykliczną.
* **Okres ciągu wartości** (po mapowaniu) — liczony **osobno**, na bloku pokrywającym
  pełny okres stanu, z potwierdzeniem przez powtórzenie bloku i redukcją do najmniejszego
  dzielnika. To różna rzecz od okresu stanu (np. LFSR: 65535 vs 12801).

### Testy pierwszości
* Dokładny test: dzielenie przez **liczby pierwsze** do `⌊√n⌋` (sito Eratostenesa,
  własna implementacja, lista przygotowana **przed** pomiarem czasu).
* `pow_mod` — własne potęgowanie binarne od najstarszego bitu (wg `pot_mod2` z notatki).
  Wbudowane `pow` występuje **tylko** w testach jednostkowych, jako niezależna kontrola.
* Fermat: `s = 5` losowych podstaw z `{2, …, n−2}`; Miller–Rabin: `s = 5` iteracji.
* Ziarno losowania: `random.Random(12345)`, tworzone od nowa dla każdego testu
  i scenariusza → identyczne podstawy przy każdym uruchomieniu.
* **Podstawa odniesienia** („rzeczywisty status pierwszości”) to wyłącznie dokładny test
  dzielenia. Testy probabilistyczne nie są traktowane jako dowód pierwszości.
* Pomiar: `time.perf_counter_ns` (monotoniczny, rozdzielczość 1 ns), jedno wywołanie =
  jeden pomiar, czas odczytu pliku **nie** jest doliczany. Czasy mierzone dla każdej
  pozycji pliku (również powtórzeń), trafność liczona na zbiorze liczb unikalnych.

---

## 4. Porównanie modeli (zakres grupy 5)

Żeby porównać inny model GenAI na **tych samych wejściach, kryteriach i środowisku**:

1. skopiuj `params.py` bez zmian — to on definiuje wejścia i warunki;
2. uruchom `python3 run_all.py` w folderze danego modelu;
3. porównaj `results/benchmark.json`: parametry, liczby kolizji i okresy muszą być
   **identyczne** (są deterministyczne), a różnice czasów interpretuj tylko wtedy,
   gdy przebiegi wykonano na tej samej maszynie;
4. sumy SHA-256 plików z liczbami pokazują natychmiast, czy inny model wygenerował
   dokładnie ten sam ciąg (czyli czy przyjął tę samą konwencję mapowania).

Niniejszy folder to **jeden przebieg jednego modelu**. Ranking modeli, łączna liczba
błędów i wybór najlepszego modelu dla poszczególnych zadań wymagają zebrania kilku
niezależnych przebiegów — tutaj ich nie ma i nie są udawane (patrz `REPORT.md`, sekcja 9).
