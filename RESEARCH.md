# RESEARCH — notatka robocza

**Ostatnia aktualizacja:** 2026-10-24

Tu trzymamy opcje, wyniki researchu i otwarte decyzje. Nic w tym pliku nie jest ostateczne. Po decyzji użytkownika przenosimy ustalenie do `CLAUDE.md`.

**Statusy:** `zweryfikowane` = sprawdzone u źródła (API, raport) · `z wyszukiwania` = z wyników wyszukiwania lub prasy, nie sprawdzone u źródła · `do sprawdzenia` = otwarte

---

## 1. Tytuł i pytanie badawcze

**Pytanie (propozycja):** jak dochód, inflacja, stopy zwrotu z giełdy i stopa procentowa banku centralnego wpływają na liczbę aktywnych inwestorów indywidualnych?

**Propozycje tytułu:**
- „Makroekonomiczne determinanty aktywności inwestorów indywidualnych w Polsce w latach 2003–2026”
- „Co skłania Polaków do inwestowania na giełdzie? Dochód, inflacja, stopy procentowe i koniunktura giełdowa a liczba aktywnych inwestorów”

## 2. Konstrukcja badania — warianty

| Wariant | Opis | Obserwacje | Plusy | Minusy |
|---|---|---|---|---|
| **A. Polska, szereg czasowy (rekomendowany jako główny)** | Aktywne rachunki GPW (półrocznie) objaśniane 4 zmiennymi dla Polski | 46 półroczy (II 2003 – I 2026) | Najlepsza dostępna miara *aktywnych* inwestorów, 20+ lat, wszystkie zmienne objaśniające łatwo dostępne | Jeden kraj |
| **B. Panel krajów UE** | % osób kupujących lub sprzedających papiery wartościowe przez internet (Eurostat ISOC) objaśniany tymi samymi zmiennymi | ok. 10 lat × 10–12 krajów | Zharmonizowane | Tylko 2016–2025, zerwanie serii w 2020 r., miara ankietowa |
| **C. A + slajd porównawczy** | A jako główna analiza, plus jeden slajd „Polska na tle innych krajów” z liczbą aktywnych inwestorów na 1000 mieszkańców (sekcja 4) | — | Daje oba wątki bez budowania panelu | Porównanie tylko opisowe, bo definicje się różnią |

## 3. Zmienna zależna — aktywne rachunki GPW

### 3.1. Dane — `zweryfikowane`
Plik: `data/gpw_aktywne_rachunki_pl.csv`, generowany przez `scripts/gpw_aktywne_rachunki.py` z raportów w `data/raw/gpw/`.

| Kolumna | Opis | Źródło |
|---|---|---|
| `aktywne_rachunki_akcje` | Liczba aktywnych rachunków na rynku akcji w półroczu | GPW, tabela „Rachunki internetowe / Aktywne rachunki – akcje / Liczba wszystkich rachunków obsługiwanych przez CG” |
| `aktywne_pct_rachunkow_CG` | Aktywne rachunki jako % rachunków członków giełdy (CG) | jw. |
| `rachunki_CG` | Wszystkie rachunki obsługiwane przez członków giełdy | jw. |
| `rachunki_KDPW` | Wszystkie rachunki maklerskie według KDPW | jw. |
| `rachunki_internetowe` | Rachunki internetowe | jw. |
| `ludnosc_1_stycznia` | Ludność Polski na 1 stycznia danego roku (dla 2026 r. użyto 2025 r., najnowszego dostępnego) | Eurostat `demo_pjan` |
| `aktywne_na_1000_mieszk`, `rachunki_KDPW_na_1000_mieszk` | Wartość / ludność × 1000 | obliczenie |

Pliki źródłowe:
- I 2003 – II 2015: https://www.gpw.pl/pub/GPW/analizy/Udzial_inwestorow_2019.pdf
- I 2016 – I 2026: https://www.gpw.pl/pub/GPW/analizy/Udzial_inwestorow_1H2026.pdf
- Kontrola: wartości z lat 2003–2013 zgadzają się z https://www.gpw.pl/pub/GPW/analizy/badanie_inwestorow_dane_na_www20.pdf, a lata 2016–2019 są identyczne w obu raportach. Skrypt sprawdza też, czy podany w raporcie % zgadza się z ilorazem liczb.

Wybrane punkty:

