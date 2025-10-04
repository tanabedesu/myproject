import pandas as pd
import os
prefectures = ["Tokyo","Kanagawa","Saitama","Chiba","Ibaraki","Tochigi","Gunma"]
dfs = []

for pref in prefectures:
    file_path = os.path.join("kanto",f"{pref}_2024_ndvi_temp.csv")
    df=pd.read_csv(file_path)
    df['prefecture'] = pref  # 県名列を追加
    dfs.append(df)

all_data = pd.concat(dfs, ignore_index=True)
all_data['date'] = pd.to_datetime(all_data['date'])

import geopandas as gpd

gdf = gpd.read_file("gadm41_JPN_1.json")
kanto_pref_names = ["Tokyo","Kanagawa","Saitama","Chiba","Ibaraki","Tochigi","Gunma"]
gdf = gdf[gdf['NAME_1'].isin(kanto_pref_names)]

gdf_merged = gdf.merge(all_data, left_on='NAME_1', right_on='prefecture')

import matplotlib.pyplot as plt

# 表示したい日付
dates = pd.date_range("2024-03-01", "2024-03-31")

for date in dates:
    day_data = gdf_merged[gdf_merged['date'] == date]
    
    fig, ax = plt.subplots(figsize=(8,8))
    day_data.plot(column='NDVI', cmap='YlGn', legend=True, ax=ax, edgecolor='black')
    ax.set_title(f"NDVI Map on {date.date()}")
    plt.axis('off')
    plt.savefig(f"NDVI_{date.date()}.png", dpi=300)
    plt.close()
