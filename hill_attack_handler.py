from kryptolib.utils import read_file, write_file
from hill_attack import brute_force, freq_analysis

def main():
    input_file = input("File name: ")

    lang = input("Language (en = english, pl = polish): ")
    if lang not in {"en", "pl"}:
        return

    input_path = f"ciphertexts/{lang}/{input_file}"
    
    cipher = read_file(input_path)

    mode = input("Mode (bf = brute force, fa = frequency analysis): ")

    letters = int(input("How many letters to check: "))

    if mode == "bf":
        output = brute_force(cipher, lang, letters)
    elif mode == "fa":
        output = freq_analysis(cipher, lang, letters)
    else:
        return
    
    output_path = f"output/{lang}/{input_file[:-4]}_{mode}.txt"
    write_file(output_path, output)
    print(f"Key and message saved to {output_path}")

if __name__ == "__main__":
    main()  