| Półrocze | Aktywne rachunki | na 1000 mieszk. | % rachunków | Kontekst |
|---|---|---|---|---|
| II 2003 | 211 732 | 5,5 | 23 | początek szeregu |
| I 2010 | 412 015 | 10,8 | 31 | szczyt hossy, IPO PZU |
| I 2016 | 140 586 | 3,7 | 10 | minimum historyczne |
| II 2019 | 131 427 | 3,5 | 11 | dołek przed pandemią |
| II 2020 | 255 598 | 6,7 | 21 | „pandemiczny” napływ inwestorów |
| II 2025 | 377 796 | 10,4 | 15 | hossa 2025 |
| I 2026 | 444 122 | 12,2 | 15 | nowy rekord |

### 3.2. Plan rozwoju statystyki
1. **Weryfikacja definicji.** Według prasy aktywny rachunek to taki, z którego w półroczu złożono co najmniej jedno zlecenie na rynku akcji GPW. W raportach nie ma tej definicji (`do sprawdzenia`: zapytać GPW, dział analiz / IR). Sprawdzić też:
   - czy do ok. 2007 r. dane pochodziły z ankiety wśród członków giełdy, a później z systemu transakcyjnego (możliwe zerwanie szeregu),
   - przypis „bez danych zdalnych CG” (zdalni członkowie giełdy, czyli zagraniczni brokerzy, mogą nie być ujęci),
   - anomalię II 2020: rachunki CG spadły do 1,20 mln przy 1,33 mln w KDPW.
2. **Lepsza normalizacja.** Zamiast całej ludności użyć ludności 18+ (Eurostat `demo_pjangroup`), bo rachunek może mieć tylko dorosły. Druga miara: % wszystkich rachunków, czyli intensywność aktywności.
3. **Przekształcenia do modelu.** Logarytm liczby aktywnych rachunków; zmiana półroczna lub r/r; ewentualnie wyrównanie sezonowe, jeśli I i II półrocze systematycznie się różnią.
4. **Dopasowanie zmiennych objaśniających do półroczy.** Średnia z półrocza dla inflacji i stopy NBP, stopa zwrotu WIG za półrocze lub kroczące 12 mies., dochód kwartalny uśredniony do półrocza.
5. **Zmienne pomocnicze z tych samych raportów GPW.** Udział inwestorów indywidualnych w obrotach akcjami i wartość ich obrotów. Mogą posłużyć jako alternatywna zmienna zależna w teście odporności.
6. **Ograniczenia do opisania na slajdzie:**
   - rachunek ≠ osoba (jedna osoba może mieć kilka rachunków, a aplikacje typu XTB to ułatwiają),
   - liczone są tylko transakcje na GPW, bez akcji zagranicznych, ETF-ów na giełdach zagranicznych i CFD,
   - koniunkturę na GPW mocno kształtują pojedyncze zdarzenia (IPO PZU 2010, JSW 2011, Allegro 2020, Żabka 2024).

### 3.3. Wariant zapasowy — wszystkie rachunki KDPW
Kolumna `rachunki_KDPW` w tym samym pliku, z tych samych raportów. Miesięcznie od 01.2020 na portalu data.kdpw.pl. Mało wrażliwa na koniunkturę, bo rachunki rzadko się zamyka.

## 4. Porównanie międzynarodowe — czy inne kraje mają podobną statystykę?

### 4.0. Kraje postransformacyjne (główna grupa porównawcza)
Pliki:
- `data/kraje_postransformacyjne_inwestorzy.csv`: statystyki krajowe; wejście ręczne w `data/reczne/`, przeliczenie przez `scripts/porownanie_na_1000.py`,
- `data/eurostat/isoc_inwestowanie_online.csv`: wskaźnik zharmonizowany (`scripts/eurostat_dane.py`).

**a) Statystyki krajowe aktywnych inwestorów (najbliższe odpowiedniki GPW)**

| Kraj | Miara | Definicja | Okres | Wartość | Na 1000 mieszk. | Status |
|---|---|---|---|---|---|---|
| **PL** | Aktywne rachunki (GPW) | ≥1 zlecenie w półroczu (wg prasy) | II 2019 | 131 427 | 3,5 | zweryfikowane |
| **PL** | jw. | jw. | II 2024 | 267 146 | 7,3 | zweryfikowane |
| **PL** | jw. | jw. | II 2025 | 377 796 | **10,4** | zweryfikowane |
| **RO** | Aktywne rachunki klientów rumuńskich firm inwestycyjnych SSIF (nadzór ASF) | **≥1 transakcja w ostatnich 6 mies.**, czyli definicja niemal identyczna z GPW | 03.2019 | 15 726 | 0,8 | z wyszukiwania |
| **RO** | jw. | jw. | 12.2024 | ok. 124 000 | 6,5 | z wyszukiwania |
| **RO** | jw. | jw. | 12.2025 | 151 412 | **8,0** | z wyszukiwania |
| **LT** | Litewscy inwestorzy z ≥1 transakcją na Nasdaq Vilnius (Bank Litwy) | ≥1 transakcja w roku | 2020 | 16 605 | 5,9 | z wyszukiwania |
| **LT** | Litewscy obywatele aktywni na Nasdaq Vilnius | jw. | 2024 | ok. 16 200 | 5,6 | z wyszukiwania |

