# RESEARCH — notatka robocza

**Projekt:** „Makroekonomiczne i społeczne determinanty liczby rachunków maklerskich w Polsce” (prezentacja ok. 10 min)
**Ostatnia aktualizacja:** 2026-10-14

**Statusy:** `zweryfikowane` = sprawdzone u źródła · `z prasy` = znane z artykułów, nie sprawdzone u źródła · `do sprawdzenia` = otwarte

---

## 1. Status i zasady notatki

Ta notatka to miejsce na opcje danych, ustalenia researchu i dyskusję — nic tutaj nie jest ostateczną decyzją. Gdy coś zostanie ustalone, przenosimy to do `CLAUDE.md`, a tutaj zostawiamy tylko odnośnik lub usuwamy pozycję.

---

## 2. Zmienna zależna — opcje

### 2.1. Dostępne źródła dla Polski

| Źródło | Miara | Częstotliwość | Zakres | Status |
|---|---|---|---|---|
| KDPW (portal data.kdpw.pl) | Liczba rachunków papierów wartościowych i zbiorczych u uczestników KDPW | miesięcznie | 31.01.2020 – 31.08.2026 (81 plików) | zweryfikowane |
| GPW, raport „Udział inwestorów w obrotach” | Aktywne rachunki (≥1 zlecenie na rynku akcji w półroczu) | półrocznie | od ok. 2010 | z prasy + PDF GPW; zakres do sprawdzenia |
| NBP, Badanie Zasobności Gospodarstw Domowych | Odsetek gospodarstw z akcjami / obligacjami / TFI | rzadko (rundy badania) | runda i rok do sprawdzenia | z prasy (SII) |

### 2.2. KDPW — szczegóły (zweryfikowane 2026-10-14)

- Raport „Liczba rachunków papierów wartościowych oraz rachunków zbiorczych prowadzonych przez uczestników KDPW”, publiczny, bez logowania. — `zweryfikowane`
- Lista plików: `https://data.kdpw.pl/portal/files/csd/number_securities_accounts/list?take=500` — `zweryfikowane`
- Pobieranie pliku: `https://data.kdpw.pl/portal/files/download?uuid=<uuid>` — `zweryfikowane`
- 81 plików miesięcznych, 31.01.2020 – 31.08.2026; `.xls` do 12.2021, `.xlsx` od 2022. — `zweryfikowane`
- Danych sprzed 2020 r. portal nie udostępnia; możliwe źródła: raporty roczne KDPW, archiwum. — `do sprawdzenia`
- Ostatnia wartość: 3 029 784 rachunków (koniec 08.2026). — `z prasy`
- Obejmuje wszystkie rachunki z dostępem do rynku polskiego, także puste i nieaktywne; jedna osoba może mieć wiele rachunków. — `zweryfikowane`
- IKE/IKZE prawdopodobnie wliczane (skoki w grudniu i styczniu). — `z prasy`
- KDPW **nie** wydziela IKE/IKZE osobno. Plik zawiera tylko kolumny: L.p., kod uczestnika, uczestnik, liczba rachunków oraz wiersz RAZEM. — `zweryfikowane` (pliki 01.2020–08.2026)
- Pobieranie: `scripts/pobierz_kdpw.py` → `data/kdpw/kdpw_rachunki_suma.csv` (81 miesięcy) i `data/kdpw/kdpw_rachunki_uczestnicy.csv` (w podziale na domy maklerskie). Suma uczestników zgadza się z RAZEM we wszystkich plikach. — `zweryfikowane`
- Uwaga: kody uczestników zmieniają się w czasie (np. „815/929” → „815”, fuzje, np. Santander → Erste), więc analiza w podziale na domy maklerskie wymaga mapowania nazw.
- Domy maklerskie okresowo czyszczą nieaktywne konta → spadki w szeregu. — `z prasy`

### 2.3. GPW — aktywne rachunki (z prasy + PDF GPW)

| Okres | Aktywne rachunki | Status |
|---|---|---|
| 2010 (szczyt) | 412 tys. | z prasy |
| koniec 2019 | 131 tys. | z prasy |
| I poł. 2024 | 246 732 | z prasy |
| I poł. 2025 | 321 124 | z prasy |
| I poł. 2026 | 444 122 | z prasy |

