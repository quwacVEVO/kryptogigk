import math
import time

def Shanks(g, h, p):
    m = math.ceil(math.sqrt(p-1)) # sufit z pierwiastka

    male_potegi = {} # małe potęgi jako słownik
    potega = 1
    for j in range(m):
        male_potegi[potega] = j
        potega = (potega * g) % p

    x = h
    mnoznik = pow(g, -m, p)  # g^(-m) modulo p

    i = 0
    while x not in male_potegi:
        x = (x*mnoznik)%p
        i += 1

    j = male_potegi[x]

    a = i*m + j
    return a

if __name__ == "__main__":
    p = 37781
    g = 3
    h = 24581

    print(f"Dane: p = {p}, g = {g}, h = {h}")

    start_time = time.perf_counter()
    a = Shanks (g, h, p)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    sprawdzenie = pow(g, a, p)

    print("Znalezione a spełniające g^a = h mod p wynosi:", a)
    print(f"Czas wykonania: {elapsed_time:.10f} sekund")
    print(f"Sprawdzenie: {sprawdzenie} = {h}")