**a2) Pełne szeregi zweryfikowane u źródła (subagent, 2026-10-24)** — plik `data/rumunia_litwa_szeregi.csv` (wejście `data/reczne/rumunia_litwa_szeregi.csv`; skrypty `scripts/rumunia_asf.py`, `scripts/rumunia_fci.py`, `scripts/litwa_lb.py`; źródła w `data/raw/ro/`, `data/raw/lt/`). Wartości z tabeli a) dla RO i LT są nimi zastąpione.

| Kraj | Miara | Zakres | Wybrane punkty (na 1000 mieszk.) |
|---|---|---|---|
| **RO** | Aktywne rachunki klientów SSIF (ASF, ≥1 transakcja w 6 mies.) | **XII 2015 – VI 2026, kwartalnie (43 obs.)** | 2015: 24 567 (1,2) → 2019: 16 009 (0,8) → 2021: 32 644 (1,7) → 2023: 84 687 (4,4) → 2025: 151 412 (8,0) → VI 2026: 161 011 (8,5) |
| RO | Inwestorzy zgłoszeni do funduszu FCI (posiadacze) | XII 2008 – IX 2026 (60 obs.) | 2008: 92 865 (4,5) → 2019: 53 550 (2,8) → 2025: 285 582 (15,0); zerwanie metodyki od VI 2022 r. |
| **LT** | Aktywni inwestorzy-rezydenci, osoby fizyczne, wszystkie rynki (Bank Litwy, ≥1 transakcja w roku przez litewskiego pośrednika) | 2020–2025, rocznie | 2020: 42 601 (15,2) → 2022: 53 820 (19,2) → 2024: 176 524 (61,2) → 2025: ok. 250 000 (86,5, z prasy) |
| LT | Aktywni inwestorzy na Nasdaq Vilnius, osoby fizyczne z Litwy | 2019–2024 (bez 2021) | 2019: 8 204 (2,9) → 2024: 16 191 (5,6) |
| LT | Też: akcjonariusze spółek z Nasdaq Vilnius, rachunki osób fizycznych z saldem, klienci nieprofesjonalni | 2018–2025 | patrz CSV |

Wnioski:
- **Rumunia (ta sama definicja co GPW):** od 2015 do 2019 r. stagnacja przy ok. 1 na 1000, potem wzrost ok. 10× do 8,5 na 1000. Polska w tym samym czasie: 4,5 (II 2015) → 3,5 (II 2019) → 12,2 (I 2026). Polska ma wyższy poziom, ale Rumunia rośnie szybciej. Obie serie mają podobny przebieg: dołek w 2019 r., wzrost w 2020–2021 r., przyspieszenie od 2023 r.
- **Litwa:** aktywni rezydenci na *wszystkich* rynkach (61 na 1000 w 2024 r.) przewyższają Polskę, ale polskie GPW liczy tylko rynek akcji GPW. Najbliższa definicyjnie miara litewska to aktywni na Nasdaq Vilnius (5,6 na 1000). Przy porównaniach trzeba uważać.

**b) Miary posiadania (nie aktywności)**

| Kraj | Miara | Okres | Wartość | Na 1000 mieszk. | Status |
|---|---|---|---|---|---|
| PL | Wszystkie rachunki maklerskie (KDPW) | 12.2025 | 2 534 606 | 69,4 | zweryfikowane |
| RO | Rachunki inwestorów na BVB objęte funduszem kompensacyjnym FCI | 12.2020 → 12.2025 | 65 600 → 285 582 | 3,4 → 15,0 | z wyszukiwania |
| EE | Rezydenci z rachunkiem zawierającym ≥1 papier z Nasdaq Tallinn | 2019 → 06.2023 | 37 000 → 111 600 | 27,9 → 81,7 | z wyszukiwania |
| CZ | Klienci firm inwestycyjnych (ČNB, wypowiedź członka zarządu) | 12.2025 | ok. 1,5 mln | 137,5 | z wyszukiwania |

