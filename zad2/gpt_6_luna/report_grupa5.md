# Sprawozdanie Grupy 5 — łamanie szyfru monoalfabetycznego

**Model oznaczony w tej pracy:** GPT-6 Luna Extra High, zgodnie z poleceniem.  
**Język głównej próby ALFA26:** polski.  
**Kod:** Python 3, KryptoLib z projektu i biblioteka standardowa; `matplotlib`
wykorzystano tylko do wykresu.

## Zakres i przygotowanie danych

Przygotowano osiem szyfrogramów i osiem odpowiadających im plików klucza:

| Plik szyfrogramu | Język | Tryb | Długość |
|---|---|---:|---:|
| `cipher1_alfa26_2k.txt` | polski | ALFA26 | 2 000 |
| `cipher2_alfa26_30k.txt` | polski | ALFA26 | 30 000 |
| `cipher3_alfa26_2k.txt` | angielski | ALFA26 | 2 000 |
| `cipher4_alfa26_30k.txt` | angielski | ALFA26 | 30 000 |
| `cipher5_alfa37_2k.txt` | polski | ALFA37 | 2 000 |
| `cipher6_alfa37_30k.txt` | polski | ALFA37 | 30 000 |
| `cipher7_alfa37_2k.txt` | angielski | ALFA37 | 2 000 |
| `cipher8_alfa37_30k.txt` | angielski | ALFA37 | 30 000 |

Każdy klucz zapisano jako `<nazwa_szyfrogramu>_key.txt` w `data/evaluation/keys/`.
Teksty jawne znajdują się osobno w `data/evaluation/plaintexts/`. Teksty
przetworzono funkcjami KryptoLib: ALFA26 usuwa spacje, cyfry, interpunkcję
i diakrytyki, a ALFA37 zachowuje pojedyncze spacje i cyfry. Szyfrogramy ALFA26
są wielkimi literami.

Nie otrzymaliśmy szyfrogramów przygotowanych przez inną grupę. Dlatego
przygotowano kontrolowany zestaw dla tej pracy, z osobnym losowym kluczem dla
każdej próbki. Dla par 2k/30k tekst dłuższy zaczyna się od tych samych 2 000
znaków co krótki, ale klucze są różne. Test i trening ataku są syntetyczne,
utworzone tym samym generatorem zdań z niezależnymi ziarnami. To ułatwia
powtarzalną ocenę algorytmu, ale może zawyżać skuteczność względem naturalnego,
niezależnego korpusu. Nie należy traktować tych wyników jako miary skuteczności
na dowolnym polskim tekście.

Atak nie odczytywał katalogu ewaluacyjnego. Klucze i teksty jawne sprawdzono
dopiero po zapisaniu kandydatów, za pomocą osobnego `evaluate_after_cracking.py`.

## Analiza częstości i metoda łamania

`frequency.py` zlicza wystąpienia każdego symbolu alfabetu, sortuje je malejąco
i podaje udział procentowy. `analyze_all.py` uruchamia analizę dla wszystkich
ośmiu szyfrogramów i zapisuje pełne tabele do
`results/frequency_analysis.json`. W ALFA37 uwzględniany jest również symbol
spacji oraz wszystkie cyfry.

Pierwszą realizację ALFA26 wykonano po polsku: raport jest polskojęzyczny, a
polski daje charakterystyczne ciągi liter (np. `SZ`, `CZ`, `RZ`) po usunięciu
diakrytyków. Zgodnie z poleceniem zadanie 4 zaczynało od wyboru jednego języka.
Po dodatkowej prośbie wykonano również ślepy atak dwujęzyczny na wszystkich
polskich i angielskich próbkach; wyniki opisano niżej.

Automatyczny atak dla wybranego języka wykonuje następujące kroki:

1. Tworzy niezależny model częstości dwuznaków, trójek i czwórek liter.
2. Inicjalizuje podstawienie przez dopasowanie rang częstości szyfrogramu
   i modelu językowego.
3. Losowo zamienia pary przypisań symboli, ocenia kandydatów n-gramami
   i wykonuje kilka niezależnych startów.
4. Dopracowuje najlepszy wynik zamianami poprawiającymi punktację.
5. Zapisuje pełny tekst kandydujący oraz częściowy zapis. W ALFA26 małe litery
   oznaczają uzgodnione lub lokalnie stabilne odczyty, a wielkie znaki
   pozostawione z szyfrogramu oznaczają niepewne miejsca.

Zgoda startów i lokalna różnica punktacji są heurystykami, a nie
prawdopodobieństwem poprawności.

### Dodatkowe podejście do ALFA37

Pierwszy atak ALFA37 potraktował wszystkie 37 symboli tak samo. Kolejne
warianty rozdzieliły problem na hipotezy o spacji i model liczb:

