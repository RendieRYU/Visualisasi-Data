
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Mengatur konfigurasi halaman Streamlit
# 'wide' layout menggunakan seluruh lebar layar
st.set_page_config(
    page_title="Dashboard Analisis Penggunaan Media Sosial",
    page_icon="📊",
    layout="wide"
)

# --- FUNGSI UNTUK MEMUAT DATA ---
# Menggunakan cache agar data tidak perlu dimuat ulang setiap kali ada interaksi user
@st.cache_data
def load_data(file_path):
    """Fungsi untuk memuat data dari file CSV."""
    try:
        df = pd.read_csv(file_path)
        # Mengganti nama kolom agar lebih mudah dibaca dan diproses
        df.columns = [
            'student_id', 'age', 'gender', 'academic_level', 'country', 
            'avg_daily_usage_hours', 'most_used_platform', 
            'affects_academic_performance', 'sleep_hours_per_night', 
            'mental_health_score', 'conflicts_over_social_media', 'addicted_score'
        ]
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan di path: {file_path}")
        return None

# --- MEMUAT DATA ---
# Ganti 'kecanduan_siswa_terhadap_medsos.csv' dengan path yang sesuai jika file tidak berada di folder yang sama
file_name = 'kecanduan_siswa_terhadap_medsos.csv'
df = load_data(file_name)

if df is None:
    st.stop() # Menghentikan eksekusi script jika data gagal dimuat

# --- SIDEBAR ---
st.sidebar.header("⚙️ Filter Data")

# Filter berdasarkan Negara
countries = sorted(df['country'].unique())
selected_countries = st.sidebar.multiselect(
    'Pilih Negara:',
    options=countries,
    default=countries
)

# Filter berdasarkan Jenjang Pendidikan
academic_levels = df['academic_level'].unique()
selected_levels = st.sidebar.multiselect(
    'Pilih Jenjang Pendidikan:',
    options=academic_levels,
    default=academic_levels
)

# Filter berdasarkan Gender
genders = df['gender'].unique()
selected_genders = st.sidebar.multiselect(
    'Pilih Gender:',
    options=genders,
    default=genders
)

# --- (BAGIAN BARU) INFORMASI DATASET DI SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.header("📄 Informasi Dataset")

# Menampilkan metrik utama dari dataset asli (sebelum difilter)
st.sidebar.markdown(f"""
- **Total Baris Data:** `{df.shape[0]}`
- **Total Kolom:** `{df.shape[1]}`
- **Jumlah Negara:** `{df['country'].nunique()}`
""")

# Expander untuk menampilkan daftar kolom
with st.sidebar.expander("Lihat Daftar Kolom"):
    st.write(df.columns.tolist())
# --- AKHIR BAGIAN BARU ---


# --- MENERAPKAN FILTER PADA DATAFRAME ---
if not selected_countries: selected_countries = countries
if not selected_levels: selected_levels = academic_levels
if not selected_genders: selected_genders = genders

df_filtered = df[
    df['country'].isin(selected_countries) &
    df['academic_level'].isin(selected_levels) &
    df['gender'].isin(selected_genders)
]

if df_filtered.empty:
    st.warning("Tidak ada data yang cocok dengan filter yang dipilih. Silakan ubah pilihan Anda.")
    st.stop()

# --- JUDUL UTAMA DASHBOARD ---
st.title("📊 Dashboard Analisis Kecanduan Media Sosial di Kalangan Pelajar")
st.markdown("---")

# --- (BAGIAN BARU) TUJUAN ANALISIS/PERTANYAAN ---
with st.expander("❓ **Tujuan Analisis Dashboard**"):
    st.markdown("""
    Dashboard ini dirancang untuk menjawab beberapa pertanyaan kunci mengenai pola penggunaan media sosial di kalangan pelajar, yaitu:
    - **Demografi Pengguna:** Bagaimana rata-rata durasi penggunaan media sosial harian berbeda berdasarkan jenjang pendidikan dan gender?
    - **Dampak Kesejahteraan:** Apakah ada korelasi antara durasi penggunaan media sosial, jam tidur, dan skor kesehatan mental?
    - **Analisis Platform:** Platform media sosial manakah yang paling banyak menyita waktu dan menunjukkan potensi adiktif tertinggi berdasarkan data?
    """)

