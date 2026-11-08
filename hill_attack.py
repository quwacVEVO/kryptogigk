import time
import json
import math
from itertools import product, combinations, permutations

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOD = len(ALPHABET)
N = 2 # n-gram length

# MATRIX OPERATIONS
def det(M):
    '''Determinant of a 2x2 matrix'''
    a, b, c, d = M
    return (a * d - b * c) % MOD

def is_inv(det):
    return math.gcd(det, MOD) == 1

def inv(M):
    '''Inverse of a 2x2 matrix'''
    a, b, c, d = M
    inv_det = pow(det(M), -1, MOD)
    
    inv_a = (d * inv_det) % MOD
    inv_b = (-b * inv_det) % MOD
    inv_c = (-c * inv_det) % MOD
    inv_d = (a * inv_det) % MOD
    
    return (inv_a, inv_b, inv_c, inv_d)

def mult(A, B):
    '''Multiplication of 2x2 matrices'''
    a11, a12, a21, a22 = A
    b11, b12, b21, b22 = B

    a = (a11 * b11 + a12 * b21) % MOD
    b = (a11 * b12 + a12 * b22) % MOD
    c = (a21 * b11 + a22 * b21) % MOD
    d = (a21 * b12 + a22 * b22) % MOD

    return (a, b, c, d)


# ANALYSIS OPERATIONS
def hill_matrix(h1, h2):
    '''A 2x2 matrix constructed from 2 bigrams'''
    H = f"{h1[0]}{h2[0]}{h1[1]}{h2[1]}"

    return [ALPHABET.index(h) for h in H]

def hill_decipher(cipher, inv_K):
    inv_a, inv_b, inv_c, inv_d = inv_K
    text = ""

    for i in range(0, len(cipher), N):

        y1 = ALPHABET.index(cipher[i])
        y2 = ALPHABET.index(cipher[i+1])

        x1 = (inv_a * y1 + inv_b * y2) % MOD
        x2 = (inv_c * y1 + inv_d * y2) % MOD

        text += ALPHABET[x1] + ALPHABET[x2]

    return text

def ngrams_fitness_score(text, freq):
    '''Calculates fitness score by log probability of n-grams'''
    score = 0
    
    for i in range(len(text)-N+1):
        ngram = text[i:i+N].upper()
        if ngram not in freq.keys():
            score = -float('inf')
            break
        else:
            score += math.log10(freq[ngram])

    return score


def load_stats(lang):
    if lang == "en":
        folder = "Język angielski"
    elif lang == "pl":
        folder = "Język polski"
    with open(f"Statystyki częstości występowania/{folder}/alfa26_bigramy.json", "r", encoding="utf-8") as f:
        stats = json.load(f)
    return stats

def generate_output(cipher, K, t):
    full_text = hill_decipher(cipher, inv(K))
    
    key = ""
    for k in K:
        key += f"{k} "

    return f"Key: {key}\nElapsed time: {t} s\n\n{full_text}"


# ATTACK ALGORITHMS
def brute_force(cipher, lang, letters):
    print("Brute Force Attack...")

    start_time = time.perf_counter() # START

    stats = load_stats(lang)
    
    all_matrixs = product(range(26), repeat=4) 
    inv_matrixs = []

    for K in all_matrixs:
        if is_inv(det(K)):
            inv_matrixs.append((K, inv(K)))
            
    best_score = -float('inf')
    best_K = None
     
    for K, K_inv in inv_matrixs:
        test_text = hill_decipher(cipher[:letters], K_inv)
        score = ngrams_fitness_score(test_text, stats)
        
        if score > best_score:
            best_score = score
            best_K = K
                
    end_time = time.perf_counter() # END
    elapsed_time = end_time - start_time

    return generate_output(cipher, best_K, elapsed_time)

def freq_analysis(cipher, lang, letters):
    print("Frequency Analysis Attack...")

    start_time = time.perf_counter() # START

    ngrams = dict()
    # ngrams count
    for i in range(0, len(cipher), N):
        ngram = cipher[i:i+N]
        if ngram in ngrams.keys():
            ngrams[ngram] += 1
        else:
            ngrams[ngram] = 1

    sorted_ngrams = dict(sorted(ngrams.items(), key=lambda item: item[1], reverse=True))

    stats = load_stats(lang)

    #look for an invertible ciphertext matrix
    for c1, c2 in combinations(sorted_ngrams.keys(), r=2):
        C = hill_matrix(c1, c2)
        if is_inv(det(C)):
            inv_C = inv(C)
            break

    best_score = -float('inf')
    best_K = None

    for p1, p2 in permutations(list(stats.keys())[:50], r=2): # check only 50 most common ngrams
        P = hill_matrix(p1, p2)
        inv_K = mult(P, inv_C) # K^{-1} = P * C^{-1}        

        plaintext = hill_decipher(cipher[:letters], inv_K)
        score = ngrams_fitness_score(plaintext, stats)
        
        if score > best_score:
            if is_inv(det(inv_K)):
                best_K = inv(inv_K)
                best_score = score
                #print(f"{plaintext}..., {score}")
                
    end_time = time.perf_counter() # END
    elapsed_time = end_time - start_time

    return generate_output(cipher, best_K, elapsed_time)
