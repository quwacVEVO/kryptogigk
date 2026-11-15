# Wymagania, harmonogram i deadline'y - Laboratorium 4

- **Wymagania:** 
1. znalezienie liczby a dowolną metodą i opisanie podjętych kroków w sprawozdaniu;
2. weryfikacja wyniku (sprawdzenie, że $g^a \equiv h \pmod{p}$) oraz zapisanie czasu pracy;
3. użycie minimum dwóch metod (np. atak siłowy, baby-step giant-step, Pohlig–Hellman, rho Pollarda);
4. porównanie metod, ich szybkości oraz dokładności.

---

### Grupa 1 - `zad4-gr1`

**Zestaw:** Z1. p = 37781, g = 3, h = 24581

---

### Grupa 2 - `zad4-gr2`

**Zestaw:** Z2. p = 100000127, g = 5, h = 5910514

---

### Grupa 3 - `zad3-gr3`

**Zestaw:** Z3. p = 1000000000547, g = 2, h = 514634099897

---

### Grupa 4 - `zad3-gr4`

**Zestaw:** Z4. p = 33815155531460793491, g = 19, h = 30073559734842340154

---

### Grupa 5 - `zad3-gr5`

Dokonanie próby ataku na protokół Diffiego-Hellmana dla wszystkich zestawów p, g, h, na których pracują grupy 1-4. 
Testowanie i porównanie różnych modeli w tych samych przypadkach; dokumentowanie promptów, oczekiwanego formatu odpowiedzi, sposobu weryfikacji wyników i przebiegu pracy.

---

## Harmonogram

**Wersje końcowe - do 19.11.2026 na zajęciach**

- Grupy 2-4: przygotowane co najmniej dwie metody ataku dla swojego zestawu
- Grupa 5: tak jak grupy 2-4, jednak najlepiej z wykorzystaniem wszystkich 4 metod, jako że zestawy są skonstruowane tak, że niektóre metody są o wiele bardziej optymalne dla konkretnego zestawu.

**Sprawozdania - do 22.11.2026, godz. 23:59**

---

## Inne uwagi

- Sugerowane jest, aby każda grupa podzieliła swoją pracę tak, by każda osoba z grupy pracowała nad inną metodą 
- Wymagane jest zaimplementowanie w każdej metodzie ataku czasu działania algorytmu.
- Nie jest wymagane skuteczne złamanie każdego przypadku. Należy przedstawić rzeczywiście wykonane próby, wyniki, ograniczenia i przyczyny niepowodzeń; również wskazać, jakich prób nie podjęto.
- Każdy członek grupy zapisuje czas pracy przy poszczególnych zadaniach; w sprawozdaniu należy te roboczogodziny zsumować.
- Wnioski powinny dotyczyć trudności, błędów, poprawek i sposobów weryfikacji. Informacje porównujące pracę samodzielną z AI powinny obejmować jakość, czas, konieczne poprawki i poziom kontroli nad wynikiem.

<sub>W przypadku pytań lub problemów prosimy o kontakt z grupą koordynującą.</sub>