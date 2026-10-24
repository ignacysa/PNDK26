"""Szeregi liczby inwestorów na Litwie z publikacji Banku Litwy (Lietuvos bankas, LB).

Źródła (pliki w data/raw/lt/):
- „Lietuvos investuotojo paveikslas” (infografiki roczne LB za lata 2020–2024),
- analizy LB „Asmenų, investavusių į Nasdaq Vilniaus biržos sąrašus įtrauktas finansines
  priemones, analizė” za 2019 r. (komunikat z 20.04.2020) i 2020 r. (prezentacja PDF i komunikat
  z 20.04.2021),
- komunikaty LB z 01.08.2022 (dane za 2021 r.) i 27.05.2025 (dane za 2024 r.),
- artykuł LRT/BNS z 08.07.2026 streszczający komunikat LB z danymi za 2025 r.
  (strony LB z tym komunikatem nie ma w Wayback Machine).

lb.lt stoi za zaporą Cloudflare (403 dla skryptów), dlatego pliki pobieramy z Wayback Machine
(https://web.archive.org/web/<znacznik>id_/<adres w lb.lt>). Wayback czasem zwraca plik ucięty
do 1 MB – skrypt sprawdza znacznik końca PDF.

Miary i definicje (z publikacji LB):
- aktywni inwestorzy Nasdaq Vilnius: „Investuotojai, per metus sudarę bent vieną pirkimo ar
  pardavimo sandorį” (≥1 transakcja kupna lub sprzedaży w roku) instrumentami notowanymi na
  Nasdaq Vilnius, według danych pośredników nadzorowanych przez LB; obejmuje osoby fizyczne
  i prawne. Za 2019–2020 podział „z Litwy / z zagranicy” (kraj inwestora), od 2022 r.
  „Lietuvos piliečiai / Užsieniečiai / Lietuvos įmonės / Užsienio įmonės”. Brak danych za 2021 r.
- aktywni inwestorzy-rezydenci (wszystkie rynki): „Fizinių asmenų, kuriems tarpininkauta,
  skaičius” – osoby fizyczne, rezydenci Litwy, dla których pośrednik z Litwy wykonał w danym roku
  co najmniej jedną transakcję (w infografice 2023–2024 pod nagłówkiem „Aktyvūs investuotojai”
  z przypisem o ≥1 transakcji); dotyczy wszystkich instrumentów (także akcji zagranicznych i ETF),
  ale tylko klientów firm nadzorowanych przez LB.
- akcjonariusze spółek z Nasdaq Vilnius („Bendras akcininkų skaičius”, źródło: informacja roczna
  emitentów), rachunki osób fizycznych z saldem instrumentów, klienci nieprofesjonalni ogółem.

Wartości odczytane z wykresów są zapisane ręcznie w VALUES, ale skrypt sprawdza, że każda
liczba występuje w tekście wskazanego pliku (lista „checks”) – inaczej przerywa działanie.

Wynik: wiersze miar z MEASURES w data/reczne/rumunia_litwa_szeregi.csv (pozostałe wiersze
pliku zostają bez zmian).

Użycie: python scripts/litwa_lb.py
"""

import csv
import gzip
import html
import re
import time
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "lt"
OUT = ROOT / "data" / "reczne" / "rumunia_litwa_szeregi.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
LB = "https://www.lb.lt"

