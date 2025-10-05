import ee
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pycountry
import os
import time

# === 初期設定 ===
ee.Initialize(project='pollenproject-474105')
year = 2024  # ← 対象年
output_dir = "world"
os.makedirs(output_dir, exist_ok=True)
T_base = 5.0  # GDD計算用

# MODISコレクション
modis_collection = "MODIS/006/MOD13Q1" if year <= 2023 else "MODIS/061/MOD13Q1"
modis = ee.ImageCollection(modis_collection).select('NDVI').filterDate(f'{year}-01-01', f'{year}-12-31')
print(f"🛰️ Using MODIS collection: {modis_collection}")

# 全ての国ループ
all_countries = [c.name for c in pycountry.countries]

for country_name in all_countries:
    try:
        print(f"\n🌍 Processing {country_name}")
        # 国コード
        country = pycountry.countries.lookup(country_name)
        country_iso3 = country.alpha_3

        # GADMレベル1ポリゴン取得
        url_gadm = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{country_iso3}_1.json"
        response = requests.get(url_gadm, timeout=30)
        if response.status_code != 200:
            print(f"⚠️ GADM not found for {country_name}, skipping")
            continue
        gj = response.json()
        features = gj.get("features")
        if not features:
            print(f"⚠️ No level-1 regions for {country_name}, skipping")
            continue

        # レベル1の最初の行政区だけ使う
        feature = features[0]
        region_name = feature['properties']['NAME_1']
        safe_name = f"{country_name}_{region_name}".replace("/", "_").replace(" ", "_")

        out_csv = os.path.join(output_dir, f"{safe_name}_{year}_ndvi_temp.csv")
        out_png = os.path.join(output_dir, f"{safe_name}_{year}_ndvi_curve.png")
        if os.path.exists(out_csv):
            print(f"⏩ Skipping {safe_name} (already processed)")
            continue

        # centroid取得
        ee_feature = ee.Feature(feature)
        centroid = ee.Geometry(feature['geometry']).centroid().coordinates().getInfo()
        lon, lat = centroid
        print(f"   📍 Lat: {lat:.2f}, Lon: {lon:.2f}")

        # === NDVI取得 ===
        def extract_ndvi(image):
            mean_dict = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=ee_feature.geometry(),
                scale=250,
                maxPixels=1e13
            )
            date = image.date().format('YYYY-MM-dd')
            ndvi_value = ee.Algorithms.If(mean_dict.get('NDVI'), mean_dict.get('NDVI'), -9999)
            return ee.Feature(None, {'date': date, 'NDVI': ndvi_value})

        ndvi_fc = modis.map(extract_ndvi)
        ndvi_list = ndvi_fc.getInfo()['features']
        ndvi_df = pd.DataFrame([{'date': f['properties']['date'], 'NDVI': f['properties']['NDVI']} for f in ndvi_list])
        ndvi_df['date'] = pd.to_datetime(ndvi_df['date'])
        ndvi_daily = ndvi_df.set_index('date').resample('D').interpolate().reset_index()

        # === NASA POWER T2M ===
        url_power = "https://power.larc.nasa.gov/api/temporal/daily/point"
        params = {
            "start": f"{year}0101",
            "end": f"{year}1231",
            "latitude": lat,
            "longitude": lon,
            "parameters": "T2M",
            "format": "JSON",
            "community": "AG"
        }
        power_json = requests.get(url_power, params=params, timeout=30).json()
        t2m_data = power_json["properties"]["parameter"]["T2M"]
        t2m_df = pd.DataFrame(list(t2m_data.items()), columns=["date", "T2M"])
        t2m_df["date"] = pd.to_datetime(t2m_df["date"])
        t2m_df["T2M"] = t2m_df["T2M"].astype(float)

        # === NDVI + T2M統合 ===
        merged = pd.merge(t2m_df, ndvi_daily, on='date', how='inner')
        merged['GDD_daily'] = (merged['T2M'] - T_base).clip(lower=0)
        merged['GDD_cumsum'] = merged['GDD_daily'].cumsum()

        # === NDVIピーク検出 ===
        peaks, _ = find_peaks(merged['NDVI'].values, height=0.5)
        merged['peak'] = 0
        merged.loc[peaks, 'peak'] = 1

        # === 保存 ===
        merged.to_csv(out_csv, index=False)
        plt.figure(figsize=(12,5))
        plt.plot(merged['date'], merged['NDVI'], label='NDVI')
        if len(peaks) > 0:
            plt.plot(merged['date'].iloc[peaks], merged['NDVI'].iloc[peaks], 'ro', label='peak')
        plt.xlabel("Date")
        plt.ylabel("NDVI")
        plt.title(f"{country_name} - {region_name} NDVI ({year})")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_png, dpi=300)
        plt.close()

        print(f"✅ Saved {safe_name}")
        time.sleep(1)  # サーバ負荷軽減

    except Exception as e:
        print(f"❌ Error processing {country_name}: {e}")
        continue

print("🌎 All countries processed (1 region each). Data saved in /world")
