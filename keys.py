# keys.py

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def CAESAR_KEY(shift: int) -> str:
    shift %= len(ALFA26)
    return ALFA26[shift:] + ALFA26[:shift]

def to_dict(key: str) -> dict:
    key_dict = {}
    for i in range(len(key)):
        key_dict.update({ALFA26[i]: key[i]})
    return key_dict 

ATBASZ_KEY = ALFA26[::-1]
ROT13_KEY = CAESAR_KEY(13)
GADERYPOLUKI_KEY = "GBCEDFAHKJIUMNPOQYSTLVWXRZ"
