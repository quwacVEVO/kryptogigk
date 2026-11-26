# Kontrola błędów - faktycznie wywołane przypadki

Plik generowany przez `python3 demo_errors.py`. Każdy wiersz powstał przez
rzeczywiste wywołanie podanej operacji; kolumna "komunikat" to dokładna treść
zgłoszona przez implementację.

## 1. Niepoprawne parametry generatorów

| przypadek | wyjątek | komunikat |
|---|---|---|
| LFSR: długość rejestru n = 1 | ValueError | długość rejestru n musi być >= 2, jest 1 |
| LFSR: n niecałkowite | ValueError | długość rejestru n musi być liczbą całkowitą |
| LFSR: wektor odczepów krótszy niż n | ValueError | wektor odczepów p ma długość 2, oczekiwano 4 |
| LFSR: ziarno dłuższe niż n | ValueError | ziarno S ma długość 5, oczekiwano 4 |
| LFSR: wartość 2 w wektorze odczepów | ValueError | wektor odczepów p zawiera wartość 2, dopuszczalne są tylko 0 i 1 |
| LFSR: wszystkie odczepy zerowe | ValueError | wszystkie odczepy są zerowe - brak sprzężenia zwrotnego |
| LFSR: ziarno zerowe (bez jawnej zgody) | ValueError | ziarno zerowe daje ciąg stale równy 0; użyj allow_zero_seed=True, jeśli chcesz zbadać ten przypadek brzegowy |
| LFSR: indeks odczepu poza zakresem | ValueError | indeks odczepu 9 poza zakresem 0..3 |
| LFSR: ziarno nie mieści się w rejestrze | ValueError | ziarno 16 nie mieści się w 4 bitach |
| LFSR: pusty przedział [10, 1] | ValueError | pusty przedział: [10, 1] |
| LFSR: nieznany tryb mapowania | ValueError | nieznany tryb mapowania: 'xyz' |
| LFSR: K = 1500 różnych liczb z [1, 1000] | ValueError | nie da się wygenerować 1500 różnych liczb z przedziału [1, 1000] o 1000 elementach (warunek K <= b - a + 1) |
| LFSR: okres 15 nie pokryje 100 różnych liczb z [1, 1000] | RuntimeError | przekroczono limit 101000 prób - generator nie pokrywa całego przedziału (prawdopodobnie zbyt krótki okres) |
| LCG: moduł m = 1 | ValueError | moduł m musi być >= 2, jest 1 |
| LCG: m niecałkowite | ValueError | parametr m musi być liczbą całkowitą, jest 100.0 |
| LCG: a ujemne | ValueError | parametry a i c nie mogą być ujemne (a=-5, c=1) |
| LCG: c ujemne | ValueError | parametry a i c nie mogą być ujemne (a=5, c=-1) |
| LCG: ziarno x0 = m (poza zakresem) | ValueError | ziarno x0 musi należeć do 0..m-1, jest 100 przy m=100 |
| LCG: parametr tekstowy | ValueError | parametr a musi być liczbą całkowitą, jest '5' |
| LCG: m = 15 mniejsze od szerokości przedziału (tryb mod_reject) | ValueError | przy m=15 i przedziale o 1000 elementach tryb mod_reject odrzuca wszystkie stany (m < span); zwiększ m lub użyj trybu scale |
| LCG: K = 1500 różnych liczb z [1, 1000] | ValueError | nie da się wygenerować 1500 różnych liczb z przedziału [1, 1000] o 1000 elementach (warunek K <= b - a + 1) |
| LCG: krótki okres nie pokryje przedziału | RuntimeError | przekroczono limit 101000 prób - generator nie pokrywa całego przedziału (prawdopodobnie zbyt krótki okres) |

## 2. Odczyt pliku z liczbami: brak pliku i błędny format

| przypadek | wyjątek | komunikat |
|---|---|---|
| odczyt: plik nie istnieje | FileNotFoundError | Brak pliku z danymi: /tmp/lab05_demo_kcy9cljq/nie_ma_mnie.txt |
| odczyt: ścieżka wskazuje katalog | BadNumberFile | Ścieżka wskazuje katalog, nie plik: /tmp/lab05_demo_kcy9cljq |
| odczyt: wiersz 3 nie jest liczbą całkowitą | BadNumberFile | /tmp/lab05_demo_kcy9cljq/zle_dane.txt:3: oczekiwano liczby całkowitej, jest 'siedem' |
| odczyt: liczba zmiennoprzecinkowa zamiast całkowitej | BadNumberFile | /tmp/lab05_demo_kcy9cljq/liczby_rzeczywiste.txt:1: oczekiwano liczby całkowitej, jest '3.14' |
| odczyt: plik bez żadnej liczby | BadNumberFile | /tmp/lab05_demo_kcy9cljq/pusty.txt: plik nie zawiera żadnej liczby |
| odczyt: plik binarny (nie UTF-8) | BadNumberFile | Plik nie jest tekstem UTF-8: /tmp/lab05_demo_kcy9cljq/binarny.bin |

Przypadków, które NIE zostały odrzucone: 0.
