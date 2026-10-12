# affine.py

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFA37 = f"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"

def affine_encrypt(plain: str, mode: str, A: int, B: int) -> str:
    if mode != "alfa_26" and mode != "alfa_37":
        raise Exception("Mode not supported!")

    cipher = ""
    if mode == "alfa_26":
        for k in plain:
            num = (A * ALFA26.index(k) + B) % 26
            cipher += ALFA26[num]
        return cipher
    else:
        for k in plain:
            num = (A * ALFA37.index(k) + B) % 37
            cipher += ALFA37[num]
        return cipher


def affine_decript(cipher: str, A: int, B: int) -> str:
    plain = ""
    for k in cipher:
        C = pow(A,-1,26)
        num = C * ((ord(k) - 65) - B) % 26
        plain += ALFA26[num]
    return plain

print(affine_decript(affine_encrypt(ALFA26,"alfa_26", 3, 4), 3, 4))