# plik lokalny -> (adres oryginalny, znacznik Wayback albo None = pobierz bezpośrednio)
SOURCES = {
    "lb_investuotojo_paveikslas_2020.pdf": (LB + "/uploads/documents/files/Investuotojas_7(1).pdf", "20211005181724"),
    "lb_investuotojo_paveikslas_2021.pdf": (LB + "/uploads/documents/files/news/Investuotojas_2022_visas%20infografikas.pdf", "2022"),
    "lb_investuotojo_paveikslas_2022.pdf": (LB + "/uploads/publications/docs/46720_a9d60c349c5fa1f61aedc28bc1f21e2b.pdf", "2026"),
    "lb_investuotojo_paveikslas_2023.pdf": (LB + "/uploads/publications/docs/46723_8be084bd9c17359c088de71e30d82806.pdf", "2026"),
    "lb_investuotojo_paveikslas_2024.pdf": (LB + "/uploads/documents/files/Investuotojo_paveikslas_2024.pdf", "2026"),
    "lb_analize_nasdaq_vilnius_2019_2020.pdf": (LB + "/uploads/documents/files/Asmenu%20investavusiu%20i%20listinguojamas%20finansines%20priemones%20analize-2020.pdf", "2021"),
    "lb_naujiena_2020-04-20_nasdaq_vilnius_2019.html": (LB + "/lt/naujienos/nauja-analize-daugiau-skaidrumo-birzoje-ir-papildoma-priemone-rinkos-dalyviams", "20200521230725"),
    "lb_naujiena_2021-04-20_nasdaq_vilnius_2020.html": (LB + "/lt/naujienos/analize-investuojanciuju-skaicius-isaugo-du-kartus-aktyvesni-buvo-ir-uzsienio-investuotojai", "20210509073505"),
    "lb_naujiena_2022-08-01_investuotojo_paveikslas_2021.html": (LB + "/lt/naujienos/investuotojo-paveikslas-aktyviausiai-investuoja-vyrai-taciau-sparciai-gauseja-ir-investuojanciu-moteru-gretos", "20220809234120"),
    "lb_naujiena_2025-05-27_investuotojo_paveikslas_2024.html": (LB + "/lt/naujienos/lietuvos-investuotojo-paveikslas-didejo-aktyvumas-domino-rizikingesnes-finansines-priemones", "20250714143420"),
    "lrt_2026-07-08_lb_investuotojai_2025.html": ("https://www.lrt.lt/naujienos/verslas/4/2984095/lb-investuojanciu-gyventoju-skaicius-pernai-augo-40-proc-sandoriu-60-proc", None),
}

M_NV = "Aktywni inwestorzy Nasdaq Vilnius – łącznie (LB)"
M_NV_LT_FIZ = "Aktywni inwestorzy Nasdaq Vilnius – osoby fizyczne z Litwy (LB)"
M_NV_ZAGR_FIZ = "Aktywni inwestorzy Nasdaq Vilnius – zagraniczne osoby fizyczne (LB)"
M_NV_LT = "Aktywni inwestorzy Nasdaq Vilnius – inwestorzy z Litwy łącznie (LB)"
M_NV_ZAGR = "Aktywni inwestorzy Nasdaq Vilnius – inwestorzy zagraniczni łącznie (LB)"
M_REZ = "Aktywni inwestorzy-rezydenci Litwy, osoby fizyczne, wszystkie rynki (LB)"
M_AKC = "Akcjonariusze spółek z Nasdaq Vilnius (LB)"
M_RACH = "Rachunki instrumentów finansowych osób fizycznych z saldem (LB)"
M_KLI = "Klienci nieprofesjonalni ogółem (LB)"
MEASURES = {M_NV, M_NV_LT_FIZ, M_NV_ZAGR_FIZ, M_NV_LT, M_NV_ZAGR, M_REZ, M_AKC, M_RACH, M_KLI}
TYPES = {M_NV: ("aktywni", "osoby", "rok"), M_NV_LT_FIZ: ("aktywni", "osoby", "rok"),
         M_NV_ZAGR_FIZ: ("aktywni", "osoby", "rok"), M_NV_LT: ("aktywni", "osoby", "rok"),
         M_NV_ZAGR: ("aktywni", "osoby", "rok"), M_REZ: ("aktywni", "osoby", "rok"),
         M_AKC: ("posiadacze", "osoby", "stan"), M_RACH: ("posiadacze", "rachunki", "stan"),
         M_KLI: ("posiadacze", "klienci", "stan")}

DEF_NV = ("≥1 transakcja kupna lub sprzedaży w roku instrumentami z Nasdaq Vilnius "
          "(„per metus sudarę bent vieną pirkimo ar pardavimo sandorį”), dane pośredników nadzorowanych przez LB")
DEF_REZ = ("„Fizinių asmenų, kuriems tarpininkauta” – rezydenci Litwy z ≥1 transakcją w roku przez pośrednika "
           "nadzorowanego przez LB, wszystkie instrumenty (też zagraniczne), bez klientów brokerów zagranicznych")
P20, P21, P22, P23, P24 = (f"lb_investuotojo_paveikslas_{y}.pdf" for y in range(2020, 2025))
A20 = "lb_analize_nasdaq_vilnius_2019_2020.pdf"
N19 = "lb_naujiena_2020-04-20_nasdaq_vilnius_2019.html"
N20 = "lb_naujiena_2021-04-20_nasdaq_vilnius_2020.html"
N21 = "lb_naujiena_2022-08-01_investuotojo_paveikslas_2021.html"
N24 = "lb_naujiena_2025-05-27_investuotojo_paveikslas_2024.html"
LRT = "lrt_2026-07-08_lb_investuotojai_2025.html"

