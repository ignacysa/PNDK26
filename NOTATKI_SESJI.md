# Notatki z sesji roboczych

Przebieg pracy nad projektem, żeby w kolejnej sesji szybko wrócić do kontekstu. Ustalenia są w `CLAUDE.md`, research w `RESEARCH.md`.

---

## Sesja 1 — 2026-10-24

### Co zrobiliśmy (po kolei)
1. **Porządki.** Repozytorium przeniesione z Pulpitu do `~/Projekty/PNDK26`. Wyczyściliśmy stare pliki: dane KDPW, skrypt i research z commitu `c34ca49`. Zostały dwa pliki: `CLAUDE.md` (ustalenia) i `RESEARCH.md` (notatka robocza).
2. **Struktura prezentacji.** 10 slajdów w limicie 7,5–12,5 min, zapisana w `CLAUDE.md`.
3. **Przegląd zharmonizowanych danych międzynarodowych (20 lat).** Wniosek: nie ma zharmonizowanej międzynarodowo liczby rachunków ani aktywnych inwestorów. Najlepsze dane zharmonizowane:
   - rachunki finansowe Eurostatu (akcje i fundusze gospodarstw, % PKB, 2004–2025),
   - ankieta ISOC (% osób inwestujących przez internet, 2016–2025, zerwanie w 2020 r.),
   - HFCS ma Polskę tylko w falach 2014 i 2017.
4. **Decyzja użytkownika o zmiennych.** Zmienna zależna: liczba inwestorów, najlepiej *aktywnych*. Zmienne objaśniające: dochód, inflacja, roczne stopy zwrotu z giełdy, stopa procentowa banku centralnego.
5. **Zmienna zależna zatwierdzona:** aktywne rachunki na rynku akcji GPW, półrocznie od I 2003 do I 2026, z raportów GPW „Udział inwestorów w obrotach”. Szereg jest kompletny i sprawdzony (`data/gpw_aktywne_rachunki_pl.csv`). Punkty charakterystyczne:
   - szczyt 412 tys. w I 2010 (IPO PZU),
   - dołek 131 tys. w II 2019,
   - rekord 444 tys. w I 2026 (12,2 na 1000 mieszkańców).
6. **Porównanie z innymi krajami (na 1000 mieszkańców).** Odpowiednik aktywności istnieje we Francji (AMF), Korei (KOFIA) i Indiach (NSE). W Niemczech, Szwecji i Finlandii są tylko liczby posiadaczy akcji.
7. **Kraje postransformacyjne (zasada użytkownika: porównujemy się z nimi).** Wyniki:
   - **Rumunia:** aktywne rachunki ASF z definicją niemal identyczną jak GPW (≥1 transakcja w 6 mies.), kwartalnie 2015–2026. Najlepszy odpowiednik.
   - **Litwa:** aktywni inwestorzy według Banku Litwy, 2019–2025.
   - **Węgry:** fundusz kompensacyjny BEVA, inwestorzy chronieni, 2002–2025.
   - **Bułgaria:** fundusz FKI, klienci chronieni, 2008–2025.
   - **Estonia:** posiadacze papierów z giełdy w Tallinie, punkty 2019–2026.
   - **Słowacja:** klienci firm zrzeszonych w AOCP, 2 punkty.
   - **Czechy:** 1 punkt (ok. 1,5 mln klientów firm inwestycyjnych).
   - **Chorwacja:** tylko dane pośrednie.
   - **Słowenia, Łotwa:** brak danych.
8. **Subagent** zebrał szeregi RO i LT (Wayback Machine do obejścia blokad stron ASF i Banku Litwy). Użytkownik zatrzymał go przed raportem końcowym, ale pliki i skrypty są kompletne i sprawdzone (CSV poprawny, skrypty się kompilują).

### Najważniejsze obserwacje do prezentacji (wstępne)
- Aktywne rachunki w Polsce silnie reagują na koniunkturę giełdową, co dobrze rokuje dla modelu z czterema zmiennymi.
- Na tle regionu Polska ma wysoki poziom aktywnych rachunków (12 na 1000), ale Rumunia rośnie szybciej (×10 od 2019 r.).
- Zharmonizowane miary Eurostatu (ISOC, rachunki finansowe) pokazują Polskę *nisko* i prawie bez wzrostu. Ta rozbieżność z danymi GPW jest otwarta i może być wątkiem we wnioskach.

### Struktura repozytorium
- `CLAUDE.md`: ustalenia; `RESEARCH.md`: research i otwarte decyzje; `NOTATKI_SESJI.md`: ten plik.
- `data/`: pliki wynikowe CSV (z kolumną źródła i statusu weryfikacji); `data/reczne/`: ręcznie zebrane wartości; `data/eurostat/`: dane Eurostatu; `data/raw/`: surowe PDF-y (GPW, ASF, FCI, Bank Litwy, BEVA, FKI).
- `scripts/`: każdy skrypt pobierający lub przetwarzający dane (zasada użytkownika: archiwizujemy wszystkie skrypty). Zależność zewnętrzna tylko `pypdf` (`requirements.txt`). Kolejność odświeżania:
  1. `gpw_aktywne_rachunki.py`, `eurostat_dane.py`, `wegry_beva.py`, `rumunia_asf.py`, `rumunia_fci.py`, `litwa_lb.py` (`bulgaria_fki.py` tylko wypisuje zdania z raportów),
  2. na końcu `porownanie_na_1000.py`, który dopisuje ludność i wskaźnik na 1000 mieszkańców do plików z `data/reczne/`.

### Uwagi techniczne
- Strony GPW, Banku Litwy, ASF, Nasdaq Baltic, finreport.sk i SII blokują pobieranie skryptem. Obejścia: Wayback Machine (`https://web.archive.org/web/<rok>id_/<url>`), ręczne pobranie w przeglądarce. W tej sesji nie było narzędzi przeglądarki.
- Do PDF-ów potrzebny jest `pypdf` (`pip install -r requirements.txt`).
- Statusy wartości: `zweryfikowane` (odczytane ze źródła) i `z wyszukiwania` (prasa). Przed użyciem na slajdzie potwierdzać wartości „z wyszukiwania”.

### Otwarte decyzje i następne kroki
1. Konstrukcja: sama Polska (szereg czasowy) czy Polska + slajd porównawczy z regionem?
2. Normalizacja: na 1000 mieszkańców czy na 1000 dorosłych?
3. Miara dochodu (realne wynagrodzenie czy PKB per capita) i okres (pełny szereg czy równe 20 lat).
4. Zebrać zmienne objaśniające dla Polski półrocznie: WIG (stopa zwrotu), stopa referencyjna NBP, CPI, wynagrodzenia GUS. Napisać skrypt budujący zbiór do modelu.
5. Potwierdzić u GPW definicję „aktywnego rachunku” i ciągłość metodologii (możliwa zmiana ok. 2007 r., anomalia II 2020).
6. Wyjaśnić rozbieżność ISOC/rachunki finansowe vs GPW.
7. Tytuł jest nadal roboczy.