**c) „Bliźniacze” dane z funduszy kompensacyjnych inwestorów (pogłębiony przegląd 2026-10-24)**
Każdy kraj UE ma system rekompensat dla inwestorów (dyrektywa 97/9/WE). Jego członkowie (firmy inwestycyjne, banki, TFI) raportują liczbę klientów objętych ochroną. To miara *posiadania* rachunku z aktywami, najbliższy odpowiednik liczby rachunków KDPW.

| Kraj | Źródło | Miara | Zakres | Na 1000 mieszk. | Plik | Status |
|---|---|---|---|---|---|---|
| **HU** | BEVA (Befektető-védelmi Alap), raporty z działalności | Inwestorzy (osoby) chronieni przez BEVA | **2002–2025, rocznie (24 lata)** | 63 (2002) → 62 (2005) → 112 (2015) → 106 (2020) → 134 (2025) | `data/wegry_beva.csv` (skrypt `scripts/wegry_beva.py`, PDF-y w `data/raw/hu/`) | zweryfikowane |
| **BG** | FKI (Фонд за компенсиране на инвеститорите), raporty roczne | Klienci z aktywami objętymi ochroną | **2008–2025, rocznie** | 8 (2010) → 9 (2015) → 23 (2020) → 49 (2025) | `data/bulgaria_fki.csv` (PDF-y w `data/raw/bg/`, pomocniczy skrypt `scripts/bulgaria_fki.py`) | zweryfikowane |
| PL (dla porównania) | KDPW przez GPW | Wszystkie rachunki maklerskie | 2003–2026 | 22 (2005) → 37 (2015) → 35 (2020) → 69 (2025) | `data/gpw_aktywne_rachunki_pl.csv` | zweryfikowane |
| CZ | Garanční fond obchodníků s CP | — | raport 2024 nie podaje liczby klientów | — | — | sprawdzone, brak |
| SK | Garančný fond investícií | — | strona funduszu bez publikacji | — | — | sprawdzone, brak |

Uwagi:
- **HU:** liczba dotyczy roku raportowania (*adatszolgáltatás éve*); od 2024 r. to średnia ze stanów na koniec miesięcy. Spadek w 2024 r. wynika z wyjścia Interactive Brokers z systemu. Obejmuje klientów banków z papierami wartościowymi, także obligacjami skarbowymi i funduszami, ale bez rachunków w Skarbie Państwa (MÁK), więc miara jest szersza niż rachunki maklerskie KDPW.
- **BG:** skok w 2019 r. (+69 tys.) pochodzi prawie wyłącznie od banków, co może oznaczać zmianę sposobu raportowania. Wartości za 2012, 2015 i 2016 r. są wyliczone z różnic podanych w raportach (opis w uwagach w CSV).

**d) Inne źródła sprawdzone w pogłębionym przeglądzie**
- **SK:** stowarzyszenie AOCP: klienci firm inwestycyjnych (bez banków) ok. 94 tys. (ok. 09.2022) → ok. 160 tys. (09.2024), czyli ok. 17 → 29 na 1000. NBS nie publikuje liczby klientów. — `z wyszukiwania`
- **HR:** brak liczby rachunków. Sprawdzone: miesięczne statystyki SKDD (tylko struktura wartości), raporty Hanfa i fundusz ochrony inwestorów SKDD. Dostępne są tylko liczby pośrednie:
  - ok. 9 tys. drobnych inwestorów w trzech IPO w 2025 r. (ok. 2,3 na 1000),
  - Hanfa: akcjami regularnie handluje „kilka tysięcy” osób,
  - udział osób fizycznych w wartości depozytu SKDD: 6,2% (2021) → 15,1% (I kw. 2026). — `z wyszukiwania`
- **CZ:** sprawdzone: ARAD ČNB (tylko liczba firm i aktywa), raport MF o rynku finansowym 2024, raporty roczne BCPP/CDCP 2023–2024, raport GFO 2024. Jedyna liczba to ok. 1,5 mln klientów firm inwestycyjnych (12.2025, wypowiedź członka zarządu ČNB). W „nezařazená evidence” CDCP jest ok. 529 tys. rachunków z prywatyzacji kuponowej (2025), co nie mierzy aktywności.
- **SI:** sprawdzone: ATVP, KDD, Ljubljanska borza. Brak zbiorczej liczby. Domy maklerskie raportują liczbę klientów tylko w swoich sprawozdaniach.
- **LV:** sprawdzone: system ochrony inwestorów (Latvijas Banka) i Nasdaq Riga. Brak liczby inwestorów. Jest tylko informacja, że liczba transakcji na Nasdaq Riga w latach 2018–2024 wzrosła ponad 4 razy (Signet Bank).
- **LT:** fundusz IIDraudimas nie podaje liczby inwestorów. Bank Litwy — patrz pkt a) i plik od subagenta.
- **Statystyki EBC o depozytach (SST, `data-api.ecb.europa.eu`)** sprawdzone: obejmują uczestników, emisje, wartość papierów i rozliczenia, ale nie liczbę rachunków inwestorów.
- Zbiorcza tabela obu typów miar dla regionu: `data/kraje_postransformacyjne_inwestorzy.csv`.

