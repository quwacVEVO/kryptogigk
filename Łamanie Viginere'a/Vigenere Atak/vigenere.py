"""Vigenere cipher. Text and key must contain only A-Z letters."""

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def vigenere(text, key, direction, alphabet = ALPHABET):
    result = ""
    for i, character in enumerate(text):
        letter = alphabet.index(character)
        shift = alphabet.index(key[i % len(key)])
        result += alphabet[(letter + direction * shift) % len(alphabet)]
    return result


def encrypt(text, key):
    return vigenere(text, key, 1)


def decrypt(text, key, alphabet = ALPHABET):
    return vigenere(text, key, -1, alphabet)
