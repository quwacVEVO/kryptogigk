# Ciphertexts for lab 3

This set replaces the previous eight samples. Share only `ciphertexts`
with the attacking groups. Plaintexts and keys are retained outside the repo.

The set contains 16 ciphertexts:
2 languages x 2 ciphers x 2 lengths x 2 cases.

- `pl`: Polish; `en`: English.
- `hill`: 2x2 Hill cipher, column vectors, A=0, ..., Z=25.
- `vigenere`: Vigenere cipher over A-Z.
- `2k`: exactly 2000 letters; `30k`: exactly 30000 letters.
- `01` and `02`: two separate cases, each with its own text and key.

Examples: `ciphertexts/pl/cipher_hill_2k_01.txt` and
`ciphertexts/en/cipher_vigenere_30k_02.txt`.

All files contain only A-Z, without a final newline. Text lengths are counted
after ALFA26 normalization. Both lengths are even, so Hill needs no padding.
Every plaintext is a different excerpt; cases do not share the same text.
All ciphertexts were produced by this repository's code and verified through
both encryption and decryption in the interactive handler.

| Language | Cipher | Length | Files |
| --- | --- | ---: | --- |
| pl | hill | 2000 | `cipher_hill_2k_01.txt`, `cipher_hill_2k_02.txt` |
| pl | hill | 30000 | `cipher_hill_30k_01.txt`, `cipher_hill_30k_02.txt` |
| pl | vigenere | 2000 | `cipher_vigenere_2k_01.txt`, `cipher_vigenere_2k_02.txt` |
| pl | vigenere | 30000 | `cipher_vigenere_30k_01.txt`, `cipher_vigenere_30k_02.txt` |
| en | hill | 2000 | `cipher_hill_2k_01.txt`, `cipher_hill_2k_02.txt` |
| en | hill | 30000 | `cipher_hill_30k_01.txt`, `cipher_hill_30k_02.txt` |
| en | vigenere | 2000 | `cipher_vigenere_2k_01.txt`, `cipher_vigenere_2k_02.txt` |
| en | vigenere | 30000 | `cipher_vigenere_30k_01.txt`, `cipher_vigenere_30k_02.txt` |
