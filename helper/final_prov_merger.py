import pandas as pd

# Load semua file
df_hdi = pd.read_csv("datasets/hdi_provinsi.csv")
df_le = pd.read_csv("datasets/life_expectancy_prov.csv")
df_stunting = pd.read_csv("datasets/Prev Sunting Prov 2019-2024.csv", sep=";")

# Reshape stunting: dari wide ke long
df_stunting = df_stunting.melt(
    id_vars=["Provinsi"],
    var_name="Tahun",
    value_name="stunting_prevalence"
)

# Pastikan tipe data Tahun
for df in [df_hdi, df_le, df_stunting]:
    df["Tahun"] = df["Tahun"].astype("Int64")

# Rapikan kolom Life Expectancy
df_le = df_le.rename(columns={"Life Expectancy at Birth (Year)": "life_expectancy_at_birth"})

# Samakan nama kolom HDI
df_hdi = df_hdi.rename(columns={"HDI": "hdi"})

# Gabung dengan outer join agar tahun yang tidak ada di stunting tetap muncul
df_merge = pd.merge(df_hdi, df_le, on=["Provinsi", "Tahun"], how="outer")
df_merge = pd.merge(df_merge, df_stunting, on=["Provinsi", "Tahun"], how="outer")

# Ubah nama kolom jadi huruf kecil semua
df_merge = df_merge.rename(columns={
    "Provinsi": "provinsi",
    "Tahun": "tahun"
})

# Atur urutan kolom: tahun, provinsi, stunting_prevalence, life_expectancy_at_birth, hdi
df_merge = df_merge[["tahun", "provinsi", "stunting_prevalence", "life_expectancy_at_birth", "hdi"]]

# Urutkan hasil
df_merge = df_merge.sort_values(["provinsi", "tahun"])

# Simpan
df_merge.to_csv("datasets/provinsi_final.csv", index=False, sep=";")
print("✅ File tersimpan di datasets/provinsi_final.csv")
