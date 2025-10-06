import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from datetime import datetime
import os

st.markdown(
    """
    <h1 style='
        font-family: "Playfair Display", serif; 
        color:#5C4033; 
        text-align:center; 
        font-size:64px; 
        font-weight:700;
        letter-spacing:2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    '>
        Global <br> BloomWatch
    </h1>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <div style='
        background-color:white; 
        padding:20px; 
        margin:20px auto; 
        border-radius:15px; 
        max-width:700px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align:center;
        font-size:20px;
        color:#8B5E3C;
        line-height:1.6;
    '>
        This tool estimates the flower bloom date for each country in the world 
        based on <b>GDD (Growing Degree Days)</b> and <b>NDVI (Normalized Difference Vegetation Index)</b> data.
    </div>
    """, unsafe_allow_html=True
)


# --- User Input ---
world_pref_names = [
"Albania_Berat",
"Algeria_Adrar",
"American_Samoa_Eastern",
"Andorra_AndorralaVella",
"Angola_Bengo",
"Anguilla_BlowingPoint",
"Antigua_and_Barbuda_Barbuda",
"Argentina_BuenosAires",
"Armenia_Aragatsotn",
"Australia_AshmoreandCartierIslands",
"Austria_Burgenland",
"Azerbaijan_Absheron",
"Bahamas_Acklins",
"Bahrain_Capital",
"Bangladesh_Barisal",
"Barbados_ChristChurch",
"Belarus_Brest",
"Belgium_Bruxelles",
"Belize_Belize",
"Benin_Alibori",
"Bermuda_Devonshire",
"Bhutan_Bumthang",
"Bolivia,_Plurinational_State_of_Beni",
"Bonaire,_Sint_Eustatius_and_Saba_Bonaire",
"Bosnia_and_Herzegovina_Brčko",
"Botswana_Central",
"Brazil_Acre",
"Brunei_Darussalam_Belait",
"Bulgaria_Blagoevgrad",
"Burkina_Faso_BoucleduMouhoun",
"Burundi_Bubanza",
"Cabo_Verde_BoaVista",
"Cambodia_BântéayMéanchey",
"Cameroon_Adamaoua",
"Canada_Alberta",
"Cayman_Islands_BoddenTown",
"Central_African_Republic_Bamingui-Bangoran",
"Chad_BarhelGhazel",
"Chile_Antofagasta",
"China_Anhui",
"Colombia_Amazonas",
"Comoros_Mwali",
"Congo,_The_Democratic_Republic_of_the_Bas-Uele",
"Congo_Bouenza",
"Cook_Islands_Aitutaki",
"Costa_Rica_Alajuela",
"Côte_d'Ivoire_Abidjan",
"Croatia_Bjelovarska-Bilogorska",
"Cuba_Camagüey",
"Cyprus_Famagusta",
"Czechia_Jihočeský",
"Denmark_Hovedstaden",
"Djibouti_AliSabieh",
"Dominica_SaintAndrew",
"Dominican_Republic_Azua",
"Ecuador_Azuay",
"Egypt_AdDaqahliyah",
"El_Salvador_Ahuachapán",
"Equatorial_Guinea_Annobón",
"Eritrea_Anseba",
"Estonia_Harju",
"Eswatini_Hhohho",
"Ethiopia_AddisAbeba",
"Faroe_Islands_Eysturoyar",
"Fiji_Central",
"Finland_EasternFinland",
"France_Auvergne-Rhône-Alpes",
"French_Guiana_Cayenne",
"French_Polynesia_ÎlesAustrales",
"French_Southern_Territories_ÎlesCrozet",
"Gabon_Estuaire",
"Gambia_Banjul",
"Georgia_Abkhazia",
"Germany_Baden-Württemberg",
"Ghana_Ahafo",
"Greece_Aegean",
"Greenland_Kujalleq",
"Grenada_Carriacou",
"Guadeloupe_Basse-Terre",
"Guam_AganaHeights",
"Guatemala_AltaVerapaz",
"Guernsey_Alderney",
"Guinea_Boké",
"Guinea-Bissau_Bafatá",
"Guyana_Barima-Waini",
"Haiti_Centre",
"Honduras_Atlántida",
"Hungary_Bács-Kiskun",
"Iceland_Austurland",
"India_AndamanandNicobar",
"Indonesia_Aceh",
"Iran,_Islamic_Republic_of_Alborz",
"Iraq_Al-Anbar",
"Ireland_Carlow",
"Isle_of_Man_Andreas",
"Israel_Golan",
"Italy_Abruzzo",
"Jamaica_Clarendon",
"Japan_Aichi",
"Japan_Tokyo",
"Jersey_Grouville",
"Jordan_Ajlun",
"Kazakhstan_Almaty",
"Kenya_Baringo",
"Korea,_Democratic_People's_Republic_of_Chagang-do",
"Korea,_Republic_of_Busan",
"Kuwait_AlAhmadi",
"Kyrgyzstan_Batken",
"Lao_People's_Democratic_Republic_Attapu",
"Latvia_Kurzeme",
"Lebanon_Akkar",
"Lesotho_Berea",
"Liberia_Bomi",
"Libya_AlButnan",
"Liechtenstein_Balzers",
"Lithuania_Alytaus",
"Luxembourg_Diekirch",
"Madagascar_Antananarivo",
"Malawi_Balaka",
"Malaysia_Johor",
"Mali_Bamako",
"Malta_Ċentrali",
"Marshall_Islands_Ailinglaplap",
"Martinique_Fort-de-France",
"Mauritania_Adrar",
"Mauritius_AgalegaIslands",
"Mayotte_Acoua",
"Mexico_Aguascalientes",
"Micronesia,_Federated_States_of_Chuuk",
"Moldova,_Republic_of_AneniiNoi",
"Mongolia_Arhangay",
"Montenegro_Andrijevica",
"Montserrat_SaintAnthon",
"Morocco_Chaouia-Ouardigha",
"Mozambique_CaboDelgado",
"Myanmar_Ayeyarwady",
"Namibia_!Karas",
"Nauru_Aiwo",
"Nepal_Central",
"Netherlands_Drenthe",
"New_Caledonia_ÎlesLoyauté",
"New_Zealand_Auckland",
"Nicaragua_AtlánticoNorte",
"Niger_Agadez",
"Nigeria_Abia",
"North_Macedonia_Aerodrom",
"Northern_Mariana_Islands_NorthernIslands",
"Norway_Akershus",
"Oman_AdDakhliyah",
"Pakistan_AzadKashmir",
"Palau_Aimeliik",
"Palestine,_State_of_Gaza",
"Panama_BocasdelToro",
"Papua_New_Guinea_Bougainville",
"Paraguay_AltoParaguay",
"Peru_Amazonas",
"Philippines_Abra",
"Poland_Dolnośląskie",
"Portugal_Aveiro",
"Puerto_Rico_Adjuntas",
"Qatar_AdDawhah",
"Réunion_Saint-Benoît",
"Romania_Alba",
"Russian_Federation_Adygey",
"Rwanda_Amajyaruguru",
"Saint_Barthélemy_AuVent",
"Saint_Helena,_Ascension_and_Tristan_da_Cunha_Ascension",
"Saint_Kitts_and_Nevis_ChristChurchNicholaTown",
"Saint_Lucia_Anse-la-Raye",
"Saint_Pierre_and_Miquelon_Miquelon-Langlade",
"Saint_Vincent_and_the_Grenadines_Charlotte",
"Samoa_A'ana",
"San_Marino_Acquaviva",
"Sao_Tome_and_Principe_Príncipe",
"Saudi_Arabia_'Asir",
"Senegal_Dakar",
"Serbia_Borski",
"Seychelles_AnseauxPins",
"Sierra_Leone_Eastern",
"Singapore_Central",
"Slovakia_Banskobystrický",
"Slovenia_Gorenjska",
"Solomon_Islands_Central",
"Somalia_Awdal",
"South_Africa_EasternCape",
"South_Sudan_CentralEquatoria",
"Spain_Andalucía",
"Sri_Lanka_Ampara",
"Sudan_AlJazirah",
"Suriname_Brokopondo",
"Svalbard_and_Jan_Mayen_JanMayen",
"Sweden_Blekinge",
"Switzerland_Aargau",
"Syrian_Arab_Republic_AlḤasakah",
"Taiwan,_Province_of_China_Fujian",
"Tajikistan_DistrictsofRepublicanSubordin",
"Tanzania,_United_Republic_of_Arusha",
"Thailand_AmnatCharoen",
"Timor-Leste_Aileu",
"Togo_Centre",
"Tokelau_Anafu",
"Tonga_'Eua",
"Trinidad_and_Tobago_Arima",
"Tunisia_Ariana",
"Türkiye_Adana",
"Turkmenistan_Ahal",
"Turks_and_Caicos_Islands_GrandTurk",
"Tuvalu_Funafuti",
"Uganda_Adjumani",
"United_Arab_Emirates_AbuDhabi",
"United_Kingdom_NorthernIreland",
"United_States_Alabama",
"United_States_Minor_Outlying_Islands_Baker",
"Uruguay_Artigas",
"Uzbekistan_Andijon",
"Vanuatu_Malampa",
"Venezuela,_Bolivarian_Republic_of_Amazonas",
"Viet_Nam_AnGiang",
"Virgin_Islands,_British_Anegada",
"Virgin_Islands,_U.S._SaintCroix",
"Wallis_and_Futuna_Alo",
"Western_Sahara_Boujdour",
"Yemen_`Adan",
"Zambia_Central",
"Zimbabwe_Bulawayo",
"Afghanistan_Badakhshan"

]
st.markdown(
    """
    <style>
    .stApp {
        background-color: #9ccc9c;  
        background-image: url('https://example.com/earth_plants_top.png');
        background-repeat: no-repeat;
        background-size: cover;
        background-position: top center;
    }

    .css-1d391kg {  
        background-color: #f5ede3;
    }
    </style>
    """,
    unsafe_allow_html=True
)
search_country = st.text_input("Search Country (type part of the name)")

