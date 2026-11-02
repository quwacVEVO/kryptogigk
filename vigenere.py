"""Vigenere cipher. Text and key must contain only A-Z letters."""

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def vigenere(text, key, direction):
    result = ""
    for i, character in enumerate(text):
        letter = ALPHABET.index(character)
        shift = ALPHABET.index(key[i % len(key)])
        result += ALPHABET[(letter + direction * shift) % 26]
    return result


def encrypt(text, key):
    return vigenere(text, key, 1)


def decrypt(text, key):
    return vigenere(text, key, -1)
