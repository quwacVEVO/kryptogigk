# Zasady realizacji projektu i praca z GitHubem

Realizacja zadań odbywa się w obrębie przydzielonych grup:
- Każda grupa działa głównie na oddzielnym pliku/module, aby **minimalizować konflikty**,
- Każda grupa na bieżąco informuje o postępach,
- Rozwiązania są na bieżąco sprawdzane przez testerów/koordynatorów,
- Zadania są wykonywane w zadanym terminie.

---

## Schemat gałęzi
```text
main (wersja główna/stabilna)
 └── zad1 (gałąź nadrzędna dla zadania 1)
      ├── zad1-gr1 (praca grupy 1 nad zadaniem 1)
      ├── zad1-gr2 (praca grupy 2 nad zadaniem 1)
      ├── zad1-gr3 (praca grupy 3 nad zadaniem 1)
      └── zad1-gr4 (praca grupy 4 nad zadaniem 1)
 └── zad2 (gałąź nadrzędna dla zadania 2)
      ├── zad2-gr1
      ├── zad2-gr2
      └── ...
 └── ....
```

1. **`main`** - oficjalna, ostateczna i stabilna wersja projektu. Bezpośrednio na niej nie commitujemy.
2. **`zadX`** (np. `zad1`, `zad2`, ...) - gałąź bazowa dla danego zadania `X`, tworzona na podstawie `main`.
3. **`zadX-gr1`, `zadX-gr2`, `zadX-gr3`, `zadX-gr4`** - gałęzie robocze dla poszczególnych podgrup tworzone **bezpośrednio z gałęzi `zadX`**.

---

## PRE-1: Instalacja gita
Projekt oparty jest na systemie kontroli wersji **git**. Jeśli jeszcze go nie masz:
1. Wejdź na oficjalną [stronę pobierania git](https://git-scm.com/install/).
2. Pobierz instalator dla swojego systemu (dla większości: Windows).
3. Uruchom pobrany instalator `.exe`.
4. Przejdź dalej (`Next`) przez wszystkie kroki - domyślne ustawienia są w zupełności wystarczające.

---

## PRE-2: Klonowanie repozytorium
Przed rozpoczęciem pracy sklonuj kopię repozytorium na własny dysk:
1. W dowolnym miejscu na komputerze stwórz folder na projekt.
2. Wejdź do tego folderu, kliknij w pasek adresu eksploratora Windows, wpisz **`cmd`** i wciśnij **Enter**.
3. W otwartym oknie wiersza poleceń (`cmd`) wpisz:
   ```cmd
   git clone https://github.com/quwacVEVO/kryptogigk.git
   ```
4. Po pobraniu przejdź do utworzonego folderu projektu:
   ```cmd
   cd kryptogigk
   ```

---

## 1. Pobieranie najnowszej wersji projektu
Przed rozpoczęciem pracy zawsze upewnij się, że posiadasz aktualny stan repozytorium:
1. Otwórz wiersz poleceń (`cmd`) wewnątrz folderu `kryptogigk`.
2. Pobierz najnowsze zmiany:
   ```cmd
   git pull
   ```

---

## 2. Praca we własnej gałęzi grupy

Każda grupa pracuje **wyłącznie** na swojej gałęzi dedykowanej dla danego zadania.

### A. Pobranie i przejście do gałęzi zadania (`zadX`)
Zanim zaczniesz pracę w grupie, musisz działać na podstawie aktualnej gałęzi zadania:
```cmd
git fetch origin
git checkout zadX
git pull origin zadX
```
*(Zastąp `zadX` właściwym numerem zadania, np. `zad1`)*

### B. Praca na gałęzi grupy (`gr1`, `gr2`, `gr3`, `gr4`)
Jeśli gałąź grupy już istnieje na zdalnym repozytorium:
```cmd
git checkout zadX-grX
git pull origin zadX-grX
```
*(Zastąp `grX` numerem grupy, w której obecnie pracujesz, np. `gr1`)*

Jeśli zakładasz gałąź swojej grupy jako pierwszy (odgałęziasz od `zadX`):
1. Będąc na gałęzi `zadX`, utwórz nową gałąź i od razu się na nią przełącz:
   ```cmd
   git checkout -b zadX-grX
   ```

---

## 3. Zapisywanie i wysyłanie zmian na GitHubie

Gdy wprowadzisz zmiany w kodzie:
1. Otwórz wiersz poleceń (`cmd`) w folderze `kryptogigk`.
2. Sprawdź zmodyfikowane pliki:
   ```cmd
   git status
   ```
3. Dodaj pliki do poczekalni (staging area):
   - Wszystkie zmodyfikowane pliki:
     ```cmd
     git add .
     ```
   - Lub pojedynczy plik:
     ```cmd
     git add sciezka/do/pliku.py
     ```
4. Utwórz commita (commit) z opisem zmian:
   ```cmd
   git commit -m "krótki i zwięzły opis zmian"
   ```
5. Wyślij zmiany na GitHub:
   - **pierwszy push do nowo utworzonej gałęzi:**
     ```cmd
     git push -u origin zadX-grX
     ```
   - **każde kolejne wysłanie zmian:**
     ```cmd
     git push
     ```

---

## 4. Scalanie (merge) i zgłaszanie ukończonych zadań
Gdy zadanie grupy jest ukończone, przetestowane i gotowe do wdrożenia:
1. Upewnij się, że wszystkie commity są zpushowane do GitHuba (`git push`).
2. Zgłoś ukończenie zadania lub utwórz **Pull Request** na GitHubie z gałęzi `zadX-grX` do gałęzi nadrzędnej `zadX`.

---

## Pomoc
W razie problemów z gitem, konfliktów przy łączeniu zmian lub pytań technicznych skontaktuj się z obecnymi koordynatorami projektu.
