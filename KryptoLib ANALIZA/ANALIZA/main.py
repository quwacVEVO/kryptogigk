import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from Funkcje.budowa_korpusu_PL import zbuduj_polskie_korpusy
from Funkcje.budowa_korpusu_EN import zbuduj_angielskie_korpusy
from Testy.testy_analiza import test_sprawdzenie_poprawnosci

test_sprawdzenie_poprawnosci()
zbuduj_polskie_korpusy()
zbuduj_angielskie_korpusy()
