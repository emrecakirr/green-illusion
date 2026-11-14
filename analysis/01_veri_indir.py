"""
The Green Illusion - 1. adim: veri indirme
==========================================
Indirilenler (hepsi NASA, ucretsiz, Earthdata hesabi ister):
  1) MODIS MCD64A1 v061  - Yanik alan (aylik, 500 m, 2001-2025)  -> data/mcd64a1/
  2) MODIS MOD13Q1 v061  - NDVI (16 gunluk, 250 m, 2026 yazi)    -> data/mod13q1/
  3) NISAR L2 GCOV       - L-band radar (2026)                    -> data/nisar_gcov/

Kullanim (bu klasorde):
    python 01_veri_indir.py              # hepsini indir
    python 01_veri_indir.py --sadece nisar
    python 01_veri_indir.py --nisar-liste  # NISAR'da sadece ara, indirme

Earthdata kullanici adi/sifre ilk calistirmada sorulur ve _netrc dosyasina kaydedilir.
"""
import argparse, csv, getpass, os, sys

# Calisma alani: Antalya ormanlari (Manavgat, Serik, Alanya)
from bolge import BATI, GUNEY, DOGU, KUZEY, TILE, NISAR_DIR, AD_KOD
BBOX = (BATI, GUNEY, DOGU, KUZEY)
WKT = f"POLYGON(({BATI} {GUNEY},{DOGU} {GUNEY},{DOGU} {KUZEY},{BATI} {KUZEY},{BATI} {GUNEY}))"
MODIS_TILE = TILE

KLASOR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(KLASOR, "data")


def giris():
    import earthaccess
    auth = earthaccess.login(strategy="netrc") if _netrc_var() else None
    if not auth or not auth.authenticated:
        print("\nNASA Earthdata girisi (hesap yoksa: https://urs.earthdata.nasa.gov/users/new)")
        auth = earthaccess.login(strategy="interactive", persist=True)
    if not auth.authenticated:
        sys.exit("Giris basarisiz. Kullanici adi / sifreyi kontrol et.")
    return auth


def _netrc_var():
    home = os.path.expanduser("~")
    return any(os.path.exists(os.path.join(home, n)) for n in ("_netrc", ".netrc"))


def modis_indir(short_name, bas, son, aylar, hedef, en_fazla=None):
    import earthaccess
    os.makedirs(hedef, exist_ok=True)
    print(f"\n{short_name} araniyor ({bas} - {son})...")
    g = earthaccess.search_data(short_name=short_name, version="061", bounding_box=BBOX,
                                temporal=(bas, son), count=5000)
    import re, datetime as dt
    secili = []
    for x in g:
        ad = os.path.basename(x.data_links()[0])
        m = re.search(r"\.A(\d{4})(\d{3})\.", ad)
        if MODIS_TILE not in ad or not m or not ad.endswith(".hdf"):
            continue
        ay = (dt.date(int(m.group(1)), 1, 1) + dt.timedelta(int(m.group(2)) - 1)).month
        if ay in aylar:
            secili.append(x)
    if en_fazla:
        secili = secili[-en_fazla:]
    mevcut = set(os.listdir(hedef))
    eksik = [x for x in secili if os.path.basename(x.data_links()[0]) not in mevcut]
    print(f"{short_name}: {len(secili)} dosya uygun, {len(eksik)} tanesi indirilecek -> {hedef}")
    if eksik:
        earthaccess.download(eksik, local_path=hedef, threads=4)


def _mb(p):
    b = p.get("bytes")
    if isinstance(b, dict):
        t = 0
        for v in b.values():
            if isinstance(v, dict):
                v = v.get("bytes", 0)
            try:
                t += float(v)
            except Exception:
                pass
        b = t
    try:
        return float(b or 0) / 1e6
    except Exception:
        return 0.0


def _kapsama(r):
    try:
        from shapely.geometry import shape, box
        g = shape(r.geometry)
        aoi = box(BATI, GUNEY, DOGU, KUZEY)
        return g.intersection(aoi).area / aoi.area
    except Exception:
        return 0.0


def _kuru_mevsim(r):
    t = r.properties.get("startTime", "")
    return 1 if t[5:7] in ("07", "08") else 0


def _pol(r):
    ad = (r.properties.get("fileID") or r.properties.get("sceneName") or "")
    return 2 if ("_DH" in ad or "_QP" in ad or "_QD" in ad) else 1


