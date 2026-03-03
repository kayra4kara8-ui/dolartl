import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io

st.set_page_config(
    page_title="USDTRY Analiz Platformu",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,300&display=swap');

* { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }

html, body, .stApp {
    background: #080c14;
    color: #c9d4e8;
}

.stApp { background: #080c14; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid #1e2d4a;
}
section[data-testid="stSidebar"] * { color: #c9d4e8; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1b6cf2, #0f4abf);
    color: white;
    border: none;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    padding: 0.5rem 1.2rem;
    transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(27,108,242,0.4); }

/* Download buttons */
.stDownloadButton > button {
    background: transparent;
    color: #4a9eff;
    border: 1px solid #1e2d4a;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
}
.stDownloadButton > button:hover { border-color: #4a9eff; background: rgba(74,158,255,0.05); }

/* Metric cards */
.metric-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin: 16px 0;
}
.metric-card {
    background: #0d1220;
    border: 1px solid #1e2d4a;
    border-radius: 10px;
    padding: 18px 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1b6cf2, #00d4aa);
}
.metric-card:hover { border-color: #2a4a7a; }
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #4a6080;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 10px;
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    color: #e8f0ff;
    line-height: 1;
    margin-bottom: 6px;
}
.metric-sub {
    font-size: 0.72rem;
    color: #3a5070;
}
.metric-pos { color: #00d4aa !important; }
.metric-neg { color: #ff4d6a !important; }
.metric-neu { color: #4a9eff !important; }

/* Section headers */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #4a6080;
    padding: 24px 0 8px 0;
    border-bottom: 1px solid #1e2d4a;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e2d4a, transparent);
}

/* Jump cards */
.jump-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin: 12px 0;
}
.jump-card {
    background: #0d1220;
    border: 1px solid #1e2d4a;
    border-radius: 8px;
    padding: 14px;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}
.jump-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.5); border-color: #2a4a7a; }
.jump-card.pos { border-top: 2px solid #00d4aa; }
.jump-card.neg { border-top: 2px solid #ff4d6a; }
.jump-rank {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #3a5070;
    margin-bottom: 8px;
}
.jump-date {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #c9d4e8;
    margin-bottom: 4px;
}
.jump-pct {
    font-family: 'DM Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    line-height: 1.1;
}
.jump-pct.pos { color: #00d4aa; }
.jump-pct.neg { color: #ff4d6a; }
.jump-meta {
    font-size: 0.7rem;
    color: #3a5070;
    margin-top: 6px;
    font-family: 'DM Mono', monospace;
}

/* Forward analysis */
.forward-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 12px 0;
}
.forward-card {
    background: #0d1220;
    border: 1px solid #1e2d4a;
    border-radius: 8px;
    padding: 16px;
}
.forward-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4a6080;
    margin-bottom: 10px;
}
.forward-big {
    font-family: 'DM Mono', monospace;
    font-size: 1.3rem;
    font-weight: 500;
    color: #e8f0ff;
    margin-bottom: 4px;
}
.forward-detail {
    font-size: 0.72rem;
    color: #3a5070;
    line-height: 1.6;
}
.forward-accent { color: #4a9eff; }

/* Upload box */
.upload-box {
    background: #0d1220;
    border: 1px dashed #1e2d4a;
    border-radius: 12px;
    padding: 60px 40px;
    text-align: center;
    margin: 40px auto;
    max-width: 600px;
}
.upload-icon { font-size: 3rem; margin-bottom: 16px; }
.upload-title {
    font-family: 'DM Mono', monospace;
    font-size: 1rem;
    color: #4a9eff;
    margin-bottom: 8px;
}
.upload-desc { font-size: 0.85rem; color: #3a5070; line-height: 1.7; }

/* Dataframe */
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #1e2d4a; }

/* Hide default streamlit branding */
#MainMenu, footer { visibility: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1220;
    border-bottom: 1px solid #1e2d4a;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: #4a6080;
    padding: 12px 24px;
    background: transparent;
    border: none;
    text-transform: uppercase;
}
.stTabs [aria-selected="true"] {
    color: #4a9eff !important;
    border-bottom: 2px solid #4a9eff !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 16px 0; background: transparent; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* Sliders and inputs */
.stSlider [data-baseweb="slider"] { color: #1b6cf2; }
.stSelectbox [data-baseweb="select"] { background: #0d1220; border: 1px solid #1e2d4a; border-radius: 6px; }
.stRadio label { font-size: 0.85rem !important; }
.stInfo { background: #0d1a2e; border: 1px solid #1e4a8a; border-radius: 6px; }

/* Remove default padding/margin artifacts */
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
TR_AY = {1:'Oca',2:'Şub',3:'Mar',4:'Nis',5:'May',6:'Haz',
         7:'Tem',8:'Ağu',9:'Eyl',10:'Eki',11:'Kas',12:'Ara'}
TR_AY_UZUN = {1:'Ocak',2:'Şubat',3:'Mart',4:'Nisan',5:'Mayıs',6:'Haziran',
              7:'Temmuz',8:'Ağustos',9:'Eylül',10:'Ekim',11:'Kasım',12:'Aralık'}
TR_GUN = {'Monday':'Pazartesi','Tuesday':'Salı','Wednesday':'Çarşamba',
          'Thursday':'Perşembe','Friday':'Cuma','Saturday':'Cumartesi','Sunday':'Pazar'}

PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,18,32,0.9)',
    font=dict(color='#c9d4e8', family='DM Sans, sans-serif'),
    hoverlabel=dict(bgcolor='#0d1220', font_size=12, font_color='#e8f0ff', bordercolor='#2a4a7a'),
    xaxis=dict(gridcolor='#131c2e', gridwidth=1, tickfont=dict(size=10, color='#4a6080'), zeroline=False),
    yaxis=dict(gridcolor='#131c2e', gridwidth=1, tickfont=dict(size=10, color='#4a6080'), zeroline=False),
    legend=dict(bgcolor='rgba(13,18,32,0.8)', bordercolor='#1e2d4a', borderwidth=1,
                font=dict(size=11)),
    margin=dict(l=50, r=20, t=50, b=40),
)

def apply_base(fig, **kwargs):
    cfg = {**PLOTLY_BASE, **kwargs}
    # merge nested dicts
    for k in ['xaxis', 'yaxis', 'font', 'hoverlabel', 'legend', 'margin']:
        if k in kwargs:
            cfg[k] = {**PLOTLY_BASE.get(k, {}), **kwargs[k]}
    fig.update_layout(**cfg)
    return fig

# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
@st.cache_data
def veri_isle(raw):
    df = pd.read_excel(io.BytesIO(raw), sheet_name='EVDS')
    df.columns = ['Tarih', 'Dolar_Kuru']
    n0 = len(df)
    df = df.dropna()
    cleaned = n0 - len(df)
    df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y', errors='coerce')
    df = df.dropna(subset=['Tarih'])
    df = df.sort_values('Tarih').reset_index(drop=True)
    df['Dolar_Kuru'] = pd.to_numeric(df['Dolar_Kuru'], errors='coerce')
    df = df.dropna(subset=['Dolar_Kuru'])

    df['Onceki_Kur']   = df['Dolar_Kuru'].shift(1)
    df['Onceki_Tarih'] = df['Tarih'].shift(1)
    df['Gun_Farki']    = (df['Tarih'] - df['Onceki_Tarih']).dt.days
    df['Yuzde_Degisim']= (df['Dolar_Kuru'] / df['Onceki_Kur'] - 1) * 100
    df['TL_Degisim']   = df['Dolar_Kuru'] - df['Onceki_Kur']
    df = df.dropna()

    df['Yil']     = df['Tarih'].dt.year
    df['Ay']      = df['Tarih'].dt.month
    df['Gun']     = df['Tarih'].dt.day
    df['Ay_Adi']  = df['Tarih'].dt.strftime('%B')
    df['Gun_Adi'] = df['Tarih'].dt.strftime('%A')
    df['Abs_Degisim'] = df['Yuzde_Degisim'].abs()

    # Rolling returns (her gün için)
    df_indexed = df.set_index('Tarih')
    df['Haftalik_Getiri'] = df_indexed['Dolar_Kuru'].pct_change(5).values * 100
    df['Aylik_Getiri']    = df_indexed['Dolar_Kuru'].pct_change(21).values * 100
    df['3Ay_Getiri']      = df_indexed['Dolar_Kuru'].pct_change(63).values * 100

    df['Hover_Tarih'] = df.apply(
        lambda r: f"{int(r['Tarih'].day)} {TR_AY_UZUN.get(r['Tarih'].month,'')} {int(r['Tarih'].year)}", axis=1)

    # Gercek haftalik veri: her ISO haftasinin son islem gunu
    df['ISOYil']   = df['Tarih'].dt.isocalendar().year.astype(int)
    df['ISOHafta'] = df['Tarih'].dt.isocalendar().week.astype(int)
    hafta_son = df.groupby(['ISOYil','ISOHafta'])['Tarih'].max().reset_index()
    hafta_son.columns = ['ISOYil','ISOHafta','HaftaSon']
    hafta_son = hafta_son.merge(
        df[['Tarih','Dolar_Kuru','Gun_Adi']].rename(
            columns={'Tarih':'HaftaSon','Dolar_Kuru':'HaftaKapKur','Gun_Adi':'HaftaGun'}),
        on='HaftaSon')
    hafta_son = hafta_son.sort_values('HaftaSon').reset_index(drop=True)
    hafta_son['HaftaOncekiKur']   = hafta_son['HaftaKapKur'].shift(1)
    hafta_son['HaftaOncekiTarih'] = hafta_son['HaftaSon'].shift(1)
    hafta_son['HaftaDegisim']     = (hafta_son['HaftaKapKur'] / hafta_son['HaftaOncekiKur'] - 1) * 100
    hafta_son['HaftaBaslangic']   = hafta_son['HaftaOncekiTarih'] + pd.Timedelta(days=1)
    hafta_son = hafta_son.dropna(subset=['HaftaDegisim']).reset_index(drop=True)

    return df, cleaned, hafta_son

def forward_analysis(df, threshold, periods):
    """After a daily jump >= threshold%, what happens in next N days?"""
    events = df[df['Abs_Degisim'] >= threshold].copy()
    results = {}
    for p in periods:
        changes = []
        for idx in events.index:
            future_idx = idx + p
            if future_idx < len(df):
                fwd = (df.loc[future_idx, 'Dolar_Kuru'] / df.loc[idx, 'Dolar_Kuru'] - 1) * 100
                changes.append(fwd)
        if changes:
            arr = np.array(changes)
            results[p] = {
                'mean': np.mean(arr),
                'median': np.median(arr),
                'pos_pct': (arr > 0).mean() * 100,
                'p25': np.percentile(arr, 25),
                'p75': np.percentile(arr, 75),
                'n': len(arr),
                'raw': arr.tolist()
            }
    return results

# ─── HEADER ──────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <div style="padding: 8px 0 4px 0;">
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.2em; color:#1b6cf2; margin-bottom:6px;">
            ◈ USDTRY · GÜNLÜK SIÇRAMA & İLERİ ANALİZ
        </div>
        <h1 style="font-size:2rem; font-weight:700; color:#e8f0ff; margin:0; line-height:1.1;
                   letter-spacing:-0.02em;">
            Dolar Kuru Analiz Platformu
        </h1>
        <p style="color:#3a5070; font-size:0.85rem; margin:6px 0 0 0;">
            Günlük sıçramaları keşfedin · Haftalık & aylık trendleri takip edin · İleri dönem etkisini analiz edin
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                letter-spacing:0.15em; color:#1b6cf2; padding:16px 0 12px 0; border-bottom:1px solid #1e2d4a;">
        ◈ Parametre Kontrolü
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    esik = st.slider("Günlük Sıçrama Eşiği (%)", 0.5, 10.0, 2.0, 0.1,
                     help="Bu değerin üzerindeki günlük değişimler 'sıçrama' sayılır")
    gosterim_sec = st.selectbox("Gösterilecek Sıçrama Sayısı",
                                 [10, 20, 30, 50, 75, 100, "Tümü"], index=2)
    yon = st.radio("Sıçrama Yönü", ["Tümü", "Yalnız Pozitif ↑", "Yalnız Negatif ↓"])

    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                letter-spacing:0.15em; color:#1b6cf2; padding:20px 0 12px 0; border-bottom:1px solid #1e2d4a;">
        ◈ Etiket Ayarı (Günlük)
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    etiket_quantile = st.slider("Günlük — Etiketlenecek Dilim (%)", 10, 100, 40, 5,
                                 help="Günlük değişim grafiğinde en büyük kaç %'lik dilim etiketlensin")

    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                letter-spacing:0.15em; color:#1b6cf2; padding:20px 0 12px 0; border-bottom:1px solid #1e2d4a;">
        ◈ Haftalık / Gün Analizi
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    haftalik_esik = st.slider("Haftalık Sıçrama Eşiği (%)", 0.0, 20.0, 3.0, 0.5,
                               help="Bu eşiği aşan haftalık değişimler scatter'da vurgulanır ve etiketlenir")
    haftalik_etiket = st.slider("Haftalık — Etiketlenecek Dilim (%)", 10, 100, 40, 5,
                                 help="Haftalık scatter'da en büyük kaç %'lik dilim etiketlensin")
    haftalik_yon = st.radio("Haftalık Yön", ["Tümü", "Yalnız Pozitif ↑", "Yalnız Negatif ↓"],
                             key="haftalik_yon")
    gun_filtre = st.multiselect(
        "Gün Filtresi — Scatter Renklendirme",
        ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"],
        default=[],
        help="Seçili günlerin noktaları ayrı renkle gösterilir. Boş = eşiğe göre renk."
    )

    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                letter-spacing:0.15em; color:#1b6cf2; padding:20px 0 12px 0; border-bottom:1px solid #1e2d4a;">
        ◈ İleri Analiz
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    fwd_threshold = st.slider("Tetikleyici Eşik (%)", 0.5, 15.0, 3.0, 0.5,
                               help="Bu büyüklükteki sıçramalardan sonra ne olur?")

    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                letter-spacing:0.15em; color:#1b6cf2; padding:20px 0 12px 0; border-bottom:1px solid #1e2d4a;">
        ◈ Veri Kaynağı
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Excel Dosyası (.xlsx)", type=['xlsx', 'xls'])
    st.markdown("""
    <div style="font-size:0.72rem; color:#3a5070; margin-top:8px; line-height:1.7;">
        Sayfa: <span style="color:#4a9eff; font-family:'DM Mono',monospace;">EVDS</span><br>
        Sütun 1: <span style="color:#4a9eff; font-family:'DM Mono',monospace;">Tarih (DD-MM-YYYY)</span><br>
        Sütun 2: <span style="color:#4a9eff; font-family:'DM Mono',monospace;">TP_DK_USD_A_YTL</span>
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if uploaded_file is None:
    st.markdown("""
    <div class="upload-box">
        <div class="upload-icon">◈</div>
        <div class="upload-title">EVDS Excel Dosyanızı Yükleyin</div>
        <div class="upload-desc">
            Sol panelden .xlsx dosyanızı seçin<br><br>
            Beklenen format: <strong>EVDS</strong> sayfası<br>
            Tarih sütunu: <strong>DD-MM-YYYY</strong><br>
            Kur sütunu: <strong>TP_DK_USD_A_YTL</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

with st.spinner("Veriler işleniyor..."):
    try:
        df, nan_cleaned, hafta_son = veri_isle(uploaded_file.read())
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
        st.stop()

if nan_cleaned > 0:
    st.info(f"ℹ {nan_cleaned} boş satır temizlendi.")

# Apply filters
if yon == "Yalnız Pozitif ↑":
    sicramalar = df[df['Yuzde_Degisim'] >= esik].copy()
elif yon == "Yalnız Negatif ↓":
    sicramalar = df[df['Yuzde_Degisim'] <= -esik].copy()
else:
    sicramalar = df[df['Abs_Degisim'] >= esik].copy()

sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
top_sic = sicramalar.head(int(gosterim_sec)) if gosterim_sec != "Tümü" else sicramalar.copy()

pos_j = top_sic[top_sic['Yuzde_Degisim'] > 0].copy()
neg_j = top_sic[top_sic['Yuzde_Degisim'] < 0].copy()

poz_say = (df['Yuzde_Degisim'] > 0).sum()
neg_say = (df['Yuzde_Degisim'] < 0).sum()
oran    = len(sicramalar) / len(df) * 100
max_j   = df['Yuzde_Degisim'].max()
min_j   = df['Yuzde_Degisim'].min()

# ─── KPI CARDS ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">◈ Genel İstatistikler</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-label">Toplam Gün</div>
    <div class="metric-value metric-neu">{len(df):,}</div>
    <div class="metric-sub">{df['Tarih'].min().year} – {df['Tarih'].max().year}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Ort. Günlük Değ.</div>
    <div class="metric-value">%{df['Yuzde_Degisim'].mean():.3f}</div>
    <div class="metric-sub">std ± {df['Yuzde_Degisim'].std():.3f}%</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Pozitif / Negatif</div>
    <div class="metric-value"><span class="metric-pos">{poz_say}</span> <span style="color:#1e2d4a">/</span> <span class="metric-neg">{neg_say}</span></div>
    <div class="metric-sub">gün</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Toplam Sıçrama (≥%{esik})</div>
    <div class="metric-value metric-neu">{len(sicramalar):,}</div>
    <div class="metric-sub">günlerin %{oran:.1f}'i</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">En Büyük / En Küçük</div>
    <div class="metric-value"><span class="metric-pos">+{max_j:.2f}%</span></div>
    <div class="metric-sub"><span class="metric-neg">{min_j:.2f}%</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "GÜNLÜK ANALİZ",
    "HAFTALIK & AYLIK",
    "İLERİ ANALİZ",
    "DAĞILIM & ISITMA",
    "TABLOLAR"
])

# ════════════ TAB 1 ════════════
with tab1:
    # Chart 1: Main price + jumps
    st.markdown('<div class="section-label">◈ Dolar Kuru & Sıçrama Noktaları</div>', unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['Tarih'], y=df['Dolar_Kuru'],
        mode='lines', name='USD/TRY',
        line=dict(color='#2a4a7a', width=1.5),
        text=df['Hover_Tarih'],
        hovertemplate='<b>%{text}</b><br>%{y:.4f} ₺<extra></extra>'
    ))
    if len(pos_j) > 0:
        pos_j['_h'] = pos_j.apply(lambda r: f"{int(r['Tarih'].day)} {TR_AY_UZUN.get(r['Tarih'].month,'')} {int(r['Tarih'].year)}", axis=1)
        fig1.add_trace(go.Scatter(
            x=pos_j['Tarih'], y=pos_j['Dolar_Kuru'],
            mode='markers', name='↑ Pozitif',
            marker=dict(color='#00d4aa', size=pos_j['Abs_Degisim'] * 2.5,
                        line=dict(color='rgba(0,212,170,0.3)', width=3), opacity=0.9),
            text=pos_j['_h'],
            customdata=list(zip(pos_j['Yuzde_Degisim'], pos_j['Onceki_Kur'], pos_j['Dolar_Kuru'])),
            hovertemplate='<b>%{text}</b><br>Kur: %{customdata[2]:.4f} ₺ ← %{customdata[1]:.4f} ₺<br><b style="color:#00d4aa">+%{customdata[0]:.3f}%</b><extra></extra>'
        ))
    if len(neg_j) > 0:
        neg_j['_h'] = neg_j.apply(lambda r: f"{int(r['Tarih'].day)} {TR_AY_UZUN.get(r['Tarih'].month,'')} {int(r['Tarih'].year)}", axis=1)
        fig1.add_trace(go.Scatter(
            x=neg_j['Tarih'], y=neg_j['Dolar_Kuru'],
            mode='markers', name='↓ Negatif',
            marker=dict(color='#ff4d6a', size=neg_j['Abs_Degisim'] * 2.5,
                        line=dict(color='rgba(255,77,106,0.3)', width=3), opacity=0.9),
            text=neg_j['_h'],
            customdata=list(zip(neg_j['Yuzde_Degisim'], neg_j['Onceki_Kur'], neg_j['Dolar_Kuru'])),
            hovertemplate='<b>%{text}</b><br>Kur: %{customdata[2]:.4f} ₺ ← %{customdata[1]:.4f} ₺<br><b style="color:#ff4d6a">%{customdata[0]:.3f}%</b><extra></extra>'
        ))
    apply_base(fig1, height=560,
               title=dict(text=f"USD/TRY  ·  Eşik %{esik}  ·  Top {gosterim_sec}", font=dict(size=13, color='#4a6080', family='DM Mono, monospace'), x=0),
               xaxis=dict(gridcolor='#131c2e', tickformat='%b %Y', tickfont=dict(size=10, color='#4a6080'),
                          showspikes=True, spikecolor='#2a4a7a', spikethickness=1, spikedash='dot'),
               yaxis=dict(gridcolor='#131c2e', tickformat=',.3f', ticksuffix=' ₺', tickfont=dict(size=10, color='#4a6080'),
                          showspikes=True, spikecolor='#2a4a7a', spikethickness=1, spikedash='dot'),
               hovermode='closest',
               legend=dict(bgcolor='rgba(13,18,32,0.9)', bordercolor='#1e2d4a', orientation='h', yanchor='bottom', y=1.01, xanchor='left', x=0))
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Daily % changes
    st.markdown('<div class="section-label">◈ Günlük Yüzde Değişimler</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df['Tarih'], y=df['Yuzde_Degisim'],
        mode='lines', name='Günlük %',
        line=dict(color='#1e2d4a', width=0.8), opacity=0.7,
        text=df['Hover_Tarih'],
        hovertemplate='<b>%{text}</b> — %{y:.3f}%<extra></extra>'
    ))
    if len(pos_j) > 0:
        esik_val = pos_j['Yuzde_Degisim'].quantile(1 - etiket_quantile / 100)
        pos_j['_lbl'] = pos_j.apply(
            lambda r: f"{r['Tarih'].strftime('%d.%m.%y')} +{r['Yuzde_Degisim']:.1f}%"
                      if r['Yuzde_Degisim'] >= esik_val else "", axis=1)
        fig2.add_trace(go.Scatter(
            x=pos_j['Tarih'], y=pos_j['Yuzde_Degisim'],
            mode='markers+text', name='↑ Pozitif',
            marker=dict(color='#00d4aa', size=8, symbol='triangle-up', line=dict(color='rgba(0,212,170,0.4)', width=2)),
            text=pos_j['_lbl'], textposition='top right', textfont=dict(size=8, color='#00d4aa', family='DM Mono, monospace'),
            customdata=pos_j['Yuzde_Degisim'],
            hovertemplate='%{x|%d.%m.%Y}<br><b>+%{customdata:.3f}%</b><extra></extra>'
        ))
    if len(neg_j) > 0:
        esik_val2 = neg_j['Yuzde_Degisim'].quantile(etiket_quantile / 100)
        neg_j['_lbl'] = neg_j.apply(
            lambda r: f"{r['Tarih'].strftime('%d.%m.%y')} {r['Yuzde_Degisim']:.1f}%"
                      if r['Yuzde_Degisim'] <= esik_val2 else "", axis=1)
        fig2.add_trace(go.Scatter(
            x=neg_j['Tarih'], y=neg_j['Yuzde_Degisim'],
            mode='markers+text', name='↓ Negatif',
            marker=dict(color='#ff4d6a', size=8, symbol='triangle-down', line=dict(color='rgba(255,77,106,0.4)', width=2)),
            text=neg_j['_lbl'], textposition='bottom right', textfont=dict(size=8, color='#ff4d6a', family='DM Mono, monospace'),
            customdata=neg_j['Yuzde_Degisim'],
            hovertemplate='%{x|%d.%m.%Y}<br><b>%{customdata:.3f}%</b><extra></extra>'
        ))
    fig2.add_hline(y=esik, line_dash="dash", line_color='rgba(0,212,170,0.4)', line_width=1,
                   annotation_text=f"+{esik}%", annotation_font_color='#00d4aa', annotation_font_size=10)
    fig2.add_hline(y=-esik, line_dash="dash", line_color='rgba(255,77,106,0.4)', line_width=1,
                   annotation_text=f"-{esik}%", annotation_font_color='#ff4d6a', annotation_font_size=10)
    fig2.add_hline(y=0, line_color='#1e2d4a', line_width=1)
    apply_base(fig2, height=480,
               title=dict(text=f"GÜNLÜK DEĞİŞİM DAĞILIMI  ·  Eşik %{esik}", font=dict(size=12, color='#4a6080', family='DM Mono, monospace'), x=0),
               xaxis=dict(gridcolor='#131c2e', tickformat='%b %Y', tickfont=dict(size=10, color='#4a6080')),
               yaxis=dict(gridcolor='#131c2e', ticksuffix='%', tickfont=dict(size=10, color='#4a6080')),
               hovermode='closest')
    st.plotly_chart(fig2, use_container_width=True)

    # Top 10 cards
    st.markdown('<div class="section-label">◈ En Büyük 10 Sıçrama</div>', unsafe_allow_html=True)
    top10 = sicramalar.head(10)
    rows = [top10.iloc[:5], top10.iloc[5:10]]
    for row_df in rows:
        cols = st.columns(5)
        for i, (_, r) in enumerate(row_df.iterrows()):
            is_pos = r['Yuzde_Degisim'] > 0
            sign = "+" if is_pos else ""
            icon = "↑" if is_pos else "↓"
            card_cls = "pos" if is_pos else "neg"
            pct_cls  = "pos" if is_pos else "neg"
            rank = row_df.index.get_loc(r.name) + (0 if i < 5 else 5) + 1
            global_rank = list(top10.index).index(r.name) + 1
            with cols[i]:
                st.markdown(f"""
                <div class="jump-card {card_cls}">
                  <div class="jump-rank">#{global_rank} {icon}</div>
                  <div class="jump-date">{r['Tarih'].strftime('%d.%m.%Y')}</div>
                  <div class="jump-pct {pct_cls}">{sign}{r['Yuzde_Degisim']:.2f}%</div>
                  <div class="jump-meta">{TR_GUN.get(r['Gun_Adi'], r['Gun_Adi'])}</div>
                  <div class="jump-meta">{r['Onceki_Kur']:.4f} → {r['Dolar_Kuru']:.4f} ₺</div>
                  <div class="jump-meta">+{int(r['Gun_Farki'])} gün arayla</div>
                </div>
                """, unsafe_allow_html=True)

# ════════════ TAB 2 ════════════
with tab2:
    # ── Gün renk paleti
    GUN_COLORS = {
        'Pazartesi': '#4a9eff',
        'Salı':      '#b794f4',
        'Çarşamba':  '#f6ad55',
        'Perşembe':  '#00d4aa',
        'Cuma':      '#ff4d6a',
    }
    EN_GUN = {'Pazartesi':'Monday','Salı':'Tuesday','Çarşamba':'Wednesday',
              'Perşembe':'Thursday','Cuma':'Friday'}
    ALL_DAYS_TR = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']

    df['Gun_Adi_TR'] = df['Gun_Adi'].map(TR_GUN)

    # ── Seçili günler (boşsa tümü)
    aktif_gunler = gun_filtre if gun_filtre else ALL_DAYS_TR
    df_gun = df[df['Gun_Adi_TR'].isin(aktif_gunler)].copy()

    # ── PAZARTESİ vs CUMA karşılaştırması (ana bölüm)
    st.markdown('<div class="section-label">◈ Günlük Değişim — Gün Bazlı Karşılaştırma</div>', unsafe_allow_html=True)

    # Scatter: tüm günler üst üste bindirilmiş çizgi + scatter
    fig_gd = go.Figure()
    # arka plan çizgi
    fig_gd.add_trace(go.Scatter(
        x=df['Tarih'], y=df['Yuzde_Degisim'],
        mode='lines', name='Tüm Günler',
        line=dict(color='#1e2d4a', width=0.7), opacity=0.5,
        hoverinfo='skip', showlegend=False
    ))
    for gun_tr in aktif_gunler:
        sub = df[df['Gun_Adi_TR'] == gun_tr].copy()
        color = GUN_COLORS.get(gun_tr, '#c9d4e8')
        fig_gd.add_trace(go.Scatter(
            x=sub['Tarih'], y=sub['Yuzde_Degisim'],
            mode='markers', name=gun_tr,
            marker=dict(color=color, size=5, opacity=0.85,
                        line=dict(color='rgba(0,0,0,0.3)', width=0.5)),
            customdata=list(zip(sub['Yuzde_Degisim'], sub['Dolar_Kuru'], sub['Onceki_Kur'])),
            hovertemplate=(
                f'<b>{gun_tr}</b> — %{{x|%d.%m.%Y}}<br>'
                'Değişim: <b>%{customdata[0]:.3f}%</b><br>'
                'Kur: %{customdata[2]:.4f} → %{customdata[1]:.4f} ₺<extra></extra>'
            )
        ))
    fig_gd.add_hline(y=0, line_color='#2a4a7a', line_width=1)
    apply_base(fig_gd, height=460,
               title=dict(text=f"GÜN BAZLI DEĞİŞİM DAĞILIMI — {', '.join(aktif_gunler)}", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
               xaxis=dict(gridcolor='#131c2e', tickformat='%b %Y'),
               yaxis=dict(gridcolor='#131c2e', ticksuffix='%'),
               hovermode='closest')
    st.plotly_chart(fig_gd, use_container_width=True)

    # ── Gün istatistik kartları
    st.markdown('<div class="section-label">◈ Gün Bazlı İstatistikler</div>', unsafe_allow_html=True)
    kart_cols = st.columns(len(aktif_gunler))
    for i, gun_tr in enumerate(aktif_gunler):
        sub = df[df['Gun_Adi_TR'] == gun_tr]
        ort  = sub['Yuzde_Degisim'].mean()
        std  = sub['Yuzde_Degisim'].std()
        maks = sub['Yuzde_Degisim'].max()
        mins = sub['Yuzde_Degisim'].min()
        poz  = (sub['Yuzde_Degisim'] > 0).mean() * 100
        color = GUN_COLORS.get(gun_tr, '#4a9eff')
        sign = "+" if ort >= 0 else ""
        ort_cls = "metric-pos" if ort >= 0 else "metric-neg"
        with kart_cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 2px solid {color};">
              <div class="metric-label" style="color:{color};">{gun_tr}</div>
              <div class="metric-value {ort_cls}">{sign}{ort:.3f}%</div>
              <div class="metric-sub">Ort. günlük değişim</div>
              <div style="margin-top:10px; font-size:0.72rem; color:#3a5070; font-family:'DM Mono',monospace; line-height:1.8;">
                <span style="color:#4a6080">Std:</span> <span style="color:{color}">±{std:.3f}%</span><br>
                <span style="color:#4a6080">Max:</span> <span style="color:#00d4aa">+{maks:.2f}%</span><br>
                <span style="color:#4a6080">Min:</span> <span style="color:#ff4d6a">{mins:.2f}%</span><br>
                <span style="color:#4a6080">Poz. oran:</span> <span style="color:{color}">%{poz:.0f}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Violin / box: gün bazlı dağılım
    st.markdown('<div class="section-label">◈ Dağılım Karşılaştırması (Violin)</div>', unsafe_allow_html=True)
    fig_vio = go.Figure()
    for gun_tr in ALL_DAYS_TR:
        sub = df[df['Gun_Adi_TR'] == gun_tr]
        color = GUN_COLORS.get(gun_tr, '#4a9eff')
        fig_vio.add_trace(go.Violin(
            y=sub['Yuzde_Degisim'], name=gun_tr,
            line_color=color,
            fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)',
            meanline_visible=True, box_visible=True,
            points='outliers',
            hovertemplate=f'<b>{gun_tr}</b><br>%{{y:.3f}}%<extra></extra>'
        ))
    fig_vio.add_hline(y=0, line_color='#2a4a7a', line_dash='dash', line_width=1)
    apply_base(fig_vio, height=460,
               title=dict(text="GÜN BAZLI DEĞİŞİM — VİOLİN", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
               yaxis=dict(gridcolor='#131c2e', ticksuffix='%'),
               xaxis=dict(gridcolor='#0d1220'))
    st.plotly_chart(fig_vio, use_container_width=True)

    # ── Haftalık getiri: Pazartesi açılışından Cuma kapanışına (hafta bazlı, tek nokta/hafta)
    st.markdown('<div class="section-label">◈ Haftalık Getiri — Pazartesi → Cuma</div>', unsafe_allow_html=True)

    # Her haftanın ilk (Pzt) ve son (Cum) işlem günü
    df['ISOYil']   = df['Tarih'].dt.isocalendar().year.astype(int)
    df['ISOHafta'] = df['Tarih'].dt.isocalendar().week.astype(int)

    hf_ilk = df.groupby(['ISOYil','ISOHafta']).agg(
        PztTarih=('Tarih','min'), PztKur=('Dolar_Kuru','first')
    ).reset_index()
    hf_son = df.groupby(['ISOYil','ISOHafta']).agg(
        CumTarih=('Tarih','max'), CumKur=('Dolar_Kuru','last')
    ).reset_index()
    hf = hf_ilk.merge(hf_son, on=['ISOYil','ISOHafta'])
    hf['HaftaDegisim'] = (hf['CumKur'] / hf['PztKur'] - 1) * 100
    # x ekseni = haftanın Cuma tarihi (görsel hizalama için)
    hf['XTarih'] = hf['CumTarih']
    hf['Etiket_Aralik'] = hf['PztTarih'].dt.strftime('%d.%m') + '–' + hf['CumTarih'].dt.strftime('%d.%m.%y')
    hf = hf.dropna(subset=['HaftaDegisim']).reset_index(drop=True)

    # Yön filtresi
    if haftalik_yon == "Yalnız Pozitif ↑":
        hf_sic = hf[hf['HaftaDegisim'] >= haftalik_esik].copy()
    elif haftalik_yon == "Yalnız Negatif ↓":
        hf_sic = hf[hf['HaftaDegisim'] <= -haftalik_esik].copy()
    else:
        hf_sic = hf[hf['HaftaDegisim'].abs() >= haftalik_esik].copy()

    hf_pos_sc = hf_sic[hf_sic['HaftaDegisim'] > 0].copy()
    hf_neg_sc = hf_sic[hf_sic['HaftaDegisim'] < 0].copy()

    # Etiket: sadece en büyük dilim — format "dd.mm–dd.mm.yy  +X.X%"
    def hf_lbl(sub, is_pos):
        sub = sub.copy()
        if len(sub) == 0:
            sub['_lbl'] = pd.Series(dtype=str)
            return sub
        if is_pos:
            thr = sub['HaftaDegisim'].quantile(1 - haftalik_etiket / 100)
            sub['_lbl'] = sub.apply(
                lambda r: f"{r['Etiket_Aralik']}  +{r['HaftaDegisim']:.1f}%"
                          if r['HaftaDegisim'] >= thr else "", axis=1)
        else:
            thr = sub['HaftaDegisim'].quantile(haftalik_etiket / 100)
            sub['_lbl'] = sub.apply(
                lambda r: f"{r['Etiket_Aralik']}  {r['HaftaDegisim']:.1f}%"
                          if r['HaftaDegisim'] <= thr else "", axis=1)
        return sub

    hf_pos_sc = hf_lbl(hf_pos_sc, True)
    hf_neg_sc = hf_lbl(hf_neg_sc, False)

    fig_hw = go.Figure()

    # Arka plan çizgisi — tüm haftalar
    fig_hw.add_trace(go.Scatter(
        x=hf['XTarih'], y=hf['HaftaDegisim'],
        mode='lines', name='Haftalık Δ',
        line=dict(color='#2a4a7a', width=1.2), opacity=0.5,
        customdata=list(zip(hf['Etiket_Aralik'], hf['PztKur'], hf['CumKur'])),
        hovertemplate='<b>%{customdata[0]}</b><br>Pzt: %{customdata[1]:.4f} ₺  →  Cum: %{customdata[2]:.4f} ₺<br>Değişim: %{y:.3f}%<extra></extra>'
    ))

    # Pozitif sıçramalar
    if len(hf_pos_sc) > 0:
        fig_hw.add_trace(go.Scatter(
            x=hf_pos_sc['XTarih'], y=hf_pos_sc['HaftaDegisim'],
            mode='markers+text', name='↑ Pozitif',
            marker=dict(
                color='#00d4aa',
                size=hf_pos_sc['HaftaDegisim'].abs() * 2 + 5,
                symbol='triangle-up',
                line=dict(color='rgba(0,212,170,0.3)', width=3), opacity=0.9
            ),
            text=hf_pos_sc['_lbl'],
            textposition='top right',
            textfont=dict(size=8, color='#00d4aa', family='DM Mono, monospace'),
            customdata=list(zip(hf_pos_sc['Etiket_Aralik'], hf_pos_sc['PztKur'], hf_pos_sc['CumKur'], hf_pos_sc['HaftaDegisim'])),
            hovertemplate='<b>%{customdata[0]}</b><br>Pzt: %{customdata[1]:.4f} ₺  →  Cum: %{customdata[2]:.4f} ₺<br><b style="color:#00d4aa">+%{customdata[3]:.3f}%</b><extra></extra>'
        ))

    # Negatif sıçramalar
    if len(hf_neg_sc) > 0:
        fig_hw.add_trace(go.Scatter(
            x=hf_neg_sc['XTarih'], y=hf_neg_sc['HaftaDegisim'],
            mode='markers+text', name='↓ Negatif',
            marker=dict(
                color='#ff4d6a',
                size=hf_neg_sc['HaftaDegisim'].abs() * 2 + 5,
                symbol='triangle-down',
                line=dict(color='rgba(255,77,106,0.3)', width=3), opacity=0.9
            ),
            text=hf_neg_sc['_lbl'],
            textposition='bottom right',
            textfont=dict(size=8, color='#ff4d6a', family='DM Mono, monospace'),
            customdata=list(zip(hf_neg_sc['Etiket_Aralik'], hf_neg_sc['PztKur'], hf_neg_sc['CumKur'], hf_neg_sc['HaftaDegisim'])),
            hovertemplate='<b>%{customdata[0]}</b><br>Pzt: %{customdata[1]:.4f} ₺  →  Cum: %{customdata[2]:.4f} ₺<br><b style="color:#ff4d6a">%{customdata[3]:.3f}%</b><extra></extra>'
        ))

    fig_hw.add_hline(y=haftalik_esik, line_dash="dash",
                     line_color='rgba(0,212,170,0.45)', line_width=1,
                     annotation_text=f"+{haftalik_esik}%",
                     annotation_font_color='#00d4aa', annotation_font_size=9)
    fig_hw.add_hline(y=-haftalik_esik, line_dash="dash",
                     line_color='rgba(255,77,106,0.45)', line_width=1,
                     annotation_text=f"-{haftalik_esik}%",
                     annotation_font_color='#ff4d6a', annotation_font_size=9)
    fig_hw.add_hline(y=0, line_color='#1e2d4a', line_width=1)

    apply_base(fig_hw, height=540,
               title=dict(text=f"HAFTALIK DEĞİŞİM (Pzt→Cum)  ·  Eşik ±%{haftalik_esik}  ·  Etiket top %{haftalik_etiket}",
                          font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
               yaxis=dict(gridcolor='#131c2e', ticksuffix='%',
                          showspikes=True, spikecolor='#2a4a7a', spikethickness=1, spikedash='dot'),
               xaxis=dict(gridcolor='#131c2e', tickformat='%b %Y',
                          showspikes=True, spikecolor='#2a4a7a', spikethickness=1, spikedash='dot'),
               hovermode='closest',
               legend=dict(bgcolor='rgba(13,18,32,0.9)', bordercolor='#1e2d4a',
                           orientation='h', yanchor='bottom', y=1.01, xanchor='left', x=0))
    st.plotly_chart(fig_hw, use_container_width=True)

    # KPI row
    hf_ort   = hf['HaftaDegisim'].mean()
    hf_maks  = hf['HaftaDegisim'].max()
    hf_mins  = hf['HaftaDegisim'].min()
    hf_pos_n = (hf['HaftaDegisim'] >= haftalik_esik).sum()
    hf_neg_n = (hf['HaftaDegisim'] <= -haftalik_esik).sum()
    sign_hf  = "+" if hf_ort >= 0 else ""
    st.markdown(f"""
    <div class="metric-row" style="grid-template-columns: repeat(5, 1fr);">
      <div class="metric-card" style="border-top:2px solid #4a9eff;">
        <div class="metric-label">Haftalık Ort.</div>
        <div class="metric-value metric-{'pos' if hf_ort>=0 else 'neg'}">{sign_hf}{hf_ort:.3f}%</div>
        <div class="metric-sub">Pzt→Cum ort.</div>
      </div>
      <div class="metric-card" style="border-top:2px solid #00d4aa;">
        <div class="metric-label">≥ +%{haftalik_esik} hafta</div>
        <div class="metric-value metric-pos">{hf_pos_n}</div>
        <div class="metric-sub">pozitif büyük hafta</div>
      </div>
      <div class="metric-card" style="border-top:2px solid #ff4d6a;">
        <div class="metric-label">≤ -%{haftalik_esik} hafta</div>
        <div class="metric-value metric-neg">{hf_neg_n}</div>
        <div class="metric-sub">negatif büyük hafta</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">En İyi Hafta</div>
        <div class="metric-value metric-pos">+{hf_maks:.2f}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">En Kötü Hafta</div>
        <div class="metric-value metric-neg">{hf_mins:.2f}%</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Aylık getiri
    st.markdown('<div class="section-label">◈ Aylık Getiri (21 Gün)</div>', unsafe_allow_html=True)
    col_am1, col_am2 = st.columns(2)
    with col_am1:
        aylik_g = df.dropna(subset=['Aylik_Getiri']).copy()
        aylik_g_filt = aylik_g[aylik_g['Gun_Adi_TR'].isin(aktif_gunler)] if gun_filtre else aylik_g
        aylik_g_filt = aylik_g_filt.copy()
        aylik_g_filt['renk'] = aylik_g_filt['Aylik_Getiri'].apply(lambda x: '#4a9eff' if x >= 0 else '#ff4d6a')
        fig_am = go.Figure()
        fig_am.add_trace(go.Bar(
            x=aylik_g_filt['Tarih'], y=aylik_g_filt['Aylik_Getiri'],
            marker_color=aylik_g_filt['renk'].values, opacity=0.8,
            customdata=aylik_g_filt['Gun_Adi_TR'],
            hovertemplate='%{x|%d.%m.%Y} (%{customdata})<br>21G: <b>%{y:.2f}%</b><extra></extra>'
        ))
        fig_am.add_hline(y=0, line_color='#1e2d4a', line_width=1)
        apply_base(fig_am, height=340,
                   title=dict(text="21 GÜNLÜK (AYLIK) GETİRİ", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   yaxis=dict(gridcolor='#131c2e', ticksuffix='%'),
                   xaxis=dict(gridcolor='#131c2e', tickformat='%b %Y'),
                   showlegend=False)
        st.plotly_chart(fig_am, use_container_width=True)

    with col_am2:
        # Volatilite
        df['Vol_20'] = df['Yuzde_Degisim'].rolling(20).std()
        df['Vol_60'] = df['Yuzde_Degisim'].rolling(60).std()
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=df['Tarih'], y=df['Vol_20'], mode='lines', name='20G Vol',
            line=dict(color='#4a9eff', width=1.5),
            fill='tozeroy', fillcolor='rgba(74,158,255,0.05)',
            hovertemplate='%{x|%d.%m.%Y}<br>20G: <b>%{y:.3f}%</b><extra></extra>'
        ))
        fig_vol.add_trace(go.Scatter(
            x=df['Tarih'], y=df['Vol_60'], mode='lines', name='60G Vol',
            line=dict(color='#ff4d6a', width=1.2, dash='dot'),
            hovertemplate='%{x|%d.%m.%Y}<br>60G: <b>%{y:.3f}%</b><extra></extra>'
        ))
        apply_base(fig_vol, height=340,
                   title=dict(text="YUVARLANMALI VOLATİLİTE", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   yaxis=dict(gridcolor='#131c2e', ticksuffix='%'),
                   xaxis=dict(gridcolor='#131c2e', tickformat='%b %Y'))
        st.plotly_chart(fig_vol, use_container_width=True)

    # ── Yıl-Ay ısı haritası
    st.markdown('<div class="section-label">◈ Yıl–Ay Ortalama Günlük Getiri (Isı Haritası)</div>', unsafe_allow_html=True)
    ay_pivot = df.groupby(['Yil', 'Ay'])['Yuzde_Degisim'].mean().unstack(fill_value=np.nan)
    ay_pivot.columns = [TR_AY.get(c, str(c)) for c in ay_pivot.columns]
    fig_heat = go.Figure(go.Heatmap(
        z=ay_pivot.values,
        x=ay_pivot.columns.tolist(),
        y=ay_pivot.index.astype(str).tolist(),
        colorscale=[[0, '#ff4d6a'], [0.5, '#0d1220'], [1, '#00d4aa']],
        zmid=0,
        text=np.round(ay_pivot.values, 2),
        texttemplate="%{text}%",
        textfont=dict(size=9, family='DM Mono, monospace'),
        hovertemplate='<b>%{y} — %{x}</b><br>Ort. Günlük: <b>%{z:.3f}%</b><extra></extra>',
        colorbar=dict(ticksuffix='%', tickfont=dict(size=9, color='#4a6080'))
    ))
    apply_base(fig_heat, height=500,
               title=dict(text="YIL–AY ORTALAMA GÜNLÜK GETİRİ", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
               xaxis=dict(side='bottom', tickfont=dict(size=11, color='#4a6080')),
               yaxis=dict(tickfont=dict(size=11, color='#4a6080'), autorange='reversed'))
    st.plotly_chart(fig_heat, use_container_width=True)

# ════════════ TAB 3 ════════════
with tab3:
    st.markdown(f'<div class="section-label">◈ Büyük Sıçramalardan Sonra Ne Oluyor? (Tetikleyici: ≥%{fwd_threshold})</div>', unsafe_allow_html=True)

    periods = [1, 5, 10, 21, 63]
    period_labels = {1: '1G', 5: '5G (1Hf)', 10: '10G (2Hf)', 21: '21G (1Ay)', 63: '63G (3Ay)'}
    fwd = forward_analysis(df, fwd_threshold, periods)

    if not fwd:
        st.warning(f"%{fwd_threshold} eşiğinde yeterli sıçrama bulunamadı.")
    else:
        # Summary cards
        st.markdown('<div class="forward-grid">', unsafe_allow_html=True)
        cards_html = ""
        for p in periods:
            if p in fwd:
                r = fwd[p]
                mean_cls = "metric-pos" if r['mean'] >= 0 else "metric-neg"
                sign = "+" if r['mean'] >= 0 else ""
                cards_html += f"""
                <div class="forward-card">
                  <div class="forward-title">{period_labels[p]} Sonra</div>
                  <div class="forward-big {mean_cls}">{sign}{r['mean']:.2f}%</div>
                  <div class="forward-detail">
                    <span style="color:#4a6080">Medyan:</span> <span class="forward-accent">{'+' if r['median']>=0 else ''}{r['median']:.2f}%</span><br>
                    <span style="color:#4a6080">Pozitif oran:</span> <span class="forward-accent">%{r['pos_pct']:.0f}</span><br>
                    <span style="color:#4a6080">IQR:</span> <span class="forward-accent">{r['p25']:.2f}% — {r['p75']:.2f}%</span><br>
                    <span style="color:#4a6080">Örnek sayısı:</span> <span class="forward-accent">{r['n']}</span>
                  </div>
                </div>"""
        st.markdown(f'<div class="forward-grid">{cards_html}</div>', unsafe_allow_html=True)

        # Box plot
        st.markdown('<div class="section-label">◈ Dağılım (Box Plot)</div>', unsafe_allow_html=True)
        fig_box = go.Figure()
        colors = ['#4a9eff', '#00d4aa', '#f6ad55', '#b794f4', '#ff4d6a']
        for i, p in enumerate(periods):
            if p in fwd:
                fig_box.add_trace(go.Box(
                    y=fwd[p]['raw'],
                    name=period_labels[p],
                    marker_color=colors[i],
                    boxpoints='outliers',
                    line_width=1.5,
                    fillcolor=f'rgba({int(colors[i][1:3],16)},{int(colors[i][3:5],16)},{int(colors[i][5:7],16)},0.1)',
                    hovertemplate='%{y:.3f}%<extra></extra>'
                ))
        fig_box.add_hline(y=0, line_color='#1e2d4a', line_width=1, line_dash='dash')
        apply_base(fig_box, height=480,
                   title=dict(text=f"%{fwd_threshold}+ SIÇRAMA SONRASI GETİRİ DAĞILIMI", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   yaxis=dict(gridcolor='#131c2e', ticksuffix='%'),
                   xaxis=dict(gridcolor='#0d1220'))
        st.plotly_chart(fig_box, use_container_width=True)

        # Win-rate bar
        st.markdown('<div class="section-label">◈ Pozitif Kapanış Oranı (Her Dönem)</div>', unsafe_allow_html=True)
        pos_rates = [fwd[p]['pos_pct'] for p in periods if p in fwd]
        period_names = [period_labels[p] for p in periods if p in fwd]
        bar_colors = ['#00d4aa' if v >= 50 else '#ff4d6a' for v in pos_rates]
        fig_win = go.Figure(go.Bar(
            x=period_names, y=pos_rates,
            marker_color=bar_colors,
            text=[f"%{v:.0f}" for v in pos_rates],
            textposition='outside',
            textfont=dict(size=11, color='#c9d4e8', family='DM Mono, monospace'),
            hovertemplate='%{x}<br>Pozitif oran: <b>%{y:.1f}%</b><extra></extra>'
        ))
        fig_win.add_hline(y=50, line_dash='dash', line_color='#2a4a7a', line_width=1,
                          annotation_text="50%", annotation_font_color='#4a6080')
        apply_base(fig_win, height=360,
                   title=dict(text="DÖNEM SONU POZİTİF KAPANIŞ ORANI", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   yaxis=dict(gridcolor='#131c2e', ticksuffix='%', range=[0, 105]),
                   xaxis=dict(gridcolor='#0d1220'),
                   showlegend=False)
        st.plotly_chart(fig_win, use_container_width=True)

        # Threshold sensitivity
        st.markdown('<div class="section-label">◈ Eşik Hassasiyeti (21 Günlük Ort. Getiri vs Tetikleyici Eşik)</div>', unsafe_allow_html=True)
        thresholds = np.arange(1.0, 12.0, 0.5)
        means_21 = []
        pct_pos_21 = []
        counts_21 = []
        for thr in thresholds:
            f = forward_analysis(df, thr, [21])
            if 21 in f and f[21]['n'] >= 5:
                means_21.append(f[21]['mean'])
                pct_pos_21.append(f[21]['pos_pct'])
                counts_21.append(f[21]['n'])
            else:
                means_21.append(np.nan)
                pct_pos_21.append(np.nan)
                counts_21.append(0)

        fig_sens = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sens.add_trace(go.Scatter(
            x=thresholds, y=means_21,
            mode='lines+markers', name='Ort. 21G Getiri',
            line=dict(color='#4a9eff', width=2),
            marker=dict(size=6),
            hovertemplate='Eşik: %{x:.1f}%<br>Ort. 21G: <b>%{y:.2f}%</b><extra></extra>'
        ), secondary_y=False)
        fig_sens.add_trace(go.Bar(
            x=thresholds, y=counts_21,
            name='Örnek Sayısı',
            marker_color='rgba(74,158,255,0.15)',
            hovertemplate='Eşik: %{x:.1f}%<br>n: %{y}<extra></extra>'
        ), secondary_y=True)
        fig_sens.add_hline(y=0, line_color='#1e2d4a', line_width=1)
        fig_sens.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,18,32,0.9)',
            font=dict(color='#c9d4e8', family='DM Sans, sans-serif'),
            height=400,
            title=dict(text="EŞİK HASSASIYETI — 21G ORTALAMA GETİRİ", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
            legend=dict(bgcolor='rgba(13,18,32,0.8)', bordercolor='#1e2d4a'),
            hoverlabel=dict(bgcolor='#0d1220', font_size=12, font_color='#e8f0ff'),
            xaxis=dict(gridcolor='#131c2e', ticksuffix='%', tickfont=dict(size=10, color='#4a6080')),
            yaxis=dict(gridcolor='#131c2e', ticksuffix='%', tickfont=dict(size=10, color='#4a6080')),
            yaxis2=dict(gridcolor='#0d1220', tickfont=dict(size=9, color='#3a5070'), title=dict(text='n', font=dict(color='#3a5070')))
        )
        st.plotly_chart(fig_sens, use_container_width=True)

# ════════════ TAB 4 ════════════
with tab4:
    col_l, col_r = st.columns(2)
    with col_l:
        # Cumulative jump count
        st.markdown('<div class="section-label">◈ Kümülatif Sıçrama Sayısı</div>', unsafe_allow_html=True)
        cum_df = sicramalar.sort_values('Tarih').reset_index(drop=True)
        cum_df['Kumulatif'] = range(1, len(cum_df)+1)
        fig3 = go.Figure(go.Scatter(
            x=cum_df['Tarih'], y=cum_df['Kumulatif'],
            fill='tozeroy', line=dict(color='#4a9eff', width=1.5),
            fillcolor='rgba(74,158,255,0.06)',
            hovertemplate='%{x|%d.%m.%Y}<br>Toplam: <b>%{y}</b> sıçrama<extra></extra>'
        ))
        apply_base(fig3, height=380,
                   title=dict(text="KÜMÜLATİF SIÇRAMA SAYISI", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   xaxis=dict(gridcolor='#131c2e', tickformat='%b %Y'),
                   yaxis=dict(gridcolor='#131c2e'))
        st.plotly_chart(fig3, use_container_width=True)

        # Monthly count
        st.markdown('<div class="section-label">◈ Aylara Göre Sıçrama</div>', unsafe_allow_html=True)
        ay_order_tr = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran',
                       'Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
        sicramalar['Ay_Adi_TR'] = sicramalar['Ay'].map(TR_AY_UZUN)
        ay_sayim = sicramalar.groupby('Ay_Adi_TR').size().reindex(ay_order_tr).fillna(0)
        fig4 = go.Figure(go.Bar(
            x=ay_sayim.index, y=ay_sayim.values,
            marker=dict(color=ay_sayim.values, colorscale=[[0,'#1e2d4a'],[1,'#4a9eff']],
                        line=dict(color='rgba(255,255,255,0.05)', width=1)),
            hovertemplate='<b>%{x}</b><br>%{y} sıçrama<extra></extra>'
        ))
        apply_base(fig4, height=350,
                   title=dict(text="AYLARA GÖRE SIÇRAMA SAYISI", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   xaxis=dict(gridcolor='#131c2e', tickfont=dict(size=10, color='#4a6080')),
                   yaxis=dict(gridcolor='#131c2e'),
                   showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    with col_r:
        # Distribution histogram
        st.markdown('<div class="section-label">◈ Büyüklük Dağılımı</div>', unsafe_allow_html=True)
        fig7 = go.Figure()
        fig7.add_trace(go.Histogram(
            x=sicramalar[sicramalar['Yuzde_Degisim']>0]['Yuzde_Degisim'],
            nbinsx=25, name='↑ Pozitif', marker_color='#00d4aa', opacity=0.7,
            hovertemplate='%{x:.1f}% — %{y} adet<extra></extra>'
        ))
        fig7.add_trace(go.Histogram(
            x=sicramalar[sicramalar['Yuzde_Degisim']<0]['Yuzde_Degisim'],
            nbinsx=25, name='↓ Negatif', marker_color='#ff4d6a', opacity=0.7,
            hovertemplate='%{x:.1f}% — %{y} adet<extra></extra>'
        ))
        apply_base(fig7, height=380, barmode='overlay',
                   title=dict(text="SIÇRAMA BÜYÜKLÜKLERİ DAĞILIMI", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   xaxis=dict(gridcolor='#131c2e', ticksuffix='%'),
                   yaxis=dict(gridcolor='#131c2e'))
        st.plotly_chart(fig7, use_container_width=True)

        # Year-month heatmap
        st.markdown('<div class="section-label">◈ Yıl–Ay Yoğunluk Haritası</div>', unsafe_allow_html=True)
        pivot = sicramalar.groupby(['Yil','Ay']).size().unstack(fill_value=0)
        ay_labels = [TR_AY.get(c, str(c)) for c in pivot.columns]
        fig8 = go.Figure(go.Heatmap(
            z=pivot.values, x=ay_labels, y=pivot.index.astype(str),
            colorscale=[[0,'#0d1220'],[0.5,'#1b6cf2'],[1,'#00d4aa']],
            text=pivot.values, texttemplate="%{text}",
            textfont=dict(size=9, color='#e8f0ff', family='DM Mono, monospace'),
            hovertemplate='<b>%{y} — %{x}</b><br>%{z} sıçrama<extra></extra>',
            colorbar=dict(tickfont=dict(size=9, color='#4a6080'))
        ))
        apply_base(fig8, height=350,
                   title=dict(text="YIL–AY SIÇRAMA YOĞUNLUĞU", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
                   xaxis=dict(side='bottom', tickfont=dict(size=11, color='#4a6080')),
                   yaxis=dict(tickfont=dict(size=11, color='#4a6080'), autorange='reversed'))
        st.plotly_chart(fig8, use_container_width=True)

    # Weekday pattern
    st.markdown('<div class="section-label">◈ Haftalık Pattern</div>', unsafe_allow_html=True)
    gun_order_tr = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar']
    sicramalar['Gun_Adi_TR'] = sicramalar['Gun_Adi'].map(TR_GUN)
    gun_sayim = sicramalar.groupby('Gun_Adi_TR').size().reindex(gun_order_tr).fillna(0)
    fig5 = go.Figure(go.Bar(
        x=gun_sayim.index, y=gun_sayim.values,
        marker=dict(color=gun_sayim.values, colorscale=[[0,'#1e2d4a'],[1,'#b794f4']],
                    line=dict(color='rgba(255,255,255,0.05)', width=1)),
        hovertemplate='<b>%{x}</b><br>%{y} sıçrama<extra></extra>'
    ))
    apply_base(fig5, height=340,
               title=dict(text="HAFTANIN GÜNLERİNE GÖRE SIÇRAMA SAYISI", font=dict(size=11, color='#4a6080', family='DM Mono, monospace'), x=0),
               xaxis=dict(gridcolor='#131c2e'),
               yaxis=dict(gridcolor='#131c2e'),
               showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

# ════════════ TAB 5 ════════════
with tab5:
    st.markdown('<div class="section-label">◈ Sıçrama Tablosu</div>', unsafe_allow_html=True)
    tbl = top_sic.copy().reset_index(drop=True)
    tbl.index = tbl.index + 1
    tbl_show = pd.DataFrame({
        '#':           tbl.index,
        'Tarih':       tbl['Tarih'].dt.strftime('%d.%m.%Y'),
        'Yıl':         tbl['Yil'],
        'Ay':          tbl['Ay_Adi'],
        'Gün Adı':     tbl['Gun_Adi'],
        'Kur':         tbl['Dolar_Kuru'].round(4),
        'Önceki Kur':  tbl['Onceki_Kur'].round(4),
        'Değişim %':   tbl['Yuzde_Degisim'].round(3),
        'TL Δ':        tbl['TL_Degisim'].round(4),
        'Gün Farkı':   tbl['Gun_Farki'].astype(int),
    })
    st.dataframe(tbl_show, use_container_width=True, height=420)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">◈ Aylık Özet</div>', unsafe_allow_html=True)
        aylik = sicramalar.groupby('Ay_Adi')['Abs_Degisim'].agg(['count','mean','max','min']).round(3)
        aylik.columns = ['Toplam','Ort. %','Maks %','Min %']
        st.dataframe(aylik, use_container_width=True)
    with c2:
        st.markdown('<div class="section-label">◈ Yıllık Özet</div>', unsafe_allow_html=True)
        yillik = sicramalar.groupby('Yil').agg(
            Toplam=('Abs_Degisim','count'),
            Ort_Pct=('Abs_Degisim','mean'),
            Pozitif=('Yuzde_Degisim', lambda x: (x>0).sum()),
            Negatif=('Yuzde_Degisim', lambda x: (x<0).sum()),
            Maks=('Abs_Degisim','max')
        ).round(3)
        yillik.columns = ['Toplam','Ort. %','Pozitif','Negatif','Maks %']
        st.dataframe(yillik, use_container_width=True)

    # Downloads
    st.markdown('<div class="section-label">◈ Dışa Aktar</div>', unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        csv = top_sic.to_csv(index=False).encode('utf-8-sig')
        st.download_button("CSV İndir", csv, "sicramalar.csv", "text/csv")
    with dc2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            top_sic.to_excel(w, sheet_name='Sicramalar', index=False)
            df.to_excel(w, sheet_name='Tum_Veri', index=False)
            aylik.to_excel(w, sheet_name='Aylik')
            yillik.to_excel(w, sheet_name='Yillik')
        st.download_button("Excel İndir (Tüm Analiz)", buf.getvalue(), "usdtry_analiz.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Footer
st.markdown("""
<div style="text-align:center; color:#1e2d4a; font-size:0.7rem; padding:30px 0 10px 0;
            border-top:1px solid #0d1220; margin-top:30px;
            font-family:'DM Mono',monospace; letter-spacing:0.1em;">
    USDTRY ANALYSIS PLATFORM · STREAMLIT + PLOTLY
</div>
""", unsafe_allow_html=True)
