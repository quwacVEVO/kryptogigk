# Skrót przebiegu (plik generowany przez run_all.py)

* data uruchomienia (czas lokalny): 2026-11-25 22:32:41
* czas całego przebiegu: 10.6 s
* testy jednostkowe: 117 testów, wynik OK (błędów 0, niezaliczonych 0)
* kontrola błędów: 28 wymuszonych przypadków, nieodrzuconych 0

## LFSR
* parametry: LFSR n=16 p=1011010000000000 (odczepy j=0,2,3,5) f(x)=x^16 + x^5 + x^3 + x^2 + 1 ziarno=44257 (0b1010110011100001)
* okres stanu 65535 (ogon 0), okres ciągu wartości 12801
* kolizje w K=200: 18 (różnych 182)

## LCG
* parametry: LCG m=65536 a=25173 c=13849 x0=2026
* okres stanu 65536 (ogon 0), okres ciągu wartości 65000
* kolizje w K=200: 22 (różnych 178)

## Testy pierwszości (scenariusz główny)
* LFSR / dzielenie: pomiarów 200, min 250 ns, mediana 320 ns, średnia 370 ns, max 2605 ns
* LFSR / Fermat: pomiarów 200, min 200 ns, mediana 276 ns, średnia 1489 ns, max 10069 ns
* LFSR / Miller-Rabin: pomiarów 200, min 210 ns, mediana 250 ns, średnia 1498 ns, max 6332 ns
* LCG / dzielenie: pomiarów 200, min 270 ns, mediana 336 ns, średnia 394 ns, max 3787 ns
* LCG / Fermat: pomiarów 200, min 200 ns, mediana 802 ns, średnia 1588 ns, max 6272 ns
* LCG / Miller-Rabin: pomiarów 200, min 210 ns, mediana 796 ns, średnia 1619 ns, max 6202 ns
* LFSR / Fermat: pseudopierwszych 0, pseudozłożonych 0 (unikalnych 182, pierwszych 29)
* LFSR / Miller-Rabin: pseudopierwszych 0, pseudozłożonych 0 (unikalnych 182, pierwszych 29)
* LCG / Fermat: pseudopierwszych 0, pseudozłożonych 0 (unikalnych 178, pierwszych 36)
* LCG / Miller-Rabin: pseudopierwszych 0, pseudozłożonych 0 (unikalnych 178, pierwszych 36)

## Pliki
* `results/lcg_numbers_main.txt` - lcg_main
* `results/lcg_numbers_raw_unique.txt` - lcg_raw_unique
* `results/lcg_numbers_unique.txt` - lcg_unique
* `results/lfsr_numbers_main.txt` - lfsr_main
* `results/lfsr_numbers_raw_unique.txt` - lfsr_raw_unique
* `results/lfsr_numbers_unique.txt` - lfsr_unique
* `results/lfsr_analysis.md`
* `results/lcg_analysis.md`
* `results/primality_analysis.md`
* `results/error_handling.md`
* `results/benchmark.json`
* `results/environment.txt`