**e) Wskaźnik zharmonizowany — Eurostat ISOC** (% osób 16–74 lat kupujących lub sprzedających papiery wartościowe przez internet; × 10 = na 1000 osób 16–74):

| Kraj | 2016 | 2019 | 2020* | 2023 | 2025 |
|---|---|---|---|---|---|
| **PL** | 1,4 | 0,7 | 0,7 | 0,8 | **1,6** |
| CZ | 0,4 | 0,7 | 1,5 | 3,1 | 4,0 |
| SK | 1,4 | 1,5 | 1,2 | 3,8 | 6,1 |
| HU | 0,6 | 1,2 | 2,4 | 4,6 | 6,0 |
| SI | 0,7 | 2,8 | 1,7 | 1,8 | 3,8 |
| HR | 0,9 | 1,4 | 2,0 | 1,7 | 1,2 |
| RO | 0,6 | 1,6 | 0,4 | 0,2 | 0,3 |
| BG | 0,4 | 0,1 | 0,4 | 0,4 | 0,7 |
| EE | 2,8 | 4,4 | 5,4 | 8,7 | 10,4 |
| LV | 0,6 | 0,5 | 0,6 | 1,4 | 3,1 |
| LT | 1,0 | 3,1 | 1,4 | 2,4 | 5,0 |
| UE-27 | 3,3 | 4,2 | 4,4 | 5,2 | 8,1 |

\* od 2020 r. okres odniesienia to 3 miesiące, więc seria jest zerwana.

**f) Wnioski (wstępne):**
- **Rumunia to najlepszy odpowiednik Polski.** Ma tę samą definicję aktywnego rachunku (transakcja w ciągu 6 miesięcy) i dane od 2019 r. Poziom jest zbliżony: RO 8,0 vs PL 10,4 na 1000 mieszkańców (koniec 2025 r.). Dynamika w Rumunii jest jednak wielokrotnie szybsza: od 03.2019 do 12.2025 ok. ×9,6, a w Polsce od II 2019 do II 2025 ×2,9. Uwaga: Rumunia startowała z bardzo niskiego poziomu (0,8 na 1000), a liczby ASF obejmują tylko krajowe firmy SSIF (bez zagranicznych brokerów).
- **Litwa** ma mniej aktywnych inwestorów krajowych na swojej giełdzie (ok. 6 na 1000). Mała giełda sprawia jednak, że Litwini inwestują raczej za granicą, czego ta miara nie obejmuje.
- **Estonia** ma więcej posiadaczy akcji z lokalnej giełdy niż Polska rachunków KDPW (ok. 80 vs 69 na 1000). Estońska miara liczy *osoby* z papierami na koncie, a KDPW *wszystkie rachunki*, także puste i zdublowane, więc realna różnica jest większa.
- **W zharmonizowanym ISOC Polska jest w 2025 r. czwarta od końca w regionie** (wyprzedza tylko RO, BG i HR). W latach 2016–2025 praktycznie się nie zmieniła, podczas gdy CZ, SK, HU, LT i EE wzrosły kilkukrotnie. Ta rozbieżność z danymi GPW, które pokazują wzrost, wymaga wyjaśnienia (`do sprawdzenia`). Możliwe przyczyny:
  - ISOC pyta o ostatnie 3 miesiące,
  - polscy inwestorzy są skoncentrowani w wąskiej grupie,
  - ankieta nie uchwyciła osób inwestujących przez aplikacje.
- **Aktywa gospodarstw domowych w akcjach i funduszach (% PKB, `nasa_10_f_bs`)** w latach 2005–2025: PL 7,5 → 9,3, a CZ 7,0 → 23,9, HU 7,7 → 23,8, SK 6,3 → 13,4, SI 12,3 → 16,2, HR 3,3 → 10,6. Według tej miary Polska rosła najwolniej w regionie, poza RO i LT.

