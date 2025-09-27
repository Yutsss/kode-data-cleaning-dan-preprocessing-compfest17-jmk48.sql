import pandas as pd

# === helper: baca CSV dengan auto-detect delimiter + rapikan header ===
def read_csv_flex(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = [c.strip() for c in df.columns]
    return df

# === 1. Load Data ===
df_kota = read_csv_flex("datasets/kota_final.csv")
df_prov = read_csv_flex("datasets/provinsi_final.csv")
df_nas  = read_csv_flex("datasets/nasional_final.csv")

# === 2. Rapikan Struktur ===

# Kota
df_kota = df_kota.rename(columns={
    "stunting_prevalence": "stunting",
    "life_expectancy_at_birth": "life_expectancy"
})
df_kota["level"] = "kota"
df_kota["country"] = "Indonesia"

# Provinsi
df_prov = df_prov.rename(columns={
    "stunting_prevalence": "stunting",
    "life_expectancy_at_birth": "life_expectancy"
})
df_prov["kota_kabupaten"] = None
df_prov["level"] = "provinsi"
df_prov["country"] = "Indonesia"

# 🔑 Bersihkan nilai stunting (ganti koma jadi titik, convert ke float)
df_prov["stunting"] = (
    df_prov["stunting"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)
df_prov["stunting"] = pd.to_numeric(df_prov["stunting"], errors="coerce")

# Nasional
df_nas = df_nas.rename(columns={
    "stunting_prevalence": "stunting",
    "life_expectancy_at_birth": "life_expectancy"
})
df_nas["provinsi"] = None
df_nas["kota_kabupaten"] = None
df_nas["level"] = "nasional"
df_nas["country"] = "Indonesia"

# === 3. Samakan Urutan Kolom ===
columns = ["country", "tahun", "provinsi", "kota_kabupaten",
           "stunting", "life_expectancy", "hdi", "level"]

df_kota = df_kota[columns]
df_prov = df_prov[columns]
df_nas  = df_nas[columns]

# === 4. Gabungkan Semua ===
df_master = pd.concat([df_nas, df_prov, df_kota], ignore_index=True)

# === 5. Tambahkan kolom status ===
df_master["status"] = "actual"

# === 6. Simpan ke File ===
df_master.to_csv("datasets/final_all.csv", index=False)

print("Master dataset berhasil dibuat:", df_master.shape)
