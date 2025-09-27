import pandas as pd
import glob

# Path daftar provinsi
provinsi_path = "datasets/daftar_provinsi.csv"
df_provinsi = pd.read_csv(provinsi_path)
df_provinsi.columns = ["Provinsi"]

# Normalisasi nama provinsi
def normalize_name(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace("dki jakarta", "jakarta")
        .replace("di yogyakarta", "d i yogyakarta")
        .replace("kepulauan bangka belitung", "kep. bangka belitung")
    )

df_provinsi["Provinsi_norm"] = df_provinsi["Provinsi"].apply(normalize_name)

# Ambil semua file Life Expectancy
files = sorted(glob.glob("datasets/Life Expectancy at Birth *.csv"))

all_data = []

for file in files:
    year = file.split("Life Expectancy at Birth ")[1].split(".csv")[0]
    df_temp = pd.read_csv(file, sep=None, engine="python")

    prov_col = df_temp.columns[0].strip()
    value_col = df_temp.columns[1]

    df_year = df_temp[[prov_col, value_col]].copy()
    df_year.columns = ["Provinsi", "Life Expectancy at Birth (Year)"]
    df_year["Tahun"] = int(year)

    # === PERLAKUAN KHUSUS GORONTALO (PROVINSI vs KOTA) ===
    # Buang baris yang adalah KOTA (mis. "Gorontalo" title-case atau "Kota Gorontalo"),
    # tetapi biarkan "GORONTALO" (ALL CAPS) tetap sebagai provinsi.
    _prov_raw = df_year["Provinsi"].astype(str)
    mask_kota_title = _prov_raw.str.strip().eq("Gorontalo")
    mask_kota_phrase = _prov_raw.str.contains(r"\bKota\s+Gorontalo\b", case=False, na=False)
    df_year = df_year[~(mask_kota_title | mask_kota_phrase)].copy()
    # === END KHUSUS GORONTALO ===

    # Normalisasi nama provinsi
    df_year["Provinsi_norm"] = df_year["Provinsi"].apply(normalize_name)

    all_data.append(df_year)

# Gabungkan semua tahun
df_life = pd.concat(all_data, ignore_index=True)

# Join pakai kolom norm
df_final = pd.merge(df_provinsi, df_life, on="Provinsi_norm", how="left")

# Rapikan output
df_final = df_final[["Provinsi_x", "Tahun", "Life Expectancy at Birth (Year)"]]
df_final = df_final.rename(columns={"Provinsi_x": "Provinsi"})

# Pastikan Tahun integer (bukan float .0)
df_final["Tahun"] = df_final["Tahun"].astype("Int64")

# Urutkan hasil
df_final = df_final.sort_values(["Provinsi", "Tahun"])

# Simpan
df_final.to_csv("datasets/life_expectancy_prov.csv", index=False)
