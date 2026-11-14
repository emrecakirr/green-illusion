"""
The Green Illusion - 4. adim: harita gorselleri
===============================================
NISAR HV radar goruntusu ve MODIS NDVI goruntusunu ayni enlem/boylam gridine
cevirip PNG olarak kaydeder (web uygulamasindaki "perde" karsilastirmasi icin).
Cikti: web/img/radar_hv.png, web/img/optik_ndvi.png, web/img/bounds.json
"""
import glob, json, os, importlib.util
import numpy as np

KLASOR = os.path.dirname(os.path.abspath(__file__))
from bolge import BATI, GUNEY, DOGU, KUZEY, DATA, NISAR_DIR, WEBIMG as OUT
ADIM = 0.001  # ~100 m


def m02():
    spec = importlib.util.spec_from_file_location("analiz02", os.path.join(KLASOR, "02_analiz.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def kaydet_png(rgba, yol):
    import matplotlib.image as mpimg
    mpimg.imsave(yol, rgba)


def main():
    os.makedirs(OUT, exist_ok=True)
    lons = np.arange(BATI + ADIM / 2, DOGU, ADIM)
    lats = np.arange(KUZEY - ADIM / 2, GUNEY, -ADIM)       # kuzeyden guneye (goruntu satirlari)
    LO, LA = np.meshgrid(lons, lats)
    print(f"Grid: {LO.shape[1]} x {LO.shape[0]}")

    # ---- NISAR HV ----
    import h5py
    from pyproj import Transformer
    hv = np.full(LO.shape, np.nan, np.float32)
    for d in sorted(glob.glob(os.path.join(NISAR_DIR, "*.h5"))):
        with h5py.File(d, "r") as f:
            yollar = []
            f.visititems(lambda ad, o: yollar.append(ad) if ad.endswith("frequencyA/HVHV") else None)
            if not yollar:
                continue
            grup = yollar[0].rsplit("/", 1)[0]
            xk = f[grup + "/xCoordinates"][:]; yk = f[grup + "/yCoordinates"][:]
            pr = f[grup + "/projection"]
            epsg = int(pr.attrs.get("epsg_code", pr[()] if pr.shape == () else 0))
            tr = Transformer.from_crs(4326, epsg, always_xy=True)
            px, py = tr.transform(LO, LA)
            dx = xk[1] - xk[0]; dy = yk[1] - yk[0]
            c = np.round((px - xk[0]) / dx).astype(int); r = np.round((py - yk[0]) / dy).astype(int)
            ic = (c >= 0) & (c < len(xk)) & (r >= 0) & (r < len(yk))
            r0, r1, c0, c1 = r[ic].min(), r[ic].max() + 1, c[ic].min(), c[ic].max() + 1
            blok = f[grup + "/HVHV"][r0:r1, c0:c1].astype(np.float32)
            blok[(blok <= 0) | ~np.isfinite(blok)] = np.nan
            # 5x5 ortalama (speckle azaltma, ~100 m)
            k = max(1, int(round(ADIM * 111000 / abs(dx) / 1.0)))
            k = min(k, 7)
            from scipy.ndimage import uniform_filter
            v = np.nan_to_num(blok); w = np.isfinite(blok).astype(np.float32)
            num = uniform_filter(v, k); den = uniform_filter(w, k)
            ort = np.where(den > 0.3, num / np.maximum(den, 1e-6), np.nan)
            deger = np.full(LO.shape, np.nan, np.float32)
            deger[ic] = ort[r[ic] - r0, c[ic] - c0]
            hv = np.where(np.isfinite(deger), deger, hv)
            print(f"NISAR: {os.path.basename(d)}")
    hv_db = 10 * np.log10(hv)
    lo, hi = np.nanpercentile(hv_db, [2, 98])
    g = np.clip((hv_db - lo) / (hi - lo), 0, 1)
    rgba = np.zeros(LO.shape + (4,), np.float32)
    rgba[..., 0] = g; rgba[..., 1] = g; rgba[..., 2] = g
    rgba[..., 3] = np.isfinite(hv_db).astype(np.float32)
    kaydet_png(rgba, os.path.join(OUT, "radar_hv.png"))
    print(f"radar_hv.png  (HV dB aralik {lo:.1f} .. {hi:.1f})")

    # ---- MODIS NDVI ----
    M = m02()
    x, y = M.latlon_to_sin(LA.ravel(), LO.ravel())
    nd = M.ndvi_ornekle(x, y).reshape(LO.shape)
    import matplotlib
    cmap = matplotlib.colormaps["YlGn"]
    n = np.clip((nd - 0.05) / 0.75, 0, 1)
    rgba2 = cmap(n).astype(np.float32)
    rgba2[..., 3] = np.isfinite(nd).astype(np.float32)
    kaydet_png(rgba2, os.path.join(OUT, "optik_ndvi.png"))
    print("optik_ndvi.png")

    with open(os.path.join(OUT, "bounds.json"), "w") as f:
        json.dump({"bounds": [[GUNEY, BATI], [KUZEY, DOGU]], "hv_db_range": [float(lo), float(hi)]}, f)
    print("Bitti ->", OUT)


if __name__ == "__main__":
    main()
