# affine.py

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFA37 = f"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"

def affine_encrypt(plain: str, A: int, B: int, mode: str) -> str:
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


def affine_decrypt(cipher: str, A: int, B: int, mode: str) -> str:
    if mode != "alfa_26" and mode != "alfa_37":
        raise Exception("Mode not supported!")

    plain = ""
    if mode == "alfa_26":
        for k in cipher:
            C = pow(A,-1,26)
            num = C * (ALFA26.index(k) - B) % 26
            plain += ALFA26[num]
        return plain
    else:
        for k in cipher:
            C = pow(A,-1,37)
            num = C * (ALFA37.index(k) - B) % 37
            plain += ALFA37[num]
        return plain