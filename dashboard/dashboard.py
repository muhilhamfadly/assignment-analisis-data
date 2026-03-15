import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Menggunakan path relatif yang lebih aman untuk deployment
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    
    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

# Memuat data
main_df = load_data()

# --- SIDEBAR FILTER ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("Bike Sharing Analysis")

    # Mendapatkan rentang tanggal dari dataset
    min_date = main_df["dteday"].min()
    max_date = main_df["dteday"].max()

    # FILTER TANGGAL (Detailed Range)
    try:
        # User bisa memilih rentang tanggal secara bebas (misal: Nov 2011 - Mar 2012)
        date_range = st.date_input(
            label='Pilih Rentang Waktu (Tahun-Bulan-Hari)',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
        
        # Validasi jika user baru memilih satu tanggal
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            st.info("Pilih tanggal mulai dan tanggal selesai pada kalender.")
            st.stop()
            
    except ValueError:
        st.error("Format tanggal tidak valid.")
        st.stop()

# --- FILTERING DATA ---
filtered_df = main_df[
    (main_df["dteday"] >= pd.to_datetime(start_date)) & 
    (main_df["dteday"] <= pd.to_datetime(end_date))
]

# --- MAIN PAGE HEADER ---
st.header("Bike Sharing Dashboard 🚲")

# --- METRICS ---
col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = filtered_df["cnt"].sum()
    st.metric("Total Penyewaan", f"{total_rentals:,}")

with col2:
    avg_registered = int(filtered_df["registered"].mean()) if not filtered_df.empty else 0
    st.metric("Rata-rata Registered", f"{avg_registered:,}")

with col3:
    avg_casual = int(filtered_df["casual"].mean()) if not filtered_df.empty else 0
    st.metric("Rata-rata Casual", f"{avg_casual:,}")

st.divider()

# --- VISUALISASI 1: BAR CHART CUACA ---
st.subheader("Rata-rata Penyewaan Berdasarkan Kondisi Cuaca")

if not filtered_df.empty:
    weather_rentals = filtered_df.groupby("weathersit")["cnt"].mean().reset_index()
    weather_rentals = weather_rentals.sort_values(by='cnt', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x='cnt', y='weathersit', data=weather_rentals, palette=colors, ax=ax)

    # Annotations
    for p in ax.patches:
        ax.annotate(f'{p.get_width():.0f}', 
                    (p.get_width(), p.get_y() + p.get_height()/2), 
                    xytext=(5, 0), textcoords='offset points', ha='left', va='center')

    ax.set_title('Pengaruh Cuaca terhadap Jumlah Penyewaan', fontsize=15)
    ax.set_xlabel('Rata-rata Penyewaan')
    ax.set_ylabel(None)
    st.pyplot(fig)
else:
    st.warning("Tidak ada data untuk rentang waktu ini.")

# --- Ganti bagian expander Cuaca dengan ini ---
with st.expander("Selengkapnya"):
    if not weather_rentals.empty:
        # Mengambil baris pertama (tertinggi karena sudah di-sort) dan baris terakhir
        best_weather = weather_rentals.iloc[0]
        worst_weather = weather_rentals.iloc[-1]
        
        st.write(
            f"""
            Grafik di atas menunjukkan pengaruh cuaca terhadap rata-rata jumlah penyewaan sepeda. 
            Kondisi cuaca **{best_weather['weathersit']}** merupakan yang paling populer dengan rata-rata **{best_weather['cnt']:.0f}** penyewaan. 
            Sebaliknya, kondisi **{worst_weather['weathersit']}** memiliki rata-rata penyewaan terendah yaitu **{worst_weather['cnt']:.0f}**.
            """
        )

# --- VISUALISASI 2: LINE CHART JAM ---
st.subheader("Tren Penyewaan Berdasarkan Jam (Pola Harian)")

if "hr" in filtered_df.columns and not filtered_df.empty:
    hourly_rentals = filtered_df.groupby("hr")["cnt"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x='hr', y='cnt', data=hourly_rentals, marker='o', color='#72BCD4', linewidth=2.5, ax=ax)

    # Mencari peak value
    peak_hour = hourly_rentals.loc[hourly_rentals['cnt'].idxmax(), 'hr']
    peak_value = hourly_rentals['cnt'].max()
    ax.annotate(f'Puncak: {peak_value:.0f}', xy=(peak_hour, peak_value), 
                xytext=(peak_hour+1, peak_value),
                arrowprops=dict(facecolor='black', shrink=0.05), fontsize=12)

    ax.set_xticks(range(0, 24))
    ax.set_xlabel('Jam (00:00 - 23:00)')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

with st.expander("Selengkapnya"):
    st.write(
        f"""
        Grafik di atas menunjukkan tren penyewaan sepeda berdasarkan jam dalam sehari. Terlihat bahwa terdapat puncak penyewaan pada jam **{peak_hour}:00** dengan rata-rata penyewaan mencapai **{peak_value:.0f}**.
        """
    )

# --- VISUALISASI 3: TEMPERATURE CLUSTER ---
st.subheader("Rata-rata Penyewaan Berdasarkan Kategori Temperatur")

if not filtered_df.empty:
    bins = [0, 0.3, 0.6, 0.8, 1.0]
    labels = ['Cold', 'Moderate', 'Warm', 'Hot']

    # Gunakan .copy() untuk menghindari SettingWithCopyWarning
    temp_df = filtered_df.copy()
    temp_df["temp_cluster"] = pd.cut(temp_df["temp"], bins=bins, labels=labels, include_lowest=True)

    temp_analysis = temp_df.groupby("temp_cluster", observed=True)["cnt"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='temp_cluster', y='cnt', data=temp_analysis, palette=["#72BCD4", "#BFCAD0", "#FF9F80", "#D47272"], ax=ax)

    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width()/2, p.get_height()), 
                    ha='center', va='bottom', fontsize=11)

    ax.set_title('Analisis Cluster Suhu', fontsize=15)
    ax.set_xlabel('Kategori Suhu')
    ax.set_ylabel('Rata-rata Penyewaan')
    st.pyplot(fig)

# --- Ganti bagian expander Temperature dengan ini ---
with st.expander("Selengkapnya"):
    if not temp_analysis.empty:
        # Urutkan dulu agar kita tahu mana yang tertinggi dan terendah
        temp_analysis_sorted = temp_analysis.sort_values(by='cnt', ascending=False)
        top_temp = temp_analysis_sorted.iloc[0]
        bottom_temp = temp_analysis_sorted.iloc[-1]
        
        st.write(
            f"""
            Grafik di atas menunjukkan bahwa penyewaan sepeda sangat dipengaruhi oleh suhu. 
            Kategori **{top_temp['temp_cluster']}** adalah suhu paling ideal bagi pengguna ({top_temp['cnt']:.0f} penyewaan). 
            Sedangkan pada kategori **{bottom_temp['temp_cluster']}**, minat pengguna menurun hingga ke angka **{bottom_temp['cnt']:.0f}**.
            """
        )

st.caption("Copyright (c) 2026 - Bike Sharing Dashboard Analysis")