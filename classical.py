# We assume that these keys exist from group number 2 inside keys file
from keys import ATBASZ_KEY, CAESAR_KEY, GADERYPOLUKI_KEY, ROT13_KEY
from monoalphabetic import decrypt, encrypt


def encrypt_caesar(text: str,
                   key_input: str,
                   mode: str = "ALFA26") -> str:
    return encrypt(text, CAESAR_KEY(key_input), mode)


def decrypt_caesar(text: str,
                   key_input: str,
                   mode: str = "ALFA26") -> str:
    return decrypt(text, CAESAR_KEY(key_input), mode)


def encrypt_atbash(text: str,
                   mode: str = "ALFA26") -> str:
    return encrypt(text, ATBASZ_KEY, mode)


def decrypt_atbash(text: str,
                   mode: str = "ALFA26") -> str:
    return decrypt(text, ATBASZ_KEY, mode)


def encrypt_rot13(text: str,
                  mode: str = "ALFA26") -> str:
    return encrypt(text, ROT13_KEY, mode)


def decrypt_rot13(text: str,
                  mode: str = "ALFA26") -> str:
    return decrypt(text, ROT13_KEY, mode)


def encrypt_gaderypoluki(text: str,
                         mode: str = "ALFA26") -> str:
    return encrypt(text, GADERYPOLUKI_KEY, mode)


def decrypt_gaderypoluki(text: str,
                         mode: str = "ALFA26") -> str:
    return decrypt(text, GADERYPOLUKI_KEY, mode)