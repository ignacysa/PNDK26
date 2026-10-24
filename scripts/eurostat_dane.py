"""Pobiera zharmonizowane dane Eurostatu dla krajów postransformacyjnych i krajów odniesienia.

Zapisuje pliki w formacie długim (kraj, rok, wartość) do data/eurostat/:
- isoc_inwestowanie_online.csv: % osób 16–74 lat, które kupiły lub sprzedały akcje, obligacje
  albo jednostki funduszy przez internet (isoc_ec_ifi: I_BFIN_SH, 2016–2019;
  isoc_ec_ifi20: I_BFIN_SH1, 2020+, okres odniesienia 3 miesiące, więc w 2020 r. seria jest zerwana).
  Kolumna na_1000_osob_16_74 = procent × 10.
- aktywa_gosp_dom_akcje_fundusze.csv: aktywa gospodarstw domowych (S14_S15) w akcjach
  notowanych (F511) i jednostkach funduszy (F52), % PKB (nasa_10_f_bs).
- hicp_inflacja.csv: HICP, średnia roczna zmiana w % (prc_hicp_aind).
- pkb_per_capita_pps.csv: PKB per capita w PPS (nama_10_pc).
- stopa_3m.csv: 3-miesięczna stopa rynku pieniężnego (irt_st_a); strefa euro jako EA.
- ludnosc.csv: ludność na 1 stycznia (demo_pjan).

Użycie: python scripts/eurostat_dane.py
"""

import csv
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "eurostat"
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"

POSTTRANSFORMACYJNE = ["PL", "CZ", "SK", "HU", "SI", "HR", "RO", "BG", "EE", "LV", "LT"]
ODNIESIENIE = ["DE", "AT", "SE", "EU27_2020"]
KRAJE = POSTTRANSFORMACYJNE + ODNIESIENIE

# (plik wyjściowy, tabela, filtry, opis wskaźnika)
ZAPYTANIA = [
    ("isoc_inwestowanie_online.csv", "isoc_ec_ifi",
     {"indic_is": "I_BFIN_SH", "ind_type": "IND_TOTAL", "unit": "PC_IND"},
     "% osób 16–74 kupujących/sprzedających papiery wartościowe przez internet (12 mies.)"),
    ("isoc_inwestowanie_online.csv", "isoc_ec_ifi20",
     {"indic_is": "I_BFIN_SH1", "ind_type": "IND_TOTAL", "unit": "PC_IND"},
     "% osób 16–74 kupujących/sprzedających papiery wartościowe przez internet (3 mies.)"),
    ("aktywa_gosp_dom_akcje_fundusze.csv", "nasa_10_f_bs",
     {"sector": "S14_S15", "finpos": "ASS", "na_item": "F511", "co_nco": "NCO", "unit": "PC_GDP",
      "sinceTimePeriod": "2003"},
     "Akcje notowane (F511) w aktywach gospodarstw domowych, % PKB"),
    ("aktywa_gosp_dom_akcje_fundusze.csv", "nasa_10_f_bs",
     {"sector": "S14_S15", "finpos": "ASS", "na_item": "F52", "co_nco": "NCO", "unit": "PC_GDP",
      "sinceTimePeriod": "2003"},
     "Jednostki funduszy (F52) w aktywach gospodarstw domowych, % PKB"),
    ("hicp_inflacja.csv", "prc_hicp_aind",
     {"unit": "RCH_A_AVG", "coicop": "CP00", "sinceTimePeriod": "2003"},
     "HICP, średnia roczna zmiana, %"),
    ("pkb_per_capita_pps.csv", "nama_10_pc",
     {"unit": "CP_PPS_EU27_2020_HAB", "na_item": "B1GQ", "sinceTimePeriod": "2003"},
     "PKB per capita, PPS (UE-27 = 2020)"),
    ("stopa_3m.csv", "irt_st_a",
     {"int_rt": "IRT_M3", "sinceTimePeriod": "2003"},
     "Stopa procentowa rynku pieniężnego 3M, %"),
    ("ludnosc.csv", "demo_pjan",
     {"sex": "T", "age": "TOTAL", "sinceTimePeriod": "2003"},
     "Ludność na 1 stycznia"),
]


def fetch(table, filters, geos):
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    params += "".join(f"&geo={g}" for g in geos)
    url = f"{API}{table}?{params}"
    with urllib.request.urlopen(url, timeout=120) as r:
        d = json.load(r)
    ids, size = d["id"], d["size"]
    stride = [1] * len(ids)
    for i in range(len(ids) - 2, -1, -1):
        stride[i] = stride[i + 1] * size[i + 1]
    geo_idx = d["dimension"]["geo"]["category"]["index"]
    time_idx = d["dimension"]["time"]["category"]["index"]
    gi, ti = ids.index("geo"), ids.index("time")
    for g, a in geo_idx.items():
        for t, b in time_idx.items():
            v = d["value"].get(str(a * stride[gi] + b * stride[ti]))
            if v is not None:
                yield g, int(t), v, url


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wyniki = {}
    for plik, tabela, filtry, opis in ZAPYTANIA:
        # stopy 3M dla strefy euro są publikowane tylko jako agregat EA
        geos = KRAJE + (["EA"] if tabela == "irt_st_a" else [])
        for g, rok, v, url in fetch(tabela, filtry, geos):
            wiersz = {"kraj": g, "rok": rok, "wartosc": v, "wskaznik": opis,
                      "tabela": tabela, "grupa": "postransformacyjny" if g in POSTTRANSFORMACYJNE else "odniesienie",
                      "zrodlo": url}
            if plik == "isoc_inwestowanie_online.csv":
                wiersz["na_1000_osob_16_74"] = round(v * 10, 1)
            wyniki.setdefault(plik, []).append(wiersz)

    for plik, wiersze in wyniki.items():
        wiersze.sort(key=lambda r: (r["wskaznik"], r["kraj"], r["rok"]))
        cols = ["kraj", "grupa", "rok", "wartosc"] + \
               (["na_1000_osob_16_74"] if plik == "isoc_inwestowanie_online.csv" else []) + \
               ["wskaznik", "tabela", "zrodlo"]
        with open(OUT / plik, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(wiersze)
        print(f"Zapisano {len(wiersze)} wierszy do {OUT / plik}")


if __name__ == "__main__":
    main()
