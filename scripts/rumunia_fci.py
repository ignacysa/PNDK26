"""Szereg liczby inwestorów zgłoszonych do funduszu kompensacyjnego FCI (Rumunia).

Źródło: Fondul de Compensare a Investitorilor (FCI), https://www.fond-fci.ro
- komunikaty kwartalne (od I kw. 2021): https://www.fond-fci.ro/ro/comunicate/
- raporty roczne 2021–2025: https://www.fond-fci.ro/ro/rapoarte-si-situatii-financiare-anuale/
- raporty roczne 2011–2020 (stara strona FCI, katalog /docs/) są dostępne już tylko
  w Wayback Machine, np. https://web.archive.org/web/2024id_/http://www.fond-fci.ro/docs/Raport%20anual%202011.pdf
  (raportu za 2014 nie ma w archiwum; raport za 2018 i 2023 to skany bez warstwy tekstowej).

Miara: „Numar total investitori” – wszyscy inwestorzy (klienci) zgłoszeni przez uczestników
funduszu (SSIF, banki prowadzące działalność inwestycyjną, SAI), którzy mają u nich środki
pieniężne lub instrumenty finansowe. Raport roczny 2011: „Acestia reprezinta toti investitorii
care au detineri la membrii Fondului ceea ce nu inseamna ca tranzactioneaza”. Inwestor
korzystający z kilku pośredników jest liczony kilka razy. To miara posiadaczy, nie aktywnych.

Każdy raport roczny ma tabelę 5 lat (stan na grudzień) i tabelę kwartalną bieżącego roku,
a komunikat kwartalny – tabelę 5 ostatnich kwartałów. Skrypt zbiera wszystkie odczyty,
a dla każdej daty wybiera wartość z dokumentu „własnego” dla tego okresu:
grudzień -> raport roczny za ten rok, pozostałe kwartały -> komunikat za ten kwartał,
dalej raport roczny (tabela kwartalna), dalej późniejsze dokumenty. Różne wartości tej samej
daty w innych dokumentach (rewizje) trafiają do kolumny uwagi.

Zerwanie metodyki: od 30.06.2022 dane są raportowane według Regulaminu ASF nr 10/2022
i nowej Procedury 1 FCI (stan z 31.03.2022 jeszcze według starych zasad). Raporty roczne od
2022 r. podają dla grudnia 2021 wartość zrewidowaną 95 146 zamiast 81 793.

Wynik: wiersze miary „Inwestorzy zgłoszeni do FCI” w data/reczne/rumunia_litwa_szeregi.csv
(pozostałe wiersze pliku zostają bez zmian).

Użycie: python scripts/rumunia_fci.py
"""

import csv
import re
import urllib.parse
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "ro"
OUT = ROOT / "data" / "reczne" / "rumunia_litwa_szeregi.csv"

NEW = "https://www.fond-fci.ro/plugins/files/files/"
OLD = "http://www.fond-fci.ro/docs/"
WAYBACK = "https://web.archive.org/web/2024id_/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

MIARA = "Inwestorzy zgłoszeni do FCI"
COLS = ["kraj", "miara", "typ_miary", "jednostka", "okno_aktywnosci", "wartosc", "data",
        "zrodlo", "status", "uwagi"]
QEND = {"I": "03-31", "II": "06-30", "III": "09-30", "IV": "12-31"}

# (plik lokalny, URL źródłowy, czy pobierać przez Wayback, rodzaj, rok, kwartał)
FILES = [(f"fci_raport_anual_{y}.pdf", OLD + name, True, "anual", y, None) for y, name in [
    (2011, "Raport anual 2011.pdf"), (2012, "Raport Anual 2012.pdf"),
    (2013, "Raport anual 2013.pdf"), (2015, "Raport anual 2015.pdf"),
    (2016, "Raport anual 2016.pdf"), (2017, "Raport anual FCI 2017.pdf"),
    (2018, "Raport anual 2018.pdf"), (2019, "Raport anual 2019.pdf"),
    (2020, "Raport anual FCI 2020.pdf")]]
FILES += [(f"fci_raport_anual_{y}.pdf", NEW + f"Raport anual FCI {y}.pdf", False, "anual", y, None)
          for y in range(2021, 2026)]
