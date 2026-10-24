"""Przelicza ręcznie zebrane liczby inwestorów lub rachunków na 1000 mieszkańców.

Wejście: pliki CSV w data/reczne/ (kolumny: kraj, miara, typ_miary, jednostka,
okno_aktywnosci, wartosc, data, zrodlo, status, uwagi). Wartości są zebrane ręcznie
z raportów i prasy; źródło każdej wartości jest w kolumnie `zrodlo`.
Wyjście: plik o tej samej nazwie w data/ z dodanymi kolumnami ludności i wskaźnika.

Ludność: Eurostat demo_pjan (1 stycznia roku z kolumny `data`, a jeśli go brak, najbliższy
dostępny rok); dla krajów spoza Eurostatu Bank Światowy SP.POP.TOTL.

Użycie: python scripts/porownanie_na_1000.py
"""

import csv
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "data" / "reczne"
OUT_DIR = ROOT / "data"

EUROSTAT_URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
                "demo_pjan?sex=T&age=TOTAL&sinceTimePeriod=2000&geo={geo}")
WORLDBANK_URL = ("https://api.worldbank.org/v2/country/{iso2}/indicator/SP.POP.TOTL"
                 "?format=json&date=2000:2026&per_page=100")
NON_EUROSTAT = {"KR", "IN", "US", "JP"}


def get_json(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)


def eurostat_population(geos):
    d = get_json(EUROSTAT_URL.format(geo="&geo=".join(sorted(geos))))
    geo_idx = d["dimension"]["geo"]["category"]["index"]
    time_idx = d["dimension"]["time"]["category"]["index"]
    n_time = len(time_idx)
    pop = {}
    for g, gi in geo_idx.items():
        for t, ti in time_idx.items():
            v = d["value"].get(str(gi * n_time + ti))
            if v is not None:
                pop.setdefault(g, {})[int(t)] = v
    return pop


def worldbank_population(iso2):
    d = get_json(WORLDBANK_URL.format(iso2=iso2))
    return {int(x["date"]): x["value"] for x in d[1] if x["value"] is not None}


def main():
    files = sorted(IN_DIR.glob("*.csv"))
    rows_by_file = {f: list(csv.DictReader(open(f, encoding="utf-8"))) for f in files}
    countries = {r["kraj"] for rows in rows_by_file.values() for r in rows}

    pop = eurostat_population(countries - NON_EUROSTAT)
    sources = {c: "Eurostat demo_pjan" for c in pop}
    for c in countries & NON_EUROSTAT:
        pop[c] = worldbank_population(c)
        sources[c] = "World Bank SP.POP.TOTL"

    for f, rows in rows_by_file.items():
        for r in rows:
            series = pop[r["kraj"]]
            year = int(r["data"][:4])
            year = year if year in series else min(series, key=lambda y: abs(y - year))
            r["ludnosc"] = series[year]
            r["rok_ludnosci"] = year
            r["zrodlo_ludnosci"] = sources[r["kraj"]]
            r["na_1000_mieszk"] = round(float(r["wartosc"]) / series[year] * 1000, 1)
        cols = ["kraj", "miara", "typ_miary", "jednostka", "okno_aktywnosci", "wartosc", "data",
                "ludnosc", "rok_ludnosci", "zrodlo_ludnosci", "na_1000_mieszk", "zrodlo", "status", "uwagi"]
        out = OUT_DIR / f.name
        with open(out, "w", newline="", encoding="utf-8") as fo:
            w = csv.DictWriter(fo, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        print(f"Zapisano {len(rows)} wierszy do {out}")


if __name__ == "__main__":
    main()