### 4.1. Kraje spoza regionu
Plik: `data/porownanie_krajow_inwestorzy.csv` (źródło i status każdej wartości).

**Nie istnieje zharmonizowana międzynarodowo statystyka aktywnych inwestorów.** Część krajów publikuje miary *aktywności* (transakcja w danym okresie), część tylko miary *posiadania* (rejestr akcjonariuszy albo ankieta).

| Kraj | Miara | Jednostka | Okno aktywności | Wartość | Data | Na 1000 mieszk. | Status |
|---|---|---|---|---|---|---|---|
| **PL** | Aktywne rachunki na rynku akcji (GPW) | rachunki | półrocze | 377 796 | II 2025 | **10,4** | zweryfikowane |
| **PL** | Aktywne rachunki (GPW) | rachunki | półrocze | 444 122 | I 2026 | **12,2** | zweryfikowane |
| FR | Osoby z ≥1 transakcją na akcjach (AMF, z raportów MiFID II) | osoby | kwartał | 1,07 mln | IV kw. 2025 | 15,5 | z wyszukiwania |
| FR | jw. | osoby | rok | ok. 1,9 mln | 2025 | 27,6 | z wyszukiwania |
| RO | Inwestorzy z „aktywnymi rachunkami transakcyjnymi” (BVB / FCI) | osoby | stan | 285 582 | 12.2025 | 15,0 | z wyszukiwania |
| IN | Aktywni klienci NSE (≥1 transakcja w 12 mies.) | osoby | 12 mies. | 49,2 mln | 03.2025 | 33,9 | z wyszukiwania |
| KR | Aktywne rachunki akcyjne (KOFIA: ≥100 tys. KRW i ≥1 transakcja w 6 mies.) | rachunki | 6 mies. | 98,3 mln | 12.2025 | 1 901 | z wyszukiwania |
| **Miary posiadania (nie aktywności):** | | | | | | | |
| PL | Wszystkie rachunki maklerskie (KDPW) | rachunki | stan | 2,53 mln | 12.2025 | 69,4 | zweryfikowane |
| DE | Osoby z akcjami, funduszami lub ETF (DAI, ankieta) | osoby | stan | 14,1 mln | 2025 | 168,7 | z wyszukiwania |
| DE | Osoby z akcjami pojedynczych spółek (DAI) | osoby | stan | 4,9 mln | 2025 | 58,6 | z wyszukiwania |
| SE | Prywatni akcjonariusze (Euroclear Sweden) | osoby | stan | 2,3 mln | 2025 | 217,2 | z wyszukiwania |
| FI | Akcjonariusze (Euroclear Finland) | osoby | stan | 1,017 mln | 05.2026 | 180,4 | z wyszukiwania |

Ludność: Eurostat `demo_pjan` (1.01.2025), dla KR i IN Bank Światowy `SP.POP.TOTL`.

### 4.2. Interpretacja (wstępna)
- **Najbliższy odpowiednik GPW to Francja (AMF).** Liczy osoby, a nie rachunki, z transakcją w kwartale albo roku. Okno półroczne GPW leży pomiędzy, więc Polska z 10–12 aktywnymi na 1000 mieszkańców wypada poniżej Francji (15,5 w kwartale, 27,6 w roku). Różnica w półroczu byłaby prawdopodobnie jeszcze większa. Do tego GPW liczy rachunki, a nie osoby, więc liczba aktywnych *osób* w Polsce jest raczej niższa niż 10–12 na 1000.
- **Rumunia** (15 na 1000) ma podobny lub nieco wyższy poziom niż Polska, ale jej liczba obejmuje też osoby trzymające tylko obligacje skarbowe Fidelis, a definicja „aktywnego” jest niejasna.
- **Korea** to skrajny przypadek: aktywnych rachunków jest więcej niż mieszkańców. Liczba rachunków nie nadaje się więc do porównań, gdy jedna osoba ma ich wiele.
- **Miary posiadania:** w Szwecji (217 na 1000), Finlandii (180) i Niemczech (169, z funduszami) akcje lub fundusze ma kilkanaście–ponad 20% ludności. W Polsce nawet wszystkich rachunków KDPW (także nieaktywnych i zdublowanych) jest tylko 69 na 1000.
- **Wniosek na slajd:** niezależnie od miary aktywność inwestycyjna w Polsce jest *niska* na tle Europy Zachodniej i Północnej. Ostatnie lata (2023–2026) to jednak najszybszy wzrost w historii szeregu.

