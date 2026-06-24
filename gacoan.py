import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns  # <-- PERBAIKAN: Diperbaiki dari 'import sns as sns' agar tidak error
from datetime import datetime

# ==============================================================================
# 1. KONFIGURASI HALAMAN UTAMA DASHBOARD
# ==============================================================================
st.set_page_config(
    page_title="Legal & Compliance Dashboard - Mie Gacoan",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KUNCI PALET WARNA RESMI MIE GACOAN (HEX CODES)
GACOAN_PURPLE = "#3A113E" 
GACOAN_RED = "#FF0000" 
GACOAN_YELLOW = "#FFC72C" 
NEUTRAL_BG = "#f7faff"
GACOAN_GREEN = "#028eb1"
GACOAN_PINK = "#f40093"
GACOAN_BLACK = "#000000" 

st.markdown(f"""
 <style>
 .main {{ background-color: {NEUTRAL_BG}; }}
 .metric-card {{
     background-color: #FFFFFF;
     border-top: 5px solid {GACOAN_PINK};
     border-left: 1px solid #E9ECEF;
     border-right: 1px solid #E9ECEF;
     border-bottom: 1px solid #E9ECEF;
     padding: 22px;
     border-radius: 12px;
     box-shadow: 0 4px 6px rgba(58, 17, 62, 0.04);
     text-align: center;
 }}
 .metric-title {{ font-size: 13px; color: #6C757D; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }}
 .metric-value-total {{ font-size: 38px; color: {GACOAN_BLACK}; font-weight: 800; margin-top: 5px; }}
 .metric-value-alert {{ font-size: 38px; color: {GACOAN_RED}; font-weight: 800; margin-top: 5px; }}
 [data-testid="stSidebar"] {{ background-color: {GACOAN_GREEN}; }}
 [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{ color: #FFFFFF !important; }}
 </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MEMUAT DATASET FINAL (567 BARIS ORIGINAL + HASIL PREDIKSI AI)
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data_gacoan_untuk_dashboard.csv')
    except FileNotFoundError:
        df = pd.DataFrame({
            'Nama_Cabang': [f'Mie Gacoan Cabang {i}' for i in range(1, 568)],
            'Provinsi': ['Jawa Tengah', 'Jawa Timur', 'DKI Jakarta', 'Jawa Barat'] * 141 + ['Jawa Tengah', 'Jawa Timur', 'DKI Jakarta'],
            'Status_IMB': ['Approved', 'Bermasalah', 'In Progress', 'Approved'] * 141 + ['Approved', 'Approved', 'Approved'],
            'Status_Halal': ['Halal', 'Proses', 'Halal', 'Belum Halal'] * 141 + ['Halal', 'Halal', 'Halal'], # Tambahan fallback data
            'Sewa_Berakhir': ['2026-06-01'] * 567,
            'Sisa_Hari_Sewa': [10, -12, 45, 120, -5, 80] * 94 + [10, -12, 45],
            'Prediksi_Tingkat_Sengketa': ['Low', 'High (Butuh Eskalasi)', 'Medium', 'Low'] * 141 + ['Low', 'Low', 'Low']
        })
    return df

df_gacoan = load_data()

# ==============================================================================
# 3. KEPALA DASHBOARD (VERSI LOGO DI SAMPING POJOK KIRI ATAS)
# ==============================================================================
col_logo, col_text = st.columns([1, 8])  # <-- PERBAIKAN: Rasio kolom disesuaikan agar rapi
with col_logo:
    # PERBAIKAN: Menggunakan URL cadangan Logo Gacoan transparan yang lebih stabil
    logo_url = "https://iconlogovector.com/uploads/images/2025/08/lg-688e9cd4b2d3d-Mie-Gacoan.webp"
    try:
        st.image(logo_url, width=95)
    except:
        st.write("🔴 Logo Error")

with col_text:
    st.markdown(f"""
     <div style='padding-top: 5px;'>
         <h2 style='color: {GACOAN_PINK}; font-weight: 800; margin: 0; padding: 0; font-size: 32px;'>MIE GACOAN</h2>
         <h4 style='color: #495057; font-weight: 700; margin: 0; padding: 0; font-size: 18px; margin-top: 2px;'>Legal and Compliance Asset Monitoring</h4>
     </div>
    """, unsafe_allow_html=True)

st.markdown(f"<hr style='border-top: 2px solid {GACOAN_GREEN}; opacity: 0.2; margin-top: 15px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# ==============================================================================
# 4. FILTER PANEL SIDEBAR (DIKUNCI DI ATAS AGAR SEMUA DATA KONSISTEN)
# ==============================================================================
st.sidebar.markdown(f"<h3 style='font-weight:700;'>Filter Panel</h3>", unsafe_allow_html=True)
selected_province = st.sidebar.multiselect(
    "Pilih Cakupan Provinsi Wilayah:", 
    options=df_gacoan['Provinsi'].unique(), 
    default=df_gacoan['Provinsi'].unique()
)
st.sidebar.markdown("---")
st.sidebar.info("Dashboard Executive ini terintegrasi penuh secara real-time dengan model cerdas AI Random Forest Classifier.")

# Memotong data secara dinamis berdasarkan filter pilihan user
df_filtered = df_gacoan[df_gacoan['Provinsi'].isin(selected_province)].copy()

# ==============================================================================
# 5. BAGIAN KPI CARDS (METRIK NILAI UTAMA)
# ==============================================================================
total_branches = len(df_filtered)
expiring_leases = len(df_filtered[df_filtered['Sisa_Hari_Sewa'] < 90])
high_risk_disputes = len(df_filtered[df_filtered['Prediksi_Tingkat_Sengketa'].str.contains('High', na=False)])

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Cabang Aktif</div><div class="metric-value-total">{total_branches}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Sewa Kritis (< 90 Hari)</div><div class="metric-value-alert">{expiring_leases}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Risiko Tinggi Perselisihan</div><div class="metric-value-alert">{high_risk_disputes}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# MEMBUAT TABS: MEMISAHKAN MONITORING UTAMA DENGAN AUTOMATED EDA FITUR
# ==============================================================================
tab_monitoring, tab_eda = st.tabs(["🗺️ Operational Monitoring", "📊 Automated Feature EDA"])

# --- TAB 1: OPERATIONAL MONITORING (Peta & Tabel Data Bawaanmu) ---
with tab_monitoring:
    st.markdown(f"<h3 style='color: {GACOAN_PURPLE}; font-weight:700;'>Interactive Geospatial Risk Map</h3>", unsafe_allow_html=True)
    provinsi_coords = {
        'Jawa Tengah': [-7.15, 110.14], 'Jawa Timur': [-7.53, 112.23], 'DKI Jakarta': [-6.20, 106.84],
        'Jawa Barat': [-6.91, 107.60], 'DI Yogyakarta': [-7.87, 110.42], 'Banten': [-6.40, 106.06],
        'Bali': [-8.40, 115.18], 'Sumatera Utara': [2.11, 99.13], 'Sumatera Barat': [-0.73, 100.79],
        'Aceh': [4.69, 96.74], 'Sulawesi Selatan': [-4.55, 119.97], 'Sulawesi Utara': [0.62, 123.97],
        'Kalimantan Tengah': [-1.68, 113.38], 'Lampung': [-4.55, 105.40], 'Jambi': [-1.61, 102.77],
        'Kalimantan Barat': [-0.27, 109.79], 'Kalimantan Timur': [1.08, 116.44], 'Bengkulu': [-3.79, 102.26]
    }
    
    df_filtered['Latitude'] = df_filtered['Provinsi'].map(lambda x: provinsi_coords.get(x, [-6.20, 106.84])[0] + np.random.uniform(-0.4, 0.4))
    df_filtered['Longitude'] = df_filtered['Provinsi'].map(lambda x: provinsi_coords.get(x, [-6.20, 106.84])[1] + np.random.uniform(-0.4, 0.4))
    
    if not df_filtered.empty:
        fig_map = px.scatter_mapbox(
            df_filtered,
            lat="Latitude",
            lon="Longitude",
            color="Prediksi_Tingkat_Sengketa",
            color_discrete_map={'Low': '#28A745', 'Medium': GACOAN_YELLOW, 'High (Butuh Eskalasi)': GACOAN_RED},
            size=df_filtered['Sisa_Hari_Sewa'].apply(lambda x: 12 if x < 90 else 6),
            hover_name="Nama_Cabang",
            hover_data=["Provinsi", "Status_IMB", "Sisa_Hari_Sewa"],
            zoom=4.6,
            center={"lat": -2.5, "lon": 118.0},
            mapbox_style="open-street-map",
            height=600 
        )
        fig_map.update_layout(
            margin={"r":0,"t":10,"l":0,"b":0},
            legend=dict(title_text="Tingkat Resiko:", orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1)
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Silakan pilih minimal satu provinsi pada Filter Panel untuk memunculkan peta spasial.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='color: {GACOAN_PURPLE}; font-weight:700;'>Daily Actionable Table</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6C757D; margin-top:-10px;'>Daftar seluruh gerai komersial yang membutuhkan tindakan perpanjangan kontraktual sewa segera berdasarkan urutan urgensi sisa hari sewa terendah.</p>", unsafe_allow_html=True)
    
    if not df_filtered.empty:
        df_table = df_filtered.copy()
        
        def get_action(days):
            if days <= 0: return "Overdue - Action Required 🚨"
            elif days < 90: return "Renewal Required ⚠️"
            else: return "Safe - Monitored ✅"
            
        df_table['Actions Required'] = df_table['Sisa_Hari_Sewa'].apply(get_action)
        
        kolom_tampilan = ['Nama_Cabang', 'Provinsi', 'Status_IMB', 'Sewa_Berakhir', 'Sisa_Hari_Sewa', 'Prediksi_Tingkat_Sengketa', 'Actions Required']
        df_table_final = df_table[kolom_tampilan].sort_values(by='Sisa_Hari_Sewa', ascending=True)
        df_table_final.columns = ['Branch Name', 'Province', 'IMB Status', 'Due Date', 'Days Left on Lease', 'Dispute Risk (AI)', 'Actions Required']
        
        st.dataframe(
            df_table_final,
            use_container_width=True,
            height=350,
            hide_index=True
        )
    else:
        st.info("Tidak ada data tabel untuk ditampilkan.")

# --- TAB 2: AUTOMATED FEATURE EDA (Paksa Tampil Kolom Spesifik) ---
with tab_eda:
    st.markdown(f"<h3 style='color: {GACOAN_PURPLE}; font-weight:700;'>Distribusi Fitur Dataset</h3>", unsafe_allow_html=True)
    st.write("Analisis grafikal otomatis untuk menelaah persebaran data berdasarkan seluruh kolom aktif di luar variabel teknis.")
    
    if df_filtered.empty:
        st.warning("Silakan pilih minimal satu provinsi pada panel kiri untuk menganalisis statistik fitur.")
    else:
        # Daftar kolom pengecualian terbaru dari Anda
        kolom_dikecualikan = [
            'Kategori_Encoded', 
            'Status_Halal_Encoded', 
            'Status_IMB_Encoded', 
            'Sewa_Tahunan_IDR', 
            'Sisa_Hari_Sewa', 
            'Kategori', 
            'Jumlah_Review',
            'Tingkat_Sengketa_Encoded',
            'Tingkat_Sengketa'
        ]
        
        # Kolom-kolom yang WAJIB dipaksa tampil meskipun nilai uniknya banyak atau berupa teks khusus
        kolom_wajib_tampil = ['Website', 'Status_Tempat', 'Prediksi_Tingkat_Sengketa', 'Status_IMB', 'Status_Halal', 'Provinsi', 'Rating']
        
        # Perulangan pembuatan grafik kolom
        for kolom in df_filtered.columns:
            
            # 1. Lewati kolom jika ada dalam daftar pengecualian Anda
            if kolom in kolom_dikecualikan:
                continue
                
            # 2. Lewati kolom koordinat internal buatan map dashboard
            if kolom in ['Latitude', 'Longitude', 'Sewa_Berakhir']:
                continue
                
            # A. JIKA DATA BERUPA KATEGORI / TEKS / DAFTAR WAJIB TAMPIL
            if df_filtered[kolom].dtype == 'object' or df_filtered[kolom].dtype == 'category' or kolom in kolom_wajib_tampil:
                
                # Pengaman: Hanya lewati jika nilai unik > 30 DAN kolom tersebut TIDAK ADA di daftar wajib tampil
                if df_filtered[kolom].nunique() > 30 and kolom not in kolom_wajib_tampil:
                    continue
                
                st.markdown(f"#### Distribusi Frekuensi Kolom: {kolom}")
                
                # Setup Kanvas Matplotlib
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Ambil 15 data teratas khusus untuk kolom Website agar grafik tidak terlalu panjang ke bawah
                if kolom == 'Website':
                    order_data = df_filtered[kolom].value_counts().head(15).index
                else:
                    order_data = df_filtered[kolom].value_counts().index
                
                # Render diagram batang horizontal persis Google Colab
                sns.countplot(y=kolom, data=df_filtered, order=order_data, color=GACOAN_PINK, ax=ax)
                
                # Tambahkan label angka otomatis di sebelah kanan ujung batang
                for p in ax.patches:
                    lebar = p.get_width()
                    if lebar > 0:
                        ax.annotate(f'{int(lebar)}', 
                                    (lebar, p.get_y() + p.get_height() / 2.), 
                                    ha='left', va='center', 
                                    xytext=(5, 0), 
                                    textcoords='offset points', 
                                    fontsize=10, fontweight='bold')
                
                ax.set_title(f'Distribusi Frekuensi Kolom: {kolom}', fontsize=11, fontweight='bold')
                ax.set_xlabel('Jumlah (Unit)')
                ax.set_ylabel(kolom)
                
                # Beri ruang di sisi kanan agar angka label tidak menabrak bingkai
                ax.set_xlim(0, df_filtered[kolom].value_counts().max() * 1.15)
                
                plt.tight_layout()
                st.pyplot(fig)
                st.markdown("---")
                
            # B. JIKA DATA BERUPA ANGKA MURNI LAINNYA
            elif df_filtered[kolom].dtype in ['int64', 'float64']:
                st.markdown(f"#### 🔢 Analisis Distribusi Angka Kolom: {kolom}")
                
                fig, ax = plt.subplots(figsize=(10, 3.5))
                sns.histplot(data=df_filtered, x=kolom, kde=True, color='#D11A5B', ax=ax)
                
                for p in ax.patches:
                    tinggi = p.get_height()
                    if tinggi > 0:
                        ax.annotate(f'{int(tinggi)}', 
                                    (p.get_x() + p.get_width() / 2., tinggi), 
                                    ha='center', va='center', 
                                    xytext=(0, 5), 
                                    textcoords='offset points', 
                                    fontsize=9, fontweight='bold')
                    
                ax.set_title(f'Analisis Distribusi Angka Kolom: {kolom}', fontsize=11, fontweight='bold')
                ax.set_xlabel(kolom)
                ax.set_ylabel('Frekuensi')
                
                plt.tight_layout()
                st.pyplot(fig)
                st.markdown("---")
