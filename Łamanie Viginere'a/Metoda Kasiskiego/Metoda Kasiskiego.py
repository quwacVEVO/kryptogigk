import os

try:
    from ANALIZA.analyzer import get_language_suggestions
except ImportError:
    print("Błąd importu! Upewnij się, że podfolder nazywa się dokładnie 'ANALIZA' (wielkimi literami),")
    print("a w środku znajduje się plik o nazwie 'analyzer.py' (małymi literami).")

def kasiski_test_z_pliku(file_name, seq_len=3):
    # Automatyczne ustalanie ścieżki do folderu ze skryptem
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            clean_text = f.read().strip()
    except FileNotFoundError:
        return f"Błąd: Szukałem pliku w: {file_path} i go tam nie ma."
        
    # 1. Znajdowanie pozycji powtarzających się sekwencji
    sequences = {}
    for i in range(len(clean_text) - seq_len + 1):
        seq = clean_text[i:i+seq_len]
        if seq not in sequences:
            sequences[seq] = []
        sequences[seq].append(i)
        
    # Filtrujemy i zostawiamy tylko te ciągi, które pojawiły się min. 2 razy
    powtórzenia = {}
    distances = []
    for seq, pozycje in sequences.items():
        if len(pozycje) > 1:
            powtórzenia[seq] = pozycje  # Zapisujemy co się powtarza i gdzie
            for i in range(len(pozycje) - 1):
                dist = pozycje[i+1] - pozycje[i]
                distances.append(dist)
                
    if not distances:
        return f"Nie znaleziono powtórzeń dla ciągu o długości {seq_len}."

    # 2. Zliczanie dzielników
    factor_counts = {}
    for dist in distances:
        for factor in range(2, 21):
            if dist % factor == 0:
                if factor not in factor_counts:
                    factor_counts[factor] = 0
                factor_counts[factor] += 1
                
    # 3. Sortowanie sugerowanych długości klucza
    sugerowane_dlugosci = []
    for klucz, wartosc in factor_counts.items():
        sugerowane_dlugosci.append((klucz, wartosc))
    sugerowane_dlugosci.sort(key=lambda x: x[1], reverse=True)
    
    # Funkcja zwraca teraz dwa obiekty: listę powtórzeń oraz sugerowane długości
    return powtórzenia, sugerowane_dlugosci[:3]

def wyciagnij_grupy_liter(file_name, n):
    # Automatyczne ustalanie ścieżki do folderu ze skryptem
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            clean_text = f.read().strip()
    except FileNotFoundError:
        return f"Błąd: Szukałem pliku w: {file_path} i go tam nie ma."

    # Tworzymy listę n pustych ciągów tekstowych (na każdą grupę)
    grupy = ["" for _ in range(n)]
    
    # Rozdzielamy litery do odpowiednich grup przy użyciu operatora modulo (%)
    for i in range(len(clean_text)):
        indeks_grupy = i % n
        grupy[indeks_grupy] += clean_text[i]
        
    return grupy

def zapisz_grupy_do_plikow(file_name, n):
    # 1. Wczytywanie pliku głównego
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            clean_text = f.read().strip()
    except FileNotFoundError:
        return f"Błąd: Szukałem pliku w: {file_path} i go tam nie ma."

    # 2. Podział tekstu na n grup
    grupy = ["" for _ in range(n)]
    for i in range(len(clean_text)):
        grupy[i % n] += clean_text[i]

    # 3. Zapisywanie każdej grupy do osobnego pliku tekstowego
    print(f"--- ROZPOCZĘTO ZAPISYWANIE {n} GRUP DO PLIKÓW ---")
    
    for nr, tekst_grupy in enumerate(grupy):
        # Tworzenie nazwy pliku, np. szyfr0.txt, szyfr1.txt ... szyfr12.txt
        nazwa_wyjsciowa = f"szyfr{nr}.txt"
        sciezka_wyjsciowa = os.path.join(script_dir, nazwa_wyjsciowa)
        
        with open(sciezka_wyjsciowa, "w", encoding="utf-8") as f_out:
            f_out.write(tekst_grupy)
            
        print(f" -> Zapisano {len(tekst_grupy)} znaków do: {nazwa_wyjsciowa}")
        
    print("--- ZAKOŃCZONO ZAPISYWANIE ---")

