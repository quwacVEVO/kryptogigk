# Dokumentacja pracy z GenAI

## Identyfikacja przebiegu

- Data przebiegu: 22.11.2026.
- Narzędzie: Codex w ChatGPT Work.
- Rodzina modelu: GPT-5-based zgodnie z informacją środowiska.
- Dokładna wdrożona wersja/wariant: nieujawniona w interfejsie; nie została dopisana na podstawie domysłu.
- Źródła: README projektu, szczegółowy PDF z zadaniami i notatka teoretyczna zostały odczytane w całości przed implementacją.

## Prompt i sposób współpracy

Punktem wejścia był plik `PROMPT_GLOWNY_LAB05_GRUPA5.md`, polecający: przeczytanie źródeł, wykonanie pełnego zakresu grup 1-3, jawne parametry eksperymentów, obowiązkową checklistę, uruchomienie testów, dokumentację GenAI i niewymyślanie roboczogodzin ani rezultatów innych modeli.

Przyjęty format pracy:

1. audyt trzech dokumentów źródłowych i katalogu projektu;
2. jawne ustalenie reprezentacji i mapowania;
3. małe moduły standardowej biblioteki Pythona;
4. testy jednostkowe przed benchmarkiem;
5. surowe wyniki CSV i osobne podsumowania;
6. niezależne ponowne przeliczenie zapisanych tabel;
7. końcowa checklista z dowodem dla każdego punktu.

## Zakres utworzony z pomocą modelu

- architektura katalogu i modułów;
- implementacje LFSR, LCG, detekcji cyklu i statystyk kolizji;
- implementacje testów pierwszości i własnego potęgowania binarnego;
- testy jednostkowe i przypadki regresji;
- skrypt eksperymentu, pliki CSV/JSON/Markdown i weryfikator;
- interpretacja wyników, checklista oraz materiał do sprawozdania.

Każdy z tych elementów wymaga przeglądu człowieka przed oddaniem. Model nie podpisuje sprawozdania ani nie zastępuje odpowiedzialności autorów.

## Błędy wykryte i poprawione podczas tego przebiegu

1. **Błędny ręczny wektor oczekiwanych stanów LCG w teście.** Pierwszy przebieg testów dał 1 błąd na 23. Równanie potwierdziło, że implementacja była poprawna, a błędne były liczby wpisane do testu. Wektor poprawiono; ponowny przebieg przeszedł.
2. **Ryzyko braku zakończenia rejection samplingu dla zdegenerowanego cyklu.** Przegląd po pierwszym benchmarku wykazał, że generator mogący produkować wyłącznie odrzucane kandydaty zapętliłby się. Dodano wykrywanie powrotu stanu i dwa testy regresji.

Końcowy stan: 27/27 testów przechodzi, eksperyment działa, a weryfikator CSV kończy się `OK`. Liczba zauważonych i naprawionych problemów w tej sesji: **2**.

## Co musi uzupełnić człowiek

- imiona/nazwiska autorów i podział odpowiedzialności;
- rzeczywisty czas pracy każdej osoby według zadań i suma, zaokrąglone zgodnie z README;
- subiektywna ocena czytelności i przydatności procesu;
- ewentualne uwagi prowadzącego oraz dostosowanie formatu sprawozdania;
- wyniki identycznego benchmarku z innych modeli GenAI.

## Czego nie można jeszcze rozstrzygnąć

Nie ma podstaw do rankingu modeli, wyboru najlepszego modelu dla LFSR/LCG/pierwszości ani łącznej liczby błędów między modelami, ponieważ wykonano jeden niezależny przebieg. Do porównania należy użyć tych samych plików źródłowych, parametrów, poleceń, środowiska oraz kryteriów z `CHECKLIST.md`.
