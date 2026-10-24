"""Szereg liczby aktywnych rachunków klientów firm inwestycyjnych SSIF (Rumunia) z raportów ASF.

Źródło: Autoritatea de Supraveghere Financiară (ASF), raporty kwartalne, półroczne,
9-miesięczne i roczne „Raport privind evoluția pieței de capital”
(lista: https://asfromania.ro/ro/a/970/rapoarte -> „Rapoarte piața de capital”,
roczniki 2019–2026 i „Arhiva” 2014–2018). W rozdziale o pośrednikach (SSIF) raporty od
połowy 2016 r. podają zdanie „Numărul cumulat al conturilor de clienți activi ai SSIF-urilor
la finalul lunii ... a fost de N (un investitor poate avea simultan conturi deschise la mai
mulți intermediari)”. Raporty za 2015 r. i I kw. 2016 r. podają „clienți activi” obok liczby
wszystkich klientów SSIF; raporty od I kw. 2026 r. – liczbę wszystkich rachunków klientów
i „din care N clienți activi”. Raporty z lat 2024–2025 podają wartości zaokrąglone („124 mii”).
Raport za 2025 r. ma ponad 10 MB i nie jest w Wayback Machine, dlatego stan z 31.12.2025
to suma kolumny „Conturi active” w arkuszu „Grafic 29” załącznika XLSX do tego raportu
(https://asfromania.ro/uploads/articole/attachments/69ce49c580ba0714890712.xlsx).

Definicja: raporty nie definiują „cont activ”. Według prasy cytującej ASF (np.
https://financialintelligence.ro/5000-de-investitori-nu-mai-tranzactioneaza-activ-la-bursa-fata-de-2016/)
to rachunek, na którym w ostatnich 6 miesiącach była co najmniej jedna transakcja; ASF zaczęła
publikować tę liczbę w połowie 2016 r. Rachunek ≠ osoba (jedna osoba może mieć rachunki
w kilku SSIF). Nie obejmuje klientów banków ani firm zagranicznych (np. brokerów z UE).

Serwer ASF ma zabezpieczenie przed botami (F5/TSPD), dlatego skrypt najpierw próbuje
pobrać plik bezpośrednio, a gdy dostanie stronę HTML zamiast PDF, pobiera surowy plik
z Wayback Machine (https://web.archive.org/web/<rok>id_/<url>). Gdy i to zawiedzie,
plik trzeba pobrać ręcznie w przeglądarce do data/raw/ro/ pod nazwą z listy REPORTS
(tak pobrano większość plików w data/raw/ro/asf_*).

Wynik: wiersze miar „Aktywne rachunki klientów SSIF (ASF)” i „Rachunki klientów SSIF ogółem
(ASF)” w data/reczne/rumunia_litwa_szeregi.csv (pozostałe wiersze pliku zostają bez zmian).

Użycie: python scripts/rumunia_asf.py
"""

import csv
import re
import time
import urllib.request
import zipfile
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "ro"
OUT = ROOT / "data" / "reczne" / "rumunia_litwa_szeregi.csv"

