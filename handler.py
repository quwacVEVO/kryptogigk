"""Choose a cipher, read input files and save the result."""

from math import isqrt

import hill
import vigenere
from kryptolib.utils import alfa_26, read_file, write_file


def main():
    cipher_name = input("Choose a cipher (vigenere/hill): ").strip().lower()
    mode = input("Choose a mode (e = encrypt, d = decrypt): ").strip().lower()
    if cipher_name not in ("vigenere", "hill") or mode not in ("e", "d"):
        print("Unknown cipher or mode.")
        return

    input_file = input("Enter the input file name: ").strip()
    key_file = input("Enter the key file name: ").strip()
    output_file = input("Enter the output file name: ").strip()

    text = alfa_26(read_file(input_file))
    key = read_file(key_file)
    if cipher_name == "vigenere":
        cipher = vigenere
        key = alfa_26(key)
    else:
        cipher = hill
        # Read matrix entries row by row, ignoring line breaks.
        numbers = [int(number) for number in key.split()]
        size = isqrt(len(numbers))
        key = [numbers[i:i + size] for i in range(0, len(numbers), size)]

    if mode == "e":
        result = cipher.encrypt(text, key)
    else:
        result = cipher.decrypt(text, key)
    write_file(output_file, result)
    print("Result saved to:", output_file)


if __name__ == "__main__":
    main()