if search_country:
    filtered_countries = [c for c in world_pref_names if search_country.lower() in c.lower()]
else:
    filtered_countries = world_pref_names

country = st.selectbox("Select Country", filtered_countries)

# Select plant type (auto threshold)
plant_types = {
    "Sakura (Cherry Blossom)": {"gdd": 120, "ndvi": 15.0},
    "magnolia": {"gdd": 100, "ndvi": 2.0},
    "Plum": {"gdd": 100, "ndvi": 12.0},
    "Camellia": {"gdd": 80, "ndvi": 10.0},
    "Other (Manual Input)": {"gdd": None, "ndvi": None},
}
plant_choice = st.selectbox("Select Plant Type", list(plant_types.keys()))
auto_values = plant_types[plant_choice]

year = st.number_input("Select Year", min_value=2000, max_value=2100, value=2024)
start_date = st.date_input("Observation Start Date", value=datetime(year, 3, 1))

# If user selects manual mode, allow input
if auto_values["gdd"] is None:
    gdd_threshold = st.number_input("Cumulative GDD Threshold", min_value=0, value=100)
    ndvi_slope_threshold = st.number_input("NDVI Slope Threshold", min_value=0.0, value=10.0)
else:
    gdd_threshold = auto_values["gdd"]
    ndvi_slope_threshold = auto_values["ndvi"]
    st.info(f"🌸 Auto thresholds for {plant_choice}:  GDD = {gdd_threshold}, NDVI Slope = {ndvi_slope_threshold}")

