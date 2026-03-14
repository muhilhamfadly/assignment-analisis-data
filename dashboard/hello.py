import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

main_df = load_data()

# Tambahkan kolom tahun, bulan, hari
main_df["year"] = main_df["dteday"].dt.year
main_df["month"] = main_df["dteday"].dt.month
main_df["day"] = main_df["dteday"].dt.day

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
with st.sidebar:

    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("Bike Sharing Analysis")

    # FILTER TAHUN
    year_range = st.slider(
        "Pilih Rentang Tahun",
        min_value=int(main_df["year"].min()),
        max_value=int(main_df["year"].max()),
        value=(int(main_df["year"].min()), int(main_df["year"].max()))
    )

    # FILTER BULAN
    month_range = st.slider(
        "Pilih Rentang Bulan",
        min_value=1,
        max_value=12,
        value=(1,12)
    )

    # FILTER HARI
    day_range = st.slider(
        "Pilih Rentang Hari",
        min_value=1,
        max_value=31,
        value=(1,31)
    )

# -----------------------------
# FILTER DATA
# -----------------------------
filtered_df = main_df[
    (main_df["year"] >= year_range[0]) &
    (main_df["year"] <= year_range[1]) &
    (main_df["month"] >= month_range[0]) &
    (main_df["month"] <= month_range[1]) &
    (main_df["day"] >= day_range[0]) &
    (main_df["day"] <= day_range[1])
]

# -----------------------------
# HEADER
# -----------------------------
st.header("Bike Sharing Dashboard 🚲")

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = filtered_df["cnt"].sum()
    st.metric("Total Penyewaan", f"{total_rentals:,}")

with col2:
    avg_registered = int(filtered_df["registered"].mean())
    st.metric("Rata-rata Registered", avg_registered)

with col3:
    avg_casual = int(filtered_df["casual"].mean())
    st.metric("Rata-rata Casual", avg_casual)

st.divider()

# ====================================================
# BAR CHART CUACA
# ====================================================
st.subheader("Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca")

weather_rentals = filtered_df.groupby("weathersit")["cnt"].mean().reset_index()

fig, ax = plt.subplots(figsize=(10,6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x='cnt',
    y='weathersit',
    data=weather_rentals.sort_values(by='cnt', ascending=False),
    palette=colors,
    ax=ax
)

ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca', fontsize=15)
ax.set_ylabel(None)
ax.set_xlabel('Rata-rata Jumlah Penyewaan')
ax.grid(axis='x', linestyle='--', alpha=0.6)
for p in ax.patches:
    ax.annotate(
        f'{p.get_width():.0f}',                # nilai bar
        (p.get_width(),                       # posisi x di ujung bar
         p.get_y() + p.get_height()/2),       # posisi y tengah bar
        xytext=(5,0),                         # jarak teks dari bar
        textcoords='offset points',
        ha='left',
        va='center',
        fontsize=11
    )

st.pyplot(fig)

# ====================================================
# LINE CHART JAM
# ====================================================
st.subheader("Tren Rata-rata Penyewaan Sepeda Berdasarkan Jam")

if "hr" in filtered_df.columns:

    hourly_rentals = filtered_df.groupby("hr")["cnt"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12,6))

    sns.lineplot(
        x='hr',
        y='cnt',
        data=hourly_rentals,
        marker='o',
        linewidth=2.5,
        color='#72BCD4',
        ax=ax
    )

    ax.set_title('Tren Rata-rata Penyewaan Sepeda Berdasarkan Jam', fontsize=15)
    ax.set_xlabel('Jam (00:00 - 23:00)')
    ax.set_ylabel('Rata-rata Jumlah Penyewaan')

    ax.set_xticks(range(0,24))
    ax.grid(True, linestyle='--', alpha=0.5)

    # mencari peak hour otomatis
    peak_hour = hourly_rentals.loc[hourly_rentals['cnt'].idxmax(), 'hr']
    peak_value = hourly_rentals['cnt'].max()

    ax.annotate(
        f'Puncak: {peak_value:.0f}',
        xy=(peak_hour, peak_value),
        xytext=(peak_hour+1, peak_value+5),
        arrowprops=dict(facecolor='black', shrink=0.05)
    )

    st.pyplot(fig)

else:
    st.info("Dataset tidak memiliki kolom 'hr'")

# ====================================================
# TEMPERATURE CLUSTER
# ====================================================
st.subheader("Rata-rata Penyewaan Berdasarkan Kategori Temperatur")

bins = [0, 0.3, 0.6, 0.8, 1.0]
labels = ['Cold', 'Moderate', 'Warm', 'Hot']

filtered_df["temp_cluster"] = pd.cut(
    filtered_df["temp"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

temp_cluster_analysis = filtered_df.groupby(
    "temp_cluster",
    observed=True
).agg({
    "cnt": "mean"
}).reset_index()

fig, ax = plt.subplots(figsize=(10,6))

colors = ["#72BCD4", "#BFCAD0", "#FF9F80", "#D47272"]

sns.barplot(
    x='temp_cluster',
    y='cnt',
    data=temp_cluster_analysis,
    palette=colors,
    ax=ax
)

ax.set_title('Analisis Cluster Suhu: Rata-rata Penyewaan per Kategori', fontsize=15)
ax.set_xlabel('Cluster Suhu')
ax.set_ylabel('Rata-rata Penyewaan')
ax.grid(axis='y', linestyle='--', alpha=0.7)

for p in ax.patches:
    ax.annotate(
        f'{p.get_height():.0f}',             # nilai bar
        (p.get_x() + p.get_width() / 2,      # posisi x tengah bar
         p.get_height()),                    # posisi y atas bar
        ha='center',
        va='bottom',
        fontsize=11
    )


st.pyplot(fig)

st.caption("Copyright (c) 2026 - Bike Sharing Dashboard")