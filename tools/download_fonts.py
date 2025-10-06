# tools/download_fonts.py
import os
import urllib.request

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "api", "pdf_utils", "assets")

FONTS = {
    "NotoNaskhArabic-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf",
    "NotoNaskhArabic-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Bold.ttf",
    # ✅ روابط DejaVu الرسمية من SourceForge (دائمة وثابتة)
    "DejaVuSans.ttf": "https://downloads.sourceforge.net/project/dejavu/dejavu/2.37/dejavu-fonts-ttf-2.37.zip",
    "DejaVuSans-Bold.ttf": "https://downloads.sourceforge.net/project/dejavu/dejavu/2.37/dejavu-fonts-ttf-2.37.zip",
}

def download_and_extract(zip_url, dest_dir, names):
    import zipfile, io
    print(f"⬇️ Downloading {zip_url} ...")
    data = urllib.request.urlopen(zip_url).read()
    zf = zipfile.ZipFile(io.BytesIO(data))
    for name in names:
        found = [x for x in zf.namelist() if x.endswith(f"/ttf/{name}")]
        if found:
            print(f"📦 Extracting {name}")
            with zf.open(found[0]) as fsrc, open(os.path.join(dest_dir, name), "wb") as fdst:
                fdst.write(fsrc.read())

os.makedirs(FONT_DIR, exist_ok=True)

# العربية
for name, url in list(FONTS.items())[:2]:
    dest = os.path.join(FONT_DIR, name)
    if not os.path.exists(dest):
        print(f"⬇️ Downloading {name} ...")
        urllib.request.urlretrieve(url, dest)
        print(f"✅ Saved to {dest}")
    else:
        print(f"✔️ {name} already exists")

# DejaVu من zip واحد
dejavu_names = ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"]
if not all(os.path.exists(os.path.join(FONT_DIR, n)) for n in dejavu_names):
    download_and_extract(FONTS["DejaVuSans.ttf"], FONT_DIR, dejavu_names)
else:
    print("✔️ DejaVuSans fonts already exist")

print("🎯 All fonts available in:", FONT_DIR)
