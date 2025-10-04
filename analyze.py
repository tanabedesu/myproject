import ee
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import json
from matplotlib.animation import FuncAnimation

# === Earth Engine 初期化 ===
ee.Initialize(project='pollenproject-474105')

# === MODIS NDVI取得設定（2024年） ===
modis = ee.ImageCollection("MODIS/061/MOD13Q1")\
            .select('NDVI')\
            .filterDate('2024-01-01','2024-12-31')

# === 関東地方県ポリゴンをローカルJSONから読み込む ===
with open("gadm41_JPN_1.json", "r", encoding="utf-8") as f:
    gj = json.load(f)

kanto_pref_names = ["Tokyo", "Kanagawa", "Saitama", "Chiba", "Ibaraki", "Tochigi", "Gunma"]
# 関東7県だけ抽出
kanto_features = [feat for feat in gj['features'] if feat['properties']['NAME_1'] in kanto_pref_names]

# NASA POWER 県庁所在地座標
pref_coords = {
    'Tokyo': [35.68, 139.76],
    'Kanagawa': [35.44, 139.64],
    'Saitama': [35.86, 139.65],
    'Chiba': [35.60, 140.12],
    'Ibaraki': [36.34, 140.45],
    'Tochigi': [36.56, 139.88],
    'Gunma': [36.39, 139.06]
}

T_base = 5.0
pref_data = {}

for pref in kanto_features:
    name = pref['properties']['NAME_1']
    print(f"🔹 Processing {name}")

    # NDVIを県境で平均
    feature = ee.Feature(pref)
    def extract_ndvi(image):
        mean_dict = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=feature.geometry(),
            scale=250
        )
        date = image.date().format('YYYY-MM-dd')
        return ee.Feature(None, {'date': date, 'NDVI': mean_dict.get('NDVI')})

    ndvi_fc = modis.map(extract_ndvi)
    ndvi_list = ndvi_fc.getInfo()['features']
    ndvi_df = pd.DataFrame([{'date': f['properties']['date'], 'NDVI': f['properties']['NDVI']} for f in ndvi_list])
    ndvi_df['date'] = pd.to_datetime(ndvi_df['date'])
    ndvi_daily = ndvi_df.set_index('date').resample('D').interpolate().reset_index()

    # NASA POWER 気温取得
    lat, lon = pref_coords[name]
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "start": "20240101",
        "end": "20241231",
        "latitude": lat,
        "longitude": lon,
        "parameters": "T2M",
        "format": "JSON",
        "community": "AG"
    }
    response = requests.get(url, params=params).json()
    print(response)
    t2m_data = response["properties"]["parameter"]["T2M"]
    t2m_df = pd.DataFrame(list(t2m_data.items()), columns=["date", "T2M"])
    t2m_df["date"] = pd.to_datetime(t2m_df["date"])
    t2m_df["T2M"] = t2m_df["T2M"].astype(float)

    # データ統合
    merged = pd.merge(t2m_df, ndvi_daily, on='date', how='inner')

    # GDD計算
    merged['GDD_daily'] = (merged['T2M'] - T_base).clip(lower=0)
    merged['GDD_cumsum'] = merged['GDD_daily'].cumsum()

    # NDVIピーク検出
    peaks, _ = find_peaks(merged['NDVI'].values, height=0.5)
    merged['peak'] = 0
    merged.loc[peaks, 'peak'] = 1

    # CSV保存
    merged.to_csv(f"{name}_2024_ndvi_temp.csv", index=False)

    # グラフ作成
    plt.figure(figsize=(12,5))
    plt.plot(merged['date'], merged['NDVI'], label='NDVI')
    plt.plot(merged['date'].iloc[peaks], merged['NDVI'].iloc[peaks], 'ro', label='peak')
    plt.xlabel("date")
    plt.ylabel("NDVI")
    plt.title(f"{name} NDVI Time Series Curve Analysis")
    plt.legend()
    plt.savefig(f"{name}_2024ndvi_curve.png", dpi=300)
    plt.close()

    pref_data[name] = merged
    print(f"{name} 完了")

print("県別NDVI＋GDD＋ピーク解析 完了")
