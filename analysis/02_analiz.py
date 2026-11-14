"""
The Green Illusion - 2. adim: analiz
====================================
"Zaman yerine mekan" yontemi:
  - MCD64A1 -> her 500 m piksel en son hangi yil yandi?
  - MOD13Q1 -> bugunku NDVI (optik "yesillik")
  - NISAR GCOV -> bugunku L-band HV geri sacilimi (orman yapisi)
  - Yanma yasina gore toparlanma egrisi: R(t) = 1 - exp(-t / tau)
  - %90 toparlanma suresi = tau * ln(10), bootstrap ile belirsizlik

Ciktilar (cikti/ klasoru):
  sonuc.json           -> web uygulamasi icin ozet
  pikseller.geojson    -> haritada gosterilecek yanik pikseller
  toparlanma_egrisi.png
Kullanim:  python 02_analiz.py
"""
import glob, json, math, os, re, sys
import numpy as np

KLASOR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(KLASOR, "data")
CIKTI = os.path.join(KLASOR, "cikti")
BATI, GUNEY, DOGU, KUZEY = 30.9, 36.6, 32.2, 37.3
GOZLEM_YILI = 2026.6          # NISAR / NDVI gozlem zamani (yaklasik Agustos 2026)

# ---------------- MODIS sinuzoidal grid ----------------
R_DUNYA = 6371007.181
X0, Y0, KARE = -20015109.354, 10007554.677, 1111950.5197


def latlon_to_sin(lat, lon):
    la = np.radians(lat)
    return R_DUNYA * np.radians(lon) * np.cos(la), R_DUNYA * la


def sin_to_latlon(x, y):
    lat = y / R_DUNYA
    lon = x / (R_DUNYA * np.cos(lat))
    return np.degrees(lat), np.degrees(lon)


def tile_hv(dosya):
    m = re.search(r"h(\d\d)v(\d\d)", os.path.basename(dosya))
    return int(m.group(1)), int(m.group(2))


def piksel_merkez(h, v, n, satir, sutun):
    boy = KARE / n
    x = X0 + h * KARE + (sutun + 0.5) * boy
    y = Y0 - v * KARE - (satir + 0.5) * boy
    return x, y


def satir_sutun(h, v, n, x, y):
    boy = KARE / n
    sutun = np.floor((x - X0 - h * KARE) / boy).astype(int)
    satir = np.floor((Y0 - v * KARE - y) / boy).astype(int)
    return satir, sutun


def hdf4_oku(dosya, sds_adi):
    from pyhdf.SD import SD, SDC
    f = SD(dosya, SDC.READ)
    veri = f.select(sds_adi)[:]
    f.end()
    return veri


def tarih_yil(dosya):
    m = re.search(r"\.A(\d{4})(\d{3})\.", os.path.basename(dosya))
    return int(m.group(1)), int(m.group(2))


# ---------------- 1) Yanma yili ----------------
def yanma_yili_haritasi():
    dosyalar = sorted(glob.glob(os.path.join(DATA, "mcd64a1", "*.hdf")))
    if not dosyalar:
        sys.exit("MCD64A1 dosyasi yok. Once: python 01_veri_indir.py --sadece yanik")
    h, v = tile_hv(dosyalar[0])
    n = 2400
    # AOI'yi kapsayan satir/sutun penceresi
    lats = np.array([GUNEY, GUNEY, KUZEY, KUZEY]); lons = np.array([BATI, DOGU, BATI, DOGU])
    xs, ys = latlon_to_sin(lats, lons)
    r, c = satir_sutun(h, v, n, xs, ys)
    r0, r1 = max(r.min(), 0), min(r.max() + 1, n)
    c0, c1 = max(c.min(), 0), min(c.max() + 1, n)

    son_yil = np.zeros((r1 - r0, c1 - c0), dtype=np.float32)   # 0 = hic yanmadi
    sayi = np.zeros_like(son_yil, dtype=np.int16)
    for d in dosyalar:
        yil, gun = tarih_yil(d)
        bd = hdf4_oku(d, "Burn Date")[r0:r1, c0:c1]
        yandi = bd > 0
        # yilin kesirli zamani (ornek: 2021.58)
        zaman = yil + np.where(yandi, bd, 0) / 365.25
        son_yil = np.where(yandi & (zaman > son_yil), zaman, son_yil)
        sayi += yandi
    print(f"MCD64A1: {len(dosyalar)} dosya okundu, yanik piksel sayisi: {(son_yil > 0).sum()}")
    rr, cc = np.mgrid[r0:r1, c0:c1]
    x, y = piksel_merkez(h, v, n, rr, cc)
    lat, lon = sin_to_latlon(x, y)
    return dict(yil=son_yil, sayi=sayi, x=x, y=y, lat=lat, lon=lon)


