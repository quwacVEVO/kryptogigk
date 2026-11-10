import os
import re
import math
import logging
from collections import Counter

DIR_OUT = "rozwiązania"
FILE_LOG = os.path.join(DIR_OUT, "kryptoanaliza.log")

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
COPRIME_26 = {1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25}
VOWELS = set("AEIOUY")

# Średnie częstości występowania liter w języku angielskim i polskim (%)
LANG_FREQ_EN = {
    'A': 8.12, 'B': 1.49, 'C': 2.71, 'D': 4.32, 'E': 12.02, 'F': 2.30,
    'G': 2.03, 'H': 5.92, 'I': 7.31, 'J': 0.10, 'K': 0.69, 'L': 3.98,
    'M': 2.61, 'N': 6.95, 'O': 7.68, 'P': 1.82, 'Q': 0.11, 'R': 6.02,
    'S': 6.28, 'T': 9.10, 'U': 2.88, 'V': 1.11, 'W': 2.09, 'X': 0.17,
    'Y': 2.11, 'Z': 0.07
}

LANG_FREQ_PL = {
    'A': 8.91, 'B': 1.47, 'C': 3.96, 'D': 3.25, 'E': 7.66, 'F': 0.30,
    'G': 1.42, 'H': 1.08, 'I': 8.21, 'J': 2.28, 'K': 3.51, 'L': 2.10,
    'M': 2.80, 'N': 5.52, 'O': 7.75, 'P': 3.13, 'Q': 0.01, 'R': 4.69,
    'S': 4.32, 'T': 3.98, 'U': 2.50, 'V': 0.04, 'W': 4.65, 'X': 0.02,
    'Y': 3.76, 'Z': 5.64
}

LETTER_LOG_P = [
    2.1, 0.4, 1.4, 1.3, 2.4, 0.5, 0.7, 1.3, 2.0, 0.5, 1.2, 1.4, 1.1,
    1.9, 2.1, 1.1, -1.5, 1.8, 1.8, 2.1, 1.0, 0.2, 1.2, -1.5, 1.1, 1.6
]

COMMON_TRIGRAMS = {
    'THE', 'AND', 'ING', 'ENT', 'ION', 'HER', 'FOR', 'THA', 'NTH', 'INT',
    'ERE', 'TIO', 'TER', 'EST', 'ERS', 'ATI', 'HAT', 'ATE', 'ALL', 'ETH',
    'NIE', 'PRZ', 'RZE', 'SZY', 'CIE', 'STA', 'WIE', 'DLA', 'POW', 'ROZ',
    'ZNA', 'KTO', 'JES', 'EST', 'ODP', 'POZ', 'WSZ', 'TAK', 'BYS', 'ICH'
}

VOCAB_PL = {
    "TO", "CO", "NA", "DO", "OD", "PO", "ZA", "ZE", "WY", "WE", "JE", "BO", "BY",
    "MA", "SA", "CI", "TU", "JA", "ON", "TY", "MY", "IM", "GO", "MU", "NIE", "SIE",
    "JAK", "ALE", "DLA", "TAK", "TEN", "TYM", "JEST", "POD", "NAD", "BEZ", "PAN",
    "KTO", "GDY", "TEZ", "BYC", "MAM", "NAS", "WAS", "ICH", "JUZ", "SZYFR", "HILLA",
    "TEKST", "TAJNE", "TAJNY", "TAJNA", "KLUCZ", "BARDZO", "ATAK", "MACIERZ",
    "WIADOMOSC", "KOMUNIKAT", "ZADANIE", "KRYPTOLOGIA", "ALFABET", "STUDENT", "STUDENTA",
    "PROSTY", "UKRYTA", "DZIS", "JUTRO", "WARTO", "KONIEC", "NOWY", "DOBRY", "WIELKI", "MALY",
    "CALY", "SAMI", "DOM", "KRAJ", "MIASTO", "SWIAT", "DROGA", "ZYCIE", "SERCE",
    "OCZY", "REKA", "GLOWA", "WODA", "ROK", "CZAS", "DZIEN", "PRACA", "LUDZIE", "RZECZ",
    "INFORMATYKA", "POLITECHNIKA", "UNIWERSYTET", "PROFESOR", "OCENA", "EGZAMIN",
    "KOLOKWIUM", "ZALICZENIE", "SEMESTR", "GRUPA", "SALA", "PUNKT", "LEKCJA", "WIEDZA"
}

