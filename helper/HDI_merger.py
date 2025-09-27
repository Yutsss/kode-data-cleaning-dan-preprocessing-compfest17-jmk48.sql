import pandas as pd
import glob

# ============================================================
# HDI PROVINSI + NASIONAL
# ============================================================

# Load daftar provinsi (acuan)
provinsi_path = "datasets/daftar_provinsi.csv"
df_provinsi = pd.read_csv(provinsi_path)
df_provinsi.columns = ["Provinsi"]

# Normalisasi nama
def normalize_name(name):
    return str(name).strip().lower()

df_provinsi["Provinsi_norm"] = df_provinsi["Provinsi"].apply(normalize_name)

# Mapping khusus untuk provinsi
prov_mapping = {
    "kep. bangka belitung": "kepulauan bangka belitung",
    "kepulauan bangka belitung": "kepulauan bangka belitung",
    "kep. riau": "kepulauan riau",
    "kepulauan riau": "kepulauan riau",
}

# Ambil semua file HDI provinsi
files = sorted(glob.glob("datasets/HDI Prov *.csv"))

all_data = []
all_nasional = []

for file in files:
    year = file.split("HDI Prov ")[1].split(".csv")[0]
    df_temp = pd.read_csv(file, sep=None, engine="python")

    wilayah_col = df_temp.columns[0].strip()
    value_col = df_temp.columns[1]

    df_year = df_temp[[wilayah_col, value_col]].copy()
    df_year.columns = ["Provinsi", "HDI"]
    df_year["Tahun"] = int(year)

    # Terapkan mapping
    df_year["Provinsi"] = df_year["Provinsi"].str.strip()
    df_year["Provinsi_norm"] = df_year["Provinsi"].str.lower()
    df_year["Provinsi_norm"] = df_year["Provinsi_norm"].replace(prov_mapping)

    # Simpan data nasional
    if "indonesia" in df_year["Provinsi_norm"].values:
        val = df_year.loc[df_year["Provinsi_norm"] == "indonesia", "HDI"].values[0]
        all_nasional.append({"Tahun": int(year), "HDI": val})

    all_data.append(df_year)

# Gabungkan semua tahun (provinsi)
df_hdi = pd.concat(all_data, ignore_index=True)

# Join dengan daftar provinsi
df_final = pd.merge(df_provinsi, df_hdi, on="Provinsi_norm", how="left")

# Rapikan output provinsi
df_final = df_final[["Tahun", "Provinsi_x", "HDI"]]
df_final = df_final.rename(columns={"Provinsi_x": "Provinsi"})

# Urutkan hasil
df_final = df_final.sort_values(["Provinsi", "Tahun"]).reset_index(drop=True)

# Simpan provinsi
df_final.to_csv("datasets/hdi_provinsi.csv", index=False)

# Gabungkan nasional
df_nasional = pd.DataFrame(all_nasional).sort_values("Tahun").reset_index(drop=True)

# Simpan nasional
df_nasional.to_csv("datasets/hdi_nasional.csv", index=False)


# ============================================================
# HDI KOTA
# ============================================================

# Load daftar kota (acuan)
df_kota = pd.read_csv("datasets/daftar_kota.csv")
df_kota.columns = ["Kota/Kabupaten"]
df_kota["kota_norm"] = df_kota["Kota/Kabupaten"].str.strip().str.lower()

# Mapping nama kota (HDI -> standar daftar_kota)
name_mapping = {
    "batang hari": "batanghari",
    "fakfak": "fak fak",
    "kota palangka raya": "kota palangkaraya",
    "kota makasar": "kota makassar",
    "kota parepare": "kota pare pare",
    "kota pematang siantar": "kota pematangsiantar",
    "kota lubuklinggau": "kota lubuk linggau",
    "kota sawah lunto": "kota sawahlunto",
    "kep. seribu": "kepulauan seribu",
    "siau tagulandang biaro": "kepulauan siau tagulandang biaro (sitaro)",
    "maluku tenggara barat / kepulauan tanimbar": "kepulauan tanimbar (maluku tenggara barat)",
    "mamuju utara / pasangkayu": "pasangkayu (mamuju utara)",
    "toba samosir / toba": "toba",
    "labuhan batu": "labuhanbatu",
    "labuhan batu selatan": "labuhanbatu selatan",
    "labuhan batu utara": "labuhanbatu utara",
    "mukomuko": "muko muko",
    "pohuwato": "pahuwato",
    "pangkajene dan kepulauan": "pangkajene kepulauan",
    "tojo una-una": "tojo una una",
    "toli-toli": "toli toli",
    "tulangbawang": "tulang bawang",
    "banyu asin": "banyuasin",
    "gunung kidul": "gunungkidul",
    "kota banjar baru": "kota banjarbaru",
    "kota baubau": "kota bau bau",
}

# Ambil semua file HDI kota
files_kota = sorted([f for f in glob.glob("datasets/HDI *.csv") if "Prov" not in f])

all_data_kota = []
for file in files_kota:
    year = int(file.split("HDI ")[1].split(".csv")[0])
    df_temp = pd.read_csv(file, sep=None, engine="python")

    wilayah_col = df_temp.columns[0].strip()
    value_col = df_temp.columns[1]

    df_year = df_temp[[wilayah_col, value_col]].copy()
    df_year.columns = ["Kota/Kabupaten", "HDI"]
    df_year["Tahun"] = year

    # === FIX GORONTALO (MINIMAL): buang provinsi ALL CAPS yang nyasar ke data kota ===
    df_year["Kota/Kabupaten"] = df_year["Kota/Kabupaten"].astype(str)
    df_year = df_year[~df_year["Kota/Kabupaten"].str.strip().eq("GORONTALO")].copy()
    # (tidak menyentuh "Gorontalo" atau "Kota Gorontalo")
    # === END FIX ===

    # Normalisasi nama
    df_year["kota_norm"] = df_year["Kota/Kabupaten"].str.strip().str.lower()
    df_year["kota_norm"] = df_year["kota_norm"].replace(name_mapping)

    all_data_kota.append(df_year)

# Gabungkan semua tahun HDI kota
df_hdi_kota = pd.concat(all_data_kota, ignore_index=True)

# Join dengan daftar kota (acuan)
df_final_kota = pd.merge(df_kota, df_hdi_kota, on="kota_norm", how="left")

# Rapikan output kota
df_final_kota = df_final_kota[["Kota/Kabupaten_x", "Tahun", "HDI"]]
df_final_kota = df_final_kota.rename(columns={"Kota/Kabupaten_x": "Kota/Kabupaten"})

# Hilangkan duplikat per kota–tahun (ambil HDI yang tidak NaN)
df_final_kota = (
    df_final_kota
    .sort_values(["Kota/Kabupaten", "Tahun", "HDI"], ascending=[True, True, False])
    .drop_duplicates(subset=["Kota/Kabupaten", "Tahun"], keep="first")
)

# Urutkan akhir
df_final_kota = df_final_kota.sort_values(["Kota/Kabupaten", "Tahun"]).reset_index(drop=True)

# Simpan kota
df_final_kota.to_csv("datasets/hdi_kota.csv", index=False)

print("✅ hdi_provinsi.csv, hdi_nasional.csv, dan hdi_kota.csv sudah dibuat (duplikat kota fix + filter GORONTALO provinsi).")