Aktywne to ok. 15% wszystkich rachunków z dostępem do GPW (`z prasy`).

### 2.4. NBP — Badanie Zasobności Gospodarstw Domowych (z prasy, SII)

Ok. 7,5% gospodarstw ma akcje, obligacje lub TFI: 4,2% TFI, 3,5% akcje, 1% obligacje. Runda i rok — `do sprawdzenia`.

### 2.5. Porównanie opcji

| Opcja | Opis | Zalety | Wady |
|---|---|---|---|
| (a) KDPW | liczba wszystkich rachunków | miesięcznie, publicznie, łatwe pobieranie | na portalu tylko od 2020; zawiera puste/nieaktywne konta; czyszczenie kont; sezonowość IKE/IKZE |
| (b) GPW aktywne | aktywne rachunki na rynku akcji | mierzy realną aktywność; dłuższy szereg (od ok. 2010) | tylko półrocznie; definicja ograniczona do akcji |
| (c) obie | „otwieranie rachunków” vs „faktyczna aktywność”, wspólna częstotliwość półroczna | najciekawsza interpretacja; ~30 obs. od 2010 | wymaga przedłużenia KDPW wstecz; inaczej mniej obserwacji |

**Wstępna rekomendacja:** (c).

---

## 3. Porównanie międzynarodowe — dobór krajów (opcje)

**Propozycja, niezatwierdzona.**

| Grupa | Kraje | Uzasadnienie |
|---|---|---|
| Główna (CEE) | Czechy, Węgry, Rumunia; opcjonalnie kraje bałtyckie | podobna transformacja, UE od 2004/2007, system bankocentryczny |
| Benchmark | Niemcy | wysoki dochód, niski udział inwestorów |
| Benchmark | Szwecja | wysoki udział inwestorów, konta ISK |
| Odradzane | USA, UK | inna struktura rynku |

### Rola porównania

| Wariant | Opis | Ocena |
|---|---|---|
| 1) Model tylko dla PL + tło opisowe | inne kraje jako kontekst | rekomendowany na 10 min |
| 2) Panel kilku krajów | wspólny model | wymaga tej samej definicji zmiennej — praktycznie niewykonalne dla liczby rachunków |

---

## 4. Zharmonizowane dane UE

**Brak zharmonizowanej statystyki liczby rachunków maklerskich w UE.**

### 4.1. Zamienniki zmiennej zależnej

| Źródło | Miara | Zakres | Uwagi | Status |
|---|---|---|---|---|
| Eurostat, rachunki finansowe sektorów — gospodarstwa domowe | F511 akcje notowane, F52 jednostki funduszy | cała UE + PL | wartość, nie liczba; w 2023 akcje i fundusze = 35,9% aktywów finansowych gosp. dom. UE; kod zbioru `nasq_10_f_bs` / `nasa_10_f_bs` | z prasy; kod do sprawdzenia |
| EBC HFCS | odsetek gospodarstw z akcjami/funduszami | fala 2021: strefa euro + CZ, HU, HR | **brak Polski**; co ~3 lata | z prasy |
| Flash Eurobarometr 525 (2023) | wiedza finansowa, posiadanie produktów inwestycyjnych | UE-27 z PL, ~1000 resp./kraj | wartości krajowe z aneksu / GESIS ZA7985 | z prasy |
| EU-SILC | moduł o majątku | — | dopiero 2026 | z prasy |

### 4.2. Zharmonizowane zmienne objaśniające

| Zmienna | Źródło / kod | Status |
|---|---|---|
| Inflacja | HICP (Eurostat) | z prasy |
| Stopy procentowe | EBC MIR; Eurostat rentowności 10-letnie | z prasy |
| Dochód | Eurostat `ilc_di03` — mediana dochodu ekwiwalentnego w PPS | zweryfikowane |
| PKB per capita | Eurostat, PPS | z prasy |
| Bezrobocie | Eurostat LFS | z prasy |
| Stopa oszczędności gosp. domowych | Eurostat | z prasy |
| Cyfryzacja | Eurostat `isoc_bde15cbc` — % osób 16–74 korzystających z bankowości internetowej | zweryfikowane |
| Wykształcenie wyższe | Eurostat LFS | kod do sprawdzenia |
| Struktura wieku | Eurostat | z prasy |