VOCAB_EN = {
    "THE", "AND", "THAT", "HAVE", "FOR", "NOT", "WITH", "YOU", "THIS", "BUT", "HIS",
    "FROM", "THEY", "SAY", "HER", "SHE", "WILL", "ONE", "ALL", "WOULD", "THERE", "THEIR",
    "WHAT", "OUT", "ABOUT", "WHO", "GET", "WHICH", "GO", "ME", "WHEN", "MAKE", "CAN",
    "LIKE", "TIME", "JUST", "KNOW", "TAKE", "PEOPLE", "INTO", "YEAR", "YOUR", "GOOD",
    "SOME", "COULD", "THEM", "SEE", "OTHER", "THAN", "THEN", "NOW", "LOOK", "ONLY",
    "COME", "ITS", "OVER", "THINK", "ALSO", "BACK", "AFTER", "USE", "TWO", "HOW", "OUR",
    "WORK", "FIRST", "WELL", "WAY", "EVEN", "NEW", "WANT", "BECAUSE", "ANY", "THESE",
    "SECRET", "CIPHER", "ATTACK", "MESSAGE", "SYSTEM", "CRYPTO", "MATRIX", "VECTOR",
    "LINEAR", "HIDDEN", "SECURITY", "ALGORITHM", "MEETING", "TOMORROW", "MORNING"
}

VOCABULARY = list(VOCAB_PL | VOCAB_EN)

KEYWORDS_3X3 = [
    "ALPHABETS", "CIPHERKEY", "SECRETKEY", "GYMNASTIC", "COMPUTERS", "KRYPTOLOG",
    "BEZPIECZE", "MATEMATYK", "UNIWERSYT", "AKADEMIAX", "ZADANIOWY", "ABCABCABC",
    "KEYKEYKEY", "HILLMAGIC", "GYBNQKURP", "RRFRSVCCT", "PASSWORDX", "DEFENDNOW"
]

TOP_DIGRAMS_PL = [
    "IE", "PO", "PR", "ZY", "ZE", "NA", "CO", "OD", "DO", "NI", "RA", "CZ",
    "SZ", "TR", "AK", "MI", "TY", "JA", "WI", "DZ", "CH", "ZA", "TA", "RO"
]

TOP_DIGRAMS_EN = [
    "TH", "HE", "IN", "ER", "AN", "RE", "ED", "ON", "ES", "ST", "EN", "AT",
    "TO", "NT", "HA", "ND", "OU", "EA", "NG", "AS", "OR", "TI", "IS", "ET"
]