def podmien_litere_w_pliku(file_name, stara_duza, nowa_mala):
    """
    Podmienia każdą literę 'stara_duza' na 'nowa_mala' w podanym pliku.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tekst = f.read()
            
        # Wykonujemy podmianę znaków
        nowy_tekst = tekst.replace(stara_duza, nowa_mala)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(nowy_tekst)
            
        print(f"Pomyślnie podmieniono '{stara_duza}' na '{nowa_mala}' w pliku {file_name}.")
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {file_name}.")


def złącz_pliki_w_calosc(n, nazwa_wyjsciowa="odszyfrowany.txt"):
    """
    Zlepia pliki szyfr0.txt do szyfr(n-1).txt z powrotem w jeden tekst.
    Odtwarza oryginalną kolejność za pomocą przeplatania liter.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Wczytujemy zawartość wszystkich n plików do listy
    zawartosc_plikow = []
    max_dlugosc = 0
    
    for i in range(n):
        nazwa_pliku = f"szyfr{i}.txt"
        sciezka_pliku = os.path.join(script_dir, nazwa_pliku)
        
        try:
            with open(sciezka_pliku, "r", encoding="utf-8") as f:
                tekst = f.read()
                zawartosc_plikow.append(tekst)
                if len(tekst) > max_dlugosc:
                    max_dlugosc = len(tekst)
        except FileNotFoundError:
            return f"Błąd: Nie można złożyć tekstu, brakuje pliku {nazwa_pliku}."
            
    # 2. Odtwarzamy tekst przeplatając litery z poszczególnych plików
    caly_tekst = []
    for pozycja_litery in range(max_dlugosc):
        for indeks_pliku in range(n):
            # Sprawdzamy, czy dany plik ma jeszcze litery na tej pozycji
            if pozycja_litery < len(zawartosc_plikow[indeks_pliku]):
                caly_tekst.append(zawartosc_plikow[indeks_pliku][pozycja_litery])
                
    finalny_tekst = "".join(caly_tekst)
    
    # 3. Zapisujemy połączony tekst do nowego pliku
    sciezka_wyjsciowa = os.path.join(script_dir, nazwa_wyjsciowa)
    with open(sciezka_wyjsciowa, "w", encoding="utf-8") as f_out:
        f_out.write(finalny_tekst)
        
    print(f"\n--- ZAKOŃCZONO ŁĄCZENIE ---")
    print(f"Zlepiłem {n} plików i zapisałem wynik w: {nazwa_wyjsciowa}")
    return finalny_tekst

def analizuj_jezyk_wszystkich_grup(file_name, n):
    """
    Wczytuje po kolei częściowe pliki wygenerowane z pliku głównego i wywołuje
    na nich zewnętrzną analizę językową.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Rozdzielamy nazwę pliku bazowego i jego rozszerzenie (np. "szyfr" i ".txt")
    nazwa_bazowa, rozszerzenie = os.path.splitext(file_name)
    
    print(f"\n========================================================")
    print(f"   AUTOMATYCZNA ANALIZA JĘZYKOWA DLA {n} POZYCJI KLUCZA")
    print(f"   Plik bazowy: {file_name}")
    print(f"========================================================")
    print(f"{'Plik':<12} | {'Aktualne IoC':<12} | {'Sugestia IoC':<12} | {'Sugestia SSE':<12}")
    print("-" * 60)
    
    glosy_na_jezyk = {"polski": 0, "angielski": 0}
    
    for i in range(n):
        # Dynamiczne budowanie nazwy, np. "szyfr0.txt" lub "tajne0.txt"
        nazwa_czesci = f"{nazwa_bazowa}{i}{rozszerzenie}"
        sciezka_pliku = os.path.join(script_dir, nazwa_czesci)
        
        try:
            with open(sciezka_pliku, "r", encoding="utf-8") as f:
                tekst_grupy = f.read().strip()
        except FileNotFoundError:
            print(f"Błąd: Brak pliku {nazwa_czesci}. Pomiń tę pozycję.")
            continue
            
        if not tekst_grupy:
            continue
            
        # Wywołanie Twojej gotowej funkcji analizującej
        current_ioc, suggested_by_ioc, sse_scores, suggested_by_sse = get_language_suggestions(tekst_grupy)
        
        # Zliczamy głosy na ostateczny język tekstu
        glosy_na_jezyk[suggested_by_sse] += 1
        
        # Wypisanie sformatowanego wiersza dla każdego pliku
        print(f"{nazwa_czesci:<12} | {current_ioc:<12.5f} | {suggested_by_ioc:<12} | {suggested_by_sse:<12}")
        
    print("-" * 60)
    # Wybieramy język, który zdobył najwięcej głosów
    if sum(glosy_na_jezyk.values()) > 0:
        ostateczny_jezyk = max(glosy_na_jezyk, key=glosy_na_jezyk.get)
        print(f"WYNIK GLOBALNY: Cały tekst jest najprawdopodobniej w języku: {ostateczny_jezyk.upper()}")
    else:
        print("WYNIK GLOBALNY: Brak danych do określenia języka.")
    print(f"========================================================")

def stworz_tekst_z_lukami(nazwa_pliku_wynik, nazwa_wyjsciowa="sam_wynik.txt"):
    """
    Wczytuje złączony tekst, zamienia wszystkie DUŻE litery na '_' 
    oraz zapisuje wynik do nowego pliku. Małe litery i spacje zostają nienaruszone.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sciezka_wejsciowa = os.path.join(script_dir, nazwa_pliku_wynik)
    sciezka_wyjsciowa = os.path.join(script_dir, nazwa_wyjsciowa)
    
    try:
        with open(sciezka_wejsciowa, "r", encoding="utf-8") as f:
            tekst_mieszany = f.read()
    except FileNotFoundError:
        return f"Błąd: Nie znaleziono pliku wejściowego '{nazwa_pliku_wynik}'."

    nowy_tekst = []
    for char in tekst_mieszany:
        # Jeśli znak to DUŻA litera, zamieniamy go na lukę '_'
        if char.isupper():
            nowy_tekst.append("_")
        else:
            # Małe litery, spacje, znaki nowej linii zostają bez zmian
            nowy_tekst.append(char)
            
    finalny_tekst = "".join(nowy_tekst)
    
    with open(sciezka_wyjsciowa, "w", encoding="utf-8") as f_out:
        f_out.write(finalny_tekst)
        
    print(f"Utworzono tekst z lukami i zapisano go w: {nazwa_wyjsciowa}")
    return finalny_tekst



