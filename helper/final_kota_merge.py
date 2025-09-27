import pandas as pd
import re
import os

# ==== Path file ====
PATH_HDI = "datasets/hdi_kota.csv"
PATH_LE  = "datasets/life_expectancy_kota.csv"
PATH_ST  = "datasets/Prev Stunting Kota 2019-2024.csv"
OUT_CSV  = "datasets/kota_final.csv"

# ==== Load & rapikan HDI ====
df_hdi = pd.read_csv(PATH_HDI, sep=None, engine="python")
assert {"Kota/Kabupaten", "Tahun", "HDI"}.issubset(df_hdi.columns), "Struktur hdi_kota.csv tidak sesuai."
df_hdi["Tahun"] = pd.to_numeric(df_hdi["Tahun"], errors="coerce").astype("Int64")
df_hdi = df_hdi.dropna(subset=["Kota/Kabupaten", "Tahun"])
df_hdi = df_hdi.rename(columns={"HDI": "hdi"})
df_hdi["hdi"] = pd.to_numeric(df_hdi["hdi"], errors="coerce")

# ==== Load & rapikan Life Expectancy ====
df_le = pd.read_csv(PATH_LE, sep=None, engine="python")
assert {"Kota/Kabupaten", "Tahun", "Life Expectancy at Birth (Year)", "Provinsi"}.issubset(df_le.columns), "Struktur life_expectancy_kota.csv tidak sesuai."
df_le["Tahun"] = pd.to_numeric(df_le["Tahun"], errors="coerce").astype("Int64")
df_le = df_le.dropna(subset=["Kota/Kabupaten", "Tahun"])
df_le = df_le.rename(columns={"Life Expectancy at Birth (Year)": "life_expectancy_at_birth"})
df_le["life_expectancy_at_birth"] = pd.to_numeric(df_le["life_expectancy_at_birth"], errors="coerce")

# ==== Load & reshape Stunting (wide → long) ====
df_st = pd.read_csv(PATH_ST, sep=None, engine="python")

# Bersihkan BOM & spasi nama kolom
df_st.columns = [c.strip().replace("\ufeff", "") for c in df_st.columns]

# Abaikan kolom "id" kalau ada
if "id" in df_st.columns:
    df_st = df_st.drop(columns=["id"])

# Deteksi nama kolom kota & provinsi
kota_col = next((c for c in ["Kota/Kabupaten","Kabupaten/Kota","nama kota/kab","Kota/Kab"] if c in df_st.columns), None)
prov_col = next((c for c in ["Provinsi","provinsi","nama provinsi"] if c in df_st.columns), None)
if kota_col is None or prov_col is None:
    raise ValueError("CSV stunting kota harus memiliki kolom kota dan provinsi (mis. 'Kabupaten/Kota' & 'Provinsi').")

# Ambil kolom tahun valid (format 4 digit)
year_cols = [c for c in df_st.columns if re.fullmatch(r"\d{4}", str(c))]
if not year_cols:
    raise ValueError("Tidak menemukan kolom tahun (format 4 digit) pada CSV stunting kota.")

df_st = df_st.melt(
    id_vars=[kota_col, prov_col],
    value_vars=year_cols,
    var_name="Tahun",
    value_name="stunting_prevalence"
)

# Tipe tahun
df_st["Tahun"] = pd.to_numeric(df_st["Tahun"], errors="coerce").astype("Int64")

# ✅ Konversi angka desimal (biarkan titik sebagai desimal, koma ubah jadi titik)
df_st["stunting_prevalence"] = (
    df_st["stunting_prevalence"]
    .astype(str)
    .str.replace(",", ".", regex=False)  # koma → titik
    .str.strip()
)
df_st["stunting_prevalence"] = pd.to_numeric(df_st["stunting_prevalence"], errors="coerce")

# Samakan nama kolom
df_st = df_st.rename(columns={kota_col: "Kota/Kabupaten", prov_col: "Provinsi"})

# ==== Merge (outer), isi Provinsi yang hilang dari peta LE/Stunting ====
df_merge = pd.merge(df_le, df_hdi, on=["Kota/Kabupaten", "Tahun"], how="outer")
df_merge = pd.merge(df_merge, df_st, on=["Kota/Kabupaten", "Tahun", "Provinsi"], how="outer")

# Bangun peta Kota→Provinsi
prov_map = pd.concat(
    [df_le[["Kota/Kabupaten","Provinsi"]], df_st[["Kota/Kabupaten","Provinsi"]]],
    ignore_index=True
).dropna().drop_duplicates().set_index("Kota/Kabupaten")["Provinsi"].to_dict()

df_merge["Provinsi"] = df_merge.apply(
    lambda r: prov_map.get(r["Kota/Kabupaten"], r["Provinsi"]),
    axis=1
)

# Buang baris tidak valid (tanpa Tahun/Kota)
df_merge = df_merge.dropna(subset=["Kota/Kabupaten", "Tahun"])

# ==== Normalisasi nama kolom akhir ====
df_merge = df_merge.rename(columns={
    "Tahun": "tahun",
    "Provinsi": "provinsi",
    "Kota/Kabupaten": "kota_kabupaten",
})

# ==== Urutan kolom & sort ====
final_cols = ["tahun", "provinsi", "kota_kabupaten", "stunting_prevalence", "life_expectancy_at_birth", "hdi"]
for c in final_cols:
    if c not in df_merge.columns:
        df_merge[c] = pd.NA

df_merge = df_merge[final_cols].sort_values(["provinsi", "kota_kabupaten", "tahun"], kind="mergesort")

# ==== Simpan ====
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
df_merge.to_csv(OUT_CSV, index=False, sep=";")
print("✅ File tersimpan di", OUT_CSV)
