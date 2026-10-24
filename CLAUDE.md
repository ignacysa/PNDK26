# Kontekst projektu

Ten plik zawiera wyłącznie ustalenia. Opcje, propozycje i wyniki researchu trzymamy w `RESEARCH.md`. Coś trafia tutaj dopiero po decyzji użytkownika.

## Rdzeń badania
Badamy, od czego zależy zaangażowanie Polaków w rynek kapitałowy.

- **Zmienna zależna:** liczba inwestorów, najlepiej **aktywnych inwestorów**. Liczba rachunków maklerskich to wariant zapasowy.
- **Zmienne objaśniające (ustalone 2026-10-24):**
  - dochód,
  - inflacja,
  - roczne stopy zwrotu z giełdy,
  - stopa procentowa banku centralnego.
- Konkretne źródła i miary tych zmiennych są jeszcze do wyboru (patrz `RESEARCH.md`).

- Tytuł jest roboczy i dopasujemy go do ostatecznego kształtu pracy.
- Tytuł roboczy: „Makroekonomiczne i społeczne determinanty liczby rachunków maklerskich w Polsce”.

## Forma
Prezentacja na 7,5–12,5 min, docelowo ok. 10 min.

| Część        | Czas    |
| ------------ | ------- |
| Temat        | 0,5 min |
| Uzasadnienie | 1 min   |
| Metody       | 1–3 min |
| Wyniki       | 4–7 min |
| Wnioski      | 1 min   |

## Struktura prezentacji
Orientacyjnie 1 slajd na minutę, ok. 10 slajdów.

| # | Część | Slajd | Co pokazuje | Czas |
|---|---|---|---|---|
| 1 | Temat | Slajd tytułowy | Tytuł, autor, pytanie badawcze w jednym zdaniu | 0,5 min |
| 2 | Uzasadnienie | Dlaczego ten temat | Kontekst i motywacja, czyli po co to badać | 1 min |
| 3 | Metody | Dane | Zmienna zależna, zmienne objaśniające, źródła, okres i częstotliwość | 0,5–1,5 min |
| 4 | Metody | Metoda badania | Model, sposób estymacji, testy diagnostyczne | 0,5–1,5 min |
| 5 | Wyniki | Zmienna zależna w czasie | Wykres zmiennej zależnej i kluczowe zjawiska (piki, załamania) | 1–1,5 min |
| 6 | Wyniki | Zależności wstępne | Wykresy lub korelacje zmiennych objaśniających ze zmienną zależną | 1–1,5 min |
| 7 | Wyniki | Wyniki modelu | Tabela oszacowań: znaki, istotność, dopasowanie | 1–2 min |
| 8 | Wyniki | Diagnostyka i odporność | Testy modelu, warianty alternatywne | 0,5–1 min |
| 9 | Wyniki | Interpretacja | Co oznaczają najważniejsze efekty, w liczbach i słowach | 0,5–1 min |
| 10 | Wnioski | Wnioski | Odpowiedź na pytanie badawcze, ograniczenia, dalsze kierunki | 1 min |

Suma: 7,5–12,5 min. Przy krótszym wariancie slajdy 8 i 9 można połączyć.

## Ustalone dane
- **Zmienna zależna (zatwierdzona 2026-10-24):** liczba aktywnych rachunków na rynku akcji GPW, półrocznie od I 2003. Źródło: raporty GPW „Udział inwestorów w obrotach” (https://www.gpw.pl/analizy). Dane w `data/gpw_aktywne_rachunki_pl.csv`.
- Źródła zmiennych objaśniających są jeszcze do wyboru (patrz `RESEARCH.md`).

## Ustalone metody
Brak. Dobór metod jest w toku (patrz `RESEARCH.md`).

## Pliki
- `CLAUDE.md`: ustalenia (ten plik).
- `RESEARCH.md`: notatka robocza z opcjami, researchem i otwartymi decyzjami.
- `data/gpw_aktywne_rachunki_pl.csv`: półroczny szereg aktywnych rachunków GPW, wszystkich rachunków KDPW, ludności i wskaźników na 1000 mieszkańców. Generuje go `scripts/gpw_aktywne_rachunki.py` z PDF-ów w `data/raw/gpw/`. Zależności w `requirements.txt`.
- `data/kraje_postransformacyjne_inwestorzy.csv`: aktywni inwestorzy i rachunki w krajach postransformacyjnych (RO, LT, EE, CZ, SK, HR) na tle PL, na 1000 mieszkańców.
- `data/rumunia_litwa_szeregi.csv`: Rumunia (aktywne rachunki ASF kwartalnie 2015–2026, inwestorzy FCI 2008–2026) i Litwa (aktywni inwestorzy według Banku Litwy 2019–2025). Skrypty `scripts/rumunia_asf.py`, `scripts/rumunia_fci.py`, `scripts/litwa_lb.py`, źródła w `data/raw/ro/` i `data/raw/lt/`.
- `NOTATKI_SESJI.md`: przebieg sesji roboczych (kontekst dla kolejnych sesji).
- `data/wegry_beva.csv`: Węgry, liczba inwestorów chronionych przez fundusz kompensacyjny BEVA, rocznie 2002–2025 (skrypt `scripts/wegry_beva.py`, PDF-y w `data/raw/hu/`).
- `data/bulgaria_fki.csv`: Bułgaria, liczba klientów chronionych przez fundusz FKI, rocznie 2008–2025 (PDF-y w `data/raw/bg/`, pomocniczy skrypt `scripts/bulgaria_fki.py`).
- `data/porownanie_krajow_inwestorzy.csv`: to samo dla krajów spoza regionu (FR, DE, SE, FI, KR, IN).
- `data/reczne/`: ręcznie zebrane wartości (z raportów i prasy) ze źródłem i statusem każdej wartości. Plikom wynikowym w `data/` dopisuje ludność i wskaźnik na 1000 mieszkańców skrypt `scripts/porownanie_na_1000.py`.
- `data/eurostat/`: zharmonizowane dane Eurostatu dla 11 krajów postransformacyjnych i krajów odniesienia (inwestowanie przez internet, aktywa gospodarstw w akcjach i funduszach, HICP, PKB per capita, stopa 3M, ludność). Pobiera je `scripts/eurostat_dane.py`.
- `data/raw/gpw/`: surowe raporty GPW w PDF.

## Zasady współpracy
- Temat i uzasadnienie użytkownik uzupełnia sam. Nie wpisuj tam treści bez prośby.
- Dobór danych i metod planujemy wspólnie. Opcje proponuj w `RESEARCH.md`, a do `CLAUDE.md` przenoś tylko to, co użytkownik zatwierdził.
- Komunikacja i treść projektu po polsku.
- Porównania międzynarodowe robimy przede wszystkim z krajami o podobnych do Polski uwarunkowaniach potransformacyjnych (CZ, SK, HU, SI, HR, RO, BG, EE, LV, LT).
- Każdy skrypt używany do pobierania lub przetwarzania danych archiwizujemy w `scripts/`, a wyniki zapisujemy w osobnych plikach CSV w `data/`. Każda wartość musi mieć źródło.