def setup_logger():
    os.makedirs(DIR_OUT, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(FILE_LOG, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def build_bigram_table():
    table = [[0 for _ in range(26)] for _ in range(26)]
    high_bg = {
        'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 'ES', 'ST', 'EN', 'AT',
        'TO', 'NT', 'HA', 'ND', 'OU', 'EA', 'NG', 'AS', 'OR', 'TI', 'IS', 'ET',
        'IT', 'AR', 'TE', 'SE', 'HI', 'OF', 'AL', 'ME', 'VE', 'LE', 'WA', 'NE',
        'IE', 'PO', 'PR', 'ZY', 'ZE', 'NA', 'CO', 'OD', 'DO', 'NI', 'RA', 'CZ',
        'SZ', 'TR', 'AK', 'MI', 'TY', 'JA', 'WI', 'DZ', 'CH', 'ZA', 'TA', 'RO',
        'OW', 'WY', 'KO', 'EM', 'WO', 'LI', 'MA', 'KA', 'OR', 'EC', 'CI', 'SI',
        'ZI', 'BR', 'GR', 'KR', 'AM', 'OM', 'EK', 'OK', 'IK', 'UK', 'YK', 'EW'
    }
    for bg in high_bg:
        table[ord(bg[0]) - 65][ord(bg[1]) - 65] = 12

    for i in range(26):
        c1 = chr(i + 65)
        for j in range(26):
            c2 = chr(j + 65)
            if table[i][j] == 0:
                if (c1 in VOWELS and c2 not in VOWELS) or (c1 not in VOWELS and c2 in VOWELS):
                    table[i][j] = 2

    rare_chars = {'Q', 'X', 'V'}
    for i in range(26):
        c1 = chr(i + 65)
        for j in range(26):
            c2 = chr(j + 65)
            if c1 == 'Q' and c2 != 'U':
                table[i][j] = -25
            elif c1 in rare_chars and c2 in rare_chars:
                table[i][j] = -15
    return table


BIGRAM_TABLE = build_bigram_table()


def mod_inv(a, m=26):
    try:
        return pow(a, -1, m)
    except ValueError:
        return None


def invert_matrix_2x2(matrix):
    (a, b), (c, d) = matrix
    det = (a * d - b * c) % 26
    inv_d = mod_inv(det, 26)
    if inv_d is None:
        return None
    return [
        [(d * inv_d) % 26, (-b * inv_d) % 26],
        [(-c * inv_d) % 26, (a * inv_d) % 26]
    ]


def invert_matrix_3x3(m):
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    det = (a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)) % 26
    inv_d = mod_inv(det, 26)
    if inv_d is None:
        return None
    cof = [
        [(e * i - f * h) % 26, -(b * i - c * h) % 26, (b * f - c * e) % 26],
        [-(d * i - f * g) % 26, (a * i - c * g) % 26, -(a * f - c * d) % 26],
        [(d * h - e * g) % 26, -(a * h - b * g) % 26, (a * e - b * d) % 26]
    ]
    return [[(cof[r][c] * inv_d) % 26 for c in range(3)] for r in range(3)]


def deep_score(text):
    n = len(text)
    score = 0.0
    matched = []

    for w in VOCABULARY:
        if w in text:
            matched.append(w)
            score += (len(w) ** 2) * 35.0

    for i in range(n - 1):
        score += BIGRAM_TABLE[ord(text[i]) - 65][ord(text[i+1]) - 65]

    for i in range(n - 2):
        if text[i:i+3] in COMMON_TRIGRAMS:
            score += 20.0

    v_ratio = sum(1 for ch in text if ch in VOWELS) / n
    if 0.30 <= v_ratio <= 0.52:
        score += 35.0
    elif v_ratio < 0.18 or v_ratio > 0.65:
        score -= 70.0

    consec_c = 0
    for ch in text:
        if ch not in VOWELS:
            consec_c += 1
            if consec_c >= 5:
                score -= 30.0
        else:
            consec_c = 0

    return score, list(set(matched))


def decrypt_text(ciphertext, d_mat, dim):
    c_nums = [ord(ch) - 65 for ch in ciphertext]
    num_blocks = len(c_nums) // dim
    pt_chars = []
    for b in range(num_blocks):
        vec = c_nums[b * dim : (b + 1) * dim]
        for row in d_mat:
            if dim == 2:
                val = (row[0] * vec[0] + row[1] * vec[1]) % 26
            else:
                val = (row[0] * vec[0] + row[1] * vec[1] + row[2] * vec[2]) % 26
            pt_chars.append(chr(val + 65))
    return "".join(pt_chars)


def crack_hill_2x2(ciphertext):
    sample_len = min(len(ciphertext), 150)
    sample_len = (sample_len // 2) * 2
    ct_sample = ciphertext[:sample_len]

    c_pairs = [(ord(ct_sample[i]) - 65, ord(ct_sample[i+1]) - 65)
               for i in range(0, len(ct_sample), 2)]
    m = len(c_pairs)

    all_v = [(a, b) for a in range(26) for b in range(26)]
    v_out = [[(a * x + b * y) % 26 for x, y in c_pairs] for a, b in all_v]
    v_scores = [sum(LETTER_LOG_P[ch] for ch in row) for row in v_out]

    candidates = []
    for idx1, (a, b) in enumerate(all_v):
        s1 = v_scores[idx1]
        for idx2, (c, d) in enumerate(all_v):
            det = (a * d - b * c) % 26
            if det in COPRIME_26:
                candidates.append((s1 + v_scores[idx2], idx1, idx2))

    candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = candidates[:2500]

    bi_candidates = []
    for _, idx1, idx2 in top_candidates:
        r1, r2 = v_out[idx1], v_out[idx2]
        sc = sum(BIGRAM_TABLE[r1[k]][r2[k]] for k in range(m))
        sc += sum(BIGRAM_TABLE[r2[k]][r1[k+1]] for k in range(m - 1))
        bi_candidates.append((sc + v_scores[idx1] + v_scores[idx2], idx1, idx2))

    bi_candidates.sort(key=lambda x: x[0], reverse=True)
    top_bi = bi_candidates[:150]

    results = []
    for _, idx1, idx2 in top_bi:
        d_mat = [list(all_v[idx1]), list(all_v[idx2])]
        pt_sample = decrypt_text(ct_sample, d_mat, 2)
        sc, words = deep_score(pt_sample)
        results.append((sc, d_mat, pt_sample, words))

    results.sort(key=lambda x: x[0], reverse=True)
    return results


def crack_hill_3x3(ciphertext):
    sample_len = min(len(ciphertext), 240)
    sample_len = (sample_len // 3) * 3
    ct_sample = ciphertext[:sample_len]

    c_blocks = [
        (ord(ct_sample[i]) - 65, ord(ct_sample[i+1]) - 65, ord(ct_sample[i+2]) - 65)
        for i in range(0, len(ct_sample), 3)
    ]

    results = []

    for kw in KEYWORDS_3X3:
        nums = [ord(ch) - 65 for ch in kw]
        k_cand = [nums[0:3], nums[3:6], nums[6:9]]
        d_cand = invert_matrix_3x3(k_cand)
        if d_cand:
            pt = decrypt_text(ct_sample, d_cand, 3)
            sc, words = deep_score(pt)
            results.append((sc, d_cand, pt, words))

    c0 = [b[0] for b in c_blocks]
    c1 = [b[1] for b in c_blocks]
    c2 = [b[2] for b in c_blocks]

    t0 = [[(a * x) % 26 for x in c0] for a in range(26)]
    t1 = [[(b * x) % 26 for x in c1] for b in range(26)]
    t2 = [[(c * x) % 26 for x in c2] for c in range(26)]

    all_rows = []
    for a in range(26):
        t0_a = t0[a]
        for b in range(26):
            t01 = [(x + y) % 26 for x, y in zip(t0_a, t1[b])]
            for c in range(26):
                chars = [(xy + z) % 26 for xy, z in zip(t01, t2[c])]
                sc = sum(LETTER_LOG_P[ch] for ch in chars)
                all_rows.append((sc, (a, b, c)))

    all_rows.sort(key=lambda x: x[0], reverse=True)
    top_rows = all_rows[:70]

    for i in range(len(top_rows)):
        s0, r0 = top_rows[i]
        for j in range(len(top_rows)):
            if i == j:
                continue
            s1, r1 = top_rows[j]
            for k in range(len(top_rows)):
                if k == i or k == j:
                    continue
                s2, r2 = top_rows[k]

                det = (r0[0] * (r1[1] * r2[2] - r1[2] * r2[1])
                     - r0[1] * (r1[0] * r2[2] - r1[2] * r2[0])
                     + r0[2] * (r1[0] * r2[1] - r1[1] * r2[0])) % 26
                if det not in COPRIME_26:
                    continue

                d_cand = [list(r0), list(r1), list(r2)]
                pt_sample = decrypt_text(ct_sample, d_cand, 3)
                sc, words = deep_score(pt_sample)
                results.append((sc, d_cand, pt_sample, words))

    results.sort(key=lambda x: x[0], reverse=True)
    return results


def crack_hill_kpa(ciphertext, crib, dim):
    L = len(ciphertext)
    m = len(crib)
    if m > L:
        logging.error("Fragment tekstu jawnego jest dłuższy niż szyfrogram!")
        return []

    c_nums = [ord(ch) - 65 for ch in ciphertext]
    p_nums = [ord(ch) - 65 for ch in crib]

    num_blocks = L // dim
    blocks = [c_nums[b * dim : (b + 1) * dim] for b in range(num_blocks)]

    results = []

    for offset in range(L - m + 1):
        idx_start = (offset // dim) * dim
        idx_end = ((offset + m + dim - 1) // dim) * dim
        crib_start_in_slice = offset - idx_start

        b_start = (offset + dim - 1) // dim
        b_end = (offset + m) // dim

        if b_end - b_start >= dim:
            p_mat = []
            c_mat = []
            for b in range(b_start, b_start + dim):
                pos = b * dim - offset
                p_mat.append(p_nums[pos : pos + dim])
                c_mat.append(blocks[b])

            p_cols = [[p_mat[r][c] for r in range(dim)] for c in range(dim)]
            c_cols = [[c_mat[r][c] for r in range(dim)] for c in range(dim)]

            p_inv = invert_matrix_2x2(p_cols) if dim == 2 else invert_matrix_3x3(p_cols)
            if p_inv is not None:
                k_cols = [[sum(c_cols[r][k] * p_inv[k][c] for k in range(dim)) % 26
                           for c in range(dim)] for r in range(dim)]
                d_mat = invert_matrix_2x2(k_cols) if dim == 2 else invert_matrix_3x3(k_cols)
                if d_mat is not None:
                    dec_slice = decrypt_text(ciphertext[idx_start : idx_end], d_mat, dim)
                    if dec_slice[crib_start_in_slice : crib_start_in_slice + m] == crib:
                        pt_full_sample = decrypt_text(ciphertext[:min(L, 200)], d_mat, dim)
                        sc, words = deep_score(pt_full_sample)
                        results.append((sc, d_mat, crib, words))
                        continue

        all_rows = [(a, b) for a in range(26) for b in range(26)] if dim == 2 else \
                   [(a, b, c) for a in range(26) for b in range(26) for c in range(26)]

        constraints = [[] for _ in range(dim)]
        for k in range(m):
            abs_pos = offset + k
            b_idx = abs_pos // dim
            r_idx = abs_pos % dim
            constraints[r_idx].append((b_idx, p_nums[k]))

        valid_rows_for_r = []
        possible = True
        for r_idx in range(dim):
            r_cons = constraints[r_idx]
            if not r_cons:
                valid_rows_for_r.append(all_rows[:50])
                continue

            matching = []
            for row in all_rows:
                ok = True
                for b_idx, val in r_cons:
                    b_vec = blocks[b_idx]
                    res = (row[0] * b_vec[0] + row[1] * b_vec[1]) % 26 if dim == 2 else \
                          (row[0] * b_vec[0] + row[1] * b_vec[1] + row[2] * b_vec[2]) % 26
                    if res != val:
                        ok = False
                        break
                if ok:
                    matching.append(row)
            if not matching:
                possible = False
                break
            valid_rows_for_r.append(matching)

        if not possible:
            continue

        if dim == 2:
            for r0 in valid_rows_for_r[0][:25]:
                for r1 in valid_rows_for_r[1][:25]:
                    det = (r0[0] * r1[1] - r0[1] * r1[0]) % 26
                    if det in COPRIME_26:
                        d_mat = [list(r0), list(r1)]
                        dec_slice = decrypt_text(ciphertext[idx_start : idx_end], d_mat, 2)
                        if dec_slice[crib_start_in_slice : crib_start_in_slice + m] == crib:
                            pt_sample = decrypt_text(ciphertext[:min(L, 200)], d_mat, 2)
                            sc, words = deep_score(pt_sample)
                            results.append((sc, d_mat, crib, words))
        else:
            for r0 in valid_rows_for_r[0][:15]:
                for r1 in valid_rows_for_r[1][:15]:
                    for r2 in valid_rows_for_r[2][:15]:
                        det = (r0[0] * (r1[1] * r2[2] - r1[2] * r2[1])
                             - r0[1] * (r1[0] * r2[2] - r1[2] * r2[0])
                             + r0[2] * (r1[0] * r2[1] - r1[1] * r2[0])) % 26
                        if det in COPRIME_26:
                            d_mat = [list(r0), list(r1), list(r2)]
                            dec_slice = decrypt_text(ciphertext[idx_start : idx_end], d_mat, 3)
                            if dec_slice[crib_start_in_slice : crib_start_in_slice + m] == crib:
                                pt_sample = decrypt_text(ciphertext[:min(L, 200)], d_mat, 3)
                                sc, words = deep_score(pt_sample)
                                results.append((sc, d_mat, crib, words))

    results.sort(key=lambda x: x[0], reverse=True)
    unique_results = []
    seen = set()
    for item in results:
        sig = tuple(tuple(r) for r in item[1])
        if sig not in seen:
            seen.add(sig)
            unique_results.append(item)
    return unique_results


def clean_padding(text, dim):
    t = text
    keep_x = {"box", "fox", "six", "tax", "max", "fax", "matrix", "index", "relax", "complex"}
    for _ in range(dim - 1):
        if t.endswith(('x', 'X')) and not any(t.lower().endswith(w) for w in keep_x):
            t = t[:-1]
    return t


def sanitize_input(raw_text):
    lines = raw_text.splitlines()
    valid_lines = [line for line in lines if not line.strip().startswith("---")]
    cleaned = "".join(valid_lines)
    return "".join(re.findall(r"[A-Za-z]", cleaned)).upper()


def detect_language(plaintext):
    pt_up = plaintext.upper()
    pl_matches = [w for w in VOCAB_PL if w in pt_up]
    en_matches = [w for w in VOCAB_EN if w in pt_up]

    pl_score = sum(len(w) ** 2 for w in pl_matches)
    en_score = sum(len(w) ** 2 for w in en_matches)

    if pl_score > en_score:
        return "PL", "Język polski"
    elif en_score > pl_score:
        return "EN", "Język angielski"
    else:
        counts = Counter(pt_up)
        n = len(pt_up) if pt_up else 1
        dot_pl = sum((counts.get(ch, 0) / n) * LANG_FREQ_PL[ch] for ch in ALPHABET)
        dot_en = sum((counts.get(ch, 0) / n) * LANG_FREQ_EN[ch] for ch in ALPHABET)
        if dot_pl >= dot_en:
            return "PL", "Język polski"
        else:
            return "EN", "Język angielski"


def compute_ciphertext_vs_language_stats(ciphertext, lang_code, lang_name):
    n = len(ciphertext)
    if n == 0:
        return ""

    uni_counts = Counter(ciphertext)
    bi_counts = Counter(ciphertext[i:i+2] for i in range(n - 1))
    tri_counts = Counter(ciphertext[i:i+3] for i in range(n - 2))
    ic = sum(c * (c - 1) for c in uni_counts.values()) / (n * (n - 1)) if n > 1 else 0.0

    target_freq = LANG_FREQ_PL if lang_code == "PL" else LANG_FREQ_EN
    header_lang = "J. pol: Lit." if lang_code == "PL" else "J. ang: Lit."
    header_pct = "PL %" if lang_code == "PL" else "EN %"

    sorted_cipher = sorted(
        ALPHABET, 
        key=lambda ch: (uni_counts.get(ch, 0), -ord(ch)), 
        reverse=True
    )
    sorted_lang = sorted(
        target_freq.items(), 
        key=lambda item: item[1], 
        reverse=True
    )

    lines = []
    lines.append("=" * 66)
    lines.append("  STATYSTYKI SZYFROGRAMU W PORÓWNANIU Z WYKRYTYM JĘZYKIEM")
    lines.append("=" * 66)
    lines.append(f"Wykryty język tekstu jawnego: {lang_name} ({lang_code})")
    lines.append(f"Długość analizowanego szyfrogramu: {n} znaków")
    lines.append(f"Indeks Koincydencji (IC) szyfrogramu: {ic:.5f}")
    lines.append("  * Wartość referencyjna dla języka naturalnego: ~0.06500")
    lines.append("  * Wartość referencyjna dla tekstu losowego:    ~0.03846")
    lines.append("  * Wniosek: Szyfr Hilla rozprasza statystyki (dyfuzja).\n")

    lines.append("-" * 66)
    lines.append(f"{'Lp.':^5}|{'Szyfr: Lit.':^13}|{'Liczba':^8}|{'Szyfr %':^10}|{header_lang:^15}|{header_pct:^10}")
    lines.append("-" * 66)

    for i in range(26):
        ch_c = sorted_cipher[i]
        cnt_c = uni_counts.get(ch_c, 0)
        pct_c = (cnt_c / n) * 100.0 if n > 0 else 0.0

        ch_l, pct_l = sorted_lang[i]

        lines.append(
            f" {i+1:2d}. |      {ch_c:1s}      | {cnt_c:6d} | {pct_c:6.2f}% |       {ch_l:1s}       | {pct_l:6.2f}% "
        )

    lines.append("-" * 66)

    lines.append("\n" + "=" * 66)
    lines.append("  STATYSTYKA N-GRAMÓW W SZYFROGRAMIE")
    lines.append("=" * 66)
    lines.append("15 najczęstszych digramów (2-gramów) w szyfrogramie:")
    bi_str = "  " + ", ".join(f"{bg}: {cnt}" for bg, cnt in bi_counts.most_common(15))
    lines.append(bi_str)
    if lang_code == "PL":
        lines.append("  (Typowe digramy j. polskiego: IE, PO, PR, ZY, ZE, NA, CO, OD, DO)")
    else:
        lines.append("  (Typowe digramy j. angielskiego: TH, HE, IN, ER, AN, RE, ON, AT, EN)")

    lines.append("\n15 najczęstszych trigramów (3-gramów) w szyfrogramie:")
    tri_str = "  " + ", ".join(f"{tg}: {cnt}" for tg, cnt in tri_counts.most_common(15))
    lines.append(tri_str)
    if lang_code == "PL":
        lines.append("  (Typowe trigramy j. polskiego: NIE, PRZ, RZE, SZY, CIE, STA, WIE)")
    else:
        lines.append("  (Typowe trigramy j. angielskiego: THE, AND, ING, ENT, ION, HER, FOR)")
    lines.append("=" * 66 + "\n")

    return "\n".join(lines)


def generate_digram_mapping_table(enc_col, dim, lang_code):
    lines = []
    lines.append("=" * 66)
    lines.append("  DZIAŁANIE KLUCZA: TABELA PRZEKSZTAŁCEŃ DIGRAMÓW")
    lines.append("=" * 66)
    lines.append("Szyfr Hilla przekształca całe bloki znaków (szyfr poligramowy).")
    lines.append("Poniższa tabela przedstawia, jak klucz szyfrujący K zamienia")
    lines.append(f"najczęstsze digramy wykrytego języka ({lang_code}) na szyfrogram:")
    lines.append("-" * 66)
    lines.append(f"{'Tekst jawny (P)':^18} ---> {'Szyfrogram (C)':^18} | {'Deszyfrowanie':^22}")
    lines.append("-" * 66)

    sample_digrams = TOP_DIGRAMS_PL if lang_code == "PL" else TOP_DIGRAMS_EN

    if dim == 2:
        for bg in sample_digrams:
            p0, p1 = ord(bg[0]) - 65, ord(bg[1]) - 65
            c0 = (enc_col[0][0] * p0 + enc_col[0][1] * p1) % 26
            c1 = (enc_col[1][0] * p0 + enc_col[1][1] * p1) % 26
            c_bg = chr(c0 + 65) + chr(c1 + 65)
            lines.append(f"       {bg}           --->        {c_bg}         |    {c_bg} ---> {bg}")
    else:
        sample_trigrams = ["NIE", "PRZ", "RZE", "SZY", "CIE", "STA", "WIE", "DLA"] if lang_code == "PL" else \
                          ["THE", "AND", "ING", "ENT", "ION", "HER", "FOR", "THA"]
        lines.append("(Dla macierzy 3x3 przedstawiono przekształcenie trigramów):")
        for tg in sample_trigrams:
            p0, p1, p2 = ord(tg[0]) - 65, ord(tg[1]) - 65, ord(tg[2]) - 65
            c0 = (enc_col[0][0] * p0 + enc_col[0][1] * p1 + enc_col[0][2] * p2) % 26
            c1 = (enc_col[1][0] * p0 + enc_col[1][1] * p1 + enc_col[1][2] * p2) % 26
            c2 = (enc_col[2][0] * p0 + enc_col[2][1] * p1 + enc_col[2][2] * p2) % 26
            c_tg = chr(c0 + 65) + chr(c1 + 65) + chr(c2 + 65)
            lines.append(f"      {tg}          --->       {c_tg}        |   {c_tg} ---> {tg}")
    lines.append("=" * 66)
    return "\n".join(lines)


def main():
    setup_logger()
    print("=" * 66)
    print("PROGRAM KRYPTOANALIZY SZYFRU HILLA (ALFA26)")
    print("=" * 66)

    print("Wybierz tryb ataku:")
    print("  1. Atak z samym szyfrogramem (COA - Ciphertext-Only Attack)")
    print("  2. Atak ze znanym tekstem jawnym / fragmentem (KPA - Known-Plaintext Attack)")
    choice_mode = input("Twój wybór (1/2, domyślnie 1): ").strip()
    is_kpa = (choice_mode == "2")
    logging.info(f"Wybrano tryb: {'KPA (ze znanym tekstem)' if is_kpa else 'COA (sam szyfrogram)'}.")

    file_path = input("\nPodaj ścieżkę do pliku z szyfrogramem: ").strip().strip('"\'')
    if not os.path.exists(file_path):
        logging.error(f"Plik nie istnieje: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    ciphertext = sanitize_input(raw_text)
    n = len(ciphertext)
    logging.info(f"Odczytano szyfrogram o długości {n} znaków.")

    if n % 2 != 0 and n % 3 != 0:
        logging.error("Długość tekstu nie pozwala na podział na bloki 2 ani 3.")
        return

    crib = ""
    if is_kpa:
        crib_in = input("Podaj fragment tekstu jawnego (lub ścieżkę do pliku z nim): ").strip().strip('"\'')
        if os.path.exists(crib_in):
            with open(crib_in, "r", encoding="utf-8") as f:
                crib_text = f.read()
        else:
            crib_text = crib_in

        crib = sanitize_input(crib_text)
        if not crib:
            logging.error("Nie podano żadnego fragmentu tekstu jawnego!")
            return
        logging.info(f"Wprowadzono znany fragment ({len(crib)} znaków): '{crib}'")

    logging.info("Rozpoczęto analizę kryptoanalityczną...")
    if n % 2 == 0 and n % 3 != 0:
        dim = 2
        logging.info("Automatycznie wybrano wymiar macierzy: 2x2.")
        top_results = crack_hill_kpa(ciphertext, crib, 2) if is_kpa else crack_hill_2x2(ciphertext)
    elif n % 3 == 0 and n % 2 != 0:
        dim = 3
        logging.info("Automatycznie wybrano wymiar macierzy: 3x3.")
        top_results = crack_hill_kpa(ciphertext, crib, 3) if is_kpa else crack_hill_3x3(ciphertext)
    else:
        logging.info("Długość podzielna przez 2 i 3. Sprawdzanie obu wariantów...")
        if is_kpa:
            res2 = crack_hill_kpa(ciphertext, crib, 2)
            res3 = crack_hill_kpa(ciphertext, crib, 3)
        else:
            res2 = crack_hill_2x2(ciphertext)
            res3 = crack_hill_3x3(ciphertext)

        sc2 = res2[0][0] if res2 else -float('inf')
        sc3 = res3[0][0] if res3 else -float('inf')
        if sc2 >= sc3 and res2:
            dim = 2
            top_results = res2
        else:
            dim = 3
            top_results = res3

    if not top_results:
        logging.error("Nie udało się odnaleźć klucza spełniającego podane kryteria.")
        return

    best_score, best_d, _, best_words = top_results[0]

    full_plaintext = decrypt_text(ciphertext, best_d, dim)
    final_plaintext = clean_padding(full_plaintext, dim).lower()

    # Automatyczne wykrycie języka tekstu jawnego (PL lub EN)
    lang_code, lang_name = detect_language(final_plaintext)
    logging.info(f"Wykryty język wiadomości: {lang_name} ({lang_code}).")

    suffix = f"_{dim}_kpa.txt" if is_kpa else f"_{dim}.txt"
    file_dec = os.path.join(DIR_OUT, f"odszyfrowane{suffix}")
    file_key_mat = os.path.join(DIR_OUT, f"klucz_macierz{suffix}")
    file_key_alf = os.path.join(DIR_OUT, f"klucz_alfa{suffix}")
    file_stats = os.path.join(DIR_OUT, f"statystyki{suffix}")

    print("\n" + "=" * 66)
    print(f"NAJLEPSZE ROZWIĄZANIA DLA KLUCZA {dim}x{dim} ({'KPA' if is_kpa else 'COA'}):")
    print(f"Wykryty język: {lang_name} ({lang_code})")
    for rank, (sc, d_cand, _, words) in enumerate(top_results[:5], 1):
        detected = ", ".join(words) if words else "brak w słowniku"
        sample_pt = clean_padding(decrypt_text(ciphertext[:min(n, 70)], d_cand, dim), dim).lower()
        print(f" {rank}. [{sc:6.1f} pkt] -> {sample_pt}...")
        print(f"    Rozpoznane słowa: [{detected}]")
    print("=" * 66 + "\n")

    enc_col = invert_matrix_2x2(best_d) if dim == 2 else invert_matrix_3x3(best_d)
    enc_row = [[enc_col[r][c] for r in range(dim)] for c in range(dim)]

    key_alf_col = "".join(chr(val + 65) for row in enc_col for val in row)
    key_alf_row = "".join(chr(val + 65) for row in enc_row for val in row)

    # Generowanie statystyk porównawczych dla TYLKO wykrytego języka
    stats_text = compute_ciphertext_vs_language_stats(ciphertext, lang_code, lang_name)
    digram_table_text = generate_digram_mapping_table(enc_col, dim, lang_code)

    # Zapis statystyk do pliku
    with open(file_stats, "w", encoding="utf-8") as f:
        f.write(stats_text)
        f.write(digram_table_text + "\n")

    # Zapis odszyfrowanej wiadomości
    with open(file_dec, "w", encoding="utf-8") as f:
        f.write(final_plaintext + "\n")

    # Zapis klucza macierzowego z tabelą przekształceń
    with open(file_key_mat, "w", encoding="utf-8") as f:
        f.write(f"Klucz szyfrujący {dim}x{dim} (konwencja kolumnowa C = K * P mod 26):\n")
        for row in enc_col:
            f.write("  " + " ".join(f"{val:2d}" for val in row) + "\n")
        f.write(f"\nKlucz szyfrujący {dim}x{dim} (konwencja wierszowa C = P * K mod 26):\n")
        for row in enc_row:
            f.write("  " + " ".join(f"{val:2d}" for val in row) + "\n")
        f.write("\n" + digram_table_text + "\n")

    with open(file_key_alf, "w", encoding="utf-8") as f:
        f.write(f"Klucz literowy (konwencja kolumnowa): {key_alf_col}\n")
        f.write(f"Klucz literowy (konwencja wierszowa):  {key_alf_row}\n")

    logging.info(f"Odszyfrowano pomyślnie cały plik ({len(final_plaintext)} znaków).")
    logging.info(f"Początek wiadomości: {final_plaintext[:80]}...")
    logging.info(f"Zapisano odszyfrowaną wiadomość do: {file_dec}")
    logging.info(f"Zapisano klucz macierzowy do: {file_key_mat}")
    logging.info(f"Zapisano klucz literowy do: {file_key_alf}")
    logging.info(f"Zapisano statystyki porównawcze do: {file_stats}")
    logging.info("Zakończono sukcesem.")


if __name__ == "__main__":
    main()