# (miara, wartość, rok, plik, status, uwagi, liczby, które muszą wystąpić w tekście pliku)
Z, S = "zweryfikowane", "z wyszukiwania"
VALUES = [
    # --- Nasdaq Vilnius, łącznie
    (M_NV, 8813, 2019, N19, Z, "komunikat LB 20.04.2020: 8 813 inwestorów (8 204 osoby fizyczne z Litwy, 377 litewskich osób prawnych, 116 zagranicznych osób prawnych i 116 zagranicznych fizycznych)", ["8 813", "8 204"]),
    (M_NV, 21127, 2020, N20, Z, "suma 16 605 inwestorów z Litwy + 4 522 z zagranicy (komunikat LB 20.04.2021; to samo w prezentacji LB, s. 7)", ["16 605", "4 522"]),
    (M_NV, 20558, 2022, P23, Z, "infografika LB 2023, s. 3, wykres „Aktyvių investuotojų pasiskirstymas” (2022: 11 995 obywateli LT + 319 firm LT + 7 752 cudzoziemców + 492 firm zagr. = 20 558)", ["20 558", "11 995", "7 752"]),
    (M_NV, 22320, 2023, P24, Z, "infografika LB 2024, s. 3 (też infografika 2023): 14 065 + 406 + 7 387 + 462 = 22 320", ["22 320", "14 065", "7 387"]),
    (M_NV, 24529, 2024, P24, Z, "infografika LB 2024, s. 3: 16 191 obywateli LT + 533 firmy LT + 7 350 cudzoziemców + 455 firm zagr.; komunikat LB 27.05.2025 podaje 24,6 tys.", ["24 529", "16 191", "7 350"]),
    (M_NV, 33000, 2025, LRT, S, "NIEPEWNE: „daugiau kaip 33 tūkst. gyventojų” aktywnie inwestowało na Nasdaq Vilnius (BNS/LRT streszcza komunikat LB z 08.07.2026; wartość zaokrąglona w dół, nie wiadomo, czy obejmuje osoby prawne; ten sam tekst pisze o wzroście o 1/10 wobec „užpernai”, co nie zgadza się z 24 529 za 2024 r.)", ["33 tūkst"]),
    # --- osoby fizyczne z Litwy / obywatele Litwy
    (M_NV_LT_FIZ, 8204, 2019, N19, Z, "„vietiniai investuotojai – fiziniai asmenys” (kraj inwestora: Litwa)", ["8 204"]),
    (M_NV_LT_FIZ, 16342, 2020, A20, Z, "prezentacja LB „Asmenų, investavusių į listinguojamas finansines priemones, analizė” (2021), s. 7: Litwa, osoby fizyczne 16 342 (łącznie z osobami prawnymi 16 605)", ["16,342", "16,605"]),
    (M_NV_LT_FIZ, 11995, 2022, P23, Z, "„Lietuvos piliečiai” (obywatele Litwy) – inna klasyfikacja niż w 2019–2020 (kraj inwestora); infografika 2023, s. 3", ["11 995"]),
    (M_NV_LT_FIZ, 14065, 2023, P24, Z, "„Lietuvos piliečiai”; infografika 2024, s. 3", ["14 065"]),
    (M_NV_LT_FIZ, 16191, 2024, P24, Z, "„Lietuvos piliečiai”; infografika 2024, s. 3; komunikat LB: 16,2 tys.", ["16 191"]),
    # --- zagraniczne osoby fizyczne
    (M_NV_ZAGR_FIZ, 116, 2019, N19, Z, "„užsienio fizinių asmenų” (116)", ["116 užsienio"]),
    (M_NV_ZAGR_FIZ, 4234, 2020, A20, Z, "suma osób fizycznych: strefa euro 1 626 + inne kraje UE 2 478 + spoza UE 130 (prezentacja LB, s. 7)", ["1,626", "2,478"]),
    (M_NV_ZAGR_FIZ, 7752, 2022, P23, Z, "„Užsieniečiai” (cudzoziemcy); infografika 2023, s. 3", ["7 752"]),
    (M_NV_ZAGR_FIZ, 7387, 2023, P24, Z, "„Užsieniečiai”; infografika 2024, s. 3", ["7 387"]),
    (M_NV_ZAGR_FIZ, 7350, 2024, P24, Z, "„Užsieniečiai”; infografika 2024, s. 3; komunikat LB: 7,4 tys.", ["7 350"]),
    # --- z Litwy łącznie (osoby fizyczne + prawne)
    (M_NV_LT, 8581, 2019, A20, Z, "prezentacja LB, s. 7: Litwa łącznie (377 osób prawnych + 8 204 fizycznych)", ["8581"]),
    (M_NV_LT, 16605, 2020, N20, Z, "„16 605 investuotojai iš Lietuvos” (osoby fizyczne i prawne)", ["16 605"]),
    (M_NV_LT, 12314, 2022, P23, Z, "suma: obywatele Litwy 11 995 + litewskie osoby prawne 319", ["11 995", "319"]),
    (M_NV_LT, 14471, 2023, P24, Z, "suma: obywatele Litwy 14 065 + litewskie osoby prawne 406", ["14 065", "406"]),
    (M_NV_LT, 16724, 2024, P24, Z, "suma: obywatele Litwy 16 191 + litewskie osoby prawne 533", ["16 191", "533"]),
    # --- zagraniczni łącznie
    (M_NV_ZAGR, 232, 2019, N19, Z, "suma: 116 zagranicznych osób prawnych + 116 fizycznych", ["116 užsienio"]),
    (M_NV_ZAGR, 4522, 2020, N20, Z, "„4 522 investuotojai iš užsienio”", ["4 522"]),
    (M_NV_ZAGR, 8244, 2022, P23, Z, "suma: cudzoziemcy 7 752 + zagraniczne osoby prawne 492", ["7 752", "492"]),
    (M_NV_ZAGR, 7849, 2023, P24, Z, "suma: cudzoziemcy 7 387 + zagraniczne osoby prawne 462", ["7 387", "462"]),
    (M_NV_ZAGR, 7805, 2024, P24, Z, "suma: cudzoziemcy 7 350 + zagraniczne osoby prawne 455", ["7 350", "455"]),
    # --- rezydenci, wszystkie rynki
    (M_REZ, 42601, 2020, P20, Z, "infografika LB „Lietuvos investuotojo paveikslas 2020 m.”: 42 601 (16 083 kobiety + 26 518 mężczyzn)", ["42 601", "16 083"]),
    (M_REZ, 49362, 2021, P21, Z, "infografika LB 2021: 49 362 (17 887 kobiet + 31 475 mężczyzn)", ["49 362", "17 887", "31 475"]),
    (M_REZ, 53820, 2022, P22, Z, "infografika LB 2022: 53 820 (19 401 kobiet + 34 419 mężczyzn), tabela s. 2 „Bendras”", ["53 820", "19 401", "34 419"]),
    (M_REZ, 94083, 2023, P23, Z, "infografika LB 2023, tabela s. 1 „Bendras 94 083”", ["94 083"]),
    (M_REZ, 176524, 2024, P24, Z, "infografika LB 2024, tabela s. 1 „Bendras 176 524”; komunikat LB 27.05.2025: 176,5 tys.", ["176 524"]),
    (M_REZ, 250000, 2025, LRT, S, "komunikat LB z 08.07.2026 wg BNS/LRT: „Lietuvos investuotojų skaičius augo 40 proc. – iki 250 tūkst.” (162 tys. mężczyzn, 88 tys. kobiet); zaokrąglone do tysięcy", ["250 tūkst"]),
    # --- akcjonariusze spółek z Nasdaq Vilnius
    (M_AKC, 80000, 2019, N19, Z, "„Bendrovės, įtrauktos Nasdaq Vilniaus biržą, turi apie 80 tūkst. akcininkų” – przybliżenie", ["80 tūkst"]),
    (M_AKC, 124700, 2022, P23, Z, "„Bendras akcininkų skaičius” ~124,7 tys. (informacja roczna emitentów), przybliżenie", ["124,7"]),
    (M_AKC, 132300, 2023, P24, Z, "„Bendras akcininkų skaičius” ~132,3 tys., przybliżenie", ["132,3"]),
    (M_AKC, 133400, 2024, P24, Z, "„Bendras akcininkų skaičius” ~133,4 tys., przybliżenie", ["133,4"]),
    (M_AKC, 141000, 2025, LRT, S, "„akcininkų skaičius viršijo 141 tūkst.” (BNS/LRT za komunikatem LB) – dolne ograniczenie", ["141 tūkst"]),
    # --- rachunki osób fizycznych z saldem instrumentów
    (M_RACH, 46400, 2020, P23, Z, "wykres w infografice 2023 (46,4 tys.), zaokrąglone do 0,1 tys.", ["46,4"]),
    (M_RACH, 70600, 2021, P23, Z, "wykres w infografice 2023 (70,6 tys.), zaokrąglone do 0,1 tys.", ["70,6"]),
    (M_RACH, 80145, 2022, P22, Z, "infografika 2022, tabela s. 2 (rachunki z saldem; wszystkich rachunków 140 258); klient może mieć kilka rachunków", ["80 145", "140 258"]),
    (M_RACH, 132114, 2023, P23, Z, "infografika 2023, tabela s. 1 (wszystkich rachunków 237 023)", ["132 114", "237 023"]),
    (M_RACH, 217203, 2024, P24, Z, "infografika 2024, tabela s. 1 (wszystkich rachunków 341 114)", ["217 203", "341 114"]),
    # --- klienci nieprofesjonalni ogółem (tylko infografika 2021)
    (M_KLI, 64800, 2018, P21, Z, "wykres „Neprofesionaliųjų klientų skaičius” (64,8 tys.) w infografice 2021", ["64,8"]),
    (M_KLI, 52700, 2019, N21, Z, "komunikat LB 01.08.2022: wzrost „nuo 52,7 tūkst.” w ciągu dwóch lat", ["52,7"]),
    (M_KLI, 82800, 2020, N21, Z, "komunikat LB 01.08.2022: „nuo 82,8 tūkst.”", ["82,8"]),
    (M_KLI, 116200, 2021, N21, Z, "komunikat LB 01.08.2022: „Bendras neprofesionaliųjų investuotojų skaičius praėjusių metų pabaigoje buvo 116,2 tūkst.”", ["116,2"]),
]