---

## 5. Dane z centralnych depozytów i giełd innych krajów

Wszystkie pozycje w tej sekcji: `z prasy`, chyba że zaznaczono inaczej.

| Kraj | Depozyt / giełda | Regulator / inne | Miara aktywnych? |
|---|---|---|---|
| Czechy | CDCP nie publikuje liczby kont; giełda praska nie publikuje aktywnych rachunków | ČNB: ~1,5 mln klientów obchodníků s cennými papíry (2026); DIP (od 2024): ~105 tys. klientów u obchodników (ČNB) / ~184 tys. inwestorów u wszystkich dostawców (AKAT) | nie |
| Węgry | KELER nie publikuje liczby kont; BÉT brak regularnej statystyki | MNB: konta TBSZ ~354 tys. (2018, ostatnia znaleziona); szacunek 2018: ~2 mln rachunków, 50–100 tys. aktywnych inwestorów | tylko jednorazowy szacunek |
| Rumunia | FCI — konta inwestorów u brokerów BVB, kwartalnie | ASF — aktywne konta (≥1 transakcja w ostatnich 6 mies.), kwartalnie; od kiedy publikuje — `do sprawdzenia` | **tak** |
| Szwecja | Euroclear Sweden: >2,8 mln unikalnych akcjonariuszy | konta ISK prowadzone przez nominee — nie da się wydzielić | nie |
| Niemcy | Clearstream nie liczy detalicznych | DAI (ankieta Kantar, ~28 tys. osób/rok) | nie (ankieta osób) |
| Kraje bałtyckie | Nasdaq Baltic: brak aktualnych danych o liczbie kont/aktywnych | — | nie |

### 5.1. Rumunia — szczegóły

| Okres | FCI: konta u brokerów BVB | ASF: aktywne konta |
|---|---|---|
| 12.2024 | 226 057 | — |
| 09.2025 | 274 412 | 145 520 |
| 12.2025 | 285 582 | — |
| 03.2026 | — | 148 491 |
| 06.2026 | 325 003 | — |

~20–22% kont FCI ma tylko obligacje skarbowe. Rumunia to jedyny poza PL kraj z miarą aktywnych rachunków.

### 5.2. Niemcy — DAI

| Rok | Osoby z akcjami / funduszami akcyjnymi |
|---|---|
| 2022 (poprzedni szczyt) | 12,9 mln |
| 2024 | 12,1 mln |
| 2025 | 14,1 mln |

Struktura 2025: 9,2 mln tylko fundusze/ETF, 2 mln tylko akcje, 2,9 mln oba.

### 5.3. Szeregi porównawcze do danych KDPW (research 2026-10-14)

Cel: ocenić (1) poziom: czy w Polsce to dużo czy mało, (2) dynamikę przyrostu, (3) zależność od czynników w innych krajach. Do tego potrzebny jest **szereg czasowy liczby** (rachunków, inwestorów albo kont podatkowych), a nie pojedyncze punkty.

