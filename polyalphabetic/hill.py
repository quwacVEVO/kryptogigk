"""Hill cipher. Text: A-Z. Key: a square matrix invertible modulo 26."""

from math import isqrt

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# CHECK IF THE KEY IS ELIGIBLE
def parse_key(key):
    # Read matrix entries row by row, ignoring line breaks.
    numbers = [int(number) for number in key.split()]
    size = isqrt(len(numbers))
    if size == 0 or size * size != len(numbers):
        raise ValueError("Hill key must be a square matrix of integers.")
    return [numbers[i:i + size] for i in range(0, len(numbers), size)]


def minor(matrix, i, j):
    # Remove row i and column j.
    return [row[:j] + row[j + 1:]
            for k, row in enumerate(matrix) if k != i]


def determinant(matrix):
    if not matrix:
        return 1
    result = 0
    for j, number in enumerate(matrix[0]):
        result += (-1) ** j * number * determinant(minor(matrix, 0, j))
    return result


def inverse_matrix(matrix):
    inverse_det = pow(determinant(matrix), -1, 26)
    result = []
    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix)):
            # Swap i and j to transpose the cofactor matrix.
            cofactor = (-1) ** (i + j) * determinant(minor(matrix, j, i))
            row.append(cofactor * inverse_det % 26)
        result.append(row)
    return result


def hill(text, matrix):
    size = len(matrix)
    result = ""
    for start in range(0, len(text), size):
        block = [ALPHABET.index(character) for character in text[start:start + size]]
        for row in matrix:
            total = sum(row[j] * block[j] for j in range(size))
            result += ALPHABET[total % 26]
    return result


def encrypt(text, key):
    # Fill the last block with X letters.
    text += "X" * (-len(text) % len(key))
    return hill(text, key)


def decrypt(text, key):
    return hill(text, inverse_matrix(key))
