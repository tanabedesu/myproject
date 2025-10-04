import streamlit as st
import pandas as pd
from datetime import datetime

# --- タイトル ---
st.title("🌸 関東地方 開花予測ツール")
st.markdown("""
このツールは県別のGDD・NDVIデータを使い、開花予測日を計算します。
- NDVI傾きや累積GDDを閾値として使用
""")

# --- ユーザー入力 ---
kanto_pref_names = ["Tokyo", "Kanagawa", "Saitama", "Chiba", "Ibaraki", "Tochigi", "Gunma"]

prefecture = st.selectbox("県を選択してください", kanto_pref_names)
# 年を選択できるようにする
year = st.number_input("年を選択してください", min_value=2000, max_value=2100, value=2024)

start_date = st.date_input("観察開始日", value=datetime(year, 3, 1))
gdd_threshold = st.number_input("累積GDD閾値", min_value=0, value=100)
ndvi_slope_threshold = st.number_input("NDVI傾き閾値", min_value=0.0, value=10.0)

# --- データ読み込み ---
csv_path = f"kanto/{prefecture}_{year}_ndvi_temp.csv"
df = pd.read_csv(csv_path)
df['date'] = pd.to_datetime(df['date'])
df = df[df['date'] >= pd.to_datetime(start_date)]

# NDVI傾き計算
df['NDVI_slope'] = df['NDVI'].diff()

# 開花予測日判定
cond = (df['GDD_cumsum'] >= gdd_threshold) & (df['NDVI_slope'] >= ndvi_slope_threshold)
if cond.any():
    pred_date = df[cond]['date'].iloc[0]
    st.success(f"✅ {prefecture} の開花予測日: {pred_date.date()}")
else:
    st.warning(f"{prefecture}：この期間に開花予測はできません")

# --- データ表示 ---
if st.checkbox("データを表示"):
    st.dataframe(df)

# --- グラフ ---
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df['date'], df['NDVI'], label="NDVI")
ax.plot(df['date'], df['GDD_cumsum'], label="累積GDD")
ax.axvline(pred_date if cond.any() else df['date'].iloc[-1], color='r', linestyle='--', label="予測日")
ax.set_xlabel("日付")
ax.set_ylabel("値")
ax.legend()
st.pyplot(fig)
