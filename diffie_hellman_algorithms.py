# Brute force for Diffie-Hellman key exchange
# pow(g, a, p) błyskawicznie oblicza (g^a) mod p bez tworzenia gigantycznych liczb
#while pow(g, a, p) != h:
#    a += 1
# print(f"Succes! a = {a}")
# Impossible to do in finity time! (About 90 000 years)

import math

def shanks_method(g, h, p):
    n = p - 1
    m = math.ceil(math.sqrt(n))
    
    baby_steps = {}
    for j in range(m):
        g_j = pow(g, j, p)
        baby_steps[g_j] = j
        
    g_inv = pow(g, -1, p)
    g_inv_m = pow(g_inv, m, p)
    
    for i in range(m):
        giant_step = (h * pow(g_inv_m, i, p)) % p
        if giant_step in baby_steps:
            j = baby_steps[giant_step]
            a = i * m + j
            return a
            
    return None

def pollard_rho_algorithm(g, h, p):
    n = p - 1
    
    def step(x, u, v):
        remainder = x % 3
        if remainder == 0:
            return (x * x) % p, (2 * u) % n, (2 * v) % n
        elif remainder == 1:
            return (x * g) % p, (u + 1) % n, v
        else:
            return (x * h) % p, u, (v + 1) % n

    x, u, v = 1, 0, 0
    x_prim, u_prim, v_prim = 1, 0, 0
    
    while True:
        x, u, v = step(x, u, v)
        
        x_prim, u_prim, v_prim = step(x_prim, u_prim, v_prim)
        x_prim, u_prim, v_prim = step(x_prim, u_prim, v_prim)
        
        if x == x_prim:
            break
            
    left_side = (v - v_prim) % n
    right_side = (u_prim - u) % n
    
    d = math.gcd(left_side, n)
    
    if d == 1:
        a = (right_side * pow(left_side, -1, n)) % n
        return a
    else:
        left_div = left_side // d
        right_div = right_side // d
        n_div = n // d
        
        try:
            a_base = (right_div * pow(left_div, -1, n_div)) % n_div
            for k in range(d):
                a_cand = a_base + k * n_div
                if pow(g, a_cand, p) == h:
                    return a_cand
        except ValueError:
            return None
            
    return None

if __name__ == "__main__":
    pass