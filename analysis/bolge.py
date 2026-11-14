"""Calisma bolgeleri. Secim: ortam degiskeni GI_BOLGE (varsayilan antalya)."""
import os
BOLGELER = {
    "antalya":    {"ad": "Antalya, Türkiye",          "bbox": (30.9, 36.6, 32.2, 37.3),   "tile": "h20v05"},
    "mugla":      {"ad": "Muğla, Türkiye",            "bbox": (27.6, 36.7, 28.9, 37.4),   "tile": "h20v05"},
    "evia":       {"ad": "Evia (Eğriboz), Greece",    "bbox": (22.9, 38.6, 23.7, 39.1),   "tile": "h19v05"},
    "california": {"ad": "Northern Sierra, California", "bbox": (-121.9, 39.45, -120.7, 39.98), "tile": "h08v05"},
}
AD_KOD = os.environ.get("GI_BOLGE", "antalya")
B = BOLGELER[AD_KOD]
BATI, GUNEY, DOGU, KUZEY = B["bbox"]
TILE = B["tile"]
KOK = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(KOK, "data")
NISAR_DIR = os.path.join(DATA, "nisar_gcov") if AD_KOD == "antalya" else os.path.join(DATA, "nisar_gcov", AD_KOD)
CIKTI = os.path.join(KOK, "cikti", AD_KOD)
WEBIMG = os.path.join(KOK, "web", "img", AD_KOD)
for d in (NISAR_DIR, CIKTI):
    os.makedirs(d, exist_ok=True)