# --- BAGIAN 1: RATA-RATA PENGGUNAAN MEDIA SOSIAL ---
st.header("⏳ Rata-rata Jam Penggunaan Media Sosial Harian")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Berdasarkan Gender & Pendidikan")
    avg_usage = df_filtered.groupby(['academic_level', 'gender'])['avg_daily_usage_hours'].mean().round(2).reset_index()
    avg_usage = avg_usage.rename(columns={
        'academic_level': 'Jenjang Pendidikan',
        'gender': 'Gender',
        'avg_daily_usage_hours': 'Rata-rata Jam/Hari'
    })
    st.dataframe(avg_usage, use_container_width=True)

    st.info(
        """
        **Insight:**
        Tabel dan grafik di samping menunjukkan perbandingan durasi penggunaan media sosial
        antara gender yang berbeda pada setiap jenjang pendidikan.
        """
    )

with col2:
    fig_bar_usage = px.bar(
        avg_usage,
        x='Jenjang Pendidikan',
        y='Rata-rata Jam/Hari',
        color='Gender',
        barmode='group',
        title='Rata-rata Penggunaan Media Sosial Harian',
        labels={'Rata-rata Jam/Hari': 'Rata-rata Jam Penggunaan per Hari'},
        text_auto=True
    )
    fig_bar_usage.update_layout(xaxis_title='Jenjang Pendidikan', yaxis_title='Rata-rata Jam per Hari')
    st.plotly_chart(fig_bar_usage, use_container_width=True)

st.markdown("---")


# --- BAGIAN 2: KORELASI ANTARA PENGGUNAAN, TIDUR, DAN KESEHATAN MENTAL ---
st.header("🔗 Korelasi: Penggunaan Medsos, Durasi Tidur, dan Kesehatan Mental")

col1, col2 = st.columns([1.5, 2])

with col1:
    st.subheader("Heatmap Korelasi")
    # Memilih kolom yang relevan untuk korelasi
    correlation_data = df_filtered[['avg_daily_usage_hours', 'sleep_hours_per_night', 'mental_health_score']]
    correlation_matrix = correlation_data.corr()

    # Membuat heatmap menggunakan Matplotlib dan Seaborn
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        correlation_matrix,
        annot=True,          # Menampilkan nilai korelasi
        cmap='coolwarm',     # Skema warna
        fmt=".2f",           # Format angka (2 desimal)
        linewidths=.5,
        ax=ax
    )
    ax.set_title('Matriks Korelasi', fontsize=16)
    st.pyplot(fig)

with col2:
    st.subheader("Interpretasi Korelasi")
    correlation_usage_sleep = correlation_matrix.loc['avg_daily_usage_hours', 'sleep_hours_per_night']
    correlation_usage_mental = correlation_matrix.loc['avg_daily_usage_hours', 'mental_health_score']

    st.markdown(f"""
    Analisis korelasi menghasilkan nilai antara -1 dan 1 untuk mengukur hubungan antar variabel.

    * **Penggunaan Medsos vs Durasi Tidur:**
        Korelasi: **${correlation_usage_sleep:.2f}$**
        Artinya: Terdapat **korelasi negatif kuat**. Semakin tinggi durasi penggunaan media sosial,
        semakin rendah durasi tidur malam hari, dan sebaliknya.

    * **Penggunaan Medsos vs Skor Kesehatan Mental:**
        Korelasi: **${correlation_usage_mental:.2f}$**
        Artinya: Terdapat **korelasi negatif sangat kuat**. Semakin lama waktu yang dihabiskan di media sosial,
        semakin rendah skor kesehatan mental pelajar.

    * **Kesimpulan:** Data menunjukkan bahwa penggunaan media sosial yang berlebihan memiliki
        hubungan negatif yang signifikan dengan durasi tidur dan kesehatan mental pelajar.
    """)