def complete(data, name):
    if name.endswith(".pdf"):
        return data.startswith(b"%PDF") and b"%%EOF" in data[-2048:]
    return len(data) > 10000


def download_missing():
    RAW.mkdir(parents=True, exist_ok=True)
    for name, (url, ts) in SOURCES.items():
        path = RAW / name
        if path.exists():
            continue
        src = f"https://web.archive.org/web/{ts}id_/{url}" if ts else url
        try:
            req = urllib.request.Request(src, headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=180).read()
        except OSError as e:
            print(f"BRAK: {name} – błąd {e}; otwórz ręcznie {src}")
            continue
        if data[:2] == b"\x1f\x8b":
            data = gzip.decompress(data)
        if complete(data, name):
            path.write_bytes(data)
            print(f"Pobrano {name}")
        else:
            print(f"BRAK: {name} – plik niepełny; otwórz ręcznie {src}")
        time.sleep(3)


def text_of(name):
    path = RAW / name
    if name.endswith(".pdf"):
        t = " ".join(p.extract_text() or "" for p in PdfReader(path).pages)
    else:
        t = path.read_text(encoding="utf-8", errors="replace")
        t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
        t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t.replace("\xa0", " "))


def build_rows():
    texts, rows = {}, []
    for miara, val, year, name, status, note, checks in VALUES:
        if name not in texts:
            texts[name] = text_of(name)
        lost = [c for c in checks if c not in texts[name]]
        if lost:
            raise SystemExit(f"{miara} {year}: w pliku {name} nie ma {lost} – sprawdź wartość")
        typ, jedn, okno = TYPES[miara]
        definition = DEF_REZ if miara == M_REZ else DEF_NV if miara.startswith("Aktywni inwestorzy Nasdaq") else ""
        url, ts = SOURCES[name]
        rows.append({"kraj": "LT", "miara": miara, "typ_miary": typ, "jednostka": jedn,
                     "okno_aktywnosci": okno, "wartosc": val, "data": f"{year}-12-31",
                     "zrodlo": url, "status": status,
                     "uwagi": "; ".join(x for x in [definition, note, f"plik {name}"
                                                     + (f" (kopia z Wayback {ts})" if ts else "")] if x)})
    return rows


def update_csv(rows, measures):
    cols = ["kraj", "miara", "typ_miary", "jednostka", "okno_aktywnosci", "wartosc", "data",
            "zrodlo", "status", "uwagi"]
    old = []
    if OUT.exists():
        with open(OUT, encoding="utf-8", newline="") as f:
            old = [r for r in csv.DictReader(f) if r["miara"] not in measures]
    allrows = old + rows
    allrows.sort(key=lambda r: (r["kraj"], r["miara"], r["data"]))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(allrows)


def main():
    download_missing()
    rows = build_rows()
    update_csv(rows, MEASURES)
    print(f"Zapisano {len(rows)} wierszy (LT) do {OUT}")


if __name__ == "__main__":
    main()
