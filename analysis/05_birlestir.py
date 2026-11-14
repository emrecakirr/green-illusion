"""
The Green Illusion - 5. adim: tum bolgeleri birlestir -> web/gi_data.js
- Bolge bazli egriler (02_analiz ciktisi)
- Orman tipi (grup) bazli ortak egri: yangin olaylarinin medyanlarina agirlikli uyum,
  belirsizlik icin YANGIN BAZLI bootstrap (olaylar yeniden orneklenir)
- Kosul katsayilari (yukseklik, kuzeylik): bolge modellerinin piksel sayisina gore agirlikli ortalamasi
Kullanim: python 05_birlestir.py [kok_klasor]
"""
import json, math, os, sys
import numpy as np
from scipy.optimize import curve_fit

KOK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
OBS = 2026.6
REGIONS = [
    ("antalya", "med", [[36.70, 31.05], [37.12, 31.95]]),
    ("mugla", "med", None),
    ("evia", "med", None),
    ("california", "sierra", None),
]
from bolge import BOLGELER  # noqa: E402

f = lambda t, tau: 1 - np.exp(-t / tau)


def fit_events(ages, vals, w):
    tau, _ = curve_fit(f, ages, vals, p0=[15], sigma=1 / np.sqrt(w), bounds=(0.5, 400))
    return float(tau[0])


def group_fit(evs, key, n_boot=1000, seed=7):
    a = np.array([e["age"] for e in evs], float); v = np.array([e[key] for e in evs], float)
    w = np.array([e["n"] for e in evs], float) ** 0.5
    v = np.clip(v, -0.2, 1.1)
    tau = fit_events(a, v, w)
    rng = np.random.default_rng(seed); taus = []
    for _ in range(n_boot):
        i = rng.integers(0, len(a), len(a))
        if len(set(np.round(a[i]))) < 2:
            continue
        try:
            taus.append(fit_events(a[i], v[i], w[i]))
        except Exception:
            pass
    taus = np.array(taus)
    L = math.log(10)
    return {"tau": round(tau, 3), "t90": round(tau * L, 1),
            "lo": round(float(np.percentile(taus, 5)) * L, 1), "hi": round(float(np.percentile(taus, 95)) * L, 1)}


