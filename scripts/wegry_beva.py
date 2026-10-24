"""Wyciąga roczny szereg liczby inwestorów chronionych przez węgierski fundusz BEVA i zapisuje go do CSV.

Źródło: raporty z działalności Befektető-védelmi Alap (BEVA, węgierski fundusz kompensacyjny
inwestorów), https://bva.hu/hu/beva/tevekenysegi-jelentes/. Członkami BEVA są banki, firmy
inwestycyjne i TFI; co kwartał raportują liczbę klientów (osób) z rachunkami papierów
wartościowych lub pieniężnymi objętymi ochroną. To miara posiadania, nie aktywności.
Nie obejmuje rachunków w Skarbie Państwa (Magyar Államkincstár), który nie jest członkiem BEVA.

Tabele w raportach mają wiersz „Adatszolgáltatás éve” (rok raportowania) i wiersz z liczbą
inwestorów („Védett ügyfélszám”, „Védett/Biztosított befektetők száma (ezer fő)”). Dla każdego
roku bierzemy wartość z najnowszego raportu, który ją podaje.

Użycie: python scripts/wegry_beva.py  (pobiera brakujące PDF-y do data/raw/hu/)
"""

import csv
import re
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hu"
OUT = ROOT / "data" / "reczne" / "wegry_beva.csv"
INDEX = "https://bva.hu/hu/beva/tevekenysegi-jelentes/"

LABELLED_YEARS = re.compile(r"(?i)adatszolgáltatás éve\s*[¹1]?\s*((?:20\d\d\s?\.\s*){4,})")
BARE_YEARS = re.compile(r"((?:20\d\d\s?\.\s*){4,})\s*$")
VALUES = re.compile(
    r"(?i)(V[eé]dett [uü]gyf[eé]lsz[aá]m\s*[¹²1]?(?:\s*\(ezer f[őo]\))?"
    r"|(?:V[eé]dett|Biztos[ií]tott) befektet[őo]k\s*sz[aá]ma\s*1?\s*\(ezer f[őo]\)"
    r"|A biztos[ií]tott befektet[őo]k sz[aá]ma)\s*([\d\.\s]+)")


def download_reports():
    RAW.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(INDEX, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
    for href in sorted(set(re.findall(r'href="(/wp-content/uploads/[^"]+\.pdf)"', html))):
        name = urllib.request.unquote(href.rsplit("/", 1)[-1])
        path = RAW / name
        if not path.exists():
            req = urllib.request.Request("https://bva.hu" + href, headers={"User-Agent": "Mozilla/5.0"})
            path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
            print(f"Pobrano {name}")


def split_numbers(text, n):
    """Dzieli '643.915 1.044.208' (osoby, kropka = separator tysięcy), '858 1.045' (tys. osób)
    albo '1 098 1 104' (tys. osób, spacja = separator tysięcy) na n liczb w osobach."""
    tokens = text.split()
    if any("." in t for t in tokens[:n]):
        nums = [int(t.replace(".", "")) for t in tokens[:n]]
    else:
        nums, i = [], 0
        while i < len(tokens) and len(nums) < n:
            tok = tokens[i]
            if len(tok) == 1 and i + 1 < len(tokens) and len(tokens[i + 1]) == 3:
                tok += tokens[i + 1]
                i += 1
            nums.append(int(tok))
            i += 1
    if len(nums) != n:
        return None
    return [v if v > 100_000 else v * 1000 for v in nums]


def parse(path):
    text = re.sub(r"\s+", " ", "\n".join(p.extract_text() or "" for p in PdfReader(path).pages))
    text = re.sub(r"Adatszolg\s*[aá]\s*l\s*t\s*a\s*t\s*[aá]\s*s", "Adatszolgáltatás", text)
    text = text.replace("2007 .", "2007.")
    found = {}
    for m in VALUES.finditer(text):
        before = text[max(0, m.start() - 600):m.start()]
        labelled = list(LABELLED_YEARS.finditer(before))
        bare = BARE_YEARS.search(before)
        if labelled:
            years_text = labelled[-1].group(1)
        elif bare:
            years_text = bare.group(1)
        else:
            continue
        years = [int(y) for y in re.findall(r"20\d\d", years_text)]
        values = split_numbers(m.group(2), len(years))
        if values and all(500_000 <= v <= 2_000_000 for v in values):
            for y, v in zip(years, values):
                found.setdefault(y, v)
    return found


def main():
    download_reports()
    best = {}  # rok -> (rok raportu, wartość, plik)
    for path in sorted(RAW.glob("*.pdf")):
        report_year = max(int(y) for y in re.findall(r"20\d\d", path.name))
        for year, value in parse(path).items():
            if year not in best or report_year > best[year][0]:
                best[year] = (report_year, value, path.name)

    cols = ["kraj", "miara", "typ_miary", "jednostka", "okno_aktywnosci", "wartosc", "data",
            "zrodlo", "status", "uwagi"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for year in sorted(best):
            _, value, name = best[year]
            w.writerow({
                "kraj": "HU",
                "miara": "Inwestorzy chronieni przez fundusz kompensacyjny BEVA",
                "typ_miary": "posiadacze",
                "jednostka": "osoby",
                "okno_aktywnosci": "stan",
                "wartosc": value,
                "data": f"{year}-12-31",
                "zrodlo": "https://bva.hu/hu/beva/tevekenysegi-jelentes/",
                "status": "zweryfikowane",
                "uwagi": f"rok raportowania (adatszolgáltatás éve); raport {name} w data/raw/hu/; "
                         "od ok. 2010 r. raporty podają wartości w tys. osób",
            })
    print(f"Zapisano {len(best)} lat ({min(best)}–{max(best)}) do {OUT}")
    for year in sorted(best):
        print(year, best[year][1], best[year][2])


if __name__ == "__main__":
    main()
