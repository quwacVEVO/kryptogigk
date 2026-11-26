# Dziennik pracy z GenAI — lab05, grupa 5

Dokument wymagany zakresem grupy 5: **jak** powstało rozwiązanie, nie tylko co powstało.
Zapisane są tu wyłącznie rzeczy, które faktycznie miały miejsce w tej sesji.

---

## 1. Model i tryb pracy

| pozycja | wartość |
|---|---|
| model | Claude Opus 5 |
| identyfikator | `claude-opus-5` |
| narzędzie / tryb | Claude Code (agent w terminalu, z dostępem do plików i uruchamiania kodu) |
| poziom „effort” | high (ustawiony przez człowieka komendą `/effort` przed rozpoczęciem) |
| data sesji | 25.11.2026, ok. 22:00–22:50 czasu lokalnego |
| język pracy | polski (kod: nazwy angielskie, dokumentacja i komunikaty polskie) |
| czego **nie** wiem | zużycia tokenów ani zajętości okna kontekstu — te liczniki nie są dostępne modelowi w tym trybie, więc ich nie podaję |

Model miał dostęp do: plików w repozytorium, powłoki (uruchamianie Pythona), narzędzi
do zapisu plików. Nie korzystał z internetu ani z żadnych bibliotek zewnętrznych.

---

## 2. Prompty i korekty człowieka — pełna lista

Sesja była prowadzona **jednym promptem głównym** plus jedną interakcją decyzyjną.

**(1) Prompt główny** — plik `zad5/PROMPT_GLOWNY_LAB05_GRUPA5.md`, przekazany polecenim
„Wykonaj polecenia zgodnie z treścią pliku …”. Prompt zawierał: rolę, zakres grup 1–3,
wymagania na rzetelność eksperymentu, obowiązek listy kontrolnej i zakaz wymyślania
danych (roboczogodzin, czasów, statusu pierwszości).

Fragmenty promptu, które **najbardziej zmieniły kształt rozwiązania** (warte zebrania
jako „najciekawsze prompty” dla sprawozdania):

* *„Policz powtórzenia/kolizje w otrzymanych liczbach i zbadaj długość cyklu stanu
  generatora. Jeśli analizujesz też cykl ciągu wartości wynikowych, oznacz go oddzielnie.”*
  → wymuszenie rozdzielenia **okresu stanu** od **okresu ciągu wartości**. To właśnie
  ta para pomiarów ujawniła najważniejszy wynik części LCG (załamanie okresu wartości
  do 1024 przy mapowaniu modulo i `span = 2^10`).
* *„Nie ogłaszaj okresu maksymalnego bez sprawdzenia warunków lub pomiaru.”*
  → tabele mają kolumnę „okres zmierzony” i wpis „nieustalony (> 200 000)” zamiast
  przepisanych z literatury wartości `2^31`, `2^48`.
* *„Gdy drugiej kategorii jest zero, pokaż zero i wyjaśnij…”*
  → zero pseudozłożonych jest w raporcie wyjaśnione jako własność testów, a nie
  przedstawione jako sukces implementacji.
* *„Nie łącz czasu wczytywania pliku z czasem samego testu bez wyraźnej informacji.”*
  → pomiar obejmuje wyłącznie wywołanie funkcji testującej; sito liczb pierwszych
  jest budowane przed pomiarem (`prepare_primes`).
* *„Zaimplementuj samodzielnie szybkie potęgowanie binarne (…) nie zastępuj wymaganej
  implementacji samym `pow(a,k,n)`.”*
  → `pow_mod` wg pseudokodu z notatki; wbudowane `pow` użyte **tylko** w testach
  jednostkowych jako niezależna kontrola (5000 losowych przypadków).
* *„Jeśli napotkasz ważną decyzję architektoniczną (…) możesz zapytać użytkownika.”*
  → zadane jedno pytanie z dwiema kwestiami (poniżej), zamiast milczącego wyboru.

**(2) Pytanie modelu do człowieka i odpowiedzi** (zadane przed napisaniem kodu):

| pytanie | opcje | odpowiedź człowieka |
|---|---|---|
| katalog roboczy dla tego przebiegu | `zad5/opus_5_high/` (rekomendowana, zgodna z konwencją `zad2/`), `zad5/gr5/opus_5_high/`, `zad5/` bezpośrednio | **`zad5/opus_5_high/`** |
| czy ruszać gałęzie git (sesja startowała na `zad2-gr2`, README przewiduje `zad5-gr5`) | nic nie robić, utworzyć gałąź, gałąź + commit | **nic nie robić z gitem** |

