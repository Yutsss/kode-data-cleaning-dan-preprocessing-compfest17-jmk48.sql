import pandas as pd

# --- 1. Load data ---
df_master = pd.read_csv("datasets/stunting_total_prov.csv")
df_balita = pd.read_csv("datasets/balita_stunting.csv")

# --- 2. Deteksi nama kolom provinsi asli ---
col_prov_master = [c for c in df_master.columns if c.lower() == "provinsi"][0]
provinsi_asli = df_master[col_prov_master].copy()

# --- 3. Normalisasi nama kolom & provinsi untuk merge ---
df_master.columns = df_master.columns.str.strip().str.lower()
df_balita.columns = df_balita.columns.str.strip().str.lower()

df_master['provinsi'] = df_master['provinsi'].str.strip().str.lower()
df_balita['provinsi'] = df_balita['provinsi'].str.strip().str.lower()

# Mapping salah ejaan di balita
mapping = {
    "sumatra barat": "sumatera barat",
    "sumatra selatan": "sumatera selatan",
    "sumatra utara": "sumatera utara"
}
df_balita['provinsi'] = df_balita['provinsi'].replace(mapping)

# --- 4. Hapus kolom populasi kalau ada ---
if "populasi" in df_master.columns:
    df_master = df_master.drop(columns=["populasi"])

if "jumlah stunting" in df_master.columns:
    df_master = df_master.drop(columns=["jumlah stunting"])

# --- 5. Update jumlah stunting master dengan data balita ---
if "jumlah stunting" in df_balita.columns:
    df_balita = df_balita.rename(columns={"jumlah stunting": "jumlah_stunting"})
if "jumlah_stunting" in df_balita.columns:
    df_master = df_master.merge(
        df_balita[["provinsi", "jumlah_stunting"]],
        on="provinsi",
        how="left",
        suffixes=("", "_balita")
    )
    df_master["jumlah stunting"] = df_master["jumlah_stunting"]
    df_master = df_master.drop(columns=["jumlah_stunting"])


# --- 6. Kembalikan nama provinsi asli ---
df_master["provinsi"] = provinsi_asli

# --- 7. Simpan hasil ke file yang sama ---
output_path = "datasets/stunting_total_prov.csv"
df_master.to_csv(output_path, index=False)

print(f"File berhasil diperbarui: {output_path}")
