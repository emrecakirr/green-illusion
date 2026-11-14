"""NASA NASADEM (30 m yukseklik modeli) - Antalya calisma alani icin indir -> data/nasadem/"""
import os, sys, zipfile
KLASOR = os.path.dirname(os.path.abspath(__file__))
HEDEF = os.path.join(KLASOR, "data", "nasadem")
from bolge import BATI, GUNEY, DOGU, KUZEY
BBOX = (BATI, GUNEY, DOGU, KUZEY)

def main():
    import earthaccess
    os.makedirs(HEDEF, exist_ok=True)
    earthaccess.login(strategy="netrc")
    g = earthaccess.search_data(short_name="NASADEM_HGT", version="001", bounding_box=BBOX)
    print(f"NASADEM: {len(g)} karo bulundu")
    yollar = earthaccess.download(g, local_path=HEDEF, threads=4)
    for y in yollar:
        y = str(y)
        if y.endswith(".zip"):
            with zipfile.ZipFile(y) as z:
                for n in z.namelist():
                    if n.endswith(".hgt") and not os.path.exists(os.path.join(HEDEF, n)):
                        z.extract(n, HEDEF); print("  acildi:", n)
    print("Bitti. Simdi: 3_KOSUL_MODELI.bat")

if __name__ == "__main__":
    main()
