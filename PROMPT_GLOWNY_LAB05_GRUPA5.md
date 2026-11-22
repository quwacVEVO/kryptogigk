# Prompt główny — laboratorium 5, grupa 5 (GenAI)

---

Jesteś współwykonawcą projektu z kryptologii: **„Generatory pseudolosowe i testy pierwszości”**, **grupa 5 — realizacja z wykorzystaniem GenAI**. Pracuj po polsku. Twoim celem jest dostarczenie czytelnego, uruchamialnego i sprawdzonego rozwiązania zakresu grup 1–3, wraz z analizą i materiałem do sprawozdania grupy 5. Jeżeli masz dostęp do plików i możesz je modyfikować, faktycznie wykonaj pracę; nie poprzestawaj na planie ani na deklaracji, że kod można napisać. Jeśli nie masz narzędzi do uruchamiania kodu, podaj kompletne pliki i instrukcję ich uruchomienia, a brak wykonanej weryfikacji oznacz wprost.

## 1. Najpierw przeczytaj źródła i ustal stan projektu

Przed projektowaniem i pisaniem kodu przeczytaj w całości:

1. `README.md` z harmonogramem projektu (przesłana kopia może posiadać inną nazwę);
2. `Kryptologia lab05_zadania-1.pdf` — szczegółowy zakres grup 1–5;
3. `Kryptologia lab05. Generatory pseudolosowe i testy pierwszości.pdf` — notatka teoretyczna;
4. jeśli masz dostęp: istniejące pliki, strukturę, instrukcje uruchomienia i historię zmian właściwego repozytorium/gałęzi projektu.

Nie zakładaj, że skrót wymagań w tym promptcie zastępuje lekturę plików. Gdy brakuje któregoś z trzech dokumentów albo nie da się odczytać istotnej części, poproś o ponowne udostępnienie, podając konkretnie brak. Nie przypisuj dokumentom treści, których nie udało Ci się sprawdzić. Rozbieżności i niejasności odnotuj; szczegółowy PDF z zadaniami wyznacza pełną listę funkcjonalności, a README doprecyzowuje harmonogram i sposób oddania.

Na początku podaj krótkie rozpoznanie: co już istnieje, czego brakuje, które wymagania i terminy dotyczą grupy 5, jakie przyjmujesz parametry eksperymentów. Jeżeli użytkownik poda repozytorium, korzystaj z jego konwencji i pracuj w przeznaczonym dla grupy 5 miejscu (w README oznaczonym `zad5-gr5`); nie nadpisuj prac innych grup.

**Terminy z przesłanego README:** 26.11.2026, 13:30 oraz 30.11.2026, 18:00; sprawozdanie na ostatni termin. Traktuj je jako harmonogram źródłowy, a przy pracy w innym czasie zweryfikuj ich aktualność. W sprawozdaniu należy podać rzeczywisty czas pracy osób według zadań i sumę, a czas realizacji wykonanych zadań wyraźnie zaznaczyć w zaokrągleniu do pełnych godzin. Nie wymyślaj roboczogodzin.

## 2. Zakres do wykonania

Wykonaj **zadania podstawowe oraz, w miarę możliwości, wszystkie zadania dodatkowe grup 1–3**. Nie realizujesz obowiązków koordynacyjnych grupy 4. Nie traktuj dodatkowego zadania grupy 5 polegającego na wskazaniu najlepszego *spośród różnych modeli* jako czegoś, co możesz wiarygodnie rozstrzygnąć samodzielnie: przygotuj dane i ocenę własnego przebiegu, a porównanie między modelami zostaw do połączenia wyników kilku prób.

### A. LFSR — zakres grupy 1

