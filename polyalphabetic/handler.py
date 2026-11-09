"""Choose a cipher, read input files and save the result."""

from polyalphabetic import hill, vigenere
from kryptolib.utils import alfa_26, alfa_37, read_file, write_file

# name -> (normalising function, alphabet)
ALPHABETS = {
    "26": (alfa_26, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "37": (alfa_37, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "),
}

def run():
    cipher_name = input("Choose a cipher (vigenere/hill): ").strip().lower()
    mode = input("Choose a mode (e = encrypt, d = decrypt): ").strip().lower()
    alphabet_name = input("Choose an alphabet (26/37) [26]: ").strip() or "26"

    ######################
    # INPUT ERROR HANDLING
    if cipher_name not in ("vigenere", "hill") or mode not in ("e", "d") \
            or alphabet_name not in ALPHABETS:
        raise ValueError("Unknown cipher, mode or alphabet.")
    normalize, alphabet = ALPHABETS[alphabet_name]

    input_file = input("Enter the input file name: ").strip()
    key_file = input("Enter the key file name: ").strip()
    output_file = input("Enter the output file name: ").strip()

    ######################
    # CIPHER TYPE HANDLING
    text = normalize(read_file(input_file))
    key = read_file(key_file)
    if cipher_name == "vigenere":
        cipher = vigenere
        key = normalize(key)
    else:
        cipher = hill
        key = hill.parse_key(key)

    #############################
    # TEXT AND KEY ERROR HANDLING
    if not text or not key:
        raise ValueError("Text and key must not be empty.")
    if not set(text) <= set(alphabet) or \
            (cipher_name == "vigenere" and not set(key) <= set(alphabet)):
        raise ValueError("Text or key has characters outside the alphabet.")

    #######################
    # ENCRYPTING/DECRYPTING
    if mode == "e":
        result = cipher.encrypt(text, key, alphabet)
    else:
        result = cipher.decrypt(text, key, alphabet)
    write_file(output_file, result)
    print("Result saved to:", output_file)


if __name__ == "__main__":
    run()
