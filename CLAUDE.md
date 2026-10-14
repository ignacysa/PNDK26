# Kontekst projektu

Ten plik zawiera tylko ustalenia. Opcje, założenia do dyskusji i wyniki researchu trzymamy w `RESEARCH.md`. Coś trafia tutaj dopiero po decyzji użytkownika.

## Temat
Makroekonomiczne i społeczne determinanty liczby rachunków maklerskich w Polsce.

## Forma
Prezentacja, łącznie ok. 7,5–12,5 min:

| Część        | Czas    |
| ------------ | ------- |
| Temat        | 0,5 min |
| Uzasadnienie | 1 min   |
| Metody       | 1–3 min |
| Wyniki       | 4–7 min |
| Wnioski      | 1 min   |

## Struktura pracy
- Temat
- Uzasadnienie
- Metody
  - Dane
  - Metody badania
- Wyniki
- Wnioski

## Ustalone dane
- Liczba rachunków maklerskich w Polsce: KDPW, raport „Liczba rachunków papierów wartościowych oraz rachunków zbiorczych prowadzonych przez uczestników KDPW”, https://data.kdpw.pl (pliki miesięczne od 01.2020).

## Pliki
- `CLAUDE.md`: ustalenia (ten plik).
- `RESEARCH.md`: notatka robocza z opcjami, założeniami i otwartymi decyzjami.
- `scripts/pobierz_kdpw.py`: pobiera dane KDPW do `data/kdpw/` (surowe pliki w `raw/`, CSV z sumą i z podziałem na uczestników). Zależności w `requirements.txt`.
- Dokument projektu (szkielet sekcji): https://claude.ai/code/artifact/88f2d461-d077-4e4a-a7f5-6b9ab03d23e1

## Zasady współpracy
- Temat i uzasadnienie użytkownik uzupełnia sam. Nie wpisuj tam treści bez prośby.
- Dobór danych i metod badawczych planujemy wspólnie. Proponuj opcje w `RESEARCH.md`, a do `CLAUDE.md` przenoś tylko to, co użytkownik zatwierdził.
- Komunikacja i treść projektu po polsku.
