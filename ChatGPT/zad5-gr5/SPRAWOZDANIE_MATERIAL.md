# Materiał do sprawozdania grupy 5

## 1. Cel i zakres

Celem było wykonanie z użyciem GenAI pełnego zakresu grup 1-3: implementacji i analizy LFSR, implementacji i analizy LCG oraz trzech testów pierwszości. Opracowano również wszystkie wymagania dodatkowe, które dało się wykonać w pojedynczym przebiegu: kontrolę błędów, warianty parametrów, testy poprawności, różne rozmiary liczb i wpływ liczby iteracji Millera-Rabina.

Nie wykonywano zadań koordynacyjnych grupy 4. Nie sporządzono rankingu różnych modeli, ponieważ dostępny był tylko jeden przebieg.

## 2. Metoda

Kod napisano w Pythonie przy użyciu wyłącznie biblioteki standardowej. Dla obu generatorów stan i wynik po mapowaniu analizowano osobno. Pełny stan zapisywano w słowniku do chwili pierwszego powtórzenia, uzyskując długość części przedcyklicznej i cyklu. Kolizje wartości opisano trzema miarami: nadmiarowymi wystąpieniami, liczbą powtarzających się wartości i liczbą par kolidujących.

Mapowanie do przedziału zrealizowano przez rejection sampling, dzięki czemu uniknięto obciążenia prostego modulo. Wykrycie powrotu stanu bez akceptowanego kandydata zgłasza błąd zamiast powodować pętlę nieskończoną.

Dokładnym punktem odniesienia był test dzielenia przez liczby pierwsze do `floor(sqrt(n))`. Testy Fermata i Millera-Rabina używały własnej implementacji szybkiego potęgowania binarnego. Losowanie było odtwarzalne dzięki stałym ziarnom.

## 3. Parametry główne

| Element | Parametry |
|---|---|
| Liczba wyników | `K=200` z każdego generatora |
| Przedział | `[10000,59999]`, rozmiar 50000 |
| LFSR | `n=16`, odczepy 0-based `(0,2,3,5)`, ziarno `0000000000000001` |
| LCG | `m=65536`, `a=5`, `c=1`, `x0=20226` |
| Fermat | 5 iteracji |
| Miller-Rabin | 5 iteracji |
| Ziarno losowania | `20261122` |
| Pomiar | `time.perf_counter_ns`, czas pojedynczego wywołania |

Warunek konieczny dla ciągu bez kolizji, `K <= b-a+1`, jest spełniony: `200 <= 50000`.

## 4. Wyniki generatorów

| Generator | Różne wartości z 200 | Nadmiarowe wystąpienia | Pary kolidujące | Przedcykl stanu | Okres stanu |
|---|---:|---:|---:|---:|---:|
| LFSR | 200 | 0 | 0 | 0 | 65535 |
| LCG | 200 | 0 | 0 | 0 | 65536 |

Oba główne przebiegi stanowią rzeczywiście wygenerowane przykłady ciągów bez kolizji. Dane znajdują się w `data/lfsr_numbers.txt` i `data/lcg_numbers.txt`.

Analiza wariantów pokazała, że maksymalny lub długi okres stanu nie gwarantuje braku powtarzających się krótkich wartości po złożeniu bitów i mapowaniu. Dla LFSR ziarno zerowe prowadziło do stałego stanu o okresie 1, a słabe odczepy skracały okres. Dla LCG zestaw spełniający warunki Hulla-Dobella miał pełny okres, natomiast zły mnożnik prowadził do przedcyklu długości 6 i cyklu długości 1; parzysty przyrost skrócił okres z 256 do 128.

## 5. Wyniki testów pierwszości

Wykonano 1200 pomiarów: 400 liczb wejściowych razy 3 metody. Dla każdego źródła i testu zapisano 200 indywidualnych wyników oraz czasów. Dokładne liczby zależą od ostatniego uruchomienia i znajdują się w `results/primality_summary.csv`.

W zweryfikowanym przebiegu średnie czasy były rzędu:

- około 2 mikrosekund dla Fermata;
- około 2-3 mikrosekund dla Millera-Rabina;
- około 6-7 mikrosekund dla dokładnego dzielenia przy liczbach pięciocyfrowych.