BASE = "https://asfromania.ro/uploads/articole/attachments/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# (koniec okresu, plik w data/raw/ro/, identyfikator załącznika ASF, tytuł raportu)
REPORTS = [
    ("2014-12-31", "asf_piata_capital_2014.pdf", "60782f60bfd03099197541", "Piața de capital la 31 decembrie 2014"),
    ("2015-03-31", "asf_piata_capital_2015_T1.pdf", "60782f445854a403414822", "Raport Piața de capital la 31 martie 2015"),
    ("2015-09-30", "asf_piata_capital_2015_9M.pdf", "60782f2b6786a334337788", "Raport Piața de capital la 30 septembrie 2015"),
    ("2015-12-31", "asf_piata_capital_2015.pdf", "60782f0959a0b404857733", "Evoluția pieței de capital la 31.12.2015"),
    ("2016-03-31", "asf_piata_capital_2016_T1.pdf", "60782ef02e896042197202", "Evoluția pieței de capital - trimestrul I 2016"),
    ("2016-06-30", "asf_piata_capital_2016_S1.pdf", "60782ed788ae8198647009", "Evoluția pieței de capital din România - semestrul I 2016"),
    ("2016-09-30", "asf_piata_capital_2016_9M.pdf", "60782ebbd24c3173710331", "Evoluția pieței de capital - trimestrul III 2016"),
    ("2016-12-31", "asf_piata_capital_2016.pdf", "60782e96ac62f787225264", "Evoluția pieței de capital din România în anul 2016"),
    ("2017-03-31", "asf_piata_capital_2017_T1.pdf", "60782e3f586ea745399930", "Evoluția pieței de capital în trimestrul I 2017"),
    ("2017-06-30", "asf_piata_capital_2017_S1.pdf", "60782e2183f17598376906", "Evoluția pieței de capital în semestrul I 2017"),
    ("2017-09-30", "asf_piata_capital_2017_9M.pdf", "60782e0706e3f645361019", "Evoluția pieței de capital în trimestrul III 2017"),
    ("2017-12-31", "asf_piata_capital_2017.pdf", "60782dde17afb618142221", "Evoluția pieței de capital în anul 2017"),
    ("2018-03-31", "asf_piata_capital_2018_T1.pdf", "60782da33b5b3156016160", "Evoluția pieței de capital în primul trimestru din 2018"),
    ("2018-06-30", "asf_piata_capital_2018_S1.pdf", "60782d84e9864498989730", "Evoluția pieței de capital în primul semestru din 2018"),
    ("2018-09-30", "asf_piata_capital_2018_9M.pdf", "60782d65947a9865270048", "Evoluția pieței de capital în primele 9 luni din 2018"),
    ("2018-12-31", "asf_piata_capital_2018.pdf", "60782d454f173842512066", "Evoluția pieței de capital în anul 2018"),
    ("2019-03-31", "asf_piata_capital_2019_T1.pdf", "60782ada13313393059482", "Evoluția pieței de capital în primele 3 luni din 2019"),
    ("2019-06-30", "asf_piata_capital_2019_S1.pdf", "60782ac03e7b0575693543", "Evoluția pieței de capital în primul semestru din 2019"),
    ("2019-09-30", "asf_piata_capital_2019_9M.pdf", "60782a9aae7a8766160083", "Evoluția pieței de capital - trimestrul III 2019"),
    ("2019-12-31", "asf_piata_capital_2019.pdf", "60782a7f30212790927864", "Evoluția pieței de capital în anul 2019"),
    ("2020-03-31", "asf_piata_capital_2020_T1.pdf", "60782a28d444e752745423", "Evoluția pieței de capital în trimestrul I 2020"),
    ("2020-06-30", "asf_piata_capital_2020_S1.pdf", "60782a09d22d2507738536", "Evoluția pieței de capital din România în S1 2020"),
    ("2020-09-30", "asf_piata_capital_2020_9M.pdf", "607829e86ef4a879771352", "Evoluția pieței de capital din România în T3 2020"),
    ("2020-12-31", "asf_piata_capital_2020.pdf", "607829cc000c2611893109", "Raport privind evoluția pieței de capital în 2020"),
    ("2021-03-31", "asf_piata_capital_2021_T1.pdf", "60efe342ad73d454231560", "Raport privind evoluția pieței de capital - T1 2021"),
    ("2021-06-30", "asf_piata_capital_2021_S1.pdf", "61726384a2cba742824141", "Raport privind evoluția pieței de capital - S1 2021"),
    ("2021-09-30", "asf_piata_capital_2021_9M.pdf", "61e53ac9f1ddd033288431", "Raport privind evoluția pieței de capital la 9 luni 2021"),
    ("2021-12-31", "asf_piata_capital_2021.pdf", "6267b18cdcc72653798691", "Raport privind evoluția pieței de capital în anul 2021"),
    ("2022-03-31", "asf_piata_capital_2022_T1.pdf", "62d12c5381c87503956252", "Raport privind evolutia pieței de capital în T1 2022"),
    ("2022-06-30", "asf_piata_capital_2022_S1.pdf", "635fd46e34ff6151033427", "Raport privind evoluția pieței de capital în S1 2022"),
    ("2022-09-30", "asf_piata_capital_2022_9M.pdf", "63a4261ea40d6688413548", "Raport privind evoluția pieței de capital în primele 9 luni ale anului 2022"),
    ("2022-12-31", "asf_piata_capital_2022.pdf", "6433fde99d9c3382096235", "Raport privind evoluția pieței de capital în anul 2022"),
    ("2023-03-31", "asf_piata_capital_2023_T1.pdf", "64b521b5b2aeb222751332", "Raport privind evoluția pieței de capital în T1 2023"),
    ("2023-06-30", "asf_piata_capital_2023_S1.pdf", "65324bb8620bc990953384", "Raport privind evoluția pieței de capital în Semestrul I 2023"),
    ("2023-09-30", "asf_piata_capital_2023_9M.pdf", "65f2d6255bf05190940196", "Raport privind evoluția pieței de capital în T3 2023"),
    ("2023-12-31", "asf_piata_capital_2023.pdf", "660e85c7e1da6503504773", "Raport privind evoluția pieței de capital în 2023"),
    ("2024-03-31", "asf_piata_capital_2024_T1.pdf", "667d11cb16d65490651962", "Raport privind evoluția pieței de capital în T1 2024"),
    ("2024-06-30", "asf_piata_capital_2024_S1.pdf", "66f693ed2c973478421921", "Raport privind evoluția pieței de capital în primul Semestru din 2024"),
    ("2024-09-30", "asf_piata_capital_2024_9M.pdf", "676a7b60e1330288816869", "Raport privind evoluția pieței de capital în primele 9 luni ale anului 2024"),
    ("2024-12-31", "asf_piata_capital_2024.pdf", "67ee8807703e7535579959", "Raport privind evoluția pieței de capital în anul 2024"),
    ("2025-03-31", "asf_piata_capital_2025_T1.pdf", "68625a10da774468408822", "Raportul privind evoluția pieței de capital în primul trimestru din anul 2025"),
    ("2025-06-30", "asf_piata_capital_2025_S1.pdf", "68da8aba65e9e347257616", "Raportul privind evoluția pieței de capital în primul semestru din anul 2025"),
    ("2025-09-30", "asf_piata_capital_2025_9M.pdf", "69491c5a8dcea135792448", "Raportul privind evoluția pieței de capital în primele 9 luni din anul 2025"),
    ("2026-03-31", "asf_piata_capital_2026_T1.pdf", "6a3e5788e929f849770861", "Raportul privind evoluția pieței de capital în primul trimestru din anul 2026"),
    ("2026-06-30", "asf_piata_capital_2026_S1.pdf", "6abd1839bd453114384009", "Raportul privind evoluția pieței de capital în primul semestru din anul 2026"),
]
# Raport za 2025 r. (69d745100f7af086123472.pdf) jest za duży – używamy jego załącznika XLSX.
ANNEX_2025 = ("2025-12-31", "asf_piata_capital_2025_anexa.xlsx", "69ce49c580ba0714890712",
              "Raportul privind evoluția pieței de capital în anul 2025 – Anexa (arkusz Grafic 29)")