1. Przetestowano siedem najczęstszych symboli szyfrogramu oraz widoczną spację
   jako możliwe szyfrogramowe odpowiedniki jawnej spacji. Każdą hipotezę
   oceniono osobnym zestawem startów.
2. Do niezależnego modelu językowego dodano 60 różnych przykładów liczbowych
   w kontekstach numeru, roku i czasu. Wartości różnią się od sekwencji testowej.
3. Najlepszy wynik posłużył jako start kolejnego przeszukiwania z sześcioma
   restartami i ustaloną hipotezą spacji.

Najwyżej oceniona hipoteza przypisała symbol `W` do jawnej spacji. Pierwszy
wariant hipotez dał 44,42%, model liczbowy podniósł wynik do 85,03%, a ciepłe
wznowienie wyszukiwania do 99,283% poprawnych znaków.

## Wyniki ślepego ataku

| Tryb | Długość | Poprawność znaków | Poprawność mapowania widocznych symboli | Pełne odtworzenie | Czas ataku |
|---|---:|---:|---:|---|---:|
| ALFA26, polski | 2k | 100,000% | 100,000% (23/23) | tak | 8,10 s |
| ALFA26, polski | 30k | 99,357% | 91,304% (21/23) | nie | 27,32 s |
| ALFA37, polski | 2k | 77,200% | 51,724% (15/29) | nie | 9,62 s |
| ALFA37, polski | 30k, pierwszy atak | 0,153% | 3,030% (1/33) | nie | 11,38 s |
| ALFA37, polski | 30k, poprawiona metoda | 99,283% | 72,727% (24/33) | nie | 27,33 s |

W krótkiej próbce ALFA26 odzyskano tekst dokładnie. Długa próbka również
została odtworzona niemal w całości, ale dwa z 23 użytych symboli otrzymały
błędne przypisanie, więc tekst nie był identyczny. W tym kontrolowanym teście
większa długość nie zagwarantowała idealnego wyniku: końcowy rezultat zależał
również od losowych startów optymalizacji.

Pierwszy atak ALFA37/30k rzeczywiście utkwił w słabym maksimum lokalnym. Nie
był to błąd KryptoLib ani kierunku podstawienia: po poprawionym ataku
porównanie wykazało 100% poprawności liter i spacji. Błąd skupiał się w rzadkich
symbolach cyfr. Dla długiego tekstu odzyskano wszystkie 25 448 liter i 4 337
spacji, ale żadną z 215 cyfr. Zapisany w `results/symbol_class_metrics.json`
podział wyjaśnia wynik 99,283%: pomyłki dotyczą tylko 0,717% tekstu.

Pierwsza konfiguracja używała 900 prób na restart, czterech restartów i jednej
rundy dopracowania dla alfabetu o 37! możliwych permutacjach. Dawało to 3 600
losowych zamian. Model liczbowy zawierał zbyt mało przykładów względem testowych
sekwencji cyfr, a ranking częstości nie rozpoznawał ich mapowania. Przeszukanie
hipotez spacji, większy model liczbowy i wznowienie z najlepszego klucza
kandydującego usunęły większość błędów.

### Próba z publiczną literaturą

Na sugestię użycia tekstów literackich pobrano z Wolnych Lektur _Chłopów,
część pierwszą: Jesień_ Władysława Stanisława Reymonta oraz _Lalkę_ Bolesława
Prusa. Źródła zawierają łącznie około 2,05 mln znaków przed przetworzeniem.
Atak użył równych, 45-tysięcznych próbek znaków literackich i syntetycznych;
we wszystkich wariantach zastosowano tę samą niezależną próbkę kontekstów
liczbowych. Kandydat startowy pochodził z poprzedniego ślepego ataku, a spację
`W` utrzymano jako ustaloną hipotezę. Ewaluacja tekstem jawnym nastąpiła dopiero
po zapisaniu kandydatów.

| Model kalibracyjny | Poprawność znaków | Litery | Cyfry | Spacje | Czas optymalizacji |
|---|---:|---:|---:|---:|---:|
| Syntetyczny, poprzedni najlepszy wynik | 99,283% | 100% | 0% (0/215) | 100% | 27,33 s |
| Tylko literatura | 76,807% | 73,456% | 5,581% (12/215) | 100% | 8,51 s |
| 50% syntetyczny + 50% literatura | 83,877% | 81,830% | 0,930% (2/215) | 100% | 7,82 s |
| 90% syntetyczny + 10% literatura | 81,507% | 78,985% | 6,977% (15/215) | 100% | 8,61 s |