W głównym losowym zbiorze żadna metoda nie popełniła błędu względem dokładnego statusu. Nie oznacza to jednak równoważnej wiarygodności. Test jednostkowy pokazał, że złożona liczba Carmichaela 561 przechodzi test Fermata dla podstawy 2, podczas gdy Miller-Rabin ją odrzuca. We wszystkich badaniach liczba błędnych odrzuceń liczb pierwszych wyniosła 0, zgodnie z oczekiwaniem dla poprawnych implementacji.

Dla liczb siedmiocyfrowych dokładne dzielenie wyraźnie zwolniło do dziesiątek mikrosekund, podczas gdy metody probabilistyczne pozostały na poziomie kilku mikrosekund. Zwiększenie liczby iteracji Millera-Rabina z 1 do 10 podnosiło średni czas; mediana była mniej stabilna, ponieważ wiele liczb złożonych odrzucano bardzo wcześnie.

## 6. Wybór metody w badanym scenariuszu

- **Największa pewność:** dokładne dzielenie, ponieważ zwraca faktyczny status, ale skaluje się najgorzej.
- **Najmniejszy średni czas w głównym przebiegu:** Fermat, lecz jest najsłabszy merytorycznie i podatny na liczby Carmichaela.
- **Najlepszy kompromis szybkość/wiarygodność:** Miller-Rabin. Był wielokrotnie szybszy od dokładnego testu dla większych liczb, a jest znacznie odporniejszy niż Fermat. Wynik nadal należy nazywać „prawdopodobnie pierwsza”.

Dlatego jako najlepszy test ogólny dla zmierzonego scenariusza wskazano Millera-Rabina, jeśli dopuszczalny jest wynik probabilistyczny; gdy wymagany jest dowód w małym zakresie, należy użyć dokładnego dzielenia.

## 7. Problemy i rozwiązania

1. Błędny ręczny wektor kontrolny LCG został wykryty przez pierwszy przebieg testów i poprawiony po ponownym obliczeniu równania.
2. Potencjalna pętla nieskończona rejection samplingu dla zdegenerowanego generatora została usunięta przez wykrywanie powrotu pełnego stanu.
3. Bardzo krótkie czasy są podatne na szum. Zachowano surowe pomiary, użyto zegara monotonicznego o wysokiej rozdzielczości i nie wyciągano wniosków z pojedynczego minimum.

## 8. Weryfikacja

- 27 testów jednostkowych: wszystkie zaliczone;
- 500 losowych porównań własnego potęgowania z wbudowanym `pow`: wszystkie zgodne;
- ponowne przeliczenie cykli, statusów i statystyk z zapisanych plików: `OK`;
- liczby 0, 1, 2, 3, parzyste, pierwsze, złożone i 561: sprawdzone.

## 9. Użycie GenAI i udział człowieka

GenAI pomogło utworzyć kod, testy, eksperyment, dokumentację oraz pierwszą interpretację. Człowiek musi przejrzeć kod i wnioski, uruchomić projekt w środowisku oddawanym prowadzącemu, wpisać rzeczywisty podział pracy i roboczogodziny oraz zestawić ten przebieg z wynikami innych modeli.

### Tabela do uzupełnienia rzeczywistymi czasami

| Osoba | Zadanie | Rzeczywisty czas | Czas po zaokrągleniu do pełnych godzin |
|---|---|---:|---:|
| [uzupełnić] | [uzupełnić] | [uzupełnić] | [uzupełnić] |
| **Suma** |  | **[uzupełnić]** | **[uzupełnić]** |

Nie wpisano hipotetycznych roboczogodzin.

## 10. Wymagania dodatkowe i braki

Podjęto i zakończono próbę wszystkich dodatkowych wymagań grup 1-3. Nie wykonano porównania wielu modeli, rankingu modeli i wyboru najlepszego modelu dla poszczególnych zadań, ponieważ nie dostarczono innych przebiegów. Projekt przygotowano tak, aby można było uruchomić ten sam benchmark i zastosować tę samą checklistę do kolejnych modeli.

Terminy źródłowe: 26.11.2026, 13:30 oraz 30.11.2026, 18:00; własne sprawozdanie grupy 5 przypada na drugi termin.
