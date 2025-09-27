import pandas as pd
import glob

# --- helper: pilih kolom pertama yang ada dari daftar kandidat ---
def pick_col(df, candidates):
    cols = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.strip().lower()
        if key in cols:
            return cols[key]
    return None

# Load daftar kota + provinsi dari stunting source
stunting_path = "datasets/Prev Stunting Kota 2019-2024.csv"
df_stunting = pd.read_csv(stunting_path, sep=None, engine="python")
df_stunting.columns = [c.strip() for c in df_stunting.columns]

# --- AUTO DETECT kolom kota & provinsi (perbaikan KeyError) ---
kota_name_col = pick_col(df_stunting, [
    "nama kota/kab", "kota/kabupaten", "kota / kabupaten",
    "kabupaten/kota", "kabupaten / kota", "kota", "municipality", "city/regency"
])
prov_name_col = pick_col(df_stunting, ["provinsi", "province"])

if kota_name_col is None or prov_name_col is None:
    raise KeyError(
        f"Kolom referensi tidak ditemukan.\n"
        f"Kolom tersedia: {list(df_stunting.columns)}\n"
        f"Diperlukan salah satu dari kota={{'nama kota/kab','kota/kabupaten','kabupaten/kota',...}} "
        f"dan provinsi={{'provinsi','province'}}"
    )

# Buat referensi Kota → Provinsi (drop duplicates)
df_provref = df_stunting[[kota_name_col, prov_name_col]].drop_duplicates()
df_provref.columns = ["Kota/Kabupaten", "Provinsi"]

# Load daftar kota (acuan)
kota_path = "datasets/daftar_kota.csv"
df_kota = pd.read_csv(kota_path)
df_kota.columns = ["Kota/Kabupaten"]

# Name mapping (life expectancy → daftar_kota)
name_mapping = {
    "Batang Hari": "Batanghari",
    "Fakfak": "Fak Fak",
    "Kota Palangka Raya": "Kota Palangkaraya",
    "Kota Makasar": "Kota Makassar",
    "Kota Parepare": "Kota Pare Pare",
    "Kota Pematang Siantar": "Kota Pematangsiantar",
    "Kota Lubuklinggau": "Kota Lubuk Linggau",
    "Kota Sawah Lunto": "Kota Sawahlunto",
    "Kep. Seribu": "Kepulauan Seribu",
    "Siau Tagulandang Biaro": "Kepulauan Siau Tagulandang Biaro (Sitaro)",
    "Maluku Tenggara Barat / Kepulauan Tanimbar": "Kepulauan Tanimbar (Maluku Tenggara Barat)",
    "Mamuju Utara / Pasangkayu": "Pasangkayu (Mamuju Utara)",
    "Toba Samosir / Toba": "Toba",
    "Labuhan Batu": "Labuhanbatu",
    "Labuhan Batu Selatan": "Labuhanbatu Selatan",
    "Labuhan Batu Utara": "Labuhanbatu Utara",
    "Mukomuko": "Muko Muko",
    "Pohuwato": "Pahuwato",
    "Pangkajene dan Kepulauan": "Pangkajene Kepulauan",
    "Tojo Una-Una": "Tojo Una Una",
    "Toli-Toli": "Toli Toli",
    "Tulangbawang": "Tulang Bawang",
    "Banyu Asin": "Banyuasin",
    "Gunung Kidul": "Gunungkidul",
    "Kota Banjar Baru": "Kota Banjarbaru",
    "Kota Baubau": "Kota Bau Bau",
}

# Normalisasi nama
def normalize_name(name):
    return str(name).strip().lower()

# Ambil semua file Life Expectancy (2013–2019)
files = sorted(glob.glob("datasets/Life Expectancy at Birth *.csv"))

all_data = []
for file in files:
    year = file.split("Life Expectancy at Birth ")[1].split(".csv")[0]
    df_temp = pd.read_csv(file, sep=None, engine="python")

    wilayah_col = df_temp.columns[0].strip()
    value_col = df_temp.columns[1]

    df_year = df_temp[[wilayah_col, value_col]].copy()
    df_year.columns = ["Kota/Kabupaten", "Life Expectancy at Birth (Year)"]
    df_year["Tahun"] = int(year)

    # === FIX: Buang provinsi "GORONTALO" (ALL CAPS) yang nyasar ke data kota ===
    df_year["Kota/Kabupaten"] = df_year["Kota/Kabupaten"].astype(str)
    df_year = df_year[~df_year["Kota/Kabupaten"].str.strip().eq("GORONTALO")].copy()
    # === END FIX ===

    # Terapkan mapping (dari nama LifeExp ke nama standar daftar_kota)
    df_year["Kota/Kabupaten"] = df_year["Kota/Kabupaten"].replace(name_mapping)

    # Normalisasi nama kota
    df_year["Kota_norm"] = df_year["Kota/Kabupaten"].apply(normalize_name)

    all_data.append(df_year)

# Gabungkan semua tahun
df_life = pd.concat(all_data, ignore_index=True)

# Tambahkan kolom normalisasi di df_kota
df_kota["Kota_norm"] = df_kota["Kota/Kabupaten"].apply(normalize_name)

# Join dengan daftar kota (acuan stunting)
df_final = pd.merge(df_kota, df_life, on="Kota_norm", how="left")

# Rapikan output
df_final = df_final[["Kota/Kabupaten_x", "Tahun", "Life Expectancy at Birth (Year)"]]
df_final = df_final.rename(columns={"Kota/Kabupaten_x": "Kota/Kabupaten"})

# Tambahkan kolom Provinsi
df_final = pd.merge(df_final, df_provref, on="Kota/Kabupaten", how="left")

# Hapus duplikat per Kota–Tahun
df_final = (
    df_final
    .sort_values(["Kota/Kabupaten", "Tahun", "Life Expectancy at Birth (Year)"], ascending=[True, True, False])
    .drop_duplicates(subset=["Kota/Kabupaten", "Tahun"], keep="first")
)

# Urutkan hasil
df_final = df_final.sort_values(["Provinsi", "Kota/Kabupaten", "Tahun"]).reset_index(drop=True)

# Simpan
df_final.to_csv("datasets/life_expectancy_kota.csv", index=False)

print("✅ life_expectancy_kota.csv sudah bersih dari duplikat (dan bebas 'GORONTALO' provinsi di data kota)")