W tych danych teksty literackie nie poprawiły wyniku całościowego: najlepszy
pozostał model syntetyczny. Domieszka literatury rozpoznała maksymalnie 15 cyfr
z 215, lecz przy wariancie 10% pomyliła przy tym 5 348 liter, więc wynik
całkowity wyraźnie spadł. To pasuje do różnicy stylu: tekst testowy powstał z
proceduralnych zdań podobnych do syntetycznego modelu kalibracyjnego, a nie z
prozy Reymonta lub Prusa. Dla szyfrogramu naturalnej prozy korpus literacki
może być lepszym punktem wyjścia, ale wymaga osobnego sprawdzenia na takim
tekście. Źródła, atrybucja, warunki licencji i kroki pobierania opisano w
`data/training_literature/SOURCES.md`.

### Wspólny atak dla polskiego i angielskiego

`crack_multilingual.py` uruchamia dwa ślepe warianty dla każdego szyfrogramu:
osobny model n-gramów po polsku i po angielsku. Normalizuje wyniki przez liczbę
obserwacji w modelu, wybiera wyższy wynik i dopiero wtedy uruchamia
`refine_multilingual.py` z większym budżetem przeszukiwania. Atak nie odczytuje
języka z manifestu ani tekstów jawnych.

| Szyfrogram | Język wybrany | Wybór poprawny | Poprawność po dopracowaniu |
|---|---|---:|---:|
| `cipher1_alfa26_2k` | polski | tak | 99,850% |
| `cipher2_alfa26_30k` | polski | tak | 100,000% |
| `cipher3_alfa26_2k` | angielski | tak | 100,000% |
| `cipher4_alfa26_30k` | angielski | tak | 100,000% |
| `cipher5_alfa37_2k` | polski | tak | 98,500% |
| `cipher6_alfa37_30k` | polski | tak | 99,023% |
| `cipher7_alfa37_2k` | angielski | tak | 98,500% |
| `cipher8_alfa37_30k` | angielski | tak | 98,603% |

Język wybrano poprawnie w 8/8 przypadków. W ALFA37 wszystkie spacje są
poprawne, a prawie wszystkie litery odzyskane; cyfry nadal stanowią trudną
część. W 30-tysięcznej próbce polskiej odtworzono 15/215 cyfr, a w pozostałych
trzech próbkach ALFA37 żadnej. Dla `cipher6_alfa37_30k` wcześniejszy atak
wyspecjalizowany dla polskiego pozostaje nieco lepszy (99,283% wobec 99,023%),
więc jego najlepszy wynik zachowano w głównej tabeli. Wykres podsumowujący
dwujęzyczny przebieg znajduje się w `results/multilingual/accuracy.png`.

![Skuteczność ataku dwujęzycznego dla ośmiu polskich i angielskich próbek](results/multilingual/accuracy.png)

![Porównanie dokładności polskich próbek](results/accuracy_comparison.png)

### Przykład wymaganego zapisu

Plik `results/partial_cipher2_alfa26_30k.txt` zawiera tekst mieszany:
małe litery to propozycje stabilne między startami, a wielkie znaki to
nierozstrzygnięte symbole pozostawione z szyfrogramu. To spełnia zapis
częściowego odszyfrowania w trybie ALFA26.

W ALFA37 literalna spacja i cyfry także są symbolami szyfrogramu, nie
separatorami. Dlatego `results/partial_cipher5_alfa37_2k.txt` zapisuje każdy
symbol jako token: mała litera oznacza rozpoznaną literę jawną, `[7]` oznacza
rozpoznaną cyfrę 7, `<SP>` rozpoznaną spację, a `{X}`, `{7}` lub `{SP}` to
nierozstrzygnięty znak szyfrogramu. Przykład notacji (schematyczny):
`{4} a [3] <SP> {SP}`. Nawiasy odróżniają cyfrę jawną od cyfry, która nadal
jest symbolem szyfrogramu.

## Wnioski i ograniczenia

- Częstości szybko wskazują kandydatów na najczęstsze litery, ale sam ranking
  nie odzyskuje pełnego klucza. N-gramy i powtarzające się słowa poprawiają
  wynik ALFA26.
- Długość 30k dostarczyła więcej obserwacji. W pierwotnym ataku ALFA26/PL
  uzyskano 99,357%; po wyborze języka z dwóch modeli i zwiększeniu budżetu
  próbka ta została odzyskana w całości.
- ALFA37 ma 37! możliwych permutacji, około 10^16,53 razy więcej niż 26!.
  Spacja może zostać zaszyfrowana jako litera lub cyfra, a cyfra jawna jako
  dowolny symbol. Nieliczne cyfry utrudniają wyznaczanie mapowania, lecz
  hipotezy o spacji i liczbowy model n-gramowy pozwoliły odzyskać tekst
  prawie w całości.
