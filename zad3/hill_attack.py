import numpy as np
import json
import math
import time
import datetime
import itertools

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
MOD = len(ALPHABET)
N = 2 # n-gram length

# matrix operations
def det(M):
    '''Determinant of a matrix'''
    return round(np.linalg.det(M)) % MOD

def adj(M):
    '''Adjugate of a 2x2 matrix'''
    return np.array([[M[1,1], -M[0,1]], [-M[1,0], M[0,0]]])

def inv(M):
    '''Inverse of a 2x2 matrix'''
    M = M % MOD
    inv_det_M = pow(det(M), -1, MOD)
    return (inv_det_M * adj(M)) % MOD


def hill_matrix(a, b):
    '''A 2x2 matrix constructed from 2 bigrams'''
    a = a.lower()
    b = b.lower()
    H = np.array([[ord(a[0]), ord(b[0])], [ord(a[1]), ord(b[1])]]) - ord('a')
    return H

def hill_decipher(cipher, M, length = 20):
    text = ""
    for i in range(0, length, N):
        c = np.array([ord(cipher[i]), ord(cipher[i+1])]) - ord('A') # cipher is written in uppercase
        p = (M @ c) % MOD
        text += ALPHABET[p[0]] + ALPHABET[p[1]]

    return text

def ngrams_count(text, n = 2):
    ngrams = dict()

    for i in range(0, len(text), n):
        ngram = text[i:i+n]
        if ngram in ngrams.keys():
            ngrams[ngram] += 1
        else:
            ngrams[ngram] = 1

    return dict(sorted(ngrams.items(), key=lambda item: item[1], reverse=True))

def ngrams_fitness_score(text, freq, n = 2):
    '''Calculates fitness score by log probability of n-grams'''
    score = 0
    
    for i in range(0, len(text)-n+1):
        ngram = text[i:i+n].upper()
        if ngram not in freq.keys():
            score = -np.inf
            break
        else:
            score += math.log10(ngrams_freq[ngram])

    return score


start = time.time()

cipher_file = "hill_szyfrogram.txt"
with open(cipher_file) as f:
    cipher = f.read()

ngrams = ngrams_count(cipher)

with open("Statystyki częstości występowania/Język angielski/alfa26_bigramy.json") as f:
    ngrams_freq = json.load(f)

# look for an invertible ciphertext matrix
for c1, c2 in itertools.combinations(ngrams.keys(), r=2):
    C = hill_matrix(c1, c2)
    try:
        inv_det_C = pow(det(C), -1, MOD)
        break # invertible matrix is found
    except:
        continue


best_plaintext = ""
best_score = -np.inf
best_inv_K = None

letters = 30 # we'll check only first 30 letters

t = datetime.datetime.now()
log_file = f"{cipher_file.split('.')[0]}_{t.strftime("%F_%H-%M-%S")}.txt"
with open(log_file, 'w') as f:
    # look for the best-fitting plaintext matrix
    for p1, p2 in itertools.permutations(ngrams_freq.keys(), r=2):
        P = hill_matrix(p1, p2)
        inv_K = (P @ inv(C)) % MOD # K^{-1} = P * C^{-1}

        plaintext = hill_decipher(cipher, inv_K, letters) 
        score = ngrams_fitness_score(plaintext, ngrams_freq)
        
        if score > best_score:
            try:
                K = inv(inv_K)
                best_inv_K = inv_K
                best_score = score
                best_plaintext = plaintext
                print(f"{plaintext}..., {score}")
            except:
                continue

    K = inv(best_inv_K)
    key = ""
    for x in np.nditer(K):
        key += ALPHABET[x]

    f.write(f"{best_plaintext}...\nkey: {key}\nscore: {best_score}")
    best_plaintext += hill_decipher(cipher[letters:], best_inv_K, len(cipher)-letters)

    end = time.time()
    f.write(f'\n\nElapsed: {end - start:.2f} seconds\n\n{best_plaintext}')