| Kraj | Rola | Miara (liczba) | Częstotliwość / historia | Ostatnie wartości | Odpowiednik IKE/IKZE | Status |
|---|---|---|---|---|---|---|
| **Rumunia** | peer CEE | FCI: konta u brokerów BVB; ASF: konta aktywne (≥1 transakcja w 6 mies.) | kwartalnie; FCI co najmniej od 2022, starsze w raportach na fond-fci.ro | FCI: 159 513 inwestorów (06.2023), 262 737 kont (06.2025), 325 003 (06.2026); ASF: 148 491 aktywnych (03.2026) | brak | z prasy; historia do sprawdzenia |
| **Węgry** | peer CEE | MNB: liczba kont **TBSZ** (konto długoterminowe z ulgą podatkową) i **NYESZ** (emerytalne); łączna liczba rachunków papierów wartościowych | TBSZ: dane MNB, co najmniej od 2018; łączna liczba: tylko punktowo | TBSZ: ~354 tys. (10.2018), 386 555 (12.2024), >494 tys. (06.2025), ~519 tys. (koniec 2025?); NYESZ ~103 tys.; łącznie >2 mln rachunków (stary szacunek) | **TBSZ/NYESZ** | z prasy; szereg MNB do sprawdzenia |
| **Czechy** | peer CEE | ČNB: klienci obchodníků s cennými papíry; DIP | punktowo (komentarz ČNB 2026); szereg w bazie ČNB ARAD do sprawdzenia | ~1,5 mln klientów (2026); DIP ~105 tys. (ČNB) / ~184 tys. (AKAT) | **DIP** (od 2024) | z prasy |
| **Grecja** | peer (podobna wielkość rynku, system oparty na bankach) | ATHEX/ATHEXCSD: liczba **kont inwestorów** i **kont aktywnych** | miesięczny biuletyn statystyczny, historia od ok. 2004; czy publikowany po 2019, do sprawdzenia | brak aktualnych wartości | brak | do sprawdzenia |
| **Chorwacja** | peer | SKDD: liczba rachunków papierów wartościowych | biuletyny miesięczne/kwartalne | 881 191 rachunków (ok. 2016) | brak | z prasy (stare) |
| **Finlandia** | benchmark (najlepsze dane) | Statistics Finland: liczba **osób** z akcjami/funduszami i % ludności; Euroclear Finland: posiadacze (miesięcznie); liczba kont **osakesäästötili** | GUS Finlandii rocznie (tabele 15j6, 15jx); Euroclear miesięcznie | 2,14 mln osób = 38% ludności (2025; akcje 17%, fundusze 32%); osakesäästötili ~415 tys. (05.2025) | **osakesäästötili** | zweryfikowane (stat.fi); Euroclear z prasy |
| **Niemcy** | benchmark | DAI: liczba osób z akcjami/funduszami (ankieta) | rocznie, długi szereg | 12,1 mln (2024), 14,1 mln (2025), ok. 20% ludności 14+ | brak | z prasy |
| **Szwecja** | benchmark (wysoki udział) | Euroclear Sweden: unikalni akcjonariusze | kwartalnie | >2,83 mln | ISK (nie da się wydzielić) | z prasy |
| **Norwegia** | benchmark | Euronext Securities Oslo (VPS): liczba posiadaczy, w tym norwescy inwestorzy prywatni | rocznie od 2008 (PDF); „Analysis of private investors” | ok. 450 tys. inwestorów detalicznych na Oslo Børs (10.2020) | ASK | zweryfikowane (strona VPS, bez wartości) |
| Estonia, Słowacja | — | dane stare (2010, 2014) lub brak | — | — | — | odradzane |

**Jak to wykorzystać (propozycja do dyskusji):**
1. **Poziom („dużo czy mało”):** przeliczyć wszystko na 100 dorosłych mieszkańców (ludność z Eurostat `demo_pjan`). Polska: ok. 3,03 mln rachunków na ok. 31 mln dorosłych, czyli ok. 10 rachunków na 100 dorosłych (szacunek; to rachunki, nie osoby, więc zawyżone). Porównanie: Finlandia 38% ludności, Niemcy ok. 20% (osoby). Na slajdzie wyraźnie rozdzielić **rachunki** od **osób**.
2. **Dynamika:** indeks 2020 = 100 lub zmiana r/r dla szeregów od 2020 r.: PL (KDPW), RO (FCI), HU (TBSZ), FI, DE, SE. Okres wspólny: ok. 2020–2025.
3. **Zależność od czynników:** z innymi krajami nie ma panelu. Realne opcje: (a) ten sam prosty model (np. stopy, inflacja, stopa zwrotu indeksu) dla PL i 1–2 krajów z najdłuższym szeregiem (FI, DE, NO) i porównanie znaków współczynników; (b) korelacja dynamiki z czynnikami wspólnymi dla regionu.
4. **Konta podatkowe** (HU TBSZ, CZ DIP, FI osakesäästötili) jako osobny wątek do porównania z IKE/IKZE. Dla Polski brak danych o IKE/IKZE w KDPW; szukać w KNF/UKNF lub izbach branżowych (do sprawdzenia).