# --- PRZYKŁAD ---
nazwa_pliku = "szyfr.txt"
dlugosci_ciagow = [3, 4, 5, 6, 7]  # Sprawdzamy np. ciągi 3- i 4-literowe

print(f"--- ANALIZA PLIKU: {nazwa_pliku} ---")
for dlugosc in dlugosci_ciagow:
    wynik = kasiski_test_z_pliku(nazwa_pliku, seq_len=dlugosc)
    
    print(f"\n=============================================")
    print(f"ANALIZA DLA CIĄGÓW O DŁUGOŚCI {dlugosc}")
    print(f"=============================================")
    
    if isinstance(wynik, str):
        print(wynik)
    else:
        co_sie_powtarza, sugerowane_klucze = wynik
        
        # # Wyświetlanie znalezionych powtórzeń
        # print("Znalezione powtarzające się sekwencje:")
        # for sekwencja, pozycje in co_sie_powtarza.items():
        #     print(f" -> Ciąg '{sekwencja}' pojawia się {len(pozycje)} razy na pozycjach: {pozycje}")
            
        # Wyświetlanie sugerowanych długości klucza
        print("\nNajbardziej prawdopodobne długości klucza:")
        for dlugosc_klucza, powtórzenia in sugerowane_klucze:
            print(f" -> Sugerowana długość: {dlugosc_klucza} (liczba dopasowań: {powtórzenia})")

dlugosc_klucza = 13

# wynik_grup = wyciagnij_grupy_liter(nazwa_pliku, dlugosc_klucza)

# if isinstance(wynik_grup, str):
#     print(wynik_grup)
# else:
#     print(f"--- ROZDZIAŁ TEKSTU NA {dlugosc_klucza} GRUP ---")
#     for nr, tekst_grupy in enumerate(wynik_grup):
#         # Wyświetlamy numer grupy (od 1 do 13) oraz pierwsze 40 liter dla podglądu
#         print(f"Grupa {nr + 1:2d} (pozycja {nr}, {nr+dlugosc_klucza}...): {tekst_grupy[:40]}...")

# zapisz_grupy_do_plikow(nazwa_pliku, dlugosc_klucza)

# print("--- TEST PODMIANY ---")
# podmien_litere_w_pliku("szyfr0.txt", stara_duza="N", nowa_mala="a")

# 2. Przykład złączania plików w całość:
# Podaj liczbę plików (długość klucza), które chcesz z powrotem zlepić w jeden dokument

# złącz_pliki_w_calosc(n=dlugosc_klucza, nazwa_wyjsciowa="wynik.txt")

# analizuj_jezyk_wszystkich_grup(nazwa_pliku, dlugosc_klucza)

# nazwa_zlaczonego_pliku = "wynik.txt"

# stworz_tekst_z_lukami(nazwa_zlaczonego_pliku, "sam_wynik.txt")