- Wyniki 2k/30k pochodzą z generatora syntetycznego i wspólnego rozkładu
  trening/test. Dokładność 100% dla ALFA26/2k nie powinna być uogólniana na
  tekst naturalny. Próba z zewnętrzną literaturą potwierdziła, że korpus
  kalibracyjny trzeba dopasować do źródła tekstu; właściwym kolejnym sprawdzianem
  są szyfrogramy naturalnych tekstów spoza generatora.
- W tej sesji dostępny był tylko wynik jednego modelu. Nie da się rzetelnie
  stwierdzić, który model Grupy 5 był lepszy bez wyników pozostałych modeli.

## Czas i zużycie zasobów

Końcowe czasy obliczeń pochodzą z `time.perf_counter()`. Pierwsze cztery
ataki trwały łącznie **56,41 s**. Trzy dodatkowe próby ALFA37/30k zajęły
**143,77 s**: hipotezy spacji (57,07 s), rozszerzony model liczb (59,36 s)
i ciepły restart (27,33 s). Dwie serie prób literackich trwały łącznie **57,81 s**
(32,28 s i 25,53 s); pobranie oraz przygotowanie tekstów zajęło **29,50 s**.
Dwa ataki językowe uruchomione dla ośmiu próbek zajęły łącznie **102,87 s**,
a dopracowanie wybranych kandydatów **249,37 s**. Łącznie zmierzone przebiegi
ataku trwały **610,23 s**. Generowanie próbek, analiza częstości, ewaluacja
i wykresy trwały osobno poniżej 10 s każda. Suma nie obejmuje czasu
przygotowania kodu.

Platforma nie udostępniła dokładnego licznika tokenów ani procentowego zużycia
okna kontekstu; tych wartości nie szacowano ani nie wymyślano. Czas pracy
człowieka w roboczogodzinach nie dotyczy tej sesji modelowej i nie był
mierzony.

## Polecenia i skrócone odpowiedzi

Pierwsze pięć pozycji to jawne, skrócone rozbicie polecenia zbiorczego z
zadania, a nie cytaty z pięciu osobnych rozmów. Dwa ostatnie wiersze opisują
dodatkowe prośby użytkownika po ukończeniu pierwszego ataku.

| Prompt etapowy (skrót) | Odpowiedź / wynik modelu | Dlaczego istotny |
|---|---|---|
| Przygotuj polskie i angielskie próbki ALFA26/37 długości 2k/30k oraz oddziel klucze. | Utworzono 8 szyfrogramów i 8 plików kluczy, teksty jawne trzymane osobno. | Stworzył kontrolowany zbiór do wszystkich prób. |
| Zaimplementuj analizę częstości dla obu alfabetów. | Zliczenia i udziały procentowe wszystkich symboli zapisano dla 8 próbek. | Pokazało różnice między ALFA26 i ALFA37. |
| Wybierz język ALFA26 i wyjaśnij metodę automatycznego ataku. | Wybrano polski; połączono ranking częstości, model n-gramowy, zamiany klucza i ponowne starty. | Dało uzasadnioną, powtarzalną procedurę zamiast samego zgadywania liter. |
| Porównaj skuteczność ataku na 2k i 30k. | 2k: 100%; 30k: 99,357%; dwa błędne przypisania w dłuższym wyniku. | Pokazało, że długość pomaga, ale optymalizacja nadal może zakończyć się błędem. |
| Spróbuj ALFA37, wyjaśnij porażkę i zaproponuj inne metody. | Pierwszy atak 30k: 0,153%; przeszukanie spacji i model liczb: 85,03%; ciepły restart: 99,283%. | Pokazało, że mały budżet przeszukiwania i niedostateczny model cyfr powodowały lokalne maksimum. |
| Użyj przykładów publicznej literatury jako modelu języka. | „Chłopi” i „Lalka”: model literacki 76,807%; mieszanki 50/50 i 90/10: 83,877% i 81,507%. | W tym syntetycznym teście model z prozy literackiej nie pasuje do stylu generatora; wynik 99,283% pozostał przy treningu syntetycznym. |
| Rozszerz atak na polskie i angielskie teksty. | Dwa modele n-gramowe i wybór po wyniku wykryły język poprawnie 8/8; po dopracowaniu wynik wyniósł 98,5–100%. | Pozwala jednym przebiegiem obsłużyć oba języki, zamiast zakładać polski z góry. |

Zapis ALFA37 oznacza znaną cyfrę jawną jako `[d]`, spację jako `<SP>`, a nierozstrzygnięty symbol szyfrogramu jako `{…}`. W najlepszym wyniku dla polskiego ALFA37/30k litery i spacje są rozpoznane, a cyfry pozostają w tokenach niepewnych.