def nisar(sadece_liste=False, adet=1):
    import asf_search as asf
    print(f"\nNISAR araniyor ({AD_KOD})...")
    sonuc = asf.search(dataset="NISAR", processingLevel="GCOV", intersectsWith=WKT,
                       start="2026-06-01", maxResults=500)
    gcov = list(sonuc)
    gcov.sort(key=lambda r: r.properties.get("startTime", ""), reverse=True)
    print(f"{AD_KOD}: {len(gcov)} NISAR GCOV urunu bulundu.")

    os.makedirs(NISAR_DIR, exist_ok=True)
    liste = os.path.join(NISAR_DIR, "liste.csv")
    with open(liste, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fileID", "startTime", "flightDirection", "pathNumber", "frameNumber", "MB", "kapsama", "url"])
        for r in gcov:
            p = r.properties
            w.writerow([p.get("fileID"), p.get("startTime"), p.get("flightDirection"), p.get("pathNumber"),
                        p.get("frameNumber"), round(_mb(p)), round(_kapsama(r), 3), p.get("url")])
    for r in gcov[:8]:
        p = r.properties
        print(f"  {p.get('startTime')}  {p.get('fileID')}  ~{_mb(p):.0f} MB")
    print(f"Liste: {liste}")

    if not gcov:
        print("UYARI: Bu alanda GCOV bulunamadi. Bana liste.csv'yi gonder, yedek bolgeye geceriz.")
        return
    if sadece_liste:
        return
    if any(f.endswith(".h5") for f in os.listdir(NISAR_DIR)):
        print("NISAR dosyasi zaten var, atlaniyor."); return

    # En kucuk + en yeni (yaz sonu tercih) dosyayi sec
    # Secim: HV kanali olan + Antalya'yi en cok kapsayan + kuru mevsim (Temmuz-Agustos) + en yeni
    secim = sorted(gcov, key=lambda r: (_pol(r), round(_kapsama(r), 2), _kuru_mevsim(r),
                                        r.properties.get("startTime", "")), reverse=True)[:adet]
    for r in secim:
        print(f"  SECILDI: {r.properties.get('fileID')}  kapsama=%{_kapsama(r)*100:.0f}")
    print(f"\n{len(secim)} NISAR dosyasi indiriliyor (buyuk olabilir, sabir)...")
    import time
    urller = asf.ASFSearchResults(secim).find_urls(extension=".h5", pattern=r"^(?!.*QA_STATS).*",
                                                   directAccess=False)
    print("  " + "\n  ".join(urller))
    hedef = NISAR_DIR
    # Yol 1: earthaccess (NASA Earthdata token ile)
    try:
        import earthaccess
        print("  earthaccess ile indiriliyor...")
        sonuc = earthaccess.download(urller, local_path=hedef, threads=1)
        if sonuc and all(os.path.getsize(str(x)) > 10_000_000 for x in sonuc):
            print("NISAR indirildi.")
            return
        print("  earthaccess dosyayi tam indiremedi, ASF yolu deneniyor...")
    except Exception as e:
        print(f"  earthaccess hatasi: {e.__class__.__name__}: {e}")
    # Yol 2: asf_search
    kullanici, sifre = _netrc_kimlik()
    for deneme in range(3):
        try:
            oturum = asf.ASFSession().auth_with_creds(kullanici, sifre)
            asf.download_urls(urller, hedef, session=oturum, processes=1)
            break
        except Exception as e:
            print(f"  ASF denemesi {deneme+1} basarisiz ({e.__class__.__name__}), 10 sn sonra tekrar...")
            time.sleep(10)
    else:
        raise RuntimeError("ASF girisi basarisiz. https://search.asf.alaska.edu adresine Earthdata ile "
                           "bir kez giris yapip kullanim sartlarini onayla, sonra tekrar dene.")
    print("NISAR indirildi.")


def _netrc_kimlik():
    import netrc
    for n in ("_netrc", ".netrc"):
        yol = os.path.join(os.path.expanduser("~"), n)
        if os.path.exists(yol):
            try:
                a = netrc.netrc(yol).authenticators("urs.earthdata.nasa.gov")
                if a:
                    return a[0], a[2]
            except Exception:
                pass
    return input("Earthdata kullanici adi: "), getpass.getpass("Earthdata sifre: ")


class _Tee:
    def __init__(self, *a): self.a = a
    def write(self, x):
        for f in self.a:
            try: f.write(x); f.flush()
            except Exception: pass
    def flush(self): pass


def main():
    import traceback
    os.makedirs(DATA, exist_ok=True)
    log = open(os.path.join(KLASOR, "log_veri_indir.txt"), "w", encoding="utf-8")
    sys.stdout = _Tee(sys.__stdout__, log); sys.stderr = _Tee(sys.__stderr__, log)
    p = argparse.ArgumentParser()
    p.add_argument("--sadece", choices=["yanik", "ndvi", "nisar"], default=None)
    p.add_argument("--nisar-liste", action="store_true", help="NISAR'da sadece ara, indirme")
    p.add_argument("--nisar-adet", type=int, default=1)
    a = p.parse_args()

    giris()
    adimlar = []
    if a.sadece in (None, "nisar") or a.nisar_liste:
        adimlar.append(("NISAR", lambda: nisar(sadece_liste=a.nisar_liste, adet=a.nisar_adet)))
    if not a.nisar_liste and a.sadece in (None, "ndvi"):
        adimlar.append(("NDVI", lambda: modis_indir("MOD13Q1", "2026-07-01", "2026-08-31", [7, 8],
                                                     os.path.join(DATA, "mod13q1"), en_fazla=2)))
    if not a.nisar_liste and a.sadece in (None, "yanik"):
        adimlar.append(("YANIK", lambda: modis_indir("MCD64A1", "2001-01-01", "2025-12-31", [6, 7, 8, 9, 10],
                                                      os.path.join(DATA, "mcd64a1"))))
    for ad, f in adimlar:
        try:
            f()
        except Exception:
            print(f"\n!!! {ad} adiminda HATA (diger adimlara devam ediliyor):")
            traceback.print_exc()
    print("\nBitti. Log: log_veri_indir.txt  ->  Simdi: 2_ANALIZ.bat")


if __name__ == "__main__":
    main()