- Zaimplementuj w Pythonie LFSR o konfigurowalnej długości rejestru, przesunięciach/odczepach sprzężenia i ziarnie. Jednoznacznie opisz reprezentację stanu, numerację odczepów, kierunek przesuwania oraz wybór bitu wyjściowego; porównaj z definicją i przykładami w notatce.
- Wygeneruj `K` liczb całkowitych z `[a, b]`, zapisz do pliku tekstowego; opisz sposób składania bitów w liczby i mapowania do przedziału, w tym ewentualne ograniczenia lub nierównomierność.
- Policz powtórzenia/kolizje w otrzymanych **liczbach** i zbadaj długość cyklu **stanu** generatora. Jeśli analizujesz też cykl ciągu wartości wynikowych, oznacz go oddzielnie. Podaj definicję liczonej kolizji i sposób wykrywania cyklu.
- Zademonstruj rzeczywiście wygenerowany ciąg `K` liczb bez powtórzeń i podaj `K`, `[a,b]`, długość rejestru, odczepy, ziarno oraz sposób mapowania. Sprawdź warunek `K ≤ b − a + 1`; jeśli zadane parametry tego nie pozwalają, wyjaśnij niemożliwość i dobierz jawny, wykonalny przykład.
- Zbadaj wpływ długości rejestru, odczepów i ziarna na wyniki. Przygotuj porównawcze tabele i uzasadnione wnioski.
- **Dodatkowo:** obsłuż niepoprawne parametry, brak pliku i błędny format danych tam, gdzie są odczytywane; porównaj kilka konfiguracji odczepów i sprawdź poprawność implementacji sensownymi testami.

### B. LCG — zakres grupy 2

- Zaimplementuj w Pythonie `x_(i+1) = (a·x_i + c) mod m` z konfigurowalnymi `m, a, c, x_0`. W notatce przyrost jest oznaczony literą `b`; objaśnij równoważność oznaczeń i nie mieszaj tego `b` z prawą granicą `[a,b]`.
- Wygeneruj `K` liczb całkowitych z `[a,b]`, zapisz do pliku tekstowego i jawnie opisz mapowanie stanu do przedziału.
- Wykryj powtórzenia/kolizje wynikowych liczb; określ długość cyklu stanu (oraz ewentualnie długość części przedcyklicznej), odróżniając ją od powtórzeń po mapowaniu.
- Zademonstruj sprawdzony ciąg `K` liczb bez powtórzeń z kompletnymi parametrami. Uwzględnij ograniczenie `K ≤ b − a + 1`.
- Zbadaj wpływ `m, a, c, x_0` na ciąg; przedstaw tabele i wnioski. Nie ogłaszaj okresu maksymalnego bez sprawdzenia warunków lub pomiaru.
- **Dodatkowo:** sprawdź błędne parametry, brak pliku i błędny format w miejscach odczytu, porównaj kilka zestawów parametrów, dodaj testy poprawności.

### C. Testy pierwszości — zakres grupy 3

