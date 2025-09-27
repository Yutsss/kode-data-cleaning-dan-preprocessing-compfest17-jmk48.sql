import pandas as pd

# Load file nasional
df_hdi = pd.read_csv("datasets/hdi_nasional.csv")
df_le = pd.read_csv("datasets/life_expectancy_nasional.csv")
df_stunting = pd.read_csv("datasets/Prev Stunting Nasional 2019-2024.csv", sep=";")

# Rapikan kolom HDI & LE
df_hdi = df_hdi.rename(columns={"Tahun": "tahun", "HDI": "hdi"})
df_le = df_le.rename(columns={"Tahun": "tahun", "Life Expectancy at Birth (Year)": "life_expectancy_at_birth"})

# Rapikan stunting nasional
df_stunting = df_stunting.rename(columns={"prevalensi": "stunting_prevalence"})
df_stunting["tahun"] = pd.to_numeric(df_stunting["tahun"], errors="coerce").astype("Int64")

# Ubah prevalensi jadi float (ganti koma -> titik)
df_stunting["stunting_prevalence"] = (
    df_stunting["stunting_prevalence"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# Merge berdasarkan tahun
df_merge = pd.merge(df_hdi, df_le, on="tahun", how="outer")
df_merge = pd.merge(df_merge, df_stunting[["tahun", "stunting_prevalence"]], on="tahun", how="outer")

# Atur urutan kolom
df_merge = df_merge[["tahun", "stunting_prevalence", "life_expectancy_at_birth", "hdi"]]

# Urutkan berdasarkan tahun
df_merge = df_merge.sort_values("tahun")

# Simpan hasil
df_merge.to_csv("datasets/nasional_final.csv", index=False, sep=";")
print("✅ File nasional tersimpan di datasets/nasional_final.csv")
