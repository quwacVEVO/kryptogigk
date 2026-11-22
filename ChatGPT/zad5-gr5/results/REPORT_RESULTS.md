# Wyniki odtwarzalnego przebiegu

## Scenariusz główny

- `K = 200`, przedział `[10000, 59999]`.
- LFSR: `n=16`, odczepy 0-based `(0, 2, 3, 5)`, ziarno `0000000000000001`.
- LCG: `m=65536`, `a=5`, `c=1`, `x0=20226`.
- Mapowanie: rejection sampling, zatem bez obciążenia wynikającego z prostego modulo.
- Czasy obejmują wyłącznie pojedyncze wywołanie testu i są mierzone `perf_counter_ns`.

## Generatory

| generator | K | unique_count | duplicate_occurrences | colliding_pairs | state_preperiod | state_period |
| --- | --- | --- | --- | --- | --- | --- |
| LFSR | 200 | 200 | 0 | 0 | 0 | 65535 |
| LCG | 200 | 200 | 0 | 0 | 0 | 65536 |

`duplicate_occurrences = K - liczba różnych wartości`. `colliding_pairs` to suma `c*(c-1)/2` po licznościach każdej wartości. Okres dotyczy pełnego stanu generatora, a nie ciągu po mapowaniu.

## Czasy testów pierwszości

| source | method | measurements | min_ns | max_ns | mean_ns | median_ns |
| --- | --- | --- | --- | --- | --- | --- |
| LCG | Fermat | 200 | 180 | 195125 | 3304.89 | 616.0 |
| LCG | Miller-Rabin | 200 | 160 | 12489 | 2215.67 | 360.5 |
| LCG | dzielenie_przez_pierwsze | 200 | 3295 | 164298 | 8029.79 | 5388.0 |
| LFSR | Fermat | 200 | 170 | 36445 | 2210.2 | 280.5 |
| LFSR | Miller-Rabin | 200 | 170 | 54893 | 2384.7 | 255.0 |
| LFSR | dzielenie_przez_pierwsze | 200 | 3305 | 34572 | 5630.68 | 5213.0 |

## Błędne decyzje względem dokładnego dzielenia przez liczby pierwsze

| source | method | measurements | false_primes | false_composites |
| --- | --- | --- | --- | --- |
| LCG | Fermat | 200 | 0 | 0 |
| LCG | Miller-Rabin | 200 | 0 | 0 |
| LCG | dzielenie_przez_pierwsze | 200 | 0 | 0 |
| LFSR | Fermat | 200 | 0 | 0 |
| LFSR | Miller-Rabin | 200 | 0 | 0 |
| LFSR | dzielenie_przez_pierwsze | 200 | 0 | 0 |

Poprawnie zaimplementowane testy Fermata i Millera-Rabina nie powinny odrzucać liczb pierwszych, dlatego oczekiwano zera w kolumnie `false_composites`. Testy probabilistyczne nie są dowodem pierwszości; brak błędów w tym ograniczonym zbiorze nie gwarantuje ich braku poza nim.

## Wpływ liczby iteracji Millera-Rabina

| iterations | measurements | mean_ns | median_ns | false_primes | false_composites |
| --- | --- | --- | --- | --- | --- |
| 1 | 400 | 1495.91 | 235.5 | 0 | 0 |
| 3 | 400 | 1927.87 | 240.5 | 0 | 0 |
| 5 | 400 | 2284.42 | 231.0 | 0 | 0 |
| 10 | 400 | 3117.95 | 235.5 | 0 | 0 |

## Interpretacja

Dokładny test dzielenia jest punktem odniesienia i dla tego małego zakresu pozostaje praktyczny. Fermat może zostać oszukany przez pseudopierwsze i liczby Carmichaela, co pokazują testy jednostkowe z liczbą 561. Miller-Rabin daje lepszy kompromis dla większych liczb, lecz jego wynik nadal należy opisywać jako prawdopodobną pierwszość. Różnice bardzo krótkich czasów są podatne na szum systemowy; surowe pomiary zachowano w `primality_measurements.csv`.