**Wstępny zestaw:** peers CEE: Rumunia i Węgry (szeregi), Czechy (punktowo). Benchmarki: Finlandia (najlepsze dane), Niemcy. Opcjonalnie Grecja, jeśli biuletyn ATHEX nadal publikuje liczbę kont aktywnych.

### 5.4. „Aktywne rachunki” dla PL, CZ, HU, DE (research 2026-10-14)

Pytanie: czy da się zbudować porównywalny szereg **aktywnych** rachunków dla czterech krajów? Odpowiedź: **nie**. Miara aktywności istnieje tylko dla Polski.

| Kraj | Najbliższa dostępna miara | Aktywne? | Częstotliwość / zakres | Status |
|---|---|---|---|---|
| Polska | GPW: rachunki z ≥1 zleceniem na akcjach w półroczu | **tak** | półrocznie, od ok. 2010 | z prasy + PDF GPW |
| Niemcy | Bundesbank, Depotstatistik: liczba depozytów osób prywatnych **bez pustych**; kilka depozytów jednej osoby w jednym banku liczone jako 1 | nie (niepuste, nie aktywne) | rocznie; 2010: 26,999 mln → 2015: 22,433 mln → 2019: 23,465 mln; po 2019 — szereg u Statisty do 2024, źródło do sprawdzenia | zweryfikowane (Bundestag 19/18042) dla 2010–2019 |
| Węgry | MNB: liczba klientów z rachunkiem papierów wartościowych (z osobami prawnymi): 1,98 mln (03.2023); osobno konta TBSZ | nie | punktowo; szereg w bazie MNB do sprawdzenia | z prasy |
| Czechy | ČNB: ~1,5 mln klientów obchodníků s cennými papíry; BCPP nie publikuje liczby aktywnych inwestorów | nie | punktowo | z prasy |

Wnioski do dyskusji:
- Panel „aktywnych rachunków” PL–CZ–HU–DE jest niewykonalny: tylko PL ma miarę aktywności, a pozostałe trzy kraje mierzą co innego (niepuste depozyty, klienci, konta podatkowe).
- Jeśli celem jest panel czterech krajów, zharmonizowaną zmienną zależną może być **wartość** akcji notowanych i jednostek funduszy w aktywach gospodarstw domowych per capita (Eurostat, rachunki finansowe, kwartalnie, wszystkie 4 kraje). Mierzy jednak zaangażowanie kwotowe, a nie liczbę inwestorów.
- Niemiecki szereg Bundesbanku (niepuste depozyty) to dobre tło: pokazuje, że w DE liczba depozytów **spadała** w latach 2010–2016 mimo wysokich dochodów.

---

## 6. Zmienne objaśniające (kandydaci)

Kandydaci dla PL; w nawiasie oczekiwany znak wpływu. Źródła: NBP, GUS, GPW, Eurostat. Status całej listy: `do sprawdzenia` (dostępność i częstotliwość szeregów).

| Zmienna | Oczekiwany znak | Źródło |
|---|---|---|
| Stopa referencyjna NBP / WIBOR 3M | − | NBP |
| CPI r/r | + | GUS |
| Stopa zwrotu WIG | + | GPW |
| Realne wynagrodzenie / PKB per capita | + | GUS / Eurostat |
| Bezrobocie | − | GUS / Eurostat |
| Oprocentowanie lokat gosp. domowych (substytut) | − | NBP |
| Bankowość internetowa | + | Eurostat (`isoc_bde15cbc`) |
| Wykształcenie wyższe | + | GUS / Eurostat |
| Dummy: duże IPO (np. PZU 2010, Allegro 2020, Żabka 2024) | + | GPW |
| Dummy: COVID 2020 | + | — |
| Opcjonalnie: Google Trends „rachunek maklerski” | + | Google Trends |

---

## 7. Problemy metodologiczne / ograniczenia

