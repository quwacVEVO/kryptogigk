from Funkcje.zliczanie import licz_pojedyncze_znaki, przelicz_na_procenty, licz_ngramy

def test_sprawdzenie_poprawnosci():
    tekst_testowy = "KDJVMC R3882384JASAKJJHHJS9AKKAHHE WEWWR1U12 3Y72H"

    licznosci = licz_pojedyncze_znaki(tekst_testowy)
    procenty = przelicz_na_procenty(licznosci)
    bigramy = licz_ngramy(tekst_testowy, n=2)
    trigramy = licz_ngramy(tekst_testowy, n=3)

    assert licznosci['K'] == 4, "Błąd: Liczba liter K powinna wynosić 4."
    assert licznosci['W'] == 3, "Błąd: Liczba liter W powinna wynosić 3."
    assert procenty['H'] == 10.0, "Błąd: Częstość litery H powinna wynosić 10%."
    assert bigramy['AK'] == 2, "Błąd: Bigram AK powinien wystąpić dokładnie 2 razy."
    assert trigramy['KDJ'] == 1, "Błąd: Trigram KDJ powinien wystąpić dokładnie 1 raz."

    tekst_testowy = "MATEMATYKE ROZUMIANO DAWNIEJ JAKO NAUKE O LICZBACH I FIGURACH GEOMETRYCZNYCH DZISIAJ DEFINICJA SPRAWILABY PEWNA TRUDNOSC Z UWAGI NA WIELOSC DYSCYPLIN TEJ NAUKI I TYM SAMYM ZNALEZIENIE PRZYSTAJACEGO DO NICH WSZYSTKICH OGOLNEGO OKRESLENIA MATEMATYKA BIERZE POD UWAGE CECHY ILOSCIOWE ZJAWISK BADA ICH WZAJEMNE ZWIAZKI METODA DEDUKCYJNA OPARTA NA LOGICE "
    
    licznosci = licz_pojedyncze_znaki(tekst_testowy)
    procenty = przelicz_na_procenty(licznosci)
    bigramy = licz_ngramy(tekst_testowy, n=2)
    trigramy = licz_ngramy(tekst_testowy, n=3)

    assert licznosci['M'] == 11, "Błąd: Liczba liter M powinna wynosić 11."
    assert licznosci['A'] == 35, "Błąd: Liczba liter A powinna wynosić 35."
    assert procenty['A'] == 10.0, "Błąd: Częstość litery A powinna wynosić 10%."
    assert bigramy['MA'] == 4, "Błąd: Bigram MA powinien wystąpić dokładnie 4 razy."
    assert bigramy['CH'] == 7, "Błąd: Bigram CH powinien wystąpić dokładnie 7 razy."
    # Jest problem gdy trigram/bigram/litera się nie pojawia w tekście?
    # assert trigramy['MAH'] == 0, "Błąd: Trigram MAH nie powinien wystąpić ani razu." 

    print("Wszystkie testy poprawności zakończone sukcesem!")