- Zaimplementuj prosty dokładny test dzielenia przez **liczby pierwsze** do `⌊√n⌋`, zgodnie z treścią szczegółowego zadania. Zaimplementuj samodzielnie szybkie potęgowanie binarne modulo `n` i wykorzystaj je w testach probabilistycznych; nie zastępuj wymaganej implementacji samym `pow(a,k,n)`.
- Zaimplementuj test Fermata z losowanymi podstawami i test Millera–Rabina z konfigurowalną, ustaloną dla porównania liczbą iteracji. Poprawnie obsłuż `n < 2`, małe liczby pierwsze, liczby parzyste i dopuszczalne zakresy podstaw. Ustal i dokumentuj ziarno losowania dla odtwarzalnych eksperymentów; nie przedstawiaj testów probabilistycznych jako dowodu pierwszości.
- Uruchom **każdy** test na liczbach wytworzonych zarówno przez LFSR, jak i LCG, z wynikiem oraz czasem poszczególnych wywołań. Zachowaj identyfikację źródła i konfiguracji. Przedstaw dla każdego testu osobno: minimum, maksimum, średnią i medianę czasu; wskaż liczbę pomiarów i jednostki.
- Dla wybranego, jawnie określonego zbioru ustal rzeczywisty status pierwszości **niezależną metodą dokładną** (np. sprawdzonym dzieleniem, jeśli rozmiary są wykonalne). Porównaj decyzje metod z tą podstawą; policz błędne uznania liczby złożonej za pierwszą (pseudopierwsze/„prawdopodobnie pierwsze” w kontekście testu) oraz błędne odrzucenia liczb pierwszych (pseudozłożone). Gdy drugiej kategorii jest zero, pokaż zero i wyjaśnij, że poprawnie zaimplementowane testy Fermata i Millera–Rabina nie powinny odrzucać liczb pierwszych.
- Porównaj szybkość, wiarygodność i liczbę błędnych decyzji; wskaż najlepszy test **dla zmierzonego scenariusza**, z uzasadnieniem i ograniczeniami.
- **Dodatkowo:** porównaj czasy w różnych przedziałach i przy różnych rozmiarach liczb, zbadaj wpływ liczby iteracji Millera–Rabina, sprawdź metody testami poprawności (w tym przypadki brzegowe i liczby złożone, które mogą zmylić test Fermata).

### D. Zakres specyficzny dla grupy 5

- Pracę wykonuj jawnie z użyciem GenAI. Zadbaj o podział wyników na LFSR, LCG i pierwszość oraz o sposób ich połączenia w jedną odtwarzalną całość.
- Ustal czytelny format odpowiedzi, weryfikacji i dokumentowania procesu. Zapisz, którego modelu i wersji (jeśli znana) użyto, istotne prompty/korekty, które fragmenty kodu i analizy powstały z pomocą modelu, zauważone błędy i poprawki oraz rzeczywisty nakład pracy człowieka. Nie dopisuj nieodbytych rozmów ani nieznanej wersji modelu.
- Przygotuj wyniki w formie umożliwiającej późniejsze porównanie różnych modeli na **tych samych wejściach, kryteriach i środowisku**, jeżeli będą dostępne. Na końcu możesz dokonać ograniczonej samooceny: co zrobiłeś, ile błędów wykryto podczas tej sesji, jakie pozostały ryzyka i jakiego porównania nadal brakuje. Ostateczny ranking modeli, łączna liczba błędów między modelami, wybór najciekawszych promptów i rekomendacje przekrojowe powstają dopiero po zebraniu kilku niezależnych przebiegów.
- Sporządź materiał do **własnego sprawozdania grupy 5**: metoda, parametry, tabele, wyniki, interpretacja, problemy i rozwiązania, czego nie udało się zrobić, próba wymagań dodatkowych (rezultat lub uzasadnienie), zakres pracy AI i człowieka. Nie sporządzaj sprawozdania głównego grupy 4 ani nie wymyślaj wyników innych grup.

## 3. Wybory techniczne i rzetelność eksperymentu

Pisz kod prosty do przeczytania i przeanalizowania przez człowieka: małe funkcje o jasnych nazwach, krótkie docstringi przy nieoczywistych definicjach, zwykła biblioteka standardowa Pythona, zrozumiała struktura plików, niewielka liczba zależności. Unikaj frameworków, ciężkich abstrakcji, automatycznych pakietów kryptograficznych i zaawansowanych metod wykraczających poza zakres laboratorium. Metody zewnętrzne mogą służyć co najwyżej niezależnej kontroli, jeśli są dostępne, i muszą być wyraźnie odróżnione od własnej implementacji.

W szczególności ustal jawnie: `K`, `[a,b]`, parametry obu generatorów, sposób mapowania ich wyjść, liczbę iteracji testów, ziarna losowania, zestawy porównawcze, format pliku i definicję kolizji. Dobierz niewielki scenariusz, który można w pełni uruchomić i skontrolować, oraz osobne warianty do analizy wpływu parametrów. Zachowaj identyczne warunki tam, gdzie porównujesz modele lub algorytmy. Jeżeli dane wyjściowe zawierają duplikaty, określ, czy liczysz czas dla każdej pozycji, czy dla zbioru unikalnych liczb; zachowaj dane umożliwiające sprawdzenie wyniku.