| Problem | Konsekwencja | Możliwe rozwiązanie |
|---|---|---|
| Liczba rachunków ≠ liczba inwestorów | przeszacowanie liczby inwestorów | interpretować jako „rachunki”, nie „osoby”; uzupełnić danymi GPW/NBP |
| IKE/IKZE — sezonowość grudzień/styczeń | skoki w szeregu miesięcznym | dummy lub agregacja kwartalna/półroczna; ewentualnie zmienna limitu wpłat |
| Czyszczenie nieaktywnych kont przez domy maklerskie | sztuczne spadki | identyfikacja i dummy / komentarz |
| Różne definicje między krajami (rachunki vs inwestorzy vs klienci vs akcjonariusze) | brak porównywalności | porównanie międzynarodowe tylko ilustracyjne |
| Aktywność: GPW (zlecenie na akcjach) vs ASF (dowolna transakcja) | PL i RO nie w pełni porównywalne | zaznaczyć w prezentacji |
| Krótki szereg KDPW na portalu (od 2020) | mało obserwacji | przedłużenie wstecz (raporty roczne, archiwum) — `do sprawdzenia` |
| Zmienne społeczne roczne vs dane miesięczne/półroczne | niezgodność częstotliwości | interpolacja lub niższa częstotliwość modelu |

---

## 8. Otwarte decyzje

- [ ] Rola porównania międzynarodowego: tło opisowe vs panel
- [ ] Czy obie zmienne zależne (KDPW + GPW)
- [ ] Częstotliwość danych: miesięczna / kwartalna / półroczna
- [ ] Okres badania
- [ ] Jak przedłużyć szereg KDPW sprzed 2020
- [ ] Które zmienne objaśniające
- [ ] Jak potraktować IKE/IKZE
- [ ] Czy Rumunia jako jedyny kraj porównawczy z aktywnymi rachunkami
- [ ] Metoda badawcza (jeszcze nieomawiana)
- [ ] Zestaw krajów porównawczych (propozycja w 5.3: RO, HU, CZ + FI, DE; opcjonalnie GR)
- [ ] Miara poziomu: rachunki czy osoby na 100 dorosłych

---

## 9. Źródła

**Polska**
- KDPW, portal danych: https://data.kdpw.pl
- GPW, Udział inwestorów w obrotach 2025: https://www.gpw.pl/pub/GPW/analizy/Udzial_inwestorow_2025.pdf
- GPW, komunikat prasowy Q2 2026: https://www.gpw.pl/pub/GPW/files/PDF/raporty/R2026/Q2/Komunikat_Prasowy_GPW_Q2_2026.pdf
- SII, liczba rachunków przekroczyła 3 mln: https://www.sii.org.pl/19323/analizy/newsroom/liczba-rachunkow-maklerskich-w-polsce-przekroczyla-3-miliony-na-horyzoncie-dalszy-wzrost-dane-kdpw.html
- SII, 2,5 mln rachunków, grudniowy wzrost: https://www.sii.org.pl/18744/analizy/newsroom/2-5-mln-rachunkow-maklerskich-na-liczniku-w-samym-grudniu-wzrost-o-ponad-100-000-dane-kdpw.html
- SII, aktywne rachunki GPW: https://www.sii.org.pl/19304/analizy/newsroom/gpw-aktywnych-rachunkow-trzy-razy-wiecej-niz-przed-pandemia-zagranica-rzadzi-na-rynku-glownym.html
- SII, 7,5% Polaków z akcjami/obligacjami/TFI: https://www.sii.org.pl/9653/aktualnosci/felietony/najchetniej-trzymamy-pieniadze-w-banku-zaledwie-7-5-polakow-posiada-akcje-obligacje-lub-jednostki-tfi.html

**UE**
- EBC, HFCS fala 2021 (FAQ): https://www.ecb.europa.eu/pub/research-networks/html/hfcn_faq_2021_wave.nl.html
- Eurostat, aktywa i pasywa finansowe gospodarstw domowych: https://ec.europa.eu/eurostat/statistics-explained/index.php/Households_-_statistics_on_financial_assets_and_liabilities
- GESIS, Flash Eurobarometr 525 (ZA7985): https://data.gesis.org/gesiskg/resource/ZA7985
- Eurostat `isoc_bde15cbc` (DBnomics): https://db.nomics.world/Eurostat/isoc_bde15cbc
- Eurostat `ilc_di03` (DBnomics): https://db.nomics.world/Eurostat/ilc_di03