st.markdown("---")


# --- BAGIAN 3: PLATFORM MEDIA SOSIAL PALING ADIKTIF ---
st.header("📱 Analisis Platform Media Sosial")
st.subheader("Platform Mana yang Paling Banyak Menyita Waktu dan Berpotensi Adiktif?")

col1, col2 = st.columns(2)

with col1:
    # Menghitung rata-rata jam penggunaan per platform
    usage_by_platform = df_filtered.groupby('most_used_platform')['avg_daily_usage_hours'].mean().sort_values(ascending=False).reset_index()
    fig_platform_usage = px.bar(
        usage_by_platform,
        x='avg_daily_usage_hours',
        y='most_used_platform',
        orientation='h',
        title='Platform Paling Banyak Menyita Waktu',
        labels={'avg_daily_usage_hours': 'Rata-rata Jam Penggunaan Harian', 'most_used_platform': 'Platform Media Sosial'},
        text='avg_daily_usage_hours'
    )
    fig_platform_usage.update_traces(texttemplate='%{text:.2f} jam', textposition='outside')
    fig_platform_usage.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_platform_usage, use_container_width=True)

with col2:
    # 1. Mengelompokkan data berdasarkan platform dan menghitung rata-rata skor kecanduan.
    # 2. Diurutkan ascending=True agar saat diplot, bar tertinggi (paling adiktif) ada di paling atas.
    addiction_by_platform = df_filtered.groupby('most_used_platform')['addicted_score'].mean().sort_values(ascending=True).reset_index()

    fig_platform_addiction = px.bar(
        addiction_by_platform,
        x='addicted_score',
        y='most_used_platform',
        orientation='h',
        # Judul dibuat lebih eksplisit
        title='Platform vs Skor Kecanduan (Skor Tinggi = Lebih Adiktif)',
        labels={'addicted_score': 'Rata-rata Skor Kecanduan (1-10)', 'most_used_platform': 'Platform'},
        color='addicted_score',
        # Menggunakan skala warna Merah, di mana nilai tinggi akan berwarna merah pekat
        color_continuous_scale=px.colors.sequential.Reds,
        text='addicted_score'
    )
    # Menampilkan nilai skor di ujung bar
    fig_platform_addiction.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig_platform_addiction, use_container_width=True)
# with col2:
#     # Menghitung rata-rata skor kesehatan mental per platform
#     mental_health_by_platform = df_filtered.groupby('most_used_platform')['mental_health_score'].mean().sort_values(ascending=True).reset_index()
#     fig_platform_mental_health = px.bar(
#         mental_health_by_platform,
#         x='mental_health_score',
#         y='most_used_platform',
#         orientation='h',
#         title='Platform dengan Rata-rata Skor Kesehatan Mental Terendah',
#         labels={'mental_health_score': 'Rata-rata Skor Kesehatan Mental', 'most_used_platform': 'Platform Media Sosial'},
#         color='mental_health_score',
#         color_continuous_scale='Reds_r' # _r membalikkan skema warna
#     )
#     fig_platform_mental_health.update_layout(yaxis={'categoryorder':'total descending'})
#     st.plotly_chart(fig_platform_mental_health, use_container_width=True)

st.success(
    """
    **Insight Gabungan:**
    - **Grafik Kiri** menunjukkan platform mana yang penggunanya menghabiskan waktu paling banyak setiap hari.
    - **Grafik Kanan** menunjukkan platform mana yang penggunanya cenderung memiliki skor kesehatan mental paling rendah (skor tinggi = lebih buruk).
    - Platform yang muncul di urutan atas pada kedua grafik memiliki potensi adiktif yang lebih tinggi, karena tidak hanya menyita banyak waktu tetapi juga berkorelasi dengan dampak negatif pada kesehatan mental.
    """
)