FILES += [(f"fci_comunicat_{y}_T{q}.pdf", NEW + name, False, "comunicat", y, q) for y, q, name in [
    (2021, 1, "Comunicat trim. I  2021.pdf"), (2021, 2, "Comunicat trim. II 2021.pdf"),
    (2021, 3, "Comunicat trim. III 2021.pdf"), (2021, 4, "Comunicat trim. IV 2021.pdf"),
    (2022, 1, "Comunicat de presa trim I 2022.pdf"), (2022, 2, "Comunicat trim II 2022.pdf"),
    (2022, 3, "Comunicat trim III 2022.pdf"), (2022, 4, "Comunicat trim IV 2022.pdf"),
    (2023, 1, "Comunicat trim I 2023.pdf"), (2023, 2, "Comunicat de presa iunie 2023.pdf"),
    (2023, 3, "Comunicat de presa  septembrie 2023.pdf"),
    (2023, 4, "Comunicat de presa  decembrie 2023.pdf"),
    (2024, 1, "Comunicat de presa  martie 2024.pdf"), (2024, 2, "Comunicat de presa  iunie 2024.pdf"),
    (2024, 3, "Comunicat de presa septembrie 2024.pdf"),
    (2024, 4, "Comunicat de presa decembrie 2024.pdf"),
    (2025, 1, "Comunicat de presa martie 2025.pdf"), (2025, 2, "Comunicat de presa iunie 2025.pdf"),
    (2025, 3, "Comunicat de presa septembrie 2025.pdf"),
    (2025, 4, "Comunicat de presa decembrie 2025.pdf"),
    (2026, 1, "Comunicat de presa martie 2026.pdf"), (2026, 2, "Comunicat de presa iunie 2026.pdf"),
    (2026, 3, "Comunicat de presa septembrie 2026.pdf")]]


def quote(url):
    head, name = url.rsplit("/", 1)
    return head + "/" + urllib.parse.quote(name)


def download_missing():
    RAW.mkdir(parents=True, exist_ok=True)
    for local, url, via_wayback, *_ in FILES:
        path = RAW / local
        if path.exists():
            continue
        src = (WAYBACK + quote(url)) if via_wayback else quote(url)
        req = urllib.request.Request(src, headers={"User-Agent": UA})
        try:
            data = urllib.request.urlopen(req, timeout=180).read()
        except OSError as e:
            data = b""
            print(f"Błąd pobierania {src}: {e}")
        if data.startswith(b"%PDF"):
            path.write_bytes(data)
            print(f"Pobrano {local}")
        else:
            print(f"BRAK: {local} – pobierz ręcznie z {src}")


def number(tok):
    return int(re.sub(r"[.,\s]", "", tok))


NUM = r"\d{1,3}(?:[.,]\d{3})+"


def pages_text(path):
    return [re.sub(r"[ \t]+", " ", p.extract_text() or "") for p in PdfReader(path).pages]


def header_years(line):
    """'Categorii Dec. 2012 ... Variatie 2015/2016' -> [2012, ...]; obsługuje 'Dec-08' i '11-Dec'."""
    line = re.split(r"(?i)variat", line)[0]
    years = []
    for m in re.finditer(r"(?i)(?:dec\.?\s*-?\s*(\d{4}|\d{2})\b|\b(\d{2})-dec)", line):
        y = m.group(1) or m.group(2)
        years.append(int(y) + 2000 if len(y) == 2 else int(y))
    return years


