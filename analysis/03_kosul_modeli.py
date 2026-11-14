"""
The Green Illusion - 3. adim: KOSULA GORE TOPARLANMA TAHMINI
============================================================
Soru: "Bir yerde yangin olursa, ORANIN KOSULLARINA gore orman ne zaman geri gelir?"

Girdi:
  cikti/pikseller.geojson  (02_analiz.py ciktisi: yanma yili, optik ve radar toparlanma)
  data/nasadem/*.hgt       (NASA NASADEM 30 m yukseklik)
  data/mod13q1/*.hdf       (NDVI - orman maskesi icin)
Yontem:
  1) Her yanik piksel icin yukseklik, egim, bakı (kuzeye bakma = cos(aspect)) hesaplanir.
  2) Her pikselin "kendi" toparlanma hizi: tau_i = -yas / ln(1 - R_i)  ->  T90_i = tau_i * ln10
  3) log(T90) = b0 + b1*yukseklik + b2*egim + b3*kuzeylik + b4*tekrar_yanma + [yangin olayi sabit etkisi]
     (yangin olayi etkisi: iki buyuk yangin farkli arazide; kosul etkisi her yanginin KENDI icinde olculur)
  4) Model tum bolgeye uygulanir -> 0.01 derece grid (web uygulamasi icin).
Cikti: cikti/kosul_modeli.json, cikti/kosul_grid.json, cikti/kosul_modeli.png
"""
import glob, json, math, os, re, sys, importlib.util
import numpy as np

KLASOR = os.path.dirname(os.path.abspath(__file__))
from bolge import BATI, GUNEY, DOGU, KUZEY, DATA, CIKTI
OBS = 2026.6
LN10 = math.log(10)


# ---------- NASADEM ----------
class DEM:
    def __init__(self):
        self.k = {}
        for f in glob.glob(os.path.join(DATA, "nasadem", "**", "*.hgt"), recursive=True):
            m = re.search(r"([ns])(\d\d)([ew])(\d\d\d)", os.path.basename(f).lower())
            la = int(m.group(2)) * (1 if m.group(1) == "n" else -1)
            lo = int(m.group(4)) * (1 if m.group(3) == "e" else -1)
            a = np.fromfile(f, dtype=">i2")
            n = int(round(math.sqrt(a.size)))
            a = a.reshape(n, n).astype(np.float32); a[a < -1000] = np.nan
            self.k[(la, lo)] = a
        if not self.k:
            sys.exit("NASADEM yok. Once: 1c_DEM_INDIR.bat")
        print(f"NASADEM: {len(self.k)} karo")

    def ozellik(self, lat, lon, yari=8):
        """lat/lon dizileri -> (yukseklik m, egim derece, kuzeylik -1..1) ~500 m pencere"""
        lat = np.asarray(lat, float); lon = np.asarray(lon, float)
        z = np.full(lat.shape, np.nan); s = np.full(lat.shape, np.nan); kz = np.full(lat.shape, np.nan)
        for i in range(lat.size):
            la, lo = lat.flat[i], lon.flat[i]
            a = self.k.get((math.floor(la), math.floor(lo)))
            if a is None:
                continue
            n = a.shape[0]
            r = int(round((math.floor(la) + 1 - la) * (n - 1))); c = int(round((lo - math.floor(lo)) * (n - 1)))
            r0, r1, c0, c1 = max(r - yari, 1), min(r + yari + 1, n - 1), max(c - yari, 1), min(c + yari + 1, n - 1)
            w = a[r0 - 1:r1 + 1, c0 - 1:c1 + 1]
            if w.size < 9 or np.isnan(w).all():
                continue
            dy = 30.87; dx = 30.87 * math.cos(math.radians(la))
            gy, gx = np.gradient(w, dy, dx)          # gy: satir artisi = guneye
            gy, gx = gy[1:-1, 1:-1], gx[1:-1, 1:-1]
            egim = np.degrees(np.arctan(np.hypot(gx, gy)))
            # yamacin baktigi yon: asagi dogru egim. kuzeylik = egimin kuzey bileseni
            h = np.hypot(gx, gy); h[h < 1e-6] = np.inf
            kuzey = gy / h   # gy>0: guneye dogru yukseliyor -> kuzeye bakar
            z.flat[i] = np.nanmean(w[1:-1, 1:-1]); s.flat[i] = np.nanmean(egim); kz.flat[i] = np.nanmean(kuzey)
        return z, s, kz


