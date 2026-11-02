# Lab 3 - Group 2

Basic scope: Vigenere and Hill encryption/decryption, ALFA26 and file input/output.

## Files

- `vigenere.py`: encryption and decryption.
- `hill.py`: encryption and decryption, including the inverse matrix modulo 26.
- `handler.py`: step-by-step console prompts, files and text/key preparation.
- `../kryptolib/`: shared library from `origin/zad1-gr1`, commit `9c3a3ac`.

The handler uses the existing `alfa_26`, `read_file` and `write_file` functions.
The final filter in `alfa_26` was changed from `isalpha()` to
`"A" <= c <= "Z"` because `isalpha()` also accepts letters outside A-Z.
Polish letters are converted to their plain Latin equivalents.
The shared function names remain unchanged for compatibility.

## Usage

Use Python 3.8 or newer. No external packages are needed.
Open a terminal in `lab/kryptogigk` and run:

```powershell
python -m polyalphabetic.handler
```

Run this command from the repository root, not from `polyalphabetic`.
Both `polyalphabetic` and `kryptolib` are Python packages in that root.
In PyCharm, mark `lab/kryptogigk` as Sources Root. For a run configuration,
choose module name `polyalphabetic.handler` and use `lab/kryptogigk` as the
working directory. The local project configuration includes this source root.

Answer the prompts in order, for example:

```text
Choose a cipher (vigenere/hill): vigenere
Choose a mode (e = encrypt, d = decrypt): e
Enter the input file name: text.txt
Enter the key file name: key.txt
Enter the output file name: encrypted.txt
```

For decryption, run the program again, choose `d`, and use the encrypted
file as input with the same key. File paths are relative to the terminal's
working directory. Enter paths without surrounding quotes, even with spaces.

Create input and key files using UTF-8. A Vigenere key is a nonempty word,
for example `LEMON`. A Hill key contains integers in row order, for example:

```text
3 3
2 5
```

Writing `3 3 2 5` on one line also works. The number of entries must be
`size * size`; the matrix must be invertible modulo 26. Larger matrices
are supported, but the simple determinant calculation is intended for small
lab examples. Blocks are column vectors: `ciphertext = key * block (mod 26)`,
with A=0, ..., Z=25.

Hill fills the last block with X letters. Decryption keeps these letters
because padding cannot be distinguished from an actual X at the end.
Decryption restores ALFA26 text, without original spacing or punctuation.
The `encrypt(text, key)` and `decrypt(text, key)` functions expect prepared
A-Z input. Hill ciphertext length must be a multiple of the matrix size.
This basic implementation assumes valid files and keys; invalid input may
raise a Python exception.

## Generated ciphertexts

There are 16 cases in `samples/ciphertexts`: Polish and English, Hill and
Vigenere, lengths of 2000 and 30000 ALFA26 characters, two cases per combination.
Language folders are named `pl` and `en`; files are named, for example,
`cipher_hill_2k_01.txt`. See `samples/README.md` for the complete structure.
The 16 ALFA26 plaintexts, 16 keys and a case manifest are stored outside the
repository in the workspace's `resources/lab3/private_cases` directory.
These replace the previous samples. Keep verification files private until
the attacks are finished.