# ---------------- 2) NDVI ----------------
def ndvi_ornekle(x, y):
    dosyalar = sorted(glob.glob(os.path.join(DATA, "mod13q1", "*.hdf")))
    if not dosyalar:
        print("UYARI: MOD13Q1 yok, NDVI atlanacak.")
        return None
    katman = []
    for d in dosyalar:
        h, v = tile_hv(d)
        nd = hdf4_oku(d, "250m 16 days NDVI").astype(np.float32)
        nd[nd < -2000] = np.nan
        nd *= 0.0001
        # 500 m pikselin icindeki 2x2 adet 250 m pikselin ortalamasi
        r, c = satir_sutun(h, v, 4800, x, y)
        ort = np.nanmean([nd[np.clip(r + i, 0, 4799), np.clip(c + j, 0, 4799)]
                          for i in (-1, 0) for j in (-1, 0)], axis=0)
        katman.append(ort)
    print(f"MOD13Q1: {len(dosyalar)} dosya")
    return np.nanmean(katman, axis=0)


# ---------------- 3) NISAR GCOV ----------------
def _h5_bul(f, isim_kalibi):
    bulunan = []
    f.visititems(lambda ad, nesne: bulunan.append(ad) if re.search(isim_kalibi, ad) else None)
    return bulunan


def gcov_ornekle(lat, lon):
    import h5py
    from pyproj import Transformer
    dosyalar = sorted(glob.glob(os.path.join(DATA, "nisar_gcov", "*.h5")))
    if not dosyalar:
        print("UYARI: NISAR GCOV yok, radar atlanacak.")
        return None, None
    hv_tum, hh_tum = [], []
    for d in dosyalar:
        with h5py.File(d, "r") as f:
            yollar = _h5_bul(f, r"frequencyA/(HVHV|HHHH)$")
            if not yollar:
                print(f"  {os.path.basename(d)}: HV/HH katmani bulunamadi, atlandi"); continue
            grup = yollar[0].rsplit("/", 1)[0]
            xk = f[grup + "/xCoordinates"][:]; yk = f[grup + "/yCoordinates"][:]
            epsg = None
            if grup + "/projection" in f:
                pr = f[grup + "/projection"]
                epsg = int(pr.attrs.get("epsg_code", pr[()] if pr.shape == () else 0))
            if not epsg:
                sys.exit("GCOV projeksiyonu okunamadi; dosya yapisini bana gonder.")
            tr = Transformer.from_crs(4326, epsg, always_xy=True)
            px, py = tr.transform(lon, lat)
            dx = xk[1] - xk[0]; dy = yk[1] - yk[0]
            pencere = max(1, int(round(250 / abs(dx))))   # 500 m piksel = +/-250 m
            sut = np.round((px - xk[0]) / dx).astype(int)
            sat = np.round((py - yk[0]) / dy).astype(int)
            icinde = (sut >= pencere) & (sut < len(xk) - pencere) & (sat >= pencere) & (sat < len(yk) - pencere)
            print(f"  {os.path.basename(d)}: EPSG {epsg}, {abs(dx):.0f} m piksel, alan icinde {icinde.sum()} piksel")
            for ad, liste in (("HVHV", hv_tum), ("HHHH", hh_tum)):
                if grup + "/" + ad not in f:
                    continue
                ds = f[grup + "/" + ad]
                # Sadece AOI kutusunu oku (bellek icin)
                s0, s1 = sat[icinde].min() - pencere, sat[icinde].max() + pencere + 1
                c0, c1 = sut[icinde].min() - pencere, sut[icinde].max() + pencere + 1
                blok = ds[s0:s1, c0:c1].astype(np.float32)
                blok[(blok <= 0) | ~np.isfinite(blok)] = np.nan
                out = np.full(lat.shape, np.nan, dtype=np.float32)
                ii = np.where(icinde)
                for k in range(len(ii[0])):
                    r_, c_ = sat[ii][k] - s0, sut[ii][k] - c0
                    p = blok[r_ - pencere:r_ + pencere + 1, c_ - pencere:c_ + pencere + 1]
                    if np.isfinite(p).sum() > 0.5 * p.size:
                        out[ii[0][k], ii[1][k]] = np.nanmean(p)   # dogrusal guc ortalamasi
                liste.append(out)
    if not hv_tum:
        return None, None
    def db(L):
        if not L:
            return None
        with np.errstate(all="ignore"):
            import warnings; warnings.simplefilter("ignore", RuntimeWarning)
            return 10 * np.log10(np.nanmean(L, axis=0))
    return db(hv_tum), db(hh_tum)


