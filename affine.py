# affine.py

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def affine_encrypt(plain: str, A: int, B: int) -> str:
    cipher = ""
    for k in plain:
        num = (A * (ord(k) - 65) + B) % 26
        cipher += ALFA26[num]
    return cipher

