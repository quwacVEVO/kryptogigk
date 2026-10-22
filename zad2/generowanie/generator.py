import kryptolib as kp
import random

input_file = input("Input file: ")
output_file = input("Output file: ")
mode = input("Mode: ")

# random key generation
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
if mode == "ALFA37":
    ALPHABET += "0123456789 "

key = ''.join(random.sample(ALPHABET, len(ALPHABET)))
kp.write_file(f"{output_file.split('.')[0]}_key.txt", key)

# encryption
text = kp.read_file(input_file)

cipher = kp.encrypt(text, key, mode)
kp.write_file(output_file, cipher)