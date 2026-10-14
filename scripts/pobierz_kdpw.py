"""Pobiera z portalu danych KDPW miesięczne pliki z liczbą rachunków papierów
wartościowych i składa je w dwa pliki CSV.

Źródło: https://data.kdpw.pl, raport „Liczba rachunków papierów wartościowych
oraz rachunków zbiorczych prowadzonych przez uczestników KDPW” (dostęp publiczny).

Wynik:
  data/kdpw/raw/                         surowe pliki .xls/.xlsx
  data/kdpw/kdpw_rachunki_suma.csv       data, liczba_rachunkow (wiersz RAZEM)
  data/kdpw/kdpw_rachunki_uczestnicy.csv data, kod, uczestnik, liczba_rachunkow

Uruchomienie (z katalogu projektu):
  pip install -r requirements.txt
  python scripts/pobierz_kdpw.py
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://data.kdpw.pl/portal/files"
LIST_URL = f"{BASE}/csd/number_securities_accounts/list?take=500"
DOWNLOAD_URL = f"{BASE}/download?uuid={{uuid}}"
HEADERS = {"User-Agent": "Mozilla/5.0 (projekt studencki PNDK26)"}

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "kdpw"
RAW_DIR = OUT_DIR / "raw"


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def list_files() -> list[dict]:
    payload = json.loads(http_get(LIST_URL))
    if payload.get("hasMore"):
        print("UWAGA: portal zgłasza więcej plików niż pobrano na liście", file=sys.stderr)
    return payload["DATA"]


def download(files: list[dict]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        target = RAW_DIR / f["fileName"]
        if target.exists():
            continue
        print(f"pobieram {f['fileName']}")
        target.write_bytes(http_get(DOWNLOAD_URL.format(uuid=f["uuid"])))
        time.sleep(0.5)


def date_from_name(name: str) -> pd.Timestamp:
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", name)
    if not m:
        raise ValueError(f"brak daty w nazwie pliku: {name}")
    d, mth, y = m.groups()
    return pd.Timestamp(int(y), int(mth), int(d))


def parse(path: Path) -> tuple[pd.DataFrame, int]:
    """Zwraca (wiersze uczestników, wartość z wiersza RAZEM)."""
    df = pd.read_excel(path, header=None, sheet_name=0)
    first_col = df[0].astype(str).str.strip()

    header_idx = first_col[first_col == "L.p."].index[0]
    total_idx = first_col[first_col.str.upper().str.startswith("RAZEM")].index[0]

    rows = df.loc[header_idx + 1 : total_idx - 1, [1, 2, 3]].dropna(how="all")
    rows.columns = ["kod", "uczestnik", "liczba_rachunkow"]
    rows["kod"] = rows["kod"].astype(str).str.strip()
    rows["uczestnik"] = rows["uczestnik"].astype(str).str.strip()
    rows["liczba_rachunkow"] = pd.to_numeric(rows["liczba_rachunkow"]).astype(int)

    total = int(pd.to_numeric(df.loc[total_idx, 3]))
    if rows["liczba_rachunkow"].sum() != total:
        print(
            f"UWAGA: {path.name}: suma uczestników {rows['liczba_rachunkow'].sum()} "
            f"!= RAZEM {total}",
            file=sys.stderr,
        )
    return rows, total


def main() -> None:
    files = list_files()
    print(f"plików na portalu: {len(files)}")
    download(files)

    totals, participants = [], []
    for path in sorted(RAW_DIR.glob("liczba_rachunkow-*.xls*")):
        date = date_from_name(path.name)
        rows, total = parse(path)
        totals.append({"data": date, "liczba_rachunkow": total})
        participants.append(rows.assign(data=date))

    suma = pd.DataFrame(totals).sort_values("data")
    uczestnicy = (
        pd.concat(participants)
        .loc[:, ["data", "kod", "uczestnik", "liczba_rachunkow"]]
        .sort_values(["data", "kod"])
    )

    suma.to_csv(OUT_DIR / "kdpw_rachunki_suma.csv", index=False, date_format="%Y-%m-%d")
    uczestnicy.to_csv(
        OUT_DIR / "kdpw_rachunki_uczestnicy.csv", index=False, date_format="%Y-%m-%d"
    )
    print(
        f"zapisano {len(suma)} miesięcy "
        f"({suma['data'].min():%Y-%m} – {suma['data'].max():%Y-%m}) do {OUT_DIR}"
    )


if __name__ == "__main__":
    main()
