# keys.py

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ATBASZ_KEY = "ZYXWVUTSRQPONMLKJIHGFEDCBA"
ROT13_KEY = "NOPQRSTUVWXYZABCDEFGHIJKLM"
GADERYPOLUKI_KEY = "GBCEDFAHKJIUMNPOQYSTLVWXRZ"


def CAESAR_KEY(shift: int):
    shift %= len(ALFA26)
    return ALFA26[shift:] + ALFA26[:shift]

def to_dict(key: str) -> dict:
    key_dict = {}
    for i in range(len(key)):
        key_dict.update({ALFA26[i]: key[i]})
    return key_dict 