ACTIVE = "Aktywne rachunki klientów SSIF (ASF)"
TOTAL = "Rachunki klientów SSIF ogółem (ASF)"
COLS = ["kraj", "miara", "typ_miary", "jednostka", "okno_aktywnosci", "wartosc", "data",
        "zrodlo", "status", "uwagi"]
DEFINICJA = ("rachunek z ≥1 transakcją w ostatnich 6 miesiącach (definicja z prasy cytującej ASF, "
             "raport jej nie podaje); suma rachunków we wszystkich SSIF, osoba z kilkoma SSIF liczona kilka razy")
# Uwagi do pojedynczych raportów
NOTES = {
    "2015-12-31": "w raporcie „clienți activi” (24.567 z 78.187 klientów SSIF), przed wprowadzeniem stałego wskaźnika",
    "2016-03-31": "w raporcie „clienți activi” (15.178 z 77.741 klientów SSIF)",
    "2017-03-31": ("NIEPEWNE: raport za I kw. 2017 pisze „la finalul anului 2016 a fost de 14,409”, "
                   "a raport roczny 2016 podaje 21.985 – najpewniej błąd w opisie okresu; przypisano 31.03.2017"),
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def complete(data, ext):
    """PDF musi mieć nagłówek i znacznik końca (Wayback bywa ucięty); XLSX to archiwum ZIP."""
    if ext == ".pdf":
        return data.startswith(b"%PDF") and b"%%EOF" in data[-2048:]
    return data.startswith(b"PK")


def download_missing():
    RAW.mkdir(parents=True, exist_ok=True)
    missing = []
    for date, name, att, _ in REPORTS + [ANNEX_2025]:
        path = RAW / name
        if path.exists():
            continue
        ext = Path(name).suffix
        url = BASE + att + ext
        data = b""
        for candidate in (url, f"https://web.archive.org/web/{date[:4]}id_/{url}"):
            try:
                data = fetch(candidate)
            except OSError:
                data = b""
            if complete(data, ext):
                break
            time.sleep(3)
        if complete(data, ext):
            path.write_bytes(data)
            print(f"Pobrano {name}")
        else:
            missing.append((name, url))
        time.sleep(2)
    for name, url in missing:
        print(f"BRAK: {name} – pobierz ręcznie z {url}")


def norm(text):
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"(\d)([.,]) (\d{3})\b", r"\1\2\3", text)  # '16. 391' -> '16.391'