**Czechy**
- ČNB, J. Procházka: https://www.cnb.cz/cs/verejnost/servis-pro-media/autorske-clanky-rozhovory-s-predstaviteli-cnb/Jan-Prochazka-Cesky-investicni-trh-roste.-Roste-ale-i-ochrana-klientu
- Newstream, DIP 184 tys.: https://www.newstream.cz/money/cesi-odkladaji-penize-na-stari-do-dip-uz-jich-investovalo-184-tisic

**Węgry**
- Infostart, TBSZ 2018: https://infostart.hu/gazdasag/2018/12/31/tobb-mint-100-ezren-ferhetnek-hozza-penzukhoz-ot-ev-utan
- Economx, BÉT 2018: https://www.economx.hu/tozsde/2018/01/18/ez_var_a_pesti_tozsdere_evet_ertekel_a_bet_elnoke-655140/

**Rumunia**
- Bursa.ro, +24% kont w rok: https://www.bursa.ro/numarul-conturilor-investitorilor-la-bvb-a-crescut-cu-24-procente-intr-un-an-07847950
- Bursa.ro, +28% 09.2024–09.2025: https://www.bursa.ro/numarul-conturilor-investitorilor-la-bvb-a-crescut-cu-28-procente-in-perioada-septembrie-2024-septembrie-2025-45104752
- ZF, aktywne konta BVB: https://www.zf.ro/burse-fonduri-mutuale/bursa-numarul-conturilor-active-de-investitii-de-la-bvb-se-apropie-22988735

**Szwecja**
- Euroclear Sweden, 2018: https://www.euroclear.com/newsandinsights/en/press/2018/2018_mr-02-Sweden.html

**Węgry (TBSZ/NYESZ)**
- Economx, TBSZ 06.2025: https://www.economx.hu/magyar-gazdasag/2025/10/20/tbsz-megtakaritas-allampapir-817995/
- Economx, TBSZ 12.2024: https://www.economx.hu/magyar-gazdasag/2025/02/08/ertekpapirok-ado-elkerules-tbsz-mnb-804017/
- BiztosDöntés, TBSZ i NYESZ: https://biztosdontes.hu/cikkek/no-az-arverseny-az-ertekpapirszamlaknal-is

**Rumunia (historia)**
- Financial Intelligence, FCI 06.2023: https://financialintelligence.ro/investitori-noi-la-bursa-dupa-ipo-hidroelectrica-fondul-de-compensare-publica-primele-cifre-oficiale-crestere-cu-1267-a-numarului-de-investitori-la-final-de-iunie/

**Grecja**
- ATHEX, Monthly Statistics Bulletin (01.2019): https://www.athexgroup.gr/documents/10180/5341974/Issue+184+%28January+2019%29.pdf/0cc7257a-8779-480a-87d2-6f84614146ac

**Chorwacja**
- ECSDA, profil SKDD: https://ecsda.eu/wp-content/uploads/2018/04/HR-SKDD.pdf

**Finlandia**
- Statistics Finland, Households' assets 2025: https://stat.fi/en/publication/cmf41enznb34q07uo8bo742hv
- Euroclear Finland, statystyki: https://www.euroclear.com/finland/en/statistics.html
- Euroclear Finland, osakesäästötili: https://euroclear.com/finland/fi/statistics/equity-savings-accounts.html

**Norwegia**
- Euronext Securities Oslo (VPS), statystyki: https://csdclient.vps.no/pub/about-us/statistics/?lang=en
- Euronext, aktywność inwestorów 2020: https://www.euronext.com/en/news/investor-activity-euronext-growth-during-2020

**Niemcy**
- Bundestag, Drucksache 19/18042 (liczba depozytów 2010–2019, Bundesbank): https://dserver.bundestag.de/btd/19/180/1918042.pdf
- DAI, Aktionärszahlen 2025: https://www.dai.de/fileadmin/user_upload/Pressemitteilung___Aktionaerszahlen_2025__Aktienanlage_weiter_im_Aufwind.pdf
