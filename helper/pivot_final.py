import pandas as pd

# Baca file asli
df = pd.read_csv("datasets/final_all.csv")

# Perbaiki typo kolom "leve" → "level"
df = df.rename(columns={"leve": "level"})

# Pivot/Melt kolom indikator
df_pivot = df.melt(
    id_vars=["country", "tahun", "provinsi", "kota_kabupaten", "level"],
    value_vars=["stunting", "life_expectancy", "hdi"],
    var_name="Pivot HDI, LE, Stunting",
    value_name="Pivot HDI, LE, Stunting (Values)"
)

# Simpan ke file baru
df_pivot.to_csv("datasets/final_all_pivot.csv", index=False)
print("✅ File pivot siap: datasets/final_all_pivot.csv")