def to_int(num, mii):
    """'16,009' -> 16009; '132,5' + mii -> 132500 (zaokrąglone)."""
    if mii:
        return round(float(num.replace(",", ".")) * 1000)
    return int(re.sub(r"[.,\s]", "", num))


NUM = r"\d{1,3}(?:[.,]\d{1,3})*"


def extract(pages):
    """Zwraca (aktywne, wszystkie, zaokrąglone, cytat, strona) albo None."""
    text = norm(" ".join(pages))
    # wariant 2026: wszystkie rachunki + „din care N clienți activi”
    m = re.search(r"(?i)(Num[aă]rul cumulat al conturilor de clien\w+ ai SSIF\W*urilor[^.]{0,80}? a fost de "
                  r"(" + NUM + r")( mii)?, din care (" + NUM + r") clien\w+ activi)", text)
    if m:
        return (to_int(m.group(4), False), to_int(m.group(2), bool(m.group(3))), bool(m.group(3)),
                m.group(1), m.group(4))
    # wariant standardowy 2016–2025
    m = re.search(r"(?i)(Num[aă]rul (?:cumulat|total) al conturilor[^.]{0,40}?activ[^.]{0,120}? a fost de "
                  r"(" + NUM + r")( mii)?)", text)
    if m:
        return to_int(m.group(2), bool(m.group(3))), None, bool(m.group(3)), m.group(1), m.group(2)
    # warianty 2015 i I kw. 2016: klienci aktywni obok wszystkich klientów
    m = re.search(r"(?i)(Dintre cei (" + NUM + r") clien\w+ ai SSIF, doar (" + NUM + r") sunt clien\w+ activi)", text)
    if not m:
        m = re.search(r"(?i)(num[aă]rul cumulat al clien\w+ SSIF[^.]{0,120}? la (" + NUM + r"), din care doar ("
                      + NUM + r") dintre ace\w+ sunt clien\w+ activi)", text)
    if m:
        return to_int(m.group(3), False), to_int(m.group(2), False), False, m.group(1), m.group(3)
    # tekst z rozstrzelonymi literami (np. „N u mă r u l cu m u l a t”): szukamy bez spacji
    flat = re.sub(r"\s", "", text)
    m = re.search(r"(?i)(num[aă]rulcumulatalconturilor\w{0,40}?activ\w{0,120}?afostde(\d{1,3}[.,]\d{3}))", flat)
    if m:
        return to_int(m.group(2), False), None, False, m.group(1), m.group(2)
    return None


def page_of(pages, token):
    for i, p in enumerate(pages, 1):
        t = norm(p)
        if token in t and re.search(r"(?i)conturilor|clien", t) and "...." not in t[:200]:
            return i
    for i, p in enumerate(pages, 1):
        if token in re.sub(r"\s", "", p):
            return i
    return None