Żadnych innych korekt ani poprawek w trakcie pracy człowiek nie wprowadzał — wszystkie
zmiany opisane w sekcji 4 model wykrył i naprawił sam, po przejrzeniu własnych wyników.

---

## 3. Przyjęty format odpowiedzi, weryfikacji i dokumentowania

To była świadoma decyzja metodyczna (wymaganie „opracowanie sposobu współpracy”):

1. **Źródła przed kodem.** Najpierw lektura obu PDF-ów i obu plików README, potem
   rozpoznanie (co istnieje, czego brak, jakie rozbieżności), dopiero potem implementacja.
2. **Lista kontrolna jako kontrakt.** `CHECKLIST.md` powstał przed kodem: każdy punkt
   z PDF-a osobno, ze statusem i miejscem na dowód wykonania. Rozróżnienie
   „kod napisany” vs „uruchomione i sprawdzone” jest w niej jawne.
3. **Parametry w jednym pliku.** `params.py` jest umową przebiegu — kod nie zawiera
   ukrytych stałych eksperymentu. To warunek porównywalności między modelami.
4. **Rozdzielenie pomiaru od interpretacji.** Skrypty `exp_*.py` wypisują wyłącznie
   zmierzone liczby i tabele do `results/`; wnioski są w `REPORT.md`, z odwołaniem do
   konkretnych plików. Dzięki temu da się sprawdzić każdą liczbę w raporcie.
5. **Każda liczba z uruchomienia.** W raporcie nie ma tabel „przykładowych”.
   Gdy czegoś nie zmierzono, jest napisane „nieustalony” albo „—”.
6. **Weryfikacja trójstronna:** (a) testy jednostkowe względem definicji z notatki,
   (b) kontrole niezależne (wbudowane `pow`, sito, wartości znane teoretycznie:
   `π(10^6) = 78498`, `φ(561) − 2 = 318`, `2^15/(2^16−1)`), (c) kontrole spójności
   wewnętrznej (okres słów `65535/NWD(10,65535) = 13107`, akceptacja `1000/1024`,
   `m − (m mod span) = 65000`).
7. **Odtwarzalność jako test.** `test_lfsr.py` i `test_lcg.py` odtwarzają pliki
   z liczbami z `params.py` i porównują z zapisanymi na dysku — każda przypadkowa
   zmiana parametrów od razu psuje testy.

---

## 4. Błędy i poprawki w trakcie sesji

Dziesięć pozycji; wszystkie wykryte i naprawione w tej samej sesji, żadna nie przeszła
do wersji końcowej. Kolumna „jak wykryto” jest istotna dla sprawozdania — pokazuje,
czego **nie** wyłapałyby same testy jednostkowe.

| # | rodzaj | opis | jak wykryto | poprawka |
|---|---|---|---|---|
| 1 | metodyczny | mediana czasu myląca przy rozkładzie dwumodalnym (276 ns dla LFSR vs 802 ns dla LCG przy niemal równych średnich) | przegląd wyników: różnica nieproporcjonalna do danych → sprawdzenie liczby liczb parzystych (108 vs 100) | tabela statystyk rozbitych na grupy + ostrzeżenie w raporcie |
| 2 | metodyczny | brak rozgrzewki: pierwszy mierzony scenariusz (`s = 1`) wychodził wolniejszy od `s = 3` | niemonotoniczność średnich w tabeli wpływu iteracji | przebieg rozgrzewkowy przed każdym pomiarem, z osobnym generatorem podstaw |
| 3 | metodyczny | scenariusz `[1, 1000]` daje 0 pseudopierwszych, co mogłoby sugerować, że Fermat jest wiarygodny | porównanie wyniku z wiedzą o liczbach Carmichaela | dodane: wyczerpujące przeliczenie kłamców dla 10 liczb Carmichaela, tabela brzegowa, badanie `s = 1…40` |
| 4 | walidacja | `mod_reject` przy `m < span` odrzucał wszystkie stany i wpadał w limit prób | próba użycia przykładu z notatki (`m = 15`) na przedziale `[1, 1000]` | jawny `ValueError` z wyjaśnieniem + tryb `scale` + test |
| 5 | czytelność | `_parse_taps` w CLI opierał się na pierwszeństwie operatorów (`or` z `and`) | przegląd własnego kodu | przepisane na dwa jawne warunki |
| 6 | porządek | martwa funkcja pomocnicza i warunek `if False` pozostawione po refaktoryzacji `exp_lcg.py` | przegląd własnego kodu | usunięte |
| 7 | spójność | pierwsza wersja `common.py` miała docstringi bez polskich znaków diakrytycznych | przegląd własnego kodu | plik przepisany |
| 8 | test | test oczekiwał komunikatu „możliwe”, implementacja zwracała „możliwy” | uruchomienie testów (1 niezaliczony z 36) | poprawiona asercja testu |
| 9 | środowisko | `platform.processor()` zwraca pusty łańcuch na Linuksie → „procesor: nieustalony” w opisie warunków pomiaru | przegląd pliku `environment.txt` | odczyt `model name` z `/proc/cpuinfo` z zachowaniem starej ścieżki jako zapasowej |
| 10 | interpretacja źródeł | notatka dzieli przez wszystkie liczby naturalne do `√n`, a treść zadania wymaga dzielenia przez **liczby pierwsze** | porównanie PDF-a z zadaniami i PDF-a z notatką | zaimplementowana wersja z zadania (własne sito), różnica opisana w `REPORT.md` §1 |

