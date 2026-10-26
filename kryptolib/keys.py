ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def CAESAR_KEY(shift: int) -> str:
    shift = int(shift)
    shift %= len(ALFA26)
    return ALFA26[shift:] + ALFA26[:shift]


def to_dict(key: str) -> dict:
    key_dict = {}
    for i in range(min(len(key), len(ALFA26))):
        key_dict[ALFA26[i]] = key[i]
    return key_dict 


def GADERYPOLUKI_KEY(phrase: str) -> str:
    phrase = phrase.upper()
    pairs = {}
    for i in range(0, len(phrase) - 1, 2):
        c1, c2 = phrase[i], phrase[i + 1]
        pairs[c1] = c2
        pairs[c2] = c1
    return "".join(pairs.get(s, s) for s in ALFA26)


ATBASZ_KEY = ALFA26[::-1]
ROT13_KEY = CAESAR_KEY(13)