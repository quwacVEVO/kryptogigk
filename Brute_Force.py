import time, random
from math import gcd

def bruteforce(p, g, h):
    start_time = time.perf_counter()
    
    for n in range(p):
        if pow(g, n, p) == h:
            end_time = time.perf_counter()
            total_time = end_time - start_time
            
            print(f'a={n}')
            print(f'Czas działania: {total_time:.6f}s')
            return n, total_time  
            
    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f'Nie znaleziono rozwiązania. Czas działania: {total_time:.6f}s')
    return None, total_time

p, g, h = 37781, 3, 24581
N = 100

czas = []
for _ in range(N):
    a, total_time = bruteforce(p, g, h)
    czas.append(total_time)
print(f'bruteforce: a={a}, g^a = h: {pow(g, a, p) == h}')
print(f'Średni czas z {N} uruchomień Bruteforce: {sum(czas) / N:.6f}s')