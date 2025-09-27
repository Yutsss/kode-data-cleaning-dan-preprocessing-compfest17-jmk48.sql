import pandas as pd

# Load file actual data
df_actual = pd.read_csv("datasets/final_all.csv")

# Load file projection
df_projection = pd.read_csv("datasets/projection_nasional_2025_2029.csv")

# Samakan nama kolom "year" di projection ke "tahun" supaya konsisten
df_projection = df_projection.rename(columns={"year": "tahun"})

# Buat kolom country di projection dan isi dengan Indonesia
df_projection["country"] = "Indonesia"

# Gabungkan keduanya (append baris)
df_merged = pd.concat([df_actual, df_projection], ignore_index=True)


# Simpan hasil ke file baru
output_path = "datasets/final_all_with_projection.csv"
df_merged.to_csv(output_path, index=False)

print("File berhasil digabung dan disimpan di:", output_path)
