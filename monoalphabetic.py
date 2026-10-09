# We assume that those functions from group one exist inside utils.py file
from .utils import alfa_26, alfa_37

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

MODES = {
    "ALFA26": (ALPHABET, alfa_26),
    "ALFA37": (ALPHABET + "0123456789 ", alfa_37),
}


def encrypt(text: str,
            key: str,
            mode: str = "ALFA26") -> str:
    alphabet, normalize = MODES[mode]
    return normalize(text).translate(str.maketrans(alphabet, key))


def decrypt(text: str,
            key: str,
            mode: str = "ALFA26") -> str:
    alphabet, _ = MODES[mode]
    return text.translate(str.maketrans(key, alphabet))