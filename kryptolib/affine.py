ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFA37 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "


def affine_encrypt(plain: str, A: int, B: int, mode: str) -> str:
    if mode not in ("ALFA26", "ALFA37"):
        raise ValueError("Mode not supported!")

    alphabet = ALFA26 if mode == "ALFA26" else ALFA37
    mod = len(alphabet)
    cipher = ""
    for k in plain:
        if k in alphabet:
            num = (A * alphabet.index(k) + B) % mod
            cipher += alphabet[num]
    return cipher


def affine_decrypt(cipher: str, A: int, B: int, mode: str) -> str:
    if mode not in ("ALFA26", "ALFA37"):
        raise ValueError("Mode not supported!")

    alphabet = ALFA26 if mode == "ALFA26" else ALFA37
    mod = len(alphabet)
    C = pow(A, -1, mod)
    plain = ""
    for k in cipher:
        if k in alphabet:
            num = C * (alphabet.index(k) - B) % mod
            plain += alphabet[num]
    return plain