def annex_sum(path):
    """Suma kolumny „Conturi active” w arkuszu z wykresem aktywów w custodii vs rachunki aktywne."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        x = z.read("xl/sharedStrings.xml").decode("utf8")
        shared = ["".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))
                  for si in re.findall(r"<si>(.*?)</si>", x, re.S)]
    for name in sorted(n for n in z.namelist() if n.startswith("xl/worksheets/sheet")):
        x = z.read(name).decode("utf8")
        cells = {}
        for attrs, inner in re.findall(r"<c ([^>]*?)(?:/>|>(.*?)</c>)", x, re.S):
            v = re.search(r"<v>(.*?)</v>", inner or "")
            if not v:
                continue
            ref = re.search(r'r="([A-Z]+)(\d+)"', attrs)
            val = shared[int(v.group(1))] if 't="s"' in attrs else v.group(1)
            cells[(ref.group(1), int(ref.group(2)))] = val
        hdr = [k for k, v in cells.items() if isinstance(v, str) and v.strip() == "Conturi active"]
        if hdr:
            col, row = hdr[0]
            vals = [int(float(v)) for (c, r), v in cells.items() if c == col and r > row]
            return sum(vals), len(vals), name
    raise ValueError("Nie znaleziono kolumny „Conturi active” w załączniku")


def row(miara, typ, okno, val, date, src, uwagi):
    return {"kraj": "RO", "miara": miara, "typ_miary": typ, "jednostka": "rachunki",
            "okno_aktywnosci": okno, "wartosc": val, "data": date, "zrodlo": src,
            "status": "zweryfikowane", "uwagi": uwagi}


def build_rows():
    rows, missing = [], []
    for date, name, att, title in REPORTS:
        path = RAW / name
        src = BASE + att + ".pdf"
        if not path.exists():
            missing.append((date, name, "brak pliku"))
            continue
        try:
            pages = [p.extract_text() or "" for p in PdfReader(path).pages]
        except Exception as e:  # uszkodzony plik
            missing.append((date, name, f"nie da się odczytać PDF ({e})"))
            continue
        res = extract(pages)
        if not res:
            missing.append((date, name, "brak zdania o rachunkach aktywnych (lub skan bez tekstu)"))
            continue
        active, total, rounded, quote, token = res
        pno = page_of(pages, token)
        base = f"ASF, „{title}”, s. {pno} (plik {name})"
        cyt = f"cytat: „{quote[:200]}”"
        extra = [NOTES[date]] if date in NOTES else []
        if rounded:
            extra.append("w raporcie wartość zaokrąglona")
        rows.append(row(ACTIVE, "aktywni", "6 miesięcy", active, date, src,
                        "; ".join([DEFINICJA, base] + extra + [cyt])))
        if total:
            rows.append(row(TOTAL, "posiadacze", "stan", total, date, src,
                            "; ".join([f"wszystkie rachunki (klienci) SSIF łącznie, w tym nieaktywne; {base}"]
                                      + (["w raporcie wartość zaokrąglona"] if rounded else []) + [cyt])))
    date, name, att, title = ANNEX_2025
    path = RAW / name
    if path.exists():
        total_active, n, sheet = annex_sum(path)
        rows.append(row(ACTIVE, "aktywni", "6 miesięcy", total_active, date, BASE + att + ".xlsx",
                        f"{DEFINICJA}; ASF, „{title}” – suma kolumny „Conturi active” dla {n} SSIF "
                        f"({sheet}, plik {name}); stan na 30/31.12.2025; suma zgodna z liczbą 151 412 znaną z prasy (artykułu nie weryfikowano)"))
    return rows, missing


def update_csv(rows, measures):
    old = []
    if OUT.exists():
        with open(OUT, encoding="utf-8", newline="") as f:
            old = [r for r in csv.DictReader(f) if r["miara"] not in measures]
    allrows = old + rows
    allrows.sort(key=lambda r: (r["kraj"], r["miara"], r["data"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(allrows)


def main():
    download_missing()
    rows, missing = build_rows()
    update_csv(rows, {ACTIVE, TOTAL})
    for r in rows:
        print(r["miara"][:12], r["data"], r["wartosc"])
    for date, name, why in missing:
        print(f"Bez wartości: {date} {name} – {why}")
    print(f"Zapisano {len(rows)} wierszy do {OUT}")


if __name__ == "__main__":
    main()