# ---------------- 4) Toparlanma egrisi ----------------
def toparlanma(deger, yas, referans, taban):
    return (deger - taban) / (referans - taban)


def egri_uydur(yas, deger, referans, n_boot=300, seed=1):
    """deger(t) = referans - (referans - v0) * exp(-t/tau);  v0 ve tau serbest."""
    from scipy.optimize import curve_fit
    f = lambda t, v0, tau: referans - (referans - v0) * np.exp(-t / tau)
    ok = np.isfinite(yas) & np.isfinite(deger)
    yas, deger = yas[ok], deger[ok]
    if len(yas) < 10:
        return None
    alt = float(np.nanpercentile(deger, 1))
    p0 = [alt, 10.0]
    sinir = ([alt - abs(referans - alt) * 2, 0.3], [referans, 300])
    (v0, tau), _ = curve_fit(f, yas, deger, p0=p0, bounds=sinir)
    rng = np.random.default_rng(seed)
    taus = []
    for _ in range(n_boot):
        i = rng.integers(0, len(yas), len(yas))
        try:
            taus.append(curve_fit(f, yas[i], deger[i], p0=[v0, tau], bounds=sinir)[0][1])
        except Exception:
            pass
    taus = np.array(taus)
    t90 = lambda t: t * math.log(10)
    return dict(v0=float(v0), tau=float(tau), t90=float(t90(tau)),
                t90_alt=float(t90(np.percentile(taus, 5))), t90_ust=float(t90(np.percentile(taus, 95))),
                n=int(len(yas)))