### 4.3. Kraje bez znalezionej statystyki
- **CZ:** brak publicznej statystyki rejestrowej (CDCP). Są tylko ankiety (Index prosperity) i dane banków, np. ponad 750 tys. klientów inwestycyjnych Česká spořitelna.
- **HU:** nie znaleziono liczby inwestorów w KELER ani MNB. Skarb Państwa podaje ok. 1,2 mln klientów z obligacjami skarbowymi, co nie jest miarą rynku akcji.
- **Kraje bałtyckie:** tylko ankiety (np. 23% Estończyków deklaruje inwestowanie w akcje), bez statystyki rejestrowej.

### 4.4. Do sprawdzenia
- Szeregi historyczne: AMF (kwartalnie od 2018 r.), KOFIA, NSE, BVB, DAI (od 1997 r.), Euroclear Sweden. Z nimi można by pokazać na 1000 mieszkańców nie tylko poziom, ale też *dynamikę* w porównaniu z Polską.
- Definicja „aktywnego rachunku” w Rumunii (FCI).
- Wartości ze statusem „z wyszukiwania” trzeba potwierdzić w raportach źródłowych przed użyciem na slajdzie.

## 5. Zmienne objaśniające — źródła (wariant A, Polska, półrocznie)

| Zmienna | Proponowana miara | Źródło | Częstotliwość | Status |
|---|---|---|---|---|
| **Dochód** | Realne przeciętne wynagrodzenie w gospodarce narodowej (lub w sektorze przedsiębiorstw), ew. PKB per capita | GUS (BDL, „Wskaźniki makroekonomiczne”) | miesięcznie / kwartalnie | do sprawdzenia |
| **Inflacja** | CPI r/r (średnia w półroczu lub koniec okresu) | GUS; alternatywnie HICP Eurostat (`prc_hicp_manr`) | miesięcznie | HICP roczny w Eurostat `zweryfikowane` (2003–2025) |
| **Stopy zwrotu z giełdy** | Stopa zwrotu WIG (indeks dochodowy) za półrocze lub kroczące 12 mies. | GPW (gpwbenchmark.pl), stooq.pl | dziennie | do sprawdzenia |
| **Stopa procentowa BC** | Stopa referencyjna NBP (średnia w półroczu lub koniec okresu) | NBP, archiwum podstawowych stóp procentowych | przy zmianach | do sprawdzenia |

Dodatkowo do rozważenia: realna stopa procentowa (stopa NBP − inflacja) oraz oprocentowanie nowych depozytów gospodarstw (NBP, statystyka MIR).

### 5.1. Oczekiwane kierunki wpływu (hipotezy do dyskusji)
| Zmienna | Oczekiwany znak | Uzasadnienie |
|---|---|---|
| Dochód | + | Więcej nadwyżek do zainwestowania |
| Inflacja | ± | (+) ucieczka od realnie tracących lokat; (−) mniejsza zdolność do oszczędzania, niepewność |
| Stopy zwrotu z giełdy | + | „Gonienie trendu”: inwestorzy wchodzą po wzrostach, prawdopodobnie z opóźnieniem |
| Stopa BC | − | Wyższe oprocentowanie lokat i obligacji to alternatywa dla akcji |

## 6. Metody — wstępne pomysły
_Do zaplanowania._
- **Wariant A:** regresja szeregu czasowego, np. log aktywnych rachunków (lub jej zmiana) na zmiennych objaśniających, ze stopą zwrotu opóźnioną o jedno półrocze. Testy stacjonarności (ADF); przy niestacjonarności model w różnicach albo ARDL/ECM. Uwaga na małą próbę (46 obs.) przy 4 zmiennych.
- Wizualizacja: aktywne rachunki na tle WIG i stopy NBP jako slajd „zmienna zależna w czasie”.

## 7. Przegląd zharmonizowanych danych międzynarodowych (archiwum z wcześniejszego etapu)
- **Eurostat ISOC** (`isoc_ec_ifi` 2016–2019, `isoc_ec_ifi20` 2020–2025): % osób kupujących lub sprzedających papiery wartościowe przez internet. PL 2025: 1,6%, UE-27: 8,1%. Zerwanie serii w 2020 r. — `zweryfikowane`
- **Eurostat, rachunki finansowe** (`nasa_10_f_bs`): akcje + fundusze gospodarstw w PL 7,5% PKB (2005) → 9,3% (2025); CZ 7,0 → 23,9%; HU 7,7 → 23,8% — `zweryfikowane`
- **ECB HFCS / NBP BZGD:** Polska tylko w falach 2014 i 2017 — `z wyszukiwania`
- **Bank Światowy WDI:** obroty i kapitalizacja % PKB, 2004–2024/25 — `zweryfikowane`

