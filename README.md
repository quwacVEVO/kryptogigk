# Wytyczne, harmonogram i deadline'y - Laboratorium 3

### Grupa 2 - `zad3-gr2`

- **Podstawowe:** implementacja szyfrowania i deszyfrowania Vigenère'em i Hillem dla alfabetu 26-znakowego; odczyt tekstu i klucza z plików, zapis wyników do pliku oraz wybór trybu pracy.
- Przygotowanie nowych szyfrogramów z własnej implementacji do prób ataków Grup 3-5. Teksty jawne i klucze należy zachować do późniejszej weryfikacji wyników.
- **Dodatkowe:** kontrola błędów, wykrywanie nieodwracalnych macierzy Hilla, rozszerzony alfabet (cyfry, znaki specjalne, spacje) i testy poprawności obu implementacji.

---

### Grupa 3 - `zad3-gr3`

- **Podstawowe:** analiza literatury i metod kryptoanalizy Vigenère'a, opracowanie własnego algorytmu lub procedury ataku oraz przygotowanie narzędzi (np. metoda Kasiskiego lub indeks koincydencji do szacowania długości klucza, następnie analiza częstotliwości z testem chi-kwadrat dla kolumn; alternatywnie atak słownikowy, porównanie z próbami bruteforce).
- Próby określenia długości klucza i odzyskania klucza bez znajomości tekstu jawnego; po znalezieniu klucza - odszyfrowanie wiadomości.
- Ataki w dwóch etapach: najpierw na dostarczony szyfrogram `.txt`, następnie na nowe szyfrogramy wygenerowane przez implementację Grupy 2. Dokumentowanie wszystkich prób i wyników.
- **Dodatkowe:** odzyskiwanie klucza przy znajomości fragmentu tekstu jawnego (np. wyznaczanie przesunięć z odpowiadających sobie liter tekstu jawnego i szyfrogramu), porównanie skuteczności różnych metod oraz analiza wpływu długości klucza.

---

### Grupa 4 - `zad3-gr4`

- **Podstawowe:** analiza literatury i metod kryptoanalizy Hilla, opracowanie własnego algorytmu lub procedury ataku oraz przygotowanie narzędzi (np. dla macierzy `2x2`: brute force odwracalnych macierzy modulo 26 i ranking odszyfrowań według częstości liter lub n-gramów).
- Próby odzyskania macierzy klucza bez znajomości tekstu jawnego; po znalezieniu klucza - odszyfrowanie wiadomości. Analiza skuteczności zastosowanych metod.
- Ataki w dwóch etapach: najpierw na dostarczony szyfrogram `.txt`, następnie na nowe szyfrogramy wygenerowane przez implementację Grupy 2. Dokumentowanie wszystkich prób i wyników.
- **Dodatkowe:** odzyskiwanie klucza przy znajomości tekstu jawnego (np. wyznaczenie macierzy klucza z odpowiadających sobie bloków tekstu jawnego i szyfrogramu), analiza macierzy `2x2` i większych oraz porównanie różnych metod ataku.

---

### Grupa 5 - `zad3-gr5`

- **Podstawowe:** realizacja zakresu podstawowego Grup 2-4 z wykorzystaniem GenAI, w tym implementacja obu szyfrów i próby obu ataków na dostarczonych oraz nowych szyfrogramach z Grupy 2.
- Testowanie i porównanie różnych modeli na tych samych przypadkach; dokumentowanie promptów, oczekiwanego formatu odpowiedzi, sposobu weryfikacji wyników i przebiegu pracy.
- **Dodatkowe:** rozszerzenia z zakresu Grup 2-4, wskazanie najlepszego modelu dla danego zadania, analiza liczby błędów wymagających poprawek, wybór skutecznych promptów i rekomendacje dotyczące GenAI.

---

## Harmonogram

**Wersje wstępne - do 04.11.2026, godz. 23:59; omówienie na zajęciach 05.11.2026:**

- Grupa 2: działające oba szyfry z obsługą plików i alfabetu 26-znakowego.
- Grupy 3 i 4: przygotowane procedury ataku oraz pierwsze udokumentowane próby na dostarczonych szyfrogramach.
- Na zajęciach: przedstawienie postępów, sprawdzenie implementacji i przekazanie nowych szyfrogramów do dalszych ataków. Grupy 3-5 otrzymują wspólne przypadki testowe dla właściwego szyfru.

**Wersje końcowe i sprawozdania - do 10.11.2026, godz. 23:59:**

- Gotowy kod, instrukcja uruchomienia i wyniki, w tym próby ataków na nowe szyfrogramy z implementacji Grupy 2.
- Sprawozdania według wzoru, ewidencja czasu oraz opis podjętych wymagań dodatkowych i ich rezultatów.
- Zmiany na właściwych branchach.

**Oddanie projektu - zajęcia 12.11.2026:**

- Komplet rozwiązań, sprawozdań i materiałów do podsumowania projektu.

---

## Inne uwagi

- Grupy atakujące mogą rozpocząć pracę na dostarczonych `.txt` bez czekania na Grupę 2. Nowe szyfrogramy służą później sprawdzeniu ich metod na kolejnych tekstach i kluczach.
- Format przykładowych kluczy: Vigenère - słowo w jednej linii (małe lub wielkie litery); Hill `2x2` - cztery liczby oddzielone spacjami, odczytywane wierszami. Szczegóły zgodności implementacji należy uzgodnić przed wspólnymi testami.
- W podstawowych próbach klucze i teksty jawne pozostają nieznane atakującym do zakończenia próby. Testy ze znanym tekstem należy oznaczyć oddzielnie.
- Nie jest wymagane skuteczne złamanie każdego przypadku. Należy przedstawić rzeczywiście wykonane próby, wyniki, ograniczenia i przyczyny niepowodzeń; również wskazać, których rozszerzeń nie podjęto.
- Każdy członek grupy zapisuje czas pracy przy poszczególnych zadaniach; w sprawozdaniu należy zsumować roboczogodziny według zadań.
- Wnioski powinny opisywać trudności, błędy, poprawki i sposób weryfikacji. Materiał do porównania pracy samodzielnej z AI powinien obejmować jakość, czas, konieczne poprawki i poziom kontroli nad wynikiem.

<sub>W przypadku pytań lub problemów prosimy o kontakt z grupą koordynującą.</sub>