def main():
    out = {"obs": OBS, "regions": [], "groups": {}, "nPx": 0}
    grp_events, grp_cond, grp_n = {}, {}, {}
    for key, grp, focus in REGIONS:
        d = os.path.join(KOK, "cikti", key)
        if not os.path.exists(os.path.join(d, "pikseller.geojson")):
            print("atlandi (cikti yok):", key); continue
        S = json.load(open(os.path.join(d, "sonuc.json"), encoding="utf-8"))
        G = json.load(open(os.path.join(d, "pikseller.geojson"), encoding="utf-8"))["features"]
        px = []
        for ft in G:
            p = ft["properties"]
            if "R_ndvi" not in p or "R_hv_db" not in p:
                continue
            lo, la = ft["geometry"]["coordinates"]
            px.append([round(lo, 4), round(la, 4), round(p["yil"], 2), round(p["R_ndvi"], 3), round(p["R_hv_db"], 3)])
        P = np.array(px, float)
        yr = np.floor(P[:, 2]).astype(int)
        K = S["katmanlar"]
        nt = {}
        for kk, col in (("ndvi", 3), ("hv_db", 4)):
            e_ = K[kk]["egri"]
            nt[kk] = e_ is None or e_["t90"] > 250
            if nt[kk]:
                ref, tb = K[kk]["referans"], K[kk]["taban"]
                v = tb + P[:, col] * (ref - tb)
                ys = [y for y in sorted(set(yr), reverse=True) if (yr == y).sum() >= 50]
                floor = float(np.median(v[yr == ys[0]])) if ys else tb
                if abs(ref - floor) > 1e-6:
                    P[:, col] = (v - floor) / (ref - floor)
                for i in range(len(px)):
                    px[i][col] = round(float(P[i, col]), 3)
                print(f"  {key}: {kk} egilimi yok, taban {ys[0] if ys else '-'} yangini ile yeniden tanimlandi")
        no_trend = nt["hv_db"]
        events = []
        for y in sorted(set(yr)):
            m = yr == y
            if m.sum() < 50:
                continue
            events.append({"y": int(y), "n": int(m.sum()), "age": round(float(OBS - np.median(P[m, 2])), 1),
                           "opt": round(float(np.median(P[m, 3])), 3), "rad": round(float(np.median(P[m, 4])), 3)})
        def cur(k):
            e = K[k]["egri"]; return {"tau": round(e["tau"], 3), "t90": round(e["t90"], 1), "lo": round(e["t90_alt"], 1), "hi": round(e["t90_ust"], 1)}
        b = BOLGELER[key]["bbox"]
        reg = {"key": key, "group": grp, "bbox": list(b), "center": [round((b[1] + b[3]) / 2, 3), round((b[0] + b[2]) / 2, 3)],
               "focus": focus, "img": os.path.exists(os.path.join(KOK, "web", "img", key, "radar_hv.jpg")) or os.path.exists(os.path.join(KOK, "web", "img", key, "radar_hv.png")),
               "n": len(px), "opt": ({"noTrend": True} if nt["ndvi"] else cur("ndvi")), "rad": ({"noTrend": True} if no_trend else cur("hv_db")), "events": events, "px": px}
        out["regions"].append(reg); out["nPx"] += len(px)
        grp_events.setdefault(grp, []).extend([dict(e, noTrendR=nt["hv_db"], noTrendO=nt["ndvi"]) for e in events])
        grp_n[grp] = grp_n.get(grp, 0) + len(px)
        km = os.path.join(d, "kosul_modeli.json")
        if os.path.exists(km):
            M = json.load(open(km, encoding="utf-8"))
            st = M["standart"]
            c = {"n": len(px), "zmean": st["z"][0], "zstd": st["z"][1], "kmean": st["kz"][0], "kstd": st["kz"][1]}
            for ad, kk in (("optik", "opt"), ("radar", "rad")):
                co = M["modeller"][ad]["katsayi"]
                c["bz_" + kk] = co["yukseklik"]["b"] / st["z"][1]
                c["bk_" + kk] = co["kuzeylik"]["b"] / st["kz"][1]
            grp_cond.setdefault(grp, []).append(c)
        print(f"{key}: {len(px)} piksel, {len(events)} yangin, optik {reg['opt'].get('t90', 'egilim yok')} / radar {reg['rad'].get('t90', 'egilim yok')}")

    for grp, evs in grp_events.items():
        evr = [e for e in evs if not e.get("noTrendR")]
        evo = [e for e in evs if not e.get("noTrendO")]
        g = {"opt": group_fit(evo, "opt"), "rad": (group_fit(evr, "rad") if len(evr) >= 3 else {"noTrend": True}), "n": grp_n[grp], "nEv": len(evs)}
        cs = grp_cond.get(grp, [])
        if cs:
            w = np.array([c["n"] for c in cs], float); w /= w.sum()
            avg = lambda k: float(np.sum([wi * c[k] for wi, c in zip(w, cs)]))
            zmean = avg("zmean"); zstd = math.sqrt(avg("zstd") ** 2)
            g["cond"] = {"zmean": round(zmean, 1), "zlo": round(max(0, zmean - 2 * zstd), 0), "zhi": round(zmean + 2 * zstd, 0),
                         "kmean": round(avg("kmean"), 3),
                         "bz_opt": avg("bz_opt"), "bz_rad": avg("bz_rad"), "bk_opt": avg("bk_opt"), "bk_rad": avg("bk_rad")}
        else:
            g["cond"] = {"zmean": 500, "zlo": 0, "zhi": 2000, "kmean": 0, "bz_opt": 0, "bz_rad": 0, "bk_opt": 0, "bk_rad": 0}
        out["groups"][grp] = g
        print(f"GRUP {grp}: {len(evs)} yangin, optik {g['opt']} radar {g['rad']}")
        print("   kosul:", {k: (round(v, 6) if isinstance(v, float) else v) for k, v in g["cond"].items()})
    os.makedirs(os.path.join(KOK, "web"), exist_ok=True)
    with open(os.path.join(KOK, "web", "gi_data.js"), "w", encoding="utf-8") as fh:
        fh.write("window.GI=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False) + ";")
    print("-> web/gi_data.js")


if __name__ == "__main__":
    main()
