# Lab 3 - Group 2

Basic scope: Vigenere and Hill encryption/decryption, ALFA26 and file input/output.

## Files

- `vigenere.py`: encryption and decryption.
- `hill.py`: encryption and decryption, including the inverse matrix modulo 26.
- `handler.py`: step-by-step console prompts, files and text/key preparation.
- `kryptolib/`: shared library from `origin/zad1-gr1`, commit `9c3a3ac`.

The handler uses the existing `alfa_26`, `read_file` and `write_file` functions.
The final filter in `alfa_26` was changed from `isalpha()` to
`"A" <= c <= "Z"` because `isalpha()` also accepts letters outside A-Z.
Polish letters are converted to their plain Latin equivalents.
The shared function names remain unchanged for compatibility.

## Usage

Use Python 3.8 or newer. No external packages are needed.
Open a terminal in `lab/kryptogigk` and run:

```powershell
python handler.py
```

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

## Branches and shared code

The implementation belongs to `zad3-gr2`. No changes were committed to
`zad1-gr3`. The three scripts in `resources/lab3/grupa2_szyfry` are also
updated; use the repository versions for further development.

On 2026-11-02, GitHub references `zad3-gr2` through `zad3-gr5` all pointed
to `7220fd3`, containing only README and .gitignore. The shared library was
available on `zad1-gr1`. Its files were imported here with the ALFA26 fix
described above; this does not merge the old branch history.

Only this shared library is needed for these ciphers. The lab1 ciphers and
lab2 attack tools are not dependencies. The coordinating group can later
integrate the shared library on `main` or a common integration branch.
A direct merge of `origin/zad1-gr1` into the original `zad3-gr2` produces
a README conflict: keep the lab3 instructions and retain the ALFA26 fix.