# --- Decide which method to use ---
if year <= 2024:
    # --- Load data ---

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "world", f"{country}_{year}_ndvi_temp.csv")
    @st.cache_data
    def load_data(path):
        return pd.read_csv(path)
        
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error(f"Data file not found: {csv_path}")
        st.stop()

    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= pd.to_datetime(start_date)]
    # Threshold-based method
    df['NDVI_slope'] = df['NDVI'].diff()
    cond = (df['GDD_cumsum'] >= gdd_threshold) & (df['NDVI_slope'] >= ndvi_slope_threshold)
    if cond.any():
        pred_date = df[cond]['date'].iloc[0]
        st.markdown(f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.85);
            border-left: 8px solid #2e8b57;
            padding: 16px;
            border-radius: 12px;
            font-size: 18px;
            color: #1b4332;
            font-weight: 600;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            margin-top: 15px;
        ">
        🌸 <b>Estimated Bloom Date</b> for <span style="color:#2d6a4f;">{country}</span> ({plant_choice}) :  
        <span style="color:#d9480f; font-size:20px;">{pred_date.date()}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        pred_date = None
        st.warning(f" No bloom predicted for this period for {country}.")
    plot_values = df[['date','NDVI','GDD_cumsum']].copy()
    plot_label = "NDVI"
