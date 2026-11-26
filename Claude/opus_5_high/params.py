"""Jedno miejsce z parametrami wszystkich eksperymentów.

Ten plik jest "umową" przebiegu: żeby porównać inny model GenAI na TYCH SAMYCH
wejściach, wystarczy użyć identycznego params.py i uruchomić run_all.py.
Każda zmiana wartości poniżej unieważnia porównywalność z wcześniejszymi wynikami.
"""

# ---------------------------------------------------------------- scenariusz główny
K = 200                 # ile liczb generuje każdy generator w scenariuszu głównym
LOW, HIGH = 1, 1000     # przedział [a, b] scenariusza głównego (span = 1000)

# ---------------------------------------------------------------- LFSR (grupa 1)
LFSR_N = 16                        # długość rejestru
LFSR_TAP_INDICES = (0, 2, 3, 5)    # p_j = 1 dla j w tym zbiorze; f(x) = x^16 + x^5 + x^3 + x^2 + 1
LFSR_SEED = 0xACE1                 # ziarno jako liczba (0b1010110011100001), 16 bitów
LFSR_MAPPING = "reject"            # mapowanie bitów na [a, b] z odrzucaniem (równomierne)

# ---------------------------------------------------------------- LCG (grupa 2)
LCG_M = 65536           # moduł m = 2^16 (okres mierzalny w całości)
LCG_A = 25173           # mnożnik a
LCG_C = 13849           # przyrost c (w notatce oznaczany b)
LCG_X0 = 2026           # ziarno x0
LCG_MAPPING = "mod_reject"

# LCG do scenariuszy z dużymi przedziałami: m = 2^16 nie pokrywa przedziałów
# szerszych niż 65536 wartości, dlatego tam używamy parametrów generatora Java.
LCG_BIG_M = 2 ** 48
LCG_BIG_A = 25214903917
LCG_BIG_C = 11
LCG_BIG_X0 = 2026

# LCG do demonstracji ciągu bez kolizji BEZ filtru powtórzeń:
# pełny okres m (warunki Hull-Dobella) + mapowanie bijektywne (span = m).
LCG_RAW_M, LCG_RAW_A, LCG_RAW_C, LCG_RAW_X0 = 1024, 5, 1, 7
LCG_RAW_LOW, LCG_RAW_HIGH = 1, 1024
LCG_RAW_K = 200

# ---------------------------------------------------------------- testy pierwszości (grupa 3)
RNG_SEED = 12345        # ziarno losowania podstaw (random.Random) - odtwarzalność
FERMAT_ROUNDS = 5       # liczba iteracji testu Fermata
MR_ROUNDS = 5           # liczba iteracji testu Millera-Rabina (ustalona do porównań)
MR_ROUNDS_SWEEP = (1, 2, 3, 5, 10, 20, 40)   # badanie wpływu liczby iteracji

# Przedziały do badania wpływu rozmiaru liczb na czas testów.
# Górna granica wynika z kosztu DOKŁADNEGO testu dzielenia (podstawa odniesienia):
# dla n ~ 10^12 sito i dzielenia są jeszcze wykonalne w sekundach.
RANGE_SCENARIOS = (
    ("[1, 10^3]", 1, 10 ** 3),
    ("[10^3, 10^6]", 10 ** 3, 10 ** 6),
    ("[10^6, 10^9]", 10 ** 6, 10 ** 9),
    ("[10^9, 10^12]", 10 ** 9, 10 ** 12),
)
RANGE_K = 60            # ile liczb na jeden przedział w badaniu rozmiarów

# ---------------------------------------------------------------- demonstracja ciągu bez kolizji
UNIQUE_K = 200          # K dla ciągu K różnych liczb (filtr powtórzeń), K <= HIGH-LOW+1
RAW_UNIQUE_K = 50       # K dla ciągu bez kolizji uzyskanego BEZ filtru (dobór ziarna)
RAW_UNIQUE_LOW = 1
RAW_UNIQUE_HIGH = 10000
IMPOSSIBLE_K = 1500     # przypadek K > b-a+1 dla [1, 1000] - celowo niewykonalny

# ---------------------------------------------------------------- pliki wynikowe
RESULTS_DIR = "results"
