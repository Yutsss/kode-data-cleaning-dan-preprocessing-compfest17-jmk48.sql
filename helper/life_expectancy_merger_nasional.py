import pandas as pd
import glob

# Ambil semua file Life Expectancy
files = sorted(glob.glob("datasets/Life Expectancy at Birth *.csv"))

all_data = []

for file in files:
    # Ambil tahun dari nama file
    year = file.split("Life Expectancy at Birth ")[1].split(".csv")[0]
    df_temp = pd.read_csv(file, sep=None, engine="python")

    # Asumsi kolom pertama adalah wilayah (Provinsi/Nasional)
    prov_col = df_temp.columns[0].strip()
    value_col = df_temp.columns[1]

    # Cari baris yang berisi Indonesia (nasional)
    mask = df_temp[prov_col].str.strip().str.lower().eq("indonesia")
    if mask.any():
        val = df_temp.loc[mask, value_col].values[0]
        all_data.append({"Tahun": int(year), "Life Expectancy at Birth (Year)": val})

# Buat dataframe nasional
df_nasional = pd.DataFrame(all_data).sort_values("Tahun")

# Simpan ke CSV baru
df_nasional.to_csv("datasets/life_expectancy_nasional.csv", index=False)