def main():
    os.makedirs(CIKTI, exist_ok=True)
    Y = yanma_yili_haritasi()
    ndvi = ndvi_ornekle(Y["x"], Y["y"])
    hv, hh = gcov_ornekle(Y["lat"], Y["lon"])

    yanik = Y["yil"] > 0
    yas = np.where(yanik, GOZLEM_YILI - Y["yil"], np.nan)

    # Referans orman: hic yanmamis, yanik alanlara 5 km mesafede, NDVI yuksek
    from scipy.ndimage import distance_transform_edt
    mesafe_km = distance_transform_edt(~yanik) * 0.463
    ref_maske = (~yanik) & (mesafe_km <= 5)
    if ndvi is not None:
        ref_maske &= ndvi >= np.nanpercentile(ndvi[ref_maske], 50)

    sonuc = {"alan": [BATI, GUNEY, DOGU, KUZEY], "gozlem_yili": GOZLEM_YILI,
             "yanik_piksel": int(yanik.sum()), "katmanlar": {}}
    katmanlar = {"ndvi": ndvi, "hv_db": hv, "hh_db": hh}
    R_hepsi = {}
    for ad, k in katmanlar.items():
        if k is None:
            continue
        ref = float(np.nanmedian(k[ref_maske]))
        uyum = egri_uydur(yas[yanik], k[yanik], ref)
        taban = uyum["v0"] if uyum else float(np.nanpercentile(k[yanik], 5))
        R = toparlanma(k, yas, ref, taban)
        R_hepsi[ad] = R
        gruplar = {}
        for y0 in range(0, 26):
            m = yanik & (yas >= y0) & (yas < y0 + 1) & np.isfinite(R)
            if m.sum() >= 5:
                gruplar[y0] = {"medyan": float(np.nanmedian(R[m])), "n": int(m.sum()),
                               "q25": float(np.nanpercentile(R[m], 25)), "q75": float(np.nanpercentile(R[m], 75))}
        sonuc["katmanlar"][ad] = {"referans": ref, "taban": taban, "egri": uyum, "yas_gruplari": gruplar}
        print(f"\n[{ad}] referans={ref:.3f} taban={taban:.3f}")
        if uyum:
            print(f"   %90 toparlanma ~ {uyum['t90']:.1f} yil  (90% aralik {uyum['t90_alt']:.1f}-{uyum['t90_ust']:.1f})")

    # Yesil yanilsama: optik - radar farki
    if "ndvi" in R_hepsi and "hv_db" in R_hepsi:
        e_o = sonuc["katmanlar"]["ndvi"]["egri"]; e_r = sonuc["katmanlar"]["hv_db"]["egri"]
        if e_o and e_r:
            sonuc["yesil_yanilsama"] = {"optik_t90": e_o["t90"], "radar_t90": e_r["t90"],
                                        "fark_yil": e_r["t90"] - e_o["t90"]}
            print(f"\nYESIL YANILSAMA: optik {e_o['t90']:.1f} yil diyor, radar {e_r['t90']:.1f} yil diyor.")

    with open(os.path.join(CIKTI, "sonuc.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)

    # Harita icin pikseller
    feats = []
    for i, j in zip(*np.where(yanik)):
        pr = {"yil": round(float(Y["yil"][i, j]), 2), "kac_kez": int(Y["sayi"][i, j])}
        for ad, R in R_hepsi.items():
            if np.isfinite(R[i, j]):
                pr["R_" + ad] = round(float(R[i, j]), 3)
        feats.append({"type": "Feature", "properties": pr,
                      "geometry": {"type": "Point", "coordinates": [round(float(Y["lon"][i, j]), 5),
                                                                    round(float(Y["lat"][i, j]), 5)]}})
    with open(os.path.join(CIKTI, "pikseller.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f)

    ciz(sonuc)
    print(f"\nCiktilar: {CIKTI}")


def ciz(sonuc):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    renk = {"ndvi": ("#2a9d3a", "Optik NDVI (MODIS)"), "hv_db": ("#7b3fbf", "Radar HV (NISAR)"),
            "hh_db": ("#c05a1a", "Radar HH (NISAR)")}
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    t = np.linspace(0, 40, 200)
    for ad, k in sonuc["katmanlar"].items():
        c, etiket = renk.get(ad, ("gray", ad))
        g = k["yas_gruplari"]
        anahtar = [a for a in g if g[a]["n"] >= 30]
        xs = np.array([int(a) + 0.5 for a in anahtar]); ys = np.array([g[a]["medyan"] for a in anahtar])
        ns = np.array([g[a]["n"] for a in anahtar])
        ax.scatter(xs, ys, color=c, s=np.clip(ns / 20, 15, 200), alpha=0.8)
        for a in anahtar:
            ax.errorbar(int(a) + 0.5, g[a]["medyan"], yerr=[[g[a]["medyan"] - g[a]["q25"]], [g[a]["q75"] - g[a]["medyan"]]],
                        color=c, alpha=0.5, capsize=3)
        if k["egri"]:
            ax.plot(t, 1 - np.exp(-t / k["egri"]["tau"]), color=c,
                    label=f"{etiket}: %90 ~ {k['egri']['t90']:.0f} yil")
    ax.axhline(1, color="k", lw=0.6, ls="--"); ax.axhline(0.9, color="k", lw=0.4, ls=":")
    ax.set_xlabel("Yangindan bu yana gecen yil"); ax.set_ylabel("Toparlanma (0 = taze yanik, 1 = saglam orman)")
    ax.set_title("Antalya: Yangin sonrasi toparlanma - optik vs radar")
    ax.set_ylim(-0.2, 1.3); ax.legend(); fig.tight_layout()
    fig.savefig(os.path.join(CIKTI, "toparlanma_egrisi.png"))


if __name__ == "__main__":
    main()