def _yukle_02():
    spec = importlib.util.spec_from_file_location("analiz02", os.path.join(KLASOR, "02_analiz.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def pikselleri_oku():
    G = json.load(open(os.path.join(CIKTI, "pikseller.geojson"), encoding="utf-8"))["features"]
    rows = []
    for f in G:
        p = f["properties"]
        if "R_ndvi" not in p or "R_hv_db" not in p:
            continue
        lo, la = f["geometry"]["coordinates"]
        rows.append([lo, la, p["yil"], p.get("kac_kez", 1), p["R_ndvi"], p["R_hv_db"]])
    return np.array(rows, float)


def t90_piksel(R, yas):
    Rc = np.clip(R, 0.03, 0.95)
    tau = -yas / np.log(1 - Rc)
    return tau * LN10


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    r2 = 1 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2)
    return beta, r2


def main():
    os.makedirs(CIKTI, exist_ok=True)
    P = pikselleri_oku()
    lon, lat, yil, kez, Rn, Rr = P.T
    yas = OBS - yil
    dem = DEM()
    z, s, kz = dem.ozellik(lat, lon)

    # Olay: buyuk yanginlar (yasa gore gruplar)
    olay = np.floor(yil).astype(int)
    buyuk = [y for y in np.unique(olay) if (olay == y).sum() >= 60]
    sec = np.isin(olay, buyuk) & np.isfinite(z) & np.isfinite(s)
    print(f"Modelde kullanilan piksel: {sec.sum()} (olaylar: {[int(b) for b in buyuk]})")

    # Standartlastirma
    ist = {"z": (float(np.nanmean(z[sec])), float(np.nanstd(z[sec]))),
           "s": (float(np.nanmean(s[sec])), float(np.nanstd(s[sec]))),
           "kz": (float(np.nanmean(kz[sec])), float(np.nanstd(kz[sec])))}
    std = lambda v, k: (v - ist[k][0]) / ist[k][1]
    sonuc = {"standart": ist, "olaylar": [int(b) for b in buyuk], "modeller": {}}

    for ad, R in (("optik", Rn), ("radar", Rr)):
        T = t90_piksel(R, yas)
        ok = sec & np.isfinite(T) & (R > 0.03) & (R < 0.95)
        y = np.log(T[ok])
        cols = [np.ones(ok.sum()), std(z[ok], "z"), std(s[ok], "s"), std(kz[ok], "kz"), (kez[ok] > 1).astype(float)]
        names = ["sabit", "yukseklik", "egim", "kuzeylik", "tekrar_yanma"]
        for b in buyuk[1:]:
            cols.append((olay[ok] == b).astype(float)); names.append(f"olay_{b}")
        X = np.column_stack(cols)
        beta, r2 = ols(X, y)
        # bootstrap belirsizlik (olay icinde)
        rng = np.random.default_rng(1); bs = []
        for _ in range(200):
            i = rng.integers(0, len(y), len(y)); bs.append(ols(X[i], y[i])[0])
        bs = np.array(bs)
        # olay sabitlerinin ortalamasi -> "tipik yangin"
        olay_ort = float(np.mean([0.0] + [beta[names.index(f"olay_{b}")] for b in buyuk[1:]]))
        katsayi = {n: {"b": float(beta[j]), "lo": float(np.percentile(bs[:, j], 5)), "hi": float(np.percentile(bs[:, j], 95))}
                   for j, n in enumerate(names)}
        sonuc["modeller"][ad] = {"katsayi": katsayi, "r2": float(r2), "n": int(ok.sum()), "olay_ortalama": olay_ort,
                                 "medyan_T90": float(np.exp(np.median(y)))}
        print(f"\n[{ad}] n={ok.sum()} R2={r2:.2f}  medyan T90={np.exp(np.median(y)):.1f} yil")
        for n in names[1:5]:
            k = katsayi[n]; etki = (math.exp(k['b']) - 1) * 100
            print(f"   {n:13s}: {'var/yok' if n=='tekrar_yanma' else '1 std artis'} -> T90 {etki:+.0f}%  (90% aralik {(math.exp(k['lo'])-1)*100:+.0f}% / {(math.exp(k['hi'])-1)*100:+.0f}%)")

    with open(os.path.join(CIKTI, "kosul_modeli.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)

    # ---------- Grid: tum bolgeye uygula ----------
    adim = 0.01
    glat = np.arange(GUNEY + adim / 2, KUZEY, adim); glon = np.arange(BATI + adim / 2, DOGU, adim)
    LO, LA = np.meshgrid(glon, glat)
    gz, gs, gk = dem.ozellik(LA.ravel(), LO.ravel(), yari=6)
    # orman maskesi: NDVI
    try:
        m02 = _yukle_02()
        x, y = m02.latlon_to_sin(LA.ravel(), LO.ravel())
        nd = m02.ndvi_ornekle(x, y)
    except Exception as e:
        print("NDVI maskesi atlandi:", e); nd = np.full(LA.size, np.nan)
    grid = []
    for i in range(LA.size):
        if not np.isfinite(gz[i]) or gz[i] < 5:
            continue
        orman = bool(np.isfinite(nd[i]) and nd[i] >= 0.45)
        rec = [round(float(LO.flat[i]), 3), round(float(LA.flat[i]), 3), int(round(gz[i])), round(float(gs[i]), 1),
               round(float(gk[i]), 2), 1 if orman else 0]
        for ad in ("optik", "radar"):
            k = sonuc["modeller"][ad]["katsayi"]
            v = (k["sabit"]["b"] + sonuc["modeller"][ad]["olay_ortalama"]
                 + k["yukseklik"]["b"] * std(gz[i], "z") + k["egim"]["b"] * std(gs[i], "s") + k["kuzeylik"]["b"] * std(gk[i], "kz"))
            rec.append(round(float(np.exp(v)), 1))
        grid.append(rec)
    with open(os.path.join(CIKTI, "kosul_grid.json"), "w", encoding="utf-8") as f:
        json.dump({"adim": adim, "alanlar": ["lon", "lat", "yukseklik", "egim", "kuzeylik", "orman", "T90_optik", "T90_radar"],
                   "grid": grid}, f, separators=(",", ":"))
    print(f"\nGrid: {len(grid)} hucre -> cikti/kosul_grid.json")
    ciz(sonuc, z, s, kz, Rr, yas, sec)


def ciz(sonuc, z, s, kz, Rr, yas, sec):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    adlar = ["yukseklik", "egim", "kuzeylik", "tekrar_yanma"]
    etiket = {"yukseklik": "Yukseklik (+1 std)", "egim": "Egim (+1 std)", "kuzeylik": "Kuzeye bakma (+1 std)", "tekrar_yanma": "Tekrar yanmis"}
    for j, (ad, col, off) in enumerate([("optik", "#2f9e44", -0.15), ("radar", "#7048e8", 0.15)]):
        k = sonuc["modeller"][ad]["katsayi"]
        for i, n in enumerate(adlar):
            b, lo, hi = [(math.exp(k[n][q]) - 1) * 100 for q in ("b", "lo", "hi")]
            ax.errorbar(b, i + off, xerr=[[b - lo], [hi - b]], fmt="o", color=col, capsize=3, label=ad if i == 0 else None)
    ax.axvline(0, color="k", lw=0.6); ax.set_yticks(range(len(adlar))); ax.set_yticklabels([etiket[a] for a in adlar])
    ax.set_xlabel("%90 toparlanma suresine etkisi (%)"); ax.set_title("Kosullar toparlanma suresini nasil degistiriyor?")
    ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(CIKTI, "kosul_modeli.png"))


if __name__ == "__main__":
    main()
