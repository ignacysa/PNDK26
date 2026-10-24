"""Wyciąga półroczny szereg aktywnych rachunków z raportów GPW i zapisuje go do CSV.

Źródła (pliki w data/raw/gpw/, pobrane ze strony https://www.gpw.pl/analizy):
- Udzial_inwestorow_2019.pdf   -> półrocza I 2003 – II 2015
- Udzial_inwestorow_1H2026.pdf -> półrocza I 2016 – I 2026
Ludność Polski na 1 stycznia: Eurostat, tabela demo_pjan.

Użycie: python scripts/gpw_aktywne_rachunki.py
"""

import csv
import json
import re
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "gpw"
OUT = ROOT / "data" / "gpw_aktywne_rachunki_pl.csv"

GPW_URL = "https://www.gpw.pl/pub/GPW/analizy/"
EUROSTAT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "demo_pjan?sex=T&age=TOTAL&geo=PL&sinceTimePeriod=2003"
)

# (plik, pierwszy rok w tabeli, ostatni rok, który bierzemy z tego pliku)
SOURCES = [
    ("Udzial_inwestorow_2019.pdf", 2003, 2015),
    ("Udzial_inwestorow_1H2026.pdf", 2016, 2026),
]

HEADER = "Rachunki internetowe Aktywne rachunki - akcje"
ROW = re.compile(r"^(I|II) (.+?) (?:I|II) (.+?) (?:I|II) (.+)$")


def grouped(tokens):
    """Łączy tokeny zapisane z separatorem tysięcy ('1 373 380') w liczbę albo zwraca None."""
    if not tokens or not (1 <= len(tokens[0]) <= 3 or len(tokens) == 1):
        return None
    if any(len(t) != 3 for t in tokens[1:]):
        return None
    return int("".join(tokens))


def pct_and_count(text):
    """'68 934 313' -> (68, 934313); '---' -> (None, None)."""
    tokens = text.split()
    if "---" in tokens:
        return None, None
    return int(tokens[0]), grouped(tokens[1:])


def two_counts(text):
    """'1 373 380 1 413 042' -> (1373380, 1413042). Wybiera podział, przy którym KDPW >= CG i są podobnej wielkości."""
    tokens = text.split()
    if tokens[0] == "---":
        return None, grouped(tokens[1:])
    for i in range(1, len(tokens)):
        cg, kdpw = grouped(tokens[:i]), grouped(tokens[i:])
        if cg and kdpw and 1.0 <= kdpw / cg <= 1.25:
            return cg, kdpw
    raise ValueError(f"Nie udało się podzielić liczby rachunków: {text!r}")


def parse_pdf(path, first_year, last_year):
    text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    lines = text[text.index(HEADER):].splitlines()
    rows, year = [], first_year
    for line in lines:
        m = ROW.match(line.strip())
        if not m:
            if rows and line.strip().startswith("II II"):
                break  # koniec tabeli
            continue
        half, internet, active, accounts = m.groups()
        if year > last_year:
            break
        pct_internet, n_internet = pct_and_count(internet)
        pct_active, n_active = pct_and_count(active)
        n_cg, n_kdpw = two_counts(accounts)
        if n_active and n_cg:
            assert abs(n_active / n_cg * 100 - pct_active) <= 1, (year, half, line)
        rows.append({
            "okres": f"{year}H{1 if half == 'I' else 2}",
            "rok": year,
            "polrocze": half,
            "aktywne_rachunki_akcje": n_active,
            "aktywne_pct_rachunkow_CG": pct_active,
            "rachunki_CG": n_cg,
            "rachunki_KDPW": n_kdpw,
            "rachunki_internetowe": n_internet,
            "zrodlo": GPW_URL + path.name,
        })
        if half == "II":
            year += 1
    return rows


def population():
    with urllib.request.urlopen(EUROSTAT_URL) as r:
        d = json.load(r)
    times = d["dimension"]["time"]["category"]["index"]
    return {int(t): d["value"][str(i)] for t, i in times.items() if str(i) in d["value"]}


def download_missing():
    """Pobiera brakujące PDF-y. Serwer GPW bywa niedostępny dla skryptów (reset połączenia);
    wtedy trzeba pobrać plik ręcznie w przeglądarce do data/raw/gpw/."""
    RAW.mkdir(parents=True, exist_ok=True)
    for name, _, _ in SOURCES:
        path = RAW / name
        if path.exists():
            continue
        req = urllib.request.Request(GPW_URL + name, headers={"User-Agent": "Mozilla/5.0"})
        try:
            path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
            print(f"Pobrano {name}")
        except OSError as e:
            raise SystemExit(f"Nie udało się pobrać {GPW_URL + name} ({e}). "
                             f"Pobierz plik ręcznie do {path}.")


def main():
    download_missing()
    rows = []
    for name, first, last in SOURCES:
        rows += parse_pdf(RAW / name, first, last)

    pop = population()
    last_pop_year = max(pop)
    for r in rows:
        year = min(r["rok"], last_pop_year)
        r["ludnosc_1_stycznia"] = pop[year]
        r["rok_ludnosci"] = year
        for col, src in [("aktywne_na_1000_mieszk", "aktywne_rachunki_akcje"),
                         ("rachunki_KDPW_na_1000_mieszk", "rachunki_KDPW")]:
            r[col] = round(r[src] / pop[year] * 1000, 2) if r[src] else None

    cols = ["okres", "rok", "polrocze", "aktywne_rachunki_akcje", "aktywne_pct_rachunkow_CG",
            "rachunki_CG", "rachunki_KDPW", "rachunki_internetowe", "ludnosc_1_stycznia",
            "rok_ludnosci", "aktywne_na_1000_mieszk", "rachunki_KDPW_na_1000_mieszk", "zrodlo"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Zapisano {len(rows)} półroczy ({rows[0]['okres']}–{rows[-1]['okres']}) do {OUT}")


if __name__ == "__main__":
    main()