def parse_report(path, kind, year, quarter):
    """Zwraca listę (data, wartość, strona, opis)."""
    out = []
    pages = pages_text(path)
    for pno, page in enumerate(pages, 1):
        lines = page.splitlines()
        for i, line in enumerate(lines):
            # tabela wieloletnia (grudzień) w raporcie rocznym
            if re.search(r"(?i)^\s*categorii\b", line) and len(header_years(line)) >= 3:
                years = header_years(line)
                for nxt in lines[i + 1:i + 15]:
                    if re.search(r"(?i)total investitori", nxt):
                        vals = re.findall(NUM, nxt)[:len(years)]
                        for y, v in zip(years, vals):
                            out.append((f"{y}-12-31", number(v), pno, "tabela roczna"))
                        break
            # tabela kwartalna bieżącego roku w raporcie rocznym
            if kind == "anual" and re.search(r"(?i)categorii investitori\s*$|martie\s+iunie\s+sept", line):
                for nxt in lines[i + 1:i + 25]:
                    if re.search(r"(?i)total investitori", nxt):
                        vals = re.findall(NUM, nxt)
                        if len(vals) == 4:
                            for q, v in zip(["I", "II", "III", "IV"], vals):
                                out.append((f"{year}-{QEND[q]}", number(v), pno, "tabela kwartalna"))
                        break
    text = re.sub(r"\s+", " ", " ".join(pages))
    if kind == "comunicat":
        m = re.search(r"(?i)num[aă]rul total al investitorilor raporta\w* de (?:membrii|participan\w+) "
                      r"(?:la )?Fond\w*\s*la sf\w+ trimestrului (I{1,3}|IV) al anului (\d{4}) era de (" + NUM + ")", text)
        if m:
            date = f"{m.group(2)}-{QEND[m.group(1)]}"
            pno = next(i for i, p in enumerate(pages, 1) if m.group(3) in p)
            out.append((date, number(m.group(3)), pno, "zdanie „Numarul total al investitorilor”"))
        # tabela 5 ostatnich kwartałów; kolumny to kolejne kwartały kończące się kwartałem
        # komunikatu (nagłówki w dwóch komunikatach mają literówki w roku, więc ich nie czytamy)
        tm = re.search(r"(?i)categori\w* investitori .*?total investitori ((?:" + NUM + r" ?){5})", text)
        if tm:
            vals = re.findall(NUM, tm.group(1))
            ends = []
            yy, qq = year, quarter
            for _ in range(5):
                ends.append(f"{yy}-{QEND[['I', 'II', 'III', 'IV'][qq - 1]]}")
                yy, qq = (yy, qq - 1) if qq > 1 else (yy - 1, 4)
            for date, v in zip(reversed(ends), vals):
                out.append((date, number(v), None, "tabela 5 kwartałów"))
    if kind == "anual":
        m = re.search(r"(?i)num[aă]rul de investitori la sf\S*\s*r\S*itul anului\s*(\d{2}\s?\d{2}),.{0,200}?era de (" + NUM + ")", text)
        if m and int(m.group(1).replace(" ", "")) == year:
            pno = next((i for i, p in enumerate(pages, 1) if m.group(2) in p), None)
            out.append((f"{year}-12-31", number(m.group(2)), pno, "zdanie „Numarul de investitori la sfarsitul anului”"))
    return out


def priority(date, kind, year, quarter, how):
    y, md = int(date[:4]), date[5:]
    if kind == "anual" and year == y and md == "12-31":
        return 0 if how.startswith("zdanie") else 0.5
    if kind == "comunicat" and year == y and QEND[["I", "II", "III", "IV"][quarter - 1]] == md:
        return 1
    if kind == "anual" and year == y:
        return 2
    return 3 + abs(year - y)


def collect():
    cand = {}
    for local, url, via_wayback, kind, year, quarter in FILES:
        path = RAW / local
        if not path.exists():
            continue
        src = (WAYBACK + quote(url)) if via_wayback else quote(url)
        for date, val, pno, how in parse_report(path, kind, year, quarter):
            cand.setdefault(date, []).append((priority(date, kind, year, quarter, how), val, local, src, pno, how))
    return cand


def build_rows(cand):
    rows = []
    for date in sorted(cand):
        opts = sorted(cand[date], key=lambda c: (c[0], not c[5].startswith("zdanie")))
        best = opts[0]
        _, val, local, src, pno, how = best
        others = sorted({(o[1], o[2]) for o in opts if o[1] != val})
        uwagi = (f"FCI, „Numar total investitori” (posiadacze środków/instrumentów u uczestników FCI; "
                 f"klient kilku pośredników liczony wielokrotnie); plik {local}"
                 + (f", s. {pno}" if pno else "") + f", {how}")
        if others:
            uwagi += "; inne wartości tej daty: " + "; ".join(f"{v} ({f})" for v, f in others)
        if date == "2021-12-31":
            uwagi += "; stara metodyka – raporty roczne od 2022 podają wartość zrewidowaną 95 146 (Reg. ASF 10/2022)"
        if date == "2022-03-31":
            uwagi += "; ostatni stan według starej Procedury 1 FCI, od 30.06.2022 nowa metodyka (Reg. ASF 10/2022)"
        rows.append({"kraj": "RO", "miara": MIARA, "typ_miary": "posiadacze", "jednostka": "klienci",
                     "okno_aktywnosci": "stan", "wartosc": val, "data": date, "zrodlo": src,
                     "status": "zweryfikowane", "uwagi": uwagi})
    return rows


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
    rows = build_rows(collect())
    update_csv(rows, {MIARA})
    print(f"Zapisano {len(rows)} wierszy miary „{MIARA}” ({rows[0]['data']} – {rows[-1]['data']}) do {OUT}")
    for r in rows:
        print(r["data"], r["wartosc"], r["uwagi"].split("; plik ")[1][:90])


if __name__ == "__main__":
    main()
