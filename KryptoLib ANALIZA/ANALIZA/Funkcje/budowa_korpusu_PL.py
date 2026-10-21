from utils import process_file
from Funkcje.funkcje_pomocnicze import zapisz_json
from Funkcje.zliczanie import *

def zbuduj_polski_korpus_literacki():
    folder_lit = "Korpusy/Język polski/Język literacki/"

    literacki_alfa26 = (process_file(f"{folder_lit}/Pan_Tadeusz.txt",
                                     f"{folder_lit}/Pan_Tadeusz_alfa26.txt",
                                     "alfa_26"))
    literacki_alfa37 = (process_file(f"{folder_lit}/Pan_Tadeusz.txt",
                                     f"{folder_lit}/Pan_Tadeusz_alfa37.txt",
                                     "alfa_37"))
    
    folder_lit = "Statystyki częstości występowania/Język polski/korpus_literacki_PL"

    # Statystyki dla ALFA26
    zapisz_json(f"{folder_lit}/alfa26_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(literacki_alfa26)))
    zapisz_json(f"{folder_lit}/alfa26_bigramy.json", przelicz_na_procenty(licz_ngramy(literacki_alfa26, n=2)))
    zapisz_json(f"{folder_lit}/alfa26_trigramy.json", przelicz_na_procenty(licz_ngramy(literacki_alfa26, n=3)))

    # # Statystyki dla ALFA37
    zapisz_json(f"{folder_lit}/alfa37_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(literacki_alfa37)))
    zapisz_json(f"{folder_lit}/alfa37_bigramy.json", przelicz_na_procenty(licz_ngramy(literacki_alfa37, n=2)))
    zapisz_json(f"{folder_lit}/alfa37_trigramy.json", przelicz_na_procenty(licz_ngramy(literacki_alfa37, n=3)))
    zapisz_json(f"{folder_lit}/alfa37_poczatki_slow.json", przelicz_na_procenty(analizuj_poczatki_slow(literacki_alfa37)))
    zapisz_json(f"{folder_lit}/alfa37_konce_slow.json", przelicz_na_procenty(analizuj_konce_slow(literacki_alfa37)))


def zbuduj_polski_korpus_wspolczesny():
    folder_wsp = "Korpusy/Język polski/Język współczesny/"

    wspolczesny_alfa26 = process_file(f"{folder_wsp}/wikipedia.txt",
                                      f"{folder_wsp}/wikipedia_alfa26.txt",
                                      "alfa_26")
    wspolczesny_alfa37 = process_file(f"{folder_wsp}/wikipedia.txt",
                                      f"{folder_wsp}/wikipedia_alfa37.txt",
                                      "alfa_37")


    folder_wsp = "Statystyki częstości występowania/Język polski/korpus_wspolczesny_PL"

    # Statystyki dla ALFA26
    zapisz_json(f"{folder_wsp}/alfa26_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(wspolczesny_alfa26)))
    zapisz_json(f"{folder_wsp}/alfa26_bigramy.json", przelicz_na_procenty(licz_ngramy(wspolczesny_alfa26, n=2)))
    zapisz_json(f"{folder_wsp}/alfa26_trigramy.json", przelicz_na_procenty(licz_ngramy(wspolczesny_alfa26, n=3)))

    # Statystyki dla ALFA37
    zapisz_json(f"{folder_wsp}/alfa37_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(wspolczesny_alfa37)))
    zapisz_json(f"{folder_wsp}/alfa37_bigramy.json", przelicz_na_procenty(licz_ngramy(wspolczesny_alfa37, n=2)))
    zapisz_json(f"{folder_wsp}/alfa37_trigramy.json", przelicz_na_procenty(licz_ngramy(wspolczesny_alfa37, n=3)))
    zapisz_json(f"{folder_wsp}/alfa37_poczatki_slow.json", przelicz_na_procenty(analizuj_poczatki_slow(wspolczesny_alfa37)))
    zapisz_json(f"{folder_wsp}/alfa37_konce_slow.json", przelicz_na_procenty(analizuj_konce_slow(wspolczesny_alfa37)))


def zbuduj_polski_korpus():
    folder = "Korpusy/Język polski/"

    alfa26 = (process_file(f"{folder}/Język współczesny/wikipedia.txt",
                          f"{folder}/Język współczesny/wikipedia_alfa26.txt","alfa_26")) + (process_file(f"{folder}/Język literacki/Pan_Tadeusz.txt",
                          f"{folder}/Język literacki/Pan_Tadeusz_alfa26.txt","alfa_26"))
    alfa37 = (process_file(f"{folder}/Język współczesny/wikipedia.txt",
                          f"{folder}/Język współczesny/wikipedia_alfa37.txt","alfa_37")) + (process_file(f"{folder}/Język literacki/Pan_Tadeusz.txt",
                          f"{folder}/Język literacki/Pan_Tadeusz_alfa37.txt","alfa_37"))

    folder = "Statystyki częstości występowania/Język polski"

    # Statystyki dla ALFA26
    zapisz_json(f"{folder}/alfa26_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(alfa26)))
    zapisz_json(f"{folder}/alfa26_bigramy.json", przelicz_na_procenty(licz_ngramy(alfa26, n=2)))
    zapisz_json(f"{folder}/alfa26_trigramy.json", przelicz_na_procenty(licz_ngramy(alfa26, n=3)))

    # Statystyki dla ALFA37
    zapisz_json(f"{folder}/alfa37_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(alfa37)))
    zapisz_json(f"{folder}/alfa37_bigramy.json", przelicz_na_procenty(licz_ngramy(alfa37, n=2)))
    zapisz_json(f"{folder}/alfa37_trigramy.json", przelicz_na_procenty(licz_ngramy(alfa37, n=3)))
    zapisz_json(f"{folder}/alfa37_poczatki_slow.json", przelicz_na_procenty(analizuj_poczatki_slow(alfa37)))
    zapisz_json(f"{folder}/alfa37_konce_slow.json", przelicz_na_procenty(analizuj_konce_slow(alfa37)))


def zbuduj_polskie_korpusy():
    zbuduj_polski_korpus_literacki()
    zbuduj_polski_korpus_wspolczesny()
    zbuduj_polski_korpus()