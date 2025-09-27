import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# === 1. Load data nasional
df = pd.read_csv("datasets/nasional_final.csv", sep=";")

# Rename biar seragam
df = df.rename(columns={
    "tahun": "year",
    "stunting_prevalence": "stunting",
    "life_expectancy_at_birth": "life_expectancy",
    "hdi": "hdi"
})

df["level"] = "nasional"

# === 2. Model A: LE ~ Stunting
X1 = df[["stunting"]].dropna()
y1 = df.loc[X1.index, "life_expectancy"]

model_le = LinearRegression()
model_le.fit(X1, y1)

print("Model A (LE ~ Stunting): coef =", model_le.coef_[0], "intercept =", model_le.intercept_)

# Hitung residual error untuk LE
y1_pred = model_le.predict(X1)
se_le = np.sqrt(mean_squared_error(y1, y1_pred))

# === 3. Model B: HDI ~ Life Expectancy
X2 = df[["life_expectancy"]].dropna()
y2 = df.loc[X2.index, "hdi"]

model_hdi = LinearRegression()
model_hdi.fit(X2, y2)

print("Model B (HDI ~ Life Expectancy): coef =", model_hdi.coef_[0], "intercept =", model_hdi.intercept_)

# Hitung residual error untuk HDI
y2_pred = model_hdi.predict(X2)
se_hdi = np.sqrt(mean_squared_error(y2, y2_pred))

# === 4. Ambil nilai terakhir (2024) dan target 2029
last_year = df["year"].max()
stunting_2024 = float(df[df["year"] == last_year]["stunting"])

target_2029 = 14.2

# Proyeksi stunting 2025–2029
years_proj = np.arange(2025, 2030)
stunting_proj = np.linspace(stunting_2024, target_2029, len(years_proj))

# === 5. Prediksi LE & HDI
le_proj = model_le.predict(stunting_proj.reshape(-1, 1))
hdi_proj = model_hdi.predict(le_proj.reshape(-1, 1))

# Confidence interval (approx, pakai ±1.96 * standard error)
le_low = le_proj - 1.96 * se_le
le_high = le_proj + 1.96 * se_le

hdi_low = hdi_proj - 1.96 * se_hdi
hdi_high = hdi_proj + 1.96 * se_hdi

# === 6. Buat dataframe proyeksi
df_proj = pd.DataFrame({
    "year": years_proj,
    "stunting": stunting_proj,
    "life_expectancy": le_proj,
    "life_expectancy_low": le_low,
    "life_expectancy_high": le_high,
    "hdi": hdi_proj,
    "hdi_low": hdi_low,
    "hdi_high": hdi_high,
    "level": "nasional",
    "status": "projection"
})

# === 7. Gabungkan actual + proyeksi
df_actual = df.copy()
df_actual["status"] = "actual"

df_final = pd.concat([df_actual, df_proj], ignore_index=True)

# === 8. Simpan
df_proj.to_csv("datasets/projection_nasional_2025_2029.csv", index=False)
df_final.to_csv("datasets/nasional_with_projection.csv", index=False)

print("✅ Saved projection_nasional_2025_2029.csv and nasional_with_projection.csv")