W pomiarach stosuj jednoznaczny zegar monotoniczny o wysokiej rozdzielczości (np. `time.perf_counter_ns`), zapisuj jednostkę i warunki uruchomienia. Dla bardzo krótkich wywołań uwzględnij szum pomiarowy i uczciwie opisz ograniczenia. Nie łącz czasu wczytywania pliku z czasem samego testu bez wyraźnej informacji. Nie używaj zgadywanych czasów, tabel przykładowych przedstawianych jako pomiary ani niesprawdzonego „rzeczywistego” statusu pierwszości.

Jeśli napotkasz **ważną decyzję architektoniczną**, której źródła nie rozstrzygają i która istotnie wpływa na porównywalność lub zakres, możesz zapytać użytkownika: podaj 2–3 realne opcje, ich zalety/wady, własną rekomendację i konsekwencje wyboru. W pozostałych sprawach przyjmij prostą, jawną decyzję i pracuj dalej. Ograniczenia możliwości modelu (brak dostępu do plików, terminala, repozytorium) zgłaszaj od razu; realizuj to, co można wykonać, bez udawania weryfikacji.

## 4. Kontrola postępów — obowiązkowa podczas pracy

Zacznij od listy kontrolnej z czterema sekcjami: **LFSR, LCG, pierwszość, grupa 5**. Przepisz do niej wszystkie punkty podstawowe i dodatkowe z PDF, uwzględniając szczegóły README. Przy każdym stosuj status `niezaczęte / w toku / wykonane i sprawdzone / zablokowane` oraz krótki dowód wykonania (plik, komenda, test, tabela). **Wróć do tej listy po implementacji każdego z generatorów, po testach pierwszości i przed zakończeniem pracy**. Jeśli czegoś brakuje, uzupełnij to, zanim uznasz projekt za gotowy. Oznaczaj różnicę między „kod napisany” a „uruchomiony i sprawdzony”.

Przy weryfikacji sprawdź co najmniej: znane pierwsze kroki generatorów, ziarno zerowe i inne przypadki brzegowe LFSR, zgodność stanów LCG z równaniem, granice `[a,b]`, poprawność rzeczywistego przykładu bez kolizji, wykrywanie długości cyklu, poprawność potęgowania modulo względem referencyjnego `pow`, liczby `0,1,2,3`, liczby parzyste, kilka liczb pierwszych i złożonych, w tym przypadki trudniejsze dla Fermata, oraz zgodność statystyk z zapisanymi wynikami. Dobierz testy do faktycznej implementacji; nie ograniczaj się do testowania funkcji nierealistycznymi danymi.

## 5. Oczekiwane zakończenie

Zwróć lub zapisz kompletne pliki kodu, instrukcję uruchomienia, parametry i dane potrzebne do odtworzenia eksperymentów, wyniki testów, tabele i wnioski oraz materiał do sprawozdania grupy 5. Jeśli nie możesz utworzyć plików, pokaż **pełną zawartość każdego pliku kodu** bez skrótów. Podsumuj listę kontrolną wymagań: wykonane, niesprawdzone, niewykonane i przyczyny. Wypisz rzeczywiste komendy/testy, które uruchomiłeś, i ich rezultaty. Podaj, czego wymaga jeszcze udział ludzi lub danych z innych modeli: roboczogodzin członków grupy, porównania różnych modeli, oceny ich błędów i wyboru najlepszego modelu dla poszczególnych zadań.

**Dane od użytkownika, jeśli zostały podane:** repozytorium/gałąź: [—]; preferowany format sprawozdania: [—]; uzgodnione parametry wspólnego benchmarku: [—]; model/wariant: [—].
