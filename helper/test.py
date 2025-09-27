import pandas as pd

df_all = pd.read_csv("datasets/final_all.csv")
df_pivot = pd.read_csv("datasets/final_all_pivot.csv")

missing = pd.merge(df_all, df_pivot, 
                   on=["country","tahun","provinsi","kota_kabupaten","level"], 
                   how="left", indicator=True)

print(missing["_merge"].value_counts())
print(missing[missing["_merge"]=="left_only"].head(20))