else:
    # RandomForest prediction method
    train_years = [y for y in range(2019, 2025)]
    @st.cache_data
    def load_data(path):
        return pd.read_csv(path)
    dfs = []
    for y in train_years:
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(BASE_DIR, "world", f"{country}_{y}_ndvi_temp.csv")

        try:
            dfs.append(pd.read_csv(path))
        except FileNotFoundError:
            continue
    train_df = pd.concat(dfs, ignore_index=True)
    train_df['date'] = pd.to_datetime(train_df['date'])
    train_df = train_df.dropna(subset=['NDVI','GDD_cumsum','T2M'])
    train_df['doy'] = train_df['date'].dt.dayofyear

    # Train model
    X = train_df[['GDD_cumsum','T2M']]
    y_train = train_df['NDVI']
    model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X, y_train)

    # Generate future data
    last_year = train_df['date'].dt.year.max()
    avg_daily_temp = train_df.groupby('doy')['T2M'].mean()
    future_dates = pd.date_range(f"{year}-01-01", f"{year}-12-31")
    future_df = pd.DataFrame({'date': future_dates})
    future_df['doy'] = future_df['date'].dt.dayofyear
    temp_trend_per_year = 3.0
    future_df['T2M'] = future_df['doy'].map(avg_daily_temp) + temp_trend_per_year*(year-last_year)
    T_base = 5
    future_df['GDD_daily'] = (future_df['T2M'] - T_base).clip(lower=0)
    future_df['GDD_cumsum'] = future_df['GDD_daily'].cumsum()
    future_df['NDVI_pred'] = model.predict(future_df[['GDD_cumsum','T2M']])
    future_df = future_df[future_df['date']>=pd.to_datetime(start_date)]

    # Detect peak
    peaks, _ = find_peaks(future_df['NDVI_pred'], height=np.percentile(future_df['NDVI_pred'],90))
    if len(peaks) > 0:
        pred_date = future_df.iloc[peaks[0]]['date']
        st.success(f"✅ Predicted Bloom Date for {country} {year} ({plant_choice}): {pred_date.date()}")
    else:
        pred_date = None
        st.warning(f" No bloom predicted for this period for {country}.")
    plot_values = future_df[['date','NDVI_pred']].copy()
    plot_label = "Predicted NDVI"

# --- Plot ---
fig, ax = plt.subplots(figsize=(10,4))

# Plot NDVI and GDD
if year <= 2024:
    ax.plot(plot_values['date'], plot_values['NDVI'], label="NDVI", color='green')
    ax.plot(plot_values['date'], plot_values['GDD_cumsum'], label="Cumulative GDD", color='orange')
else:
    ax.plot(plot_values['date'], plot_values['NDVI_pred'], label="Predicted NDVI", color='green')

if pred_date is not None:
    ndvi_col = 'NDVI' if year <= 2024 else 'NDVI_pred'
    bloom_ndvi = plot_values.loc[plot_values['date']==pred_date, ndvi_col].values
    if len(bloom_ndvi) == 0:
        bloom_ndvi = plot_values[ndvi_col].iloc[0]
    else:
        bloom_ndvi = bloom_ndvi[0]
    
    ax.axvline(pred_date, color='red', linestyle='--', alpha=0.8)
    ax.scatter(pred_date, bloom_ndvi, color='red', s=150, zorder=5, marker='*')
    ax.annotate(f"Bloom Day:\n{pred_date.date()}", 
                xy=(pred_date, bloom_ndvi), 
                xytext=(10, 30), 
                textcoords='offset points',
                arrowprops=dict(facecolor='red', arrowstyle='->'),
                fontsize=12, color='red', fontweight='bold')