Dodatkowo odnotowane (bez zmian w kodzie, bo to cecha źródeł, nie błąd implementacji):
niespójna kolejność argumentów LCG między slajdami 3 i 4 notatki, literówka w zapisie
wektora odczepów (`p_{m−1}` zamiast `p_{n−1}`) oraz zachowanie pseudokodu `pierwszaMR`
przy `j = u` (przeanalizowane i uznane za poprawne — uzasadnienie w `REPORT.md` §1).

---

## 5. Co powstało z pomocą modelu

Praktycznie całość zawartości tego katalogu: cały kod (14 plików `.py`, 3451 wierszy,
z czego 802 wiersze testów), wszystkie skrypty eksperymentów, 117 testów jednostkowych,
tabele i pliki w `results/` oraz dokumenty `README.md`, `CHECKLIST.md`, `REPORT.md`
i ten dziennik.

Udział człowieka w tej sesji: dostarczenie zadań i promptu głównego, decyzja o katalogu
roboczym i o niemodyfikowaniu gałęzi git, oraz — do wykonania po sesji — przegląd
merytoryczny, roboczogodziny i oddanie pracy.

| mierzalny efekt | wartość |
|---|---|
| plików `.py` / wierszy kodu | 14 / 3451 (w tym 802 wiersze testów) |
| testów jednostkowych | 117, wynik OK, 0 pominiętych |
| wymuszonych przypadków błędnych | 28, nieodrzuconych 0 |
| pomiarów czasu w scenariuszu głównym | 1200 (2 źródła × 200 liczb × 3 testy) |
| pomiarów czasu łącznie (z badaniem rozmiarów i iteracji) | ok. 7 300 |
| plików wynikowych | 6 plików z liczbami, 5 raportów `.md`, 4 pliki CSV/JSON |
| czas pełnego przebiegu `run_all.py` | 10,6 s |
| wall-clock sesji modelu | ok. 50 minut (ok. 22:00–22:50; pierwszy utworzony plik 22:12); **nie jest to roboczogodzina człowieka** |

---

## 6. Materiał do porównania modeli (dla grupy 5)

Żeby porównanie było uczciwe, kolejny model musi dostać **to samo**:

1. ten sam `params.py` (bez żadnych zmian) — definiuje `K`, przedział, parametry obu
   generatorów, liczby iteracji i ziarno losowania;
2. to samo polecenie uruchomienia: `python3 run_all.py`;
3. ta sama maszyna — inaczej czasy są nieporównywalne (same wyniki deterministyczne
   pozostają porównywalne);
4. porównanie przez `results/benchmark.json`: sekcje `lfsr`, `lcg`, `pierwszosc`
   (okresy, kolizje, decyzje) **muszą** wyjść identycznie; różnice oznaczają inną
   konwencję mapowania albo błąd;
5. sumy SHA-256 plików z liczbami (`sumy_kontrolne_sha256`) — natychmiast pokazują,
   czy wygenerowano dokładnie ten sam ciąg.

Czego **nie** da się porównać automatycznie i trzeba ocenić ludzkim przeglądem:
czytelność kodu, jakość wniosków, trafność wychwyconych problemów metodycznych,
liczba błędów wymagających poprawki po stronie człowieka oraz to, ile korekt
trzeba było zgłosić modelowi w trakcie pracy (w tej sesji: zero korekt merytorycznych
od człowieka, dwie decyzje organizacyjne).