## 8. Otwarte decyzje
1. Konstrukcja: A (sama Polska) czy C (A + slajd porównawczy)?
2. Normalizacja w prezentacji: na 1000 mieszkańców czy na 1000 dorosłych?
3. Miara dochodu: realne wynagrodzenie czy PKB per capita?
4. Okres: pełny szereg (II 2003 – I 2026) czy równe 20 lat?

## 9. Dalsze kroki
- Potwierdzić definicję aktywnego rachunku i ciągłość metodologii GPW (sekcja 3.2).
- Zebrać zmienne objaśniające (WIG, stopa NBP, CPI, wynagrodzenia) i dopisać skrypt, który zbuduje półroczny zbiór do modelu.
- Potwierdzić u źródła wartości z sekcji 4 ze statusem „z wyszukiwania”.
- **Rumunia:** zebrać pełny szereg aktywnych rachunków z kwartalnych i rocznych raportów ASF „Raport privind evoluția pieței de capital” (asfromania.ro), najlepiej od 2019 r. To najlepszy odpowiednik szeregu GPW.
- **Litwa:** zebrać szereg z publikacji Banku Litwy „Profile of the Lithuanian investor” (od 2020 r.). Strona lb.lt blokuje pobieranie skryptem, więc trzeba to zrobić ręcznie w przeglądarce.
- **Czechy:** sprawdzić w bazie ARAD (ČNB), czy jest szereg liczby klientów firm inwestycyjnych.

## Źródła
- GPW, raporty „Udział inwestorów w obrotach”: https://www.gpw.pl/analizy · https://www.gpw.pl/pub/GPW/analizy/Udzial_inwestorow_2019.pdf · https://www.gpw.pl/pub/GPW/analizy/Udzial_inwestorow_1H2026.pdf · https://www.gpw.pl/pub/GPW/analizy/badanie_inwestorow_dane_na_www20.pdf
- Eurostat API: `demo_pjan`, `isoc_ec_ifi`, `isoc_ec_ifi20`, `nasa_10_f_bs`, `prc_hicp_aind`, `nama_10_pc`, `irt_st_a` (https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/)
- Bank Światowy, ludność `SP.POP.TOTL`: https://api.worldbank.org/v2/
- AMF, tableau de bord des investisseurs particuliers actifs: https://www.amf-france.org/sites/institutionnel/files/private/2026-03/tb-investisseurs_n21-vdef__0.pdf · metodologia: https://www.amf-france.org/fr/actualites-publications/communiques/communiques-de-lamf/lamf-publie-un-tableau-de-bord-des-investisseurs-particuliers-actifs-en-bourse · rok 2025: https://cliff.asso.fr/actualites/bourse-seduit-nombre-record-investisseurs-particuliers-en-2025
- BVB, raport roczny 2025: https://bvb.ro/infocont/infocont26/BVB_20260327173700_BVB-Raport-Anual-2025.pdf · ZF o Fidelis: https://www.zf.ro/burse-fonduri-mutuale/209-000-romani-investesc-actiuni-special-bursa-valori-bucuresti-au-22936408
- KOFIA (przez FN News): https://en.fnnews.com/news/202601311049399473
- NSE (przez Business Standard): https://www.business-standard.com/companies/news/nse-active-clients-see-21-rise-in-fy25-groww-cements-lead-with-36-growth-125041100286_1.html
- DAI Aktionärszahlen 2025: https://www.dai.de/fileadmin/user_upload/Pressemitteilung___Aktionaerszahlen_2025__Aktienanlage_weiter_im_Aufwind.pdf
- Euroclear Sweden (przez Placera): https://placera.se/nyheter/svenskt-aktieagande-slar-rekord--sa-stor-ar-medelportfoljen-2026-02-11
- Euroclear Finland: https://www.sttinfo.fi/uutishuone/69821858/euroclear-finland-oy/r
- Kraje bałtyckie (ankieta): https://www.baltictimes.com/investment_habits_of_baltic_residents__where_do_latvians__lithuanians__and_estonians_invest_/
- Czechy (Index prosperity): https://www.businessinfo.cz/clanky/index-prosperity-pres-8-z-10-cechu-zhodnocuje-sve-uspory-a-vice-nez-polovina-populace-aktivne-investuje/
- Węgry (Skarb Państwa): https://profitline.hu/tobb-mint-12-millioan-rendelkeznek-ertekpapirszamlaval-az-allamkincstarnal-490584