ax.set_xlabel("Date")
ax.set_ylabel(plot_label)
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pycountry
from datetime import datetime

#Load the CSV file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "world", f"{country}_{year}_ndvi_temp.csv")
df = pd.read_csv(csv_path)

# Convert the date column to datetime type
df['date'] = pd.to_datetime(df['date'])

# Add a column for country name
df['country_name'] = 'Japan'
# Prepare the existing df_bloom 
# ex: df_bloom = pd.DataFrame({'date': [...], 'NDVI': [...], 'country_name': [...]})

# ISO3 code
def country_to_iso3(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None
df['ISO_A3'] = df['country_name'].apply(country_to_iso3)
df_bloom = df[['date','NDVI','GDD_cumsum','country_name','ISO_A3']].copy()

df_bloom_reduced = df_bloom.iloc[::10, :]
dates = df_bloom['date'].sort_values().unique()

fig = go.Figure(
    data=[go.Choropleth(
        locations=df_bloom[df_bloom['date']==dates[0]]['ISO_A3'],
        z=df_bloom[df_bloom['date']==dates[0]]['NDVI'],
        colorscale='RdYlGn',
        zmin=df_bloom['NDVI'].min(),
        zmax=df_bloom['NDVI'].max(),
        colorbar_title='NDVI'
    )],
    layout=go.Layout(
        title_text='🌸 NDVI Animation 2024',
        geo=dict(
            projection_type='orthographic',
            showcoastlines=True,
            showland=True,
            landcolor='rgb(217,217,217)',
            showocean=True,
            oceancolor='rgb(200,230,250)'
        ),
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            y=1,
            x=1.1,
            xanchor='right',
            yanchor='top',
            buttons=[dict(
                label='Play',
                method='animate',
                args=[None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}]
            )]
        )]
    ),
    frames=[
        go.Frame(
            data=[go.Choropleth(
                locations=df_bloom[df_bloom['date']==d]['ISO_A3'],
                z=df_bloom[df_bloom['date']==d]['NDVI'],
                colorscale='RdYlGn',
                zmin=df_bloom['NDVI'].min(),
                zmax=df_bloom['NDVI'].max()
            )],
            name=str(d.date())
        ) for d in dates
    ]
)


import streamlit as st
st.plotly_chart(fig, use_container_width=True)

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
world = gpd.read_file(url)
cmap_gdd = plt.cm.YlOrRd
norm_gdd = mcolors.Normalize(vmin=df_bloom['GDD_cumsum'].min(), vmax=df_bloom['GDD_cumsum'].max())

# Colormap and normalization for GDD
cmap_gdd = plt.cm.YlOrRd
norm_gdd = mcolors.Normalize(vmin=df_bloom['GDD_cumsum'].min(), vmax=df_bloom['GDD_cumsum'].max())

# --- GDD animation ---
if st.button("Show GDD Animation"):
    placeholder = st.empty()
    fig, ax = plt.subplots(figsize=(12, 8))
    world.plot(ax=ax, color='lightgrey', edgecolor='black')
    ax.axis('off')

    japan = world[world['ADMIN']=='Japan'].copy()
    jp_plot = japan.plot(ax=ax, color=cmap_gdd(norm_gdd(df_bloom_reduced['GDD_cumsum'].iloc[0])), edgecolor='black')
    
    for i, row in df_bloom_reduced.iterrows():
        gdd_value = row['GDD_cumsum']
        date = row['date']
        jp_plot.set_facecolor(cmap_gdd(norm_gdd(gdd_value)))

        ax.set_title(f"Cumulative GDD on {date.date()} (Japan)", fontsize=16)

        placeholder.pyplot(fig)







