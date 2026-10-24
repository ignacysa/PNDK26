"""Pobiera raporty roczne bułgarskiego Funduszu Kompensacji Inwestorów (FKI) i wypisuje zdania
z liczbą klientów objętych ochroną.

Źródło: Фонд за компенсиране на инвеститорите, https://sfund-bg.com (zakładka „Годишни отчети на ФКИ”).
Uczestnicy funduszu (firmy inwestycyjne, banki prowadzące działalność maklerską, TFI) co pół roku
raportują liczbę klientów, których aktywa podlegają kompensacji. To miara posiadania, nie aktywności.

Raporty mają różne sformułowania i kodowania (raport za 2015 r. ma nieczytelne fonty, za 2016 r.
tekst w cp1251), dlatego skrypt nie zapisuje wartości automatycznie. Wartości z wypisanych zdań
przeniesiono ręcznie do data/reczne/bulgaria_fki.csv, z nazwą pliku i sposobem wyliczenia w uwagach.

Użycie: python scripts/bulgaria_fki.py  (pobiera brakujące PDF-y do data/raw/bg/)
"""

import re
import urllib.parse
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "bg"
INDEX = ("https://sfund-bg.com/%d0%bf%d1%83%d0%b1%d0%bb%d0%b8%d0%ba%d0%b0%d1%86%d0%b8%d0%b8/"
         "%d0%b3%d0%be%d0%b4%d0%b8%d1%88%d0%bd%d0%b8-%d0%be%d1%82%d1%87%d0%b5%d1%82%d0%b8-%d0%bd%d0%b0-%d1%84%d0%ba%d0%b8/")
HEADERS = {"User-Agent": "Mozilla/5.0"}
CLIENTS = re.compile(r"(?i)(клиент\w*|инвеститор\w*)")


def download_reports():
    RAW.mkdir(parents=True, exist_ok=True)
    html = urllib.request.urlopen(urllib.request.Request(INDEX, headers=HEADERS), timeout=120).read()
    for url in sorted(set(re.findall(r'href="([^"]+\.pdf)"', html.decode("utf-8", "replace")))):
        path = RAW / urllib.parse.unquote(url.rsplit("/", 1)[-1])
        if not path.exists():
            quoted = urllib.parse.quote(url, safe=":/%()")
            path.write_bytes(urllib.request.urlopen(urllib.request.Request(quoted, headers=HEADERS),
                                                    timeout=120).read())
            print(f"Pobrano {path.name}")


def text_of(path):
    text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    if "Ãîäèøåí" in text or "ÃÎÄÈØÅÍ" in text:  # cp1251 odczytane jako latin-1
        text = text.encode("latin-1", "replace").decode("cp1251", "replace")
    return re.sub(r"\s+", " ", text)


def main():
    download_reports()
    for path in sorted(RAW.glob("*.pdf")):
        text = text_of(path)
        print(f"===== {path.name}")
        shown = 0
        for m in CLIENTS.finditer(text):
            snippet = text[max(0, m.start() - 200):m.start() + 200]
            if (re.search(r"(31\.12\.|края на|31 декември)", snippet)
                    and re.search(r"\b\d{2,3} \d{3}\b", snippet) and "лв" not in snippet[180:300]):
                print("  ..", snippet)
                shown += 1
            if shown >= 3:
                break


if __name__ == "__main__":
    main()
