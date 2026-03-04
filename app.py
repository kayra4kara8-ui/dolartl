import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, date
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
html, body, .stApp { background: #080c14; color: #c9d4e8; }
.stApp { background: #080c14; }
section[data-testid="stSidebar"] { background: #0d1220 !important; border-right: 1px solid #1e2d4a; }
section[data-testid="stSidebar"] * { color: #c9d4e8; }
.stButton > button {
    background: linear-gradient(135deg, #1b6cf2, #0f4abf); color: white; border: none;
    border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 0.8rem;
    letter-spacing: 0.05em; padding: 0.5rem 1.2rem; transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(27,108,242,0.4); }
.stDownloadButton > button {
    background: transparent; color: #4a9eff; border: 1px solid #1e2d4a;
    border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 0.8rem;
}
.stDownloadButton > button:hover { border-color: #4a9eff; background: rgba(74,158,255,0.05); }
.metric-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 16px 0; }
.metric-card {
    background: #0d1220; border: 1px solid #1e2d4a; border-radius: 10px;
    padding: 18px 16px; position: relative; overflow: hidden; transition: border-color 0.2s;
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #1b6cf2, #00d4aa);
}
.metric-card:hover { border-color: #2a4a7a; }
.metric-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #4a6080; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 10px; }
.metric-value { font-family: 'DM Mono', monospace; font-size: 1.5rem; font-weight: 500; color: #e8f0ff; line-height: 1; margin-bottom: 6px; }
.metric-sub { font-size: 0.72rem; color: #3a5070; }
.metric-pos { color: #00d4aa !important; }
.metric-neg { color: #ff4d6a !important; }
.metric-neu { color: #4a9eff !important; }
.section-label {
    font-family: 'DM Mono', monospace; font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.15em; color: #4a6080; padding: 24px 0 8px 0;
    border-bottom: 1px solid #1e2d4a; margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, #1e2d4a, transparent); }
.jump-card {
    background: #0d1220; border: 1px solid #1e2d4a; border-radius: 8px; padding: 14px;
    transition: all 0.2s; position: relative; overflow: hidden;
}
.jump-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.5); border-color: #2a4a7a; }
.jump-card.pos { border-top: 2px solid #00d4aa; }
.jump-card.neg { border-top: 2px solid #ff4d6a; }
.jump-rank { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #3a5070; margin-bottom: 8px; }
.jump-date { font-family: 'DM Mono', monospace; font-size: 0.85rem; color: #c9d4e8; margin-bottom: 4px; }
.jump-pct { font-family: 'DM Mono', monospace; font-size: 1.6rem; font-weight: 500; line-height: 1.1; }
.jump-pct.pos { color: #00d4aa; }
.jump-pct.neg { color: #ff4d6a; }
.jump-meta { font-size: 0.7rem; color: #3a5070; margin-top: 6px; font-family: 'DM Mono', monospace; }
.forward-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 12px 0; }
.forward-card { background: #0d1220; border: 1px solid #1e2d4a; border-radius: 8px; padding: 16px; }
.forward-title { font-family: 'DM Mono', monospace; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: #4a6080; margin-bottom: 10px; }
.forward-big { font-family: 'DM Mono', monospace; font-size: 1.3rem; font-weight: 500; color: #e8f0ff; margin-bottom: 4px; }
.forward-detail { font-size: 0.72rem; color: #3a5070; line-height: 1.6; }
.forward-accent { color: #4a9eff; }
.api-box {
    background: #0d1220; border: 1px solid #1e2d4a; border-radius: 10px;
    padding: 20px; margin: 8px 0;
}
.api-status-ok   { color: #00d4aa; font-family: 'DM Mono', monospace; font-size: 0.75rem; }
.api-status-err  { color: #ff4d6a; font-family: 'DM Mono', monospace; font-size: 0.75rem; }
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #1e2d4a; }
#MainMenu, footer { visibility: hidden; }
.stTabs [data-baseweb="tab-list"] { background: #0d1220; border-bottom: 1px solid #1e2d4a; gap: 0; }
.stTabs [data-baseweb="tab"] { font-family: 'DM Mono', monospace; font-size: 0.75rem; letter-spacing: 0.1em; color: #4a6080; padding: 12px 24px; background: transparent; border: none; text-transform: uppercase; }
.stTabs [aria-selected="true"] { color: #4a9eff !important; border-bottom: 2px solid #4a9eff !important; background: transparent !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 16px 0; background: transparent; }
.stTabs [data-baseweb="tab-border"] { display: none; }
.stSlider [data-baseweb="slider"] { color: #1b6cf2; }
.stSelectbox [data-baseweb="select"] { background: #0d1220; border: 1px solid #1e2d4a; border-radius: 6px; }
.stRadio label { font-size: 0.85rem !important; }
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

LEGEND_RIGHT = dict(
    bgcolor='rgba(13,18,32,0.9)', bordercolor='#1e2d4a', borderwidth=1,
    font=dict(size=11), orientation='v', x=1.01, xanchor='left', y=0.5, yanchor='middle',
)

# Seri seçenekleri
SERILER = {
    "USD Satış (TP.DK.USD.S.YTL)": "TP.DK.USD.S.YTL",
    "USD Alış (TP.DK.USD.A.YTL)":  "TP.DK.USD.A.YTL",
    "EUR Satış (TP.DK.EUR.S.YTL)": "TP.DK.EUR.S.YTL",
    "EUR Alış (TP.DK.EUR.A.YTL)":  "TP.DK.EUR.A.YTL",
}

def tr_fmt_kur(val, decimals=4):
    try:
        return f"{float(val):.{decimals}f}".replace('.', ',')
    except Exception:
        return str(val)

def tr_fmt_pct(val, decimals=3):
    try:
        v = float(val)
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.{decimals}f}".replace('.', ',') + "%"
    except Exception:
        return str(val)

def fkur(v, decimals=4):
    return tr_fmt_kur(v, decimals)

def fpct(v, decimals=3, sign=False):
    try:
        s = "+" if sign and float(v) >= 0 else ""
        return f"{s}{float(v):.{decimals}f}".replace('.', ',') + "%"
    except Exception:
        return str(v)

def safe_ticks(vmin, vmax, n=8, decimals=2, suffix='', is_kur=False):
    try:
        vmin, vmax = float(vmin), float(vmax)
        if not (np.isfinite(vmin) and np.isfinite(vmax)):
            return None, None
        if vmax <= vmin:
            vmax = vmin + 1.0
        raw_step = (vmax - vmin) / max(n, 1)
        if raw_step <= 0 or not np.isfinite(raw_step):
            return None, None
        mag  = 10 ** np.floor(np.log10(raw_step))
        step = np.ceil(raw_step / mag) * mag
        if step <= 0 or not np.isfinite(step):
            return None, None
        ticks = np.arange(np.floor(vmin / step) * step, vmax + step * 1.05, step)
        ticks = ticks[np.isfinite(ticks)]
        if len(ticks) == 0:
            return None, None
        if is_kur:
            texts = [f"{f'{v:.{decimals}f}'.replace('.', ',')} ₺" for v in ticks]
        else:
            texts = [f"{f'{v:.{decimals}f}'.replace('.', ',')}{suffix}" for v in ticks]
        return ticks.tolist(), texts
    except Exception:
        return None, None

def yt(tv, tt, extra=None):
    d = dict(extra or {})
    if tv:
        d["tickvals"] = tv
        d["ticktext"] = tt
    return d

PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,18,32,0.9)',
    font=dict(color='#c9d4e8', family='DM Sans, sans-serif'),
    hoverlabel=dict(bgcolor='#0d1220', font_size=12, font_color='#e8f0ff', bordercolor='#2a4a7a'),
    xaxis=dict(gridcolor='#131c2e', gridwidth=1, tickfont=dict(size=10, color='#4a6080'), zeroline=False),
    yaxis=dict(gridcolor='#131c2e', gridwidth=1, tickfont=dict(size=10, color='#4a6080'), zeroline=False),
    legend=LEGEND_RIGHT,
    margin=dict(l=50, r=120, t=50, b=40),
)

def apply_base(fig, **kwargs):
    cfg = {**PLOTLY_BASE, **kwargs}
    for k in ['xaxis', 'yaxis', 'font', 'hoverlabel', 'legend', 'margin']:
        if k in kwargs:
            cfg[k] = {**PLOTLY_BASE.get(k, {}), **kwargs[k]}
    fig.update_layout(**cfg)
    return fig

# ─── EVDS API ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def evds_cek(api_key: str, seri: str, baslangic: str, bitis: str):
    """EVDS'den veri çek, (df, hata_mesaji) döndür."""
    url = (
        f"https://evds2.tcmb.gov.tr/service/evds/"
        f"series={seri}"
        f"&startDate={baslangic}"
        f"&endDate={bitis}"
        f"&type=json"
        f"&frequency=1"
    )
    try:
        r = requests.get(url, headers={"key": api_key}, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        return None, "EVDS bağlantısı zaman aşımına uğradı (30s)."
    except requests.exceptions.ConnectionError:
        return None, "EVDS'e bağlanılamadı. İnternet bağlantınızı kontrol edin."
    except Exception as e:
        return None, f"API hatası: {e}"

    items = data.get("items", [])
    if not items:
        return None, "API boş yanıt döndürdü. API anahtarını ve seri kodunu kontrol edin."

    # Seri kodundaki noktaları alt çizgiye çevir (JSON key formatı)
    col_key = seri.replace(".", "_")
    records = []
    for it in items:
        tarih = it.get("Tarih", "")
        deger = it.get(col_key, None)
        if tarih and deger and deger not in ("", None):
            records.append({"Tarih": tarih, "Dolar_Kuru": deger})

    if not records:
        return None, f"Veri bulunamadı. Seri: {seri}, anahtar sütun: {col_key}"

    df = pd.DataFrame(records)
    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d-%m-%Y", errors="coerce")
    df = df.dropna(subset=["Tarih"])
    df["Dolar_Kuru"] = pd.to_numeric(
        df["Dolar_Kuru"].astype(str).str.replace(",", "."), errors="coerce"
    )
    df = df.dropna(subset=["Dolar_Kuru"])
    df = df.sort_values("Tarih").reset_index(drop=True)
    return df, None

def veri_isle(df_raw):
    df = df_raw.copy()

    # Aykırı değer düzeltme (eski TL → YTL)
    medyan = df["Dolar_Kuru"].median()
    if medyan > 0:
        aykiri = (df["Dolar_Kuru"] > medyan * 10) | (df["Dolar_Kuru"] < medyan / 10)
        if aykiri.any():
            df.loc[aykiri, "Dolar_Kuru"] = df.loc[aykiri, "Dolar_Kuru"] / 1000

    df["Onceki_Kur"]    = df["Dolar_Kuru"].shift(1)
    df["Onceki_Tarih"]  = df["Tarih"].shift(1)
    df["Gun_Farki"]     = (df["Tarih"] - df["Onceki_Tarih"]).dt.days
    df["Yuzde_Degisim"] = (df["Dolar_Kuru"] / df["Onceki_Kur"] - 1) * 100
    df["TL_Degisim"]    = df["Dolar_Kuru"] - df["Onceki_Kur"]
    df = df.dropna()

    df["Yil"]         = df["Tarih"].dt.year
    df["Ay"]          = df["Tarih"].dt.month
    df["Gun"]         = df["Tarih"].dt.day
    df["Ay_Adi"]      = df["Tarih"].dt.strftime("%B")
    df["Gun_Adi"]     = df["Tarih"].dt.strftime("%A")
    df["Abs_Degisim"] = df["Yuzde_Degisim"].abs()

    df_idx = df.set_index("Tarih")
    df["Haftalik_Getiri"] = df_idx["Dolar_Kuru"].pct_change(5).values * 100
    df["Aylik_Getiri"]    = df_idx["Dolar_Kuru"].pct_change(21).values * 100
    df["3Ay_Getiri"]      = df_idx["Dolar_Kuru"].pct_change(63).values * 100

    df["Hover_Tarih"] = df.apply(
        lambda r: f"{int(r['Tarih'].day)} {TR_AY_UZUN.get(r['Tarih'].month,'')} {int(r['Tarih'].year)}", axis=1)
    df["_kur_str"]     = df["Dolar_Kuru"].apply(tr_fmt_kur)
    df["_onc_kur_str"] = df["Onceki_Kur"].apply(tr_fmt_kur)
    df["_pct_str"]     = df["Yuzde_Degisim"].apply(tr_fmt_pct)
    return df

def forward_analysis(df, threshold, periods):
    events  = df[df["Abs_Degisim"] >= threshold].copy()
    results = {}
    for p in periods:
        changes = []
        for idx in events.index:
            future_idx = idx + p
            if future_idx < len(df):
                fwd = (df.loc[future_idx, "Dolar_Kuru"] / df.loc[idx, "Dolar_Kuru"] - 1) * 100
                changes.append(fwd)
        if changes:
            arr = np.array(changes)
            results[p] = {
                "mean": np.mean(arr), "median": np.median(arr),
                "pos_pct": (arr > 0).mean() * 100,
                "p25": np.percentile(arr, 25), "p75": np.percentile(arr, 75),
                "n": len(arr), "raw": arr.tolist()
            }
    return results

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 8px 0 4px 0;">
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                letter-spacing:0.2em; color:#1b6cf2; margin-bottom:6px;">
        ◈ USDTRY · GÜNLÜK SIÇRAMA & İLERİ ANALİZ
    </div>
    <h1 style="font-size:2rem; font-weight:700; color:#e8f0ff; margin:0; line-height:1.1; letter-spacing:-0.02em;">
        Dolar Kuru Analiz Platformu
    </h1>
    <p style="color:#3a5070; font-size:0.85rem; margin:6px 0 0 0;">
        EVDS API · Günlük sıçramaları keşfedin · Haftalık & aylık trendleri takip edin · İleri dönem etkisini analiz edin
    </p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── API Ayarları
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:16px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ EVDS API</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    api_key = st.text_input(
        "API Anahtarı", value="EDS05ZLAlI",
        type="password",
        help="evds2.tcmb.gov.tr → Kullanıcı Paneli → API Anahtarı"
    )
    seri_sec = st.selectbox("Seri", list(SERILER.keys()), index=0)
    seri_kod = SERILER[seri_sec]

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        bas_tarih = st.date_input("Başlangıç", value=date(2003, 1, 1), min_value=date(1990, 1, 1))
    with col_d2:
        bit_tarih = st.date_input("Bitiş", value=date.today())

    bas_str = bas_tarih.strftime("%d-%m-%Y")
    bit_str = bit_tarih.strftime("%d-%m-%Y")

    veri_cek_btn = st.button("◈ Veriyi Çek", use_container_width=True)

    # ── Analiz Parametreleri
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ Parametre Kontrolü</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    esik            = st.slider("Günlük Sıçrama Eşiği (%)", 0.5, 10.0, 2.0, 0.1)
    gosterim_sec    = st.selectbox("Gösterilecek Sıçrama Sayısı", [10,20,30,50,75,100,"Tümü"], index=2)
    yon             = st.radio("Sıçrama Yönü", ["Tümü","Yalnız Pozitif ↑","Yalnız Negatif ↓"])
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ Etiket Ayarı</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    etiket_quantile = st.slider("Günlük — Etiketlenecek Dilim (%)", 10, 100, 40, 5)
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ Haftalık / Gün Analizi</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    haftalik_esik   = st.slider("Haftalık Sıçrama Eşiği (%)", 0.0, 20.0, 3.0, 0.5)
    haftalik_etiket = st.slider("Haftalık — Etiketlenecek Dilim (%)", 10, 100, 40, 5)
    haftalik_yon    = st.radio("Haftalık Yön", ["Tümü","Yalnız Pozitif ↑","Yalnız Negatif ↓"], key="haftalik_yon")
    gun_filtre      = st.multiselect("Gün Filtresi", ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma"], default=[])
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ İleri Analiz</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    fwd_threshold   = st.slider("Tetikleyici Eşik (%)", 0.5, 15.0, 3.0, 0.5)

# ─── STATE & VERİ ÇEKME ───────────────────────────────────────────────────────
if "df_raw" not in st.session_state:
    st.session_state.df_raw   = None
    st.session_state.df       = None
    st.session_state.api_info = None   # (seri, bas, bit, n_row)
    st.session_state.api_err  = None

if veri_cek_btn:
    if not api_key.strip():
        st.session_state.api_err = "API anahtarı boş olamaz."
    else:
        with st.spinner("EVDS'den veri çekiliyor..."):
            df_raw, hata = evds_cek(api_key.strip(), seri_kod, bas_str, bit_str)
        if hata:
            st.session_state.api_err  = hata
            st.session_state.df_raw   = None
            st.session_state.df       = None
        else:
            st.session_state.api_err  = None
            st.session_state.df_raw   = df_raw
            st.session_state.df       = veri_isle(df_raw)
            st.session_state.api_info = (seri_sec, bas_str, bit_str, len(df_raw))

# ─── BEKLEME EKRANI ───────────────────────────────────────────────────────────
if st.session_state.df is None:
    if st.session_state.api_err:
        st.error(f"⚠ {st.session_state.api_err}")

    st.markdown(f"""
    <div style="background:#0d1220;border:1px dashed #1e2d4a;border-radius:12px;
                padding:60px 40px;text-align:center;margin:40px auto;max-width:600px;">
        <div style="font-size:3rem;margin-bottom:16px;">◈</div>
        <div style="font-family:'DM Mono',monospace;font-size:1rem;color:#4a9eff;margin-bottom:8px;">
            EVDS API ile Veri Çekin
        </div>
        <div style="font-size:0.85rem;color:#3a5070;line-height:1.8;">
            Sol panelde API anahtarınızı girin<br>
            Seri ve tarih aralığını seçin<br>
            <strong style="color:#4a9eff;">◈ Veriyi Çek</strong> butonuna tıklayın<br><br>
            <span style="color:#2a4a7a;font-size:0.75rem;">
                Varsayılan: {SERILER[seri_sec]}<br>
                {bas_str} → {bit_str}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = st.session_state.df

# API bilgi bandı
if st.session_state.api_info:
    seri_label, bas_s, bit_s, n_row = st.session_state.api_info
    guncelleme = datetime.now().strftime("%d.%m.%Y %H:%M")
    st.markdown(f"""
    <div style="background:#0a1020;border:1px solid #1b3a6a;border-radius:8px;
                padding:10px 16px;margin-bottom:12px;display:flex;align-items:center;gap:24px;
                font-family:'DM Mono',monospace;font-size:0.7rem;">
        <span style="color:#1b6cf2;">◈ EVDS</span>
        <span style="color:#4a6080;">{seri_label}</span>
        <span style="color:#2a4a7a;">{bas_s} → {bit_s}</span>
        <span style="color:#00d4aa;">{n_row:,} gün</span>
        <span style="color:#2a4a7a;margin-left:auto;">Çekilme: {guncelleme}</span>
    </div>
    """, unsafe_allow_html=True)

# ─── FİLTRELEME ──────────────────────────────────────────────────────────────
if yon == "Yalnız Pozitif ↑":
    sicramalar = df[df["Yuzde_Degisim"] >= esik].copy()
elif yon == "Yalnız Negatif ↓":
    sicramalar = df[df["Yuzde_Degisim"] <= -esik].copy()
else:
    sicramalar = df[df["Abs_Degisim"] >= esik].copy()

sicramalar = sicramalar.sort_values("Abs_Degisim", ascending=False)
top_sic    = sicramalar.head(int(gosterim_sec)) if gosterim_sec != "Tümü" else sicramalar.copy()
pos_j      = top_sic[top_sic["Yuzde_Degisim"] > 0].copy()
neg_j      = top_sic[top_sic["Yuzde_Degisim"] < 0].copy()

poz_say = (df["Yuzde_Degisim"] > 0).sum()
neg_say = (df["Yuzde_Degisim"] < 0).sum()
oran    = len(sicramalar) / len(df) * 100
max_j   = df["Yuzde_Degisim"].max()
min_j   = df["Yuzde_Degisim"].min()

# KPI CARDS
st.markdown('<div class="section-label">◈ Genel İstatistikler</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card"><div class="metric-label">Toplam Gün</div>
    <div class="metric-value metric-neu">{len(df):,}</div>
    <div class="metric-sub">{df['Tarih'].min().year} – {df['Tarih'].max().year}</div></div>
  <div class="metric-card"><div class="metric-label">Ort. Günlük Değ.</div>
    <div class="metric-value">{fpct(df['Yuzde_Degisim'].mean(),3)}</div>
    <div class="metric-sub">std ± {fpct(df['Yuzde_Degisim'].std(),3)}</div></div>
  <div class="metric-card"><div class="metric-label">Pozitif / Negatif</div>
    <div class="metric-value"><span class="metric-pos">{poz_say}</span> <span style="color:#1e2d4a">/</span> <span class="metric-neg">{neg_say}</span></div>
    <div class="metric-sub">gün</div></div>
  <div class="metric-card"><div class="metric-label">Toplam Sıçrama (≥%{esik})</div>
    <div class="metric-value metric-neu">{len(sicramalar):,}</div>
    <div class="metric-sub">günlerin {fpct(oran,1)}'i</div></div>
  <div class="metric-card"><div class="metric-label">En Büyük / En Küçük</div>
    <div class="metric-value"><span class="metric-pos">+{fpct(max_j,2)}</span></div>
    <div class="metric-sub"><span class="metric-neg">{fpct(min_j,2)}</span></div></div>
</div>
""", unsafe_allow_html=True)

# HAFTALIK VERİ (global)
df["ISOYil"]   = df["Tarih"].dt.isocalendar().year.astype(int)
df["ISOHafta"] = df["Tarih"].dt.isocalendar().week.astype(int)
_hf_ilk = df.groupby(["ISOYil","ISOHafta"]).agg(PztTarih=("Tarih","min"), PztKur=("Dolar_Kuru","first")).reset_index()
_hf_son = df.groupby(["ISOYil","ISOHafta"]).agg(CumTarih=("Tarih","max"), CumKur=("Dolar_Kuru","last")).reset_index()
hf_global = _hf_ilk.merge(_hf_son, on=["ISOYil","ISOHafta"])
hf_global["HaftaDegisim"] = (hf_global["CumKur"] / hf_global["PztKur"] - 1) * 100
hf_global["XTarih"]       = hf_global["CumTarih"]
hf_global["Aralik"]       = hf_global["PztTarih"].dt.strftime("%d.%m") + "–" + hf_global["CumTarih"].dt.strftime("%d.%m.%y")
hf_global["AbsDegisim"]   = hf_global["HaftaDegisim"].abs()
hf_global = hf_global.dropna(subset=["HaftaDegisim"]).reset_index(drop=True)
hf_global["_pzt_str"] = hf_global["PztKur"].apply(tr_fmt_kur)
hf_global["_cum_str"] = hf_global["CumKur"].apply(tr_fmt_kur)
hf_global["_hf_str"]  = hf_global["HaftaDegisim"].apply(tr_fmt_pct)

# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "GÜNLÜK ANALİZ", "HAFTALIK & AYLIK", "İLERİ ANALİZ", "DAĞILIM & ISITMA", "TABLOLAR"
])

# ════════════ TAB 1 ════════════
with tab1:
    st.markdown('<div class="section-label">◈ Dolar Kuru & Sıçrama Noktaları</div>', unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df["Tarih"], y=df["Dolar_Kuru"], mode="lines", name="USD/TRY",
        line=dict(color="#2a4a7a", width=1.5),
        customdata=list(zip(df["Hover_Tarih"], df["_kur_str"])),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} ₺<extra></extra>"
    ))
    for subset, color, name, tpl_color in [
        (pos_j, "#00d4aa", "↑ Pozitif", "#00d4aa"),
        (neg_j, "#ff4d6a", "↓ Negatif", "#ff4d6a"),
    ]:
        if len(subset) == 0:
            continue
        s = subset.copy()
        s["_h"]   = s.apply(lambda r: f"{int(r['Tarih'].day)} {TR_AY_UZUN.get(r['Tarih'].month,'')} {int(r['Tarih'].year)}", axis=1)
        s["_k"]   = s["Dolar_Kuru"].apply(tr_fmt_kur)
        s["_ok"]  = s["Onceki_Kur"].apply(tr_fmt_kur)
        s["_pct"] = s["Yuzde_Degisim"].apply(tr_fmt_pct)
        fig1.add_trace(go.Scatter(
            x=s["Tarih"], y=s["Dolar_Kuru"], mode="markers", name=name,
            marker=dict(color=color, size=s["Abs_Degisim"]*2.5, line=dict(color=color, width=3), opacity=0.9),
            customdata=list(zip(s["_h"], s["_pct"], s["_ok"], s["_k"])),
            hovertemplate=f'<b>%{{customdata[0]}}</b><br>%{{customdata[3]}} ₺ ← %{{customdata[2]}} ₺<br><b style="color:{tpl_color}">%{{customdata[1]}}</b><extra></extra>'
        ))
    tv_k, tt_k = safe_ticks(df["Dolar_Kuru"].min(), df["Dolar_Kuru"].max(), n=8, decimals=2, is_kur=True)
    apply_base(fig1, height=560,
        title=dict(text=f"USD/TRY  ·  Eşik %{esik}  ·  Top {gosterim_sec}", font=dict(size=13, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y", tickfont=dict(size=10, color="#4a6080"),
                   showspikes=True, spikecolor="#2a4a7a", spikethickness=1, spikedash="dot"),
        yaxis={**yt(tv_k, tt_k, {"gridcolor":"#131c2e","tickfont":dict(size=10,color="#4a6080"),
               "showspikes":True,"spikecolor":"#2a4a7a","spikethickness":1,"spikedash":"dot"})},
        hovermode="closest")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown('<div class="section-label">◈ Günlük Değişim</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["Tarih"], y=df["Yuzde_Degisim"], mode="lines", name="Günlük Δ",
        line=dict(color="#2a4a7a", width=1), opacity=0.6,
        customdata=list(zip(df["Hover_Tarih"], df["_pct_str"])),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"
    ))
    for subset, color, name, is_pos, tpl_color, tpos, sym in [
        (pos_j, "#00d4aa", "↑ Pozitif", True,  "#00d4aa", "top right",    "triangle-up"),
        (neg_j, "#ff4d6a", "↓ Negatif", False, "#ff4d6a", "bottom right", "triangle-down"),
    ]:
        if len(subset) == 0:
            continue
        s = subset.copy()
        s["_k"]   = s["Dolar_Kuru"].apply(tr_fmt_kur)
        s["_ok"]  = s["Onceki_Kur"].apply(tr_fmt_kur)
        s["_pct"] = s["Yuzde_Degisim"].apply(tr_fmt_pct)
        ethr = s["Yuzde_Degisim"].quantile(1 - etiket_quantile/100) if is_pos else s["Yuzde_Degisim"].quantile(etiket_quantile/100)
        cond_fn = (lambda r, t=ethr: r["Yuzde_Degisim"] >= t) if is_pos else (lambda r, t=ethr: r["Yuzde_Degisim"] <= t)
        s["_lbl"] = s.apply(lambda r: f"{r['Tarih'].strftime('%d.%m.%y')} {tr_fmt_pct(r['Yuzde_Degisim'],1)}" if cond_fn(r) else "", axis=1)
        fig2.add_trace(go.Scatter(
            x=s["Tarih"], y=s["Yuzde_Degisim"], mode="markers+text", name=name,
            marker=dict(color=color, size=s["Abs_Degisim"]*1.8+5, symbol=sym,
                        line=dict(color=color, width=1), opacity=0.9),
            text=s["_lbl"], textposition=tpos,
            textfont=dict(size=8, color=color, family="DM Mono, monospace"),
            customdata=list(zip(s["Hover_Tarih"], s["_ok"], s["_k"], s["_pct"])),
            hovertemplate=f'<b>%{{customdata[0]}}</b><br>%{{customdata[1]}} → %{{customdata[2]}} ₺<br><b style="color:{tpl_color}">%{{customdata[3]}}</b><extra></extra>'
        ))
    tv_p, tt_p = safe_ticks(df["Yuzde_Degisim"].min(), df["Yuzde_Degisim"].max(), n=10, decimals=1, suffix="%")
    esik_str = str(esik).replace(".", ",")
    fig2.add_hline(y=esik,  line_dash="dash", line_color="rgba(0,212,170,0.5)",  line_width=1,
                   annotation_text=f"+{esik_str}%", annotation_font_color="#00d4aa", annotation_font_size=10)
    fig2.add_hline(y=-esik, line_dash="dash", line_color="rgba(255,77,106,0.5)", line_width=1,
                   annotation_text=f"−{esik_str}%", annotation_font_color="#ff4d6a", annotation_font_size=10)
    fig2.add_hline(y=0, line_color="#2a4a7a", line_width=1)
    apply_base(fig2, height=500,
        title=dict(text=f"GÜNLÜK DEĞİŞİM  ·  Eşik ±%{esik}  ·  Etiket top %{etiket_quantile}",
                   font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y", tickfont=dict(size=10, color="#4a6080"),
                   showspikes=True, spikecolor="#2a4a7a", spikethickness=1, spikedash="dot"),
        yaxis={**yt(tv_p, tt_p, {"gridcolor":"#131c2e","tickfont":dict(size=10,color="#4a6080")})},
        hovermode="closest")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-label">◈ En Büyük 10 Sıçrama</div>', unsafe_allow_html=True)
    top10 = sicramalar.head(10)
    for row_df in [top10.iloc[:5], top10.iloc[5:10]]:
        cols = st.columns(5)
        for i, (_, r) in enumerate(row_df.iterrows()):
            is_pos = r["Yuzde_Degisim"] > 0
            sign   = "+" if is_pos else ""
            icon   = "↑" if is_pos else "↓"
            global_rank = list(top10.index).index(r.name) + 1
            with cols[i]:
                st.markdown(f"""
                <div class="jump-card {'pos' if is_pos else 'neg'}">
                  <div class="jump-rank">#{global_rank} {icon}</div>
                  <div class="jump-date">{r['Tarih'].strftime('%d.%m.%Y')}</div>
                  <div class="jump-pct {'pos' if is_pos else 'neg'}">{sign}{f"{r['Yuzde_Degisim']:.2f}".replace('.',',')}%</div>
                  <div class="jump-meta">{TR_GUN.get(r['Gun_Adi'], r['Gun_Adi'])}</div>
                  <div class="jump-meta">{fkur(r['Onceki_Kur'])} → {fkur(r['Dolar_Kuru'])} ₺</div>
                  <div class="jump-meta">+{int(r['Gun_Farki'])} gün arayla</div>
                </div>""", unsafe_allow_html=True)

# ════════════ TAB 2 ════════════
with tab2:
    GUN_COLORS   = {"Pazartesi":"#4a9eff","Salı":"#b794f4","Çarşamba":"#f6ad55","Perşembe":"#00d4aa","Cuma":"#ff4d6a"}
    ALL_DAYS_TR  = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma"]
    df["Gun_Adi_TR"] = df["Gun_Adi"].map(TR_GUN)
    aktif_gunler = gun_filtre if gun_filtre else ALL_DAYS_TR

    st.markdown('<div class="section-label">◈ Günlük Değişim — Gün Bazlı Karşılaştırma</div>', unsafe_allow_html=True)
    fig_gd = go.Figure()
    fig_gd.add_trace(go.Scatter(x=df["Tarih"], y=df["Yuzde_Degisim"], mode="lines",
        line=dict(color="#1e2d4a", width=0.7), opacity=0.5, hoverinfo="skip", showlegend=False))
    for gun_tr in aktif_gunler:
        sub = df[df["Gun_Adi_TR"] == gun_tr].copy()
        sub["_ps"] = sub["Yuzde_Degisim"].apply(tr_fmt_pct)
        sub["_ks"] = sub["Dolar_Kuru"].apply(tr_fmt_kur)
        sub["_os"] = sub["Onceki_Kur"].apply(tr_fmt_kur)
        color = GUN_COLORS.get(gun_tr, "#c9d4e8")
        fig_gd.add_trace(go.Scatter(
            x=sub["Tarih"], y=sub["Yuzde_Degisim"], mode="markers", name=gun_tr,
            marker=dict(color=color, size=5, opacity=0.85, line=dict(color="rgba(0,0,0,0.3)", width=0.5)),
            customdata=list(zip(sub["_ps"], sub["_ks"], sub["_os"])),
            hovertemplate=f'<b>{gun_tr}</b> — %{{x|%d.%m.%Y}}<br>Değişim: <b>%{{customdata[0]}}</b><br>Kur: %{{customdata[2]}} → %{{customdata[1]}} ₺<extra></extra>'
        ))
    fig_gd.add_hline(y=0, line_color="#2a4a7a", line_width=1)
    tv_gd, tt_gd = safe_ticks(df["Yuzde_Degisim"].min(), df["Yuzde_Degisim"].max(), n=10, decimals=1, suffix="%")
    apply_base(fig_gd, height=460,
        title=dict(text=f"GÜN BAZLI DEĞİŞİM — {', '.join(aktif_gunler)}", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y"),
        yaxis={**yt(tv_gd, tt_gd, {"gridcolor":"#131c2e","tickfont":dict(size=10,color="#4a6080")})},
        hovermode="closest")
    st.plotly_chart(fig_gd, use_container_width=True)

    st.markdown('<div class="section-label">◈ Gün Bazlı İstatistikler</div>', unsafe_allow_html=True)
    kart_cols = st.columns(len(aktif_gunler))
    for i, gun_tr in enumerate(aktif_gunler):
        sub   = df[df["Gun_Adi_TR"] == gun_tr]
        ort   = sub["Yuzde_Degisim"].mean()
        std   = sub["Yuzde_Degisim"].std()
        maks  = sub["Yuzde_Degisim"].max()
        mins  = sub["Yuzde_Degisim"].min()
        poz   = (sub["Yuzde_Degisim"] > 0).mean() * 100
        color = GUN_COLORS.get(gun_tr, "#4a9eff")
        sign  = "+" if ort >= 0 else ""
        with kart_cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 2px solid {color};">
              <div class="metric-label" style="color:{color};">{gun_tr}</div>
              <div class="metric-value {'metric-pos' if ort>=0 else 'metric-neg'}">{sign}{f'{ort:.3f}'.replace('.',',')}%</div>
              <div class="metric-sub">Ort. günlük değişim</div>
              <div style="margin-top:10px;font-size:0.72rem;color:#3a5070;font-family:'DM Mono',monospace;line-height:1.8;">
                <span style="color:#4a6080">Std:</span> <span style="color:{color}">±{f'{std:.3f}'.replace('.',',')}%</span><br>
                <span style="color:#4a6080">Max:</span> <span style="color:#00d4aa">+{f'{maks:.2f}'.replace('.',',')}%</span><br>
                <span style="color:#4a6080">Min:</span> <span style="color:#ff4d6a">{f'{mins:.2f}'.replace('.',',')}%</span><br>
                <span style="color:#4a6080">Poz. oran:</span> <span style="color:{color}">%{poz:.0f}</span>
              </div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">◈ Dağılım Karşılaştırması (Violin)</div>', unsafe_allow_html=True)
    fig_vio = go.Figure()
    for gun_tr in ALL_DAYS_TR:
        sub   = df[df["Gun_Adi_TR"] == gun_tr]
        color = GUN_COLORS.get(gun_tr, "#4a9eff")
        rr, gg, bb = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fig_vio.add_trace(go.Violin(
            y=sub["Yuzde_Degisim"], name=gun_tr, line_color=color,
            fillcolor=f"rgba({rr},{gg},{bb},0.12)",
            meanline_visible=True, box_visible=True, points="outliers",
            hovertemplate=f"<b>{gun_tr}</b><br>%{{y:.3f}}%<extra></extra>"
        ))
    fig_vio.add_hline(y=0, line_color="#2a4a7a", line_dash="dash", line_width=1)
    apply_base(fig_vio, height=460,
        title=dict(text="GÜN BAZLI DEĞİŞİM — VİOLİN", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        yaxis={**yt(tv_gd, tt_gd, {"gridcolor":"#131c2e"})},
        xaxis=dict(gridcolor="#0d1220"))
    st.plotly_chart(fig_vio, use_container_width=True)

    st.markdown('<div class="section-label">◈ Haftalık Değişim — Pazartesi → Cuma</div>', unsafe_allow_html=True)
    hf = hf_global.copy()
    if haftalik_yon == "Yalnız Pozitif ↑":
        hf_sic = hf[hf["HaftaDegisim"] >= haftalik_esik].copy()
    elif haftalik_yon == "Yalnız Negatif ↓":
        hf_sic = hf[hf["HaftaDegisim"] <= -haftalik_esik].copy()
    else:
        hf_sic = hf[hf["HaftaDegisim"].abs() >= haftalik_esik].copy()
    hf_pos_sc = hf_sic[hf_sic["HaftaDegisim"] > 0].copy()
    hf_neg_sc = hf_sic[hf_sic["HaftaDegisim"] < 0].copy()

    def hf_lbl_col(sub, is_pos):
        sub = sub.copy()
        if len(sub) == 0:
            sub["_lbl"] = pd.Series(dtype=str)
            return sub
        thr = sub["HaftaDegisim"].quantile(1 - haftalik_etiket/100) if is_pos else sub["HaftaDegisim"].quantile(haftalik_etiket/100)
        sub["_lbl"] = sub.apply(
            lambda r: f"{r['Aralik']} {tr_fmt_pct(r['HaftaDegisim'],1)}"
            if (r["HaftaDegisim"] >= thr if is_pos else r["HaftaDegisim"] <= thr) else "", axis=1)
        return sub

    hf_pos_sc = hf_lbl_col(hf_pos_sc, True)
    hf_neg_sc = hf_lbl_col(hf_neg_sc, False)

    fig_hw = go.Figure()
    fig_hw.add_trace(go.Scatter(
        x=hf["XTarih"], y=hf["HaftaDegisim"], mode="lines", name="Haftalık Δ",
        line=dict(color="#2a4a7a", width=1), opacity=0.6,
        customdata=list(zip(hf["Aralik"], hf["_pzt_str"], hf["_cum_str"], hf["_hf_str"])),
        hovertemplate="<b>%{customdata[0]}</b><br>Pzt: %{customdata[1]} ₺ → Cum: %{customdata[2]} ₺<br>%{customdata[3]}<extra></extra>"
    ))
    for subset, color, name, tpos, sym, tpl_color in [
        (hf_pos_sc, "#00d4aa", "↑ Pozitif", "top right",    "triangle-up",   "#00d4aa"),
        (hf_neg_sc, "#ff4d6a", "↓ Negatif", "bottom right", "triangle-down", "#ff4d6a"),
    ]:
        if len(subset) == 0:
            continue
        s = subset.copy()
        s["_ps"] = s["PztKur"].apply(tr_fmt_kur)
        s["_cs"] = s["CumKur"].apply(tr_fmt_kur)
        s["_hs"] = s["HaftaDegisim"].apply(tr_fmt_pct)
        fig_hw.add_trace(go.Scatter(
            x=s["XTarih"], y=s["HaftaDegisim"], mode="markers+text", name=name,
            marker=dict(color=color, size=s["AbsDegisim"]*1.8+5, symbol=sym,
                        line=dict(color=color, width=2), opacity=0.9),
            text=s["_lbl"], textposition=tpos,
            textfont=dict(size=8, color=color, family="DM Mono, monospace"),
            customdata=list(zip(s["Aralik"], s["_ps"], s["_cs"], s["_hs"])),
            hovertemplate=f'<b>%{{customdata[0]}}</b><br>Pzt: %{{customdata[1]}} ₺ → Cum: %{{customdata[2]}} ₺<br><b style="color:{tpl_color}">%{{customdata[3]}}</b><extra></extra>'
        ))
    tv_hf, tt_hf = safe_ticks(hf["HaftaDegisim"].min(), hf["HaftaDegisim"].max(), n=10, decimals=1, suffix="%")
    he_str = str(haftalik_esik).replace(".", ",")
    fig_hw.add_hline(y=haftalik_esik,  line_dash="dash", line_color="rgba(0,212,170,0.5)",  line_width=1,
                     annotation_text=f"+{he_str}%", annotation_font_color="#00d4aa", annotation_font_size=10)
    fig_hw.add_hline(y=-haftalik_esik, line_dash="dash", line_color="rgba(255,77,106,0.5)", line_width=1,
                     annotation_text=f"−{he_str}%", annotation_font_color="#ff4d6a", annotation_font_size=10)
    fig_hw.add_hline(y=0, line_color="#2a4a7a", line_width=1)
    apply_base(fig_hw, height=520,
        title=dict(text=f"HAFTALIK DEĞİŞİM (Pzt→Cum) · Eşik ±%{haftalik_esik} · Etiket top %{haftalik_etiket}",
                   font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y", tickfont=dict(size=10, color="#4a6080"),
                   showspikes=True, spikecolor="#2a4a7a", spikethickness=1, spikedash="dot"),
        yaxis={**yt(tv_hf, tt_hf, {"gridcolor":"#131c2e","tickfont":dict(size=10,color="#4a6080")})},
        hovermode="closest")
    st.plotly_chart(fig_hw, use_container_width=True)

    hf_ort   = hf["HaftaDegisim"].mean()
    hf_maks  = hf["HaftaDegisim"].max()
    hf_mins  = hf["HaftaDegisim"].min()
    hf_pos_n = (hf["HaftaDegisim"] >= haftalik_esik).sum()
    hf_neg_n = (hf["HaftaDegisim"] <= -haftalik_esik).sum()
    sign_hf  = "+" if hf_ort >= 0 else ""
    st.markdown(f"""
    <div class="metric-row" style="grid-template-columns: repeat(5, 1fr);">
      <div class="metric-card" style="border-top:2px solid #4a9eff;">
        <div class="metric-label">Haftalık Ort.</div>
        <div class="metric-value metric-{'pos' if hf_ort>=0 else 'neg'}">{sign_hf}{f'{hf_ort:.3f}'.replace('.',',')}%</div>
        <div class="metric-sub">Pzt→Cum ort.</div></div>
      <div class="metric-card" style="border-top:2px solid #00d4aa;">
        <div class="metric-label">≥ +%{he_str} hafta</div>
        <div class="metric-value metric-pos">{hf_pos_n}</div>
        <div class="metric-sub">pozitif büyük hafta</div></div>
      <div class="metric-card" style="border-top:2px solid #ff4d6a;">
        <div class="metric-label">≤ −%{he_str} hafta</div>
        <div class="metric-value metric-neg">{hf_neg_n}</div>
        <div class="metric-sub">negatif büyük hafta</div></div>
      <div class="metric-card">
        <div class="metric-label">En İyi Hafta</div>
        <div class="metric-value metric-pos">+{f'{hf_maks:.2f}'.replace('.',',')}%</div></div>
      <div class="metric-card">
        <div class="metric-label">En Kötü Hafta</div>
        <div class="metric-value metric-neg">{f'{hf_mins:.2f}'.replace('.',',')}%</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">◈ Haftalık Değişim Tablosu</div>', unsafe_allow_html=True)
    hf_tablo = hf_global[["PztTarih","CumTarih","PztKur","CumKur","HaftaDegisim"]].copy()
    hf_tablo["Hafta"]     = hf_tablo["PztTarih"].dt.strftime("%d.%m.%Y") + " – " + hf_tablo["CumTarih"].dt.strftime("%d.%m.%Y")
    hf_tablo["Yıl"]       = hf_tablo["PztTarih"].dt.year
    hf_tablo["Pzt Kur"]   = hf_tablo["PztKur"].apply(tr_fmt_kur)
    hf_tablo["Cum Kur"]   = hf_tablo["CumKur"].apply(tr_fmt_kur)
    hf_tablo["Değişim %"] = hf_tablo["HaftaDegisim"].apply(tr_fmt_pct)
    hf_tablo["Yön"]       = hf_tablo["HaftaDegisim"].apply(lambda x: "↑" if x > 0 else "↓")
    hf_tablo = hf_tablo[["Yıl","Hafta","Pzt Kur","Cum Kur","Değişim %","Yön"]].sort_values("Hafta", ascending=False).reset_index(drop=True)

    def color_row(val):
        if isinstance(val, str) and val.endswith("%"):
            try:
                num = float(val.replace(",",".").replace("%","").replace("+",""))
                return "color: #00d4aa" if num > 0 else ("color: #ff4d6a" if num < 0 else "")
            except Exception:
                pass
        return ""

    styled = (hf_tablo.style.applymap(color_row, subset=["Değişim %"])
        .set_properties(**{"background-color":"#0d1220","color":"#8aa0bf","border":"1px solid #1e2d4a","font-family":"DM Mono, monospace","font-size":"12px"})
        .set_table_styles([
            {"selector":"th","props":[("background-color","#080c14"),("color","#4a6080"),("font-family","DM Mono, monospace"),("font-size","11px"),("text-transform","uppercase"),("letter-spacing","0.08em"),("border","1px solid #1e2d4a"),("padding","8px 12px")]},
            {"selector":"td","props":[("padding","6px 12px")]},
            {"selector":"tr:hover td","props":[("background-color","#131c2e")]},
        ]))
    st.dataframe(styled, use_container_width=True, height=420)

    st.markdown('<div class="section-label">◈ Aylık Getiri (21 Gün)</div>', unsafe_allow_html=True)
    col_am1, col_am2 = st.columns(2)
    with col_am1:
        aylik_g      = df.dropna(subset=["Aylik_Getiri"]).copy()
        aylik_g_filt = aylik_g[aylik_g["Gun_Adi_TR"].isin(aktif_gunler)] if gun_filtre else aylik_g.copy()
        aylik_g_filt = aylik_g_filt.copy()
        aylik_g_filt["renk"] = aylik_g_filt["Aylik_Getiri"].apply(lambda x: "#4a9eff" if x >= 0 else "#ff4d6a")
        aylik_g_filt["_ag"]  = aylik_g_filt["Aylik_Getiri"].apply(tr_fmt_pct)
        aylik_g_filt["_gun"] = aylik_g_filt["Gun_Adi_TR"]
        fig_am = go.Figure()
        fig_am.add_trace(go.Bar(
            x=aylik_g_filt["Tarih"], y=aylik_g_filt["Aylik_Getiri"],
            marker_color=aylik_g_filt["renk"].values, opacity=0.8,
            customdata=list(zip(aylik_g_filt["_gun"], aylik_g_filt["_ag"])),
            hovertemplate="%{x|%d.%m.%Y} (%{customdata[0]})<br>21G: <b>%{customdata[1]}</b><extra></extra>"
        ))
        fig_am.add_hline(y=0, line_color="#1e2d4a", line_width=1)
        tv_am, tt_am = safe_ticks(aylik_g_filt["Aylik_Getiri"].min(), aylik_g_filt["Aylik_Getiri"].max(), n=8, decimals=1, suffix="%")
        apply_base(fig_am, height=340,
            title=dict(text="21 GÜNLÜK (AYLIK) GETİRİ", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            yaxis={**yt(tv_am, tt_am, {"gridcolor":"#131c2e"})},
            xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y"), showlegend=False)
        st.plotly_chart(fig_am, use_container_width=True)
    with col_am2:
        df["Vol_20"] = df["Yuzde_Degisim"].rolling(20).std()
        df["Vol_60"] = df["Yuzde_Degisim"].rolling(60).std()
        df["_v20"]   = df["Vol_20"].apply(lambda x: tr_fmt_pct(x, 3) if pd.notna(x) else "")
        df["_v60"]   = df["Vol_60"].apply(lambda x: tr_fmt_pct(x, 3) if pd.notna(x) else "")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=df["Tarih"], y=df["Vol_20"], mode="lines", name="20G Vol",
            line=dict(color="#4a9eff", width=1.5), fill="tozeroy", fillcolor="rgba(74,158,255,0.05)",
            customdata=df["_v20"], hovertemplate="%{x|%d.%m.%Y}<br>20G: <b>%{customdata}</b><extra></extra>"))
        fig_vol.add_trace(go.Scatter(x=df["Tarih"], y=df["Vol_60"], mode="lines", name="60G Vol",
            line=dict(color="#ff4d6a", width=1.2, dash="dot"),
            customdata=df["_v60"], hovertemplate="%{x|%d.%m.%Y}<br>60G: <b>%{customdata}</b><extra></extra>"))
        vol_max = float(df["Vol_20"].dropna().max()) if df["Vol_20"].dropna().shape[0] > 0 else 1.0
        tv_vol, tt_vol = safe_ticks(0, vol_max, n=6, decimals=2, suffix="%")
        apply_base(fig_vol, height=340,
            title=dict(text="YUVARLANMALI VOLATİLİTE", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            yaxis={**yt(tv_vol, tt_vol, {"gridcolor":"#131c2e"})},
            xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y"))
        st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown('<div class="section-label">◈ Yıl–Ay Ortalama Günlük Getiri (Isı Haritası)</div>', unsafe_allow_html=True)
    ay_pivot = df.groupby(["Yil","Ay"])["Yuzde_Degisim"].mean().unstack(fill_value=np.nan)
    ay_pivot.columns = [TR_AY.get(c, str(c)) for c in ay_pivot.columns]
    text_matrix = np.where(np.isnan(ay_pivot.values), "",
        np.vectorize(lambda v: f"{f'{v:.2f}'.replace('.', ',')}%")(ay_pivot.values))
    fig_heat = go.Figure(go.Heatmap(
        z=ay_pivot.values, x=ay_pivot.columns.tolist(), y=ay_pivot.index.astype(str).tolist(),
        colorscale=[[0,"#ff4d6a"],[0.5,"#0d1220"],[1,"#00d4aa"]], zmid=0,
        text=text_matrix, texttemplate="%{text}", textfont=dict(size=9, family="DM Mono, monospace"),
        hovertemplate="<b>%{y} — %{x}</b><br>Ort. Günlük: <b>%{text}</b><extra></extra>",
        colorbar=dict(tickfont=dict(size=9, color="#4a6080"))
    ))
    apply_base(fig_heat, height=500,
        title=dict(text="YIL–AY ORTALAMA GÜNLÜK GETİRİ", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(side="bottom", tickfont=dict(size=11, color="#4a6080")),
        yaxis=dict(tickfont=dict(size=11, color="#4a6080"), autorange="reversed"))
    st.plotly_chart(fig_heat, use_container_width=True)

# ════════════ TAB 3 ════════════
with tab3:
    st.markdown(f'<div class="section-label">◈ Büyük Sıçramalardan Sonra Ne Oluyor? (≥%{fwd_threshold})</div>', unsafe_allow_html=True)
    periods       = [1, 5, 10, 21, 63]
    period_labels = {1:"1G", 5:"5G (1Hf)", 10:"10G (2Hf)", 21:"21G (1Ay)", 63:"63G (3Ay)"}
    fwd = forward_analysis(df, fwd_threshold, periods)

    if not fwd:
        st.warning(f"%{fwd_threshold} eşiğinde yeterli sıçrama bulunamadı.")
    else:
        cards_html = ""
        for p in periods:
            if p in fwd:
                r        = fwd[p]
                mean_cls = "metric-pos" if r["mean"] >= 0 else "metric-neg"
                sign     = "+" if r["mean"] >= 0 else ""
                cards_html += f"""
                <div class="forward-card">
                  <div class="forward-title">{period_labels[p]} Sonra</div>
                  <div class="forward-big {mean_cls}">{sign}{f"{r['mean']:.2f}".replace('.',',')}%</div>
                  <div class="forward-detail">
                    <span style="color:#4a6080">Medyan:</span> <span class="forward-accent">{'+' if r['median']>=0 else ''}{f"{r['median']:.2f}".replace('.',',')}%</span><br>
                    <span style="color:#4a6080">Pozitif oran:</span> <span class="forward-accent">%{r['pos_pct']:.0f}</span><br>
                    <span style="color:#4a6080">IQR:</span> <span class="forward-accent">{f"{r['p25']:.2f}".replace('.',',')}% — {f"{r['p75']:.2f}".replace('.',',')}%</span><br>
                    <span style="color:#4a6080">Örnek:</span> <span class="forward-accent">{r['n']}</span>
                  </div>
                </div>"""
        st.markdown(f'<div class="forward-grid">{cards_html}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">◈ Dağılım (Box Plot)</div>', unsafe_allow_html=True)
        fig_box    = go.Figure()
        colors_box = ["#4a9eff","#00d4aa","#f6ad55","#b794f4","#ff4d6a"]
        for i, p in enumerate(periods):
            if p in fwd:
                c = colors_box[i]
                rr, gg, bb = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
                raw_strs   = [f"{f'{v:.3f}'.replace('.',',')}%" for v in fwd[p]["raw"]]
                fig_box.add_trace(go.Box(y=fwd[p]["raw"], name=period_labels[p], marker_color=c,
                    boxpoints="outliers", line_width=1.5, fillcolor=f"rgba({rr},{gg},{bb},0.1)",
                    customdata=raw_strs, hovertemplate="%{customdata}<extra></extra>"))
        fig_box.add_hline(y=0, line_color="#1e2d4a", line_width=1, line_dash="dash")
        apply_base(fig_box, height=480,
            title=dict(text=f"%{fwd_threshold}+ SIÇRAMA SONRASI GETİRİ DAĞILIMI", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            yaxis=dict(gridcolor="#131c2e", ticksuffix="%"),
            xaxis=dict(gridcolor="#0d1220"))
        st.plotly_chart(fig_box, use_container_width=True)

        st.markdown('<div class="section-label">◈ Pozitif Kapanış Oranı (Her Dönem)</div>', unsafe_allow_html=True)
        pos_rates    = [fwd[p]["pos_pct"] for p in periods if p in fwd]
        period_names = [period_labels[p] for p in periods if p in fwd]
        fig_win = go.Figure(go.Bar(
            x=period_names, y=pos_rates,
            marker_color=["#00d4aa" if v >= 50 else "#ff4d6a" for v in pos_rates],
            text=[f"%{f'{v:.0f}'.replace('.', ',')}" for v in pos_rates],
            textposition="outside", textfont=dict(size=11, color="#c9d4e8", family="DM Mono, monospace"),
            customdata=[f"%{f'{v:.1f}'.replace('.',',')}" for v in pos_rates],
            hovertemplate="%{x}<br>Pozitif oran: <b>%{customdata}</b><extra></extra>"
        ))
        fig_win.add_hline(y=50, line_dash="dash", line_color="#2a4a7a", line_width=1,
                          annotation_text="50%", annotation_font_color="#4a6080")
        apply_base(fig_win, height=360,
            title=dict(text="DÖNEM SONU POZİTİF KAPANIŞ ORANI", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            yaxis=dict(gridcolor="#131c2e", ticksuffix="%", range=[0,105]),
            xaxis=dict(gridcolor="#0d1220"), showlegend=False)
        st.plotly_chart(fig_win, use_container_width=True)

        st.markdown('<div class="section-label">◈ Eşik Hassasiyeti (21G Ort. Getiri vs Tetikleyici Eşik)</div>', unsafe_allow_html=True)
        thresholds = np.arange(1.0, 12.0, 0.5)
        means_21, counts_21, thr_strs, m21_strs = [], [], [], []
        for thr in thresholds:
            f2 = forward_analysis(df, thr, [21])
            if 21 in f2 and f2[21]["n"] >= 5:
                means_21.append(f2[21]["mean"])
                counts_21.append(f2[21]["n"])
            else:
                means_21.append(np.nan)
                counts_21.append(0)
            thr_strs.append(f"{f'{thr:.1f}'.replace('.',',')}%")
            m21_strs.append(f"{f'{means_21[-1]:.2f}'.replace('.',',')}%" if np.isfinite(means_21[-1]) else "—")

        fig_sens = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sens.add_trace(go.Scatter(x=thresholds, y=means_21, mode="lines+markers", name="Ort. 21G Getiri",
            line=dict(color="#4a9eff", width=2), marker=dict(size=6),
            customdata=list(zip(thr_strs, m21_strs)),
            hovertemplate="Eşik: %{customdata[0]}<br>Ort. 21G: <b>%{customdata[1]}</b><extra></extra>"), secondary_y=False)
        fig_sens.add_trace(go.Bar(x=thresholds, y=counts_21, name="Örnek Sayısı",
            marker_color="rgba(74,158,255,0.15)",
            customdata=list(zip(thr_strs, counts_21)),
            hovertemplate="Eşik: %{customdata[0]}<br>n: %{customdata[1]}<extra></extra>"), secondary_y=True)
        fig_sens.add_hline(y=0, line_color="#1e2d4a", line_width=1)
        fig_sens.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,32,0.9)",
            font=dict(color="#c9d4e8", family="DM Sans, sans-serif"), height=400,
            title=dict(text="EŞİK HASSASIYETI — 21G ORTALAMA GETİRİ", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            legend={**LEGEND_RIGHT}, margin=dict(l=50, r=120, t=50, b=40),
            hoverlabel=dict(bgcolor="#0d1220", font_size=12, font_color="#e8f0ff"),
            xaxis=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10, color="#4a6080")),
            yaxis=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10, color="#4a6080")),
            yaxis2=dict(gridcolor="#0d1220", tickfont=dict(size=9, color="#3a5070"), title=dict(text="n", font=dict(color="#3a5070")))
        )
        st.plotly_chart(fig_sens, use_container_width=True)

# ════════════ TAB 4 ════════════
with tab4:
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-label">◈ Kümülatif Sıçrama Sayısı</div>', unsafe_allow_html=True)
        cum_df = sicramalar.sort_values("Tarih").reset_index(drop=True)
        cum_df["Kumulatif"] = range(1, len(cum_df)+1)
        fig3 = go.Figure(go.Scatter(
            x=cum_df["Tarih"], y=cum_df["Kumulatif"],
            fill="tozeroy", line=dict(color="#4a9eff", width=1.5), fillcolor="rgba(74,158,255,0.06)",
            hovertemplate="%{x|%d.%m.%Y}<br>Toplam: <b>%{y}</b> sıçrama<extra></extra>"
        ))
        apply_base(fig3, height=380,
            title=dict(text="KÜMÜLATİF SIÇRAMA SAYISI", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y"), yaxis=dict(gridcolor="#131c2e"))
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown('<div class="section-label">◈ Aylara Göre Sıçrama</div>', unsafe_allow_html=True)
        ay_order_tr = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
        sicramalar["Ay_Adi_TR"] = sicramalar["Ay"].map(TR_AY_UZUN)
        ay_sayim = sicramalar.groupby("Ay_Adi_TR").size().reindex(ay_order_tr).fillna(0)
        fig4 = go.Figure(go.Bar(
            x=ay_sayim.index, y=ay_sayim.values,
            marker=dict(color=ay_sayim.values, colorscale=[[0,"#1e2d4a"],[1,"#4a9eff"]], line=dict(color="rgba(255,255,255,0.05)", width=1)),
            hovertemplate="<b>%{x}</b><br>%{y} sıçrama<extra></extra>"
        ))
        apply_base(fig4, height=350,
            title=dict(text="AYLARA GÖRE SIÇRAMA SAYISI", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            xaxis=dict(gridcolor="#131c2e", tickfont=dict(size=10, color="#4a6080")),
            yaxis=dict(gridcolor="#131c2e"), showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-label">◈ Büyüklük Dağılımı</div>', unsafe_allow_html=True)
        fig7 = go.Figure()
        fig7.add_trace(go.Histogram(x=sicramalar[sicramalar["Yuzde_Degisim"]>0]["Yuzde_Degisim"],
            nbinsx=25, name="↑ Pozitif", marker_color="#00d4aa", opacity=0.7,
            hovertemplate="%{x:.1f}% — %{y} adet<extra></extra>"))
        fig7.add_trace(go.Histogram(x=sicramalar[sicramalar["Yuzde_Degisim"]<0]["Yuzde_Degisim"],
            nbinsx=25, name="↓ Negatif", marker_color="#ff4d6a", opacity=0.7,
            hovertemplate="%{x:.1f}% — %{y} adet<extra></extra>"))
        apply_base(fig7, height=380, barmode="overlay",
            title=dict(text="SIÇRAMA BÜYÜKLÜKLERİ DAĞILIMI", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            xaxis=dict(gridcolor="#131c2e", ticksuffix="%"), yaxis=dict(gridcolor="#131c2e"))
        st.plotly_chart(fig7, use_container_width=True)

        st.markdown('<div class="section-label">◈ Yıl–Ay Yoğunluk Haritası</div>', unsafe_allow_html=True)
        pivot     = sicramalar.groupby(["Yil","Ay"]).size().unstack(fill_value=0)
        ay_labels = [TR_AY.get(c, str(c)) for c in pivot.columns]
        fig8 = go.Figure(go.Heatmap(
            z=pivot.values, x=ay_labels, y=pivot.index.astype(str),
            colorscale=[[0,"#0d1220"],[0.5,"#1b6cf2"],[1,"#00d4aa"]],
            text=pivot.values, texttemplate="%{text}",
            textfont=dict(size=9, color="#e8f0ff", family="DM Mono, monospace"),
            hovertemplate="<b>%{y} — %{x}</b><br>%{z} sıçrama<extra></extra>",
            colorbar=dict(tickfont=dict(size=9, color="#4a6080"))
        ))
        apply_base(fig8, height=350,
            title=dict(text="YIL–AY SIÇRAMA YOĞUNLUĞU", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            xaxis=dict(side="bottom", tickfont=dict(size=11, color="#4a6080")),
            yaxis=dict(tickfont=dict(size=11, color="#4a6080"), autorange="reversed"))
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown('<div class="section-label">◈ Haftalık Pattern</div>', unsafe_allow_html=True)
    gun_order_tr = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    sicramalar["Gun_Adi_TR"] = sicramalar["Gun_Adi"].map(TR_GUN)
    gun_sayim = sicramalar.groupby("Gun_Adi_TR").size().reindex(gun_order_tr).fillna(0)
    fig5 = go.Figure(go.Bar(
        x=gun_sayim.index, y=gun_sayim.values,
        marker=dict(color=gun_sayim.values, colorscale=[[0,"#1e2d4a"],[1,"#b794f4"]], line=dict(color="rgba(255,255,255,0.05)", width=1)),
        hovertemplate="<b>%{x}</b><br>%{y} sıçrama<extra></extra>"
    ))
    apply_base(fig5, height=340,
        title=dict(text="HAFTANIN GÜNLERİNE GÖRE SIÇRAMA SAYISI", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e"), yaxis=dict(gridcolor="#131c2e"), showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

# ════════════ TAB 5 ════════════
with tab5:
    st.markdown('<div class="section-label">◈ Sıçrama Tablosu</div>', unsafe_allow_html=True)
    tbl = top_sic.copy().reset_index(drop=True)
    tbl.index = tbl.index + 1
    tbl_show = pd.DataFrame({
        "#":          tbl.index,
        "Tarih":      tbl["Tarih"].dt.strftime("%d.%m.%Y"),
        "Yıl":        tbl["Yil"],
        "Ay":         tbl["Ay_Adi"],
        "Gün Adı":    tbl["Gun_Adi"],
        "Kur":        tbl["Dolar_Kuru"].apply(tr_fmt_kur),
        "Önceki Kur": tbl["Onceki_Kur"].apply(tr_fmt_kur),
        "Değişim %":  tbl["Yuzde_Degisim"].apply(tr_fmt_pct),
        "TL Δ":       tbl["TL_Degisim"].apply(lambda x: tr_fmt_kur(x, 4)),
        "Gün Farkı":  tbl["Gun_Farki"].astype(int),
    })
    st.dataframe(tbl_show, use_container_width=True, height=420)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">◈ Aylık Özet</div>', unsafe_allow_html=True)
        aylik = sicramalar.groupby("Ay_Adi")["Abs_Degisim"].agg(["count","mean","max","min"]).round(3)
        aylik.columns = ["Toplam","Ort. %","Maks %","Min %"]
        st.dataframe(aylik, use_container_width=True)
    with c2:
        st.markdown('<div class="section-label">◈ Yıllık Özet</div>', unsafe_allow_html=True)
        yillik = sicramalar.groupby("Yil").agg(
            Toplam=("Abs_Degisim","count"), Ort_Pct=("Abs_Degisim","mean"),
            Pozitif=("Yuzde_Degisim", lambda x: (x>0).sum()),
            Negatif=("Yuzde_Degisim", lambda x: (x<0).sum()),
            Maks=("Abs_Degisim","max")
        ).round(3)
        yillik.columns = ["Toplam","Ort. %","Pozitif","Negatif","Maks %"]
        st.dataframe(yillik, use_container_width=True)

    st.markdown('<div class="section-label">◈ Haftalık Değişim Tablosu (Pzt → Cum)</div>', unsafe_allow_html=True)
    hf_t = hf_global[["PztTarih","CumTarih","PztKur","CumKur","HaftaDegisim"]].copy()
    hf_t.insert(0, "Hafta", hf_t["PztTarih"].dt.strftime("%d.%m.%Y") + " – " + hf_t["CumTarih"].dt.strftime("%d.%m.%Y"))
    hf_t.insert(0, "Yıl", hf_t["PztTarih"].dt.year)
    hf_t["Pzt Kur"]   = hf_t["PztKur"].apply(tr_fmt_kur)
    hf_t["Cum Kur"]   = hf_t["CumKur"].apply(tr_fmt_kur)
    hf_t["Değişim %"] = hf_t["HaftaDegisim"].apply(tr_fmt_pct)
    hf_t["Yön"]       = hf_t["HaftaDegisim"].apply(lambda x: "↑" if x > 0 else "↓")
    hf_t = hf_t[["Yıl","Hafta","Pzt Kur","Cum Kur","Değişim %","Yön"]].sort_values("Hafta", ascending=False).reset_index(drop=True)
    hf_t.index = hf_t.index + 1
    st.dataframe(hf_t, use_container_width=True, height=420)

    st.markdown('<div class="section-label">◈ Dışa Aktar</div>', unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        csv = top_sic.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV İndir", csv, "sicramalar.csv", "text/csv")
    with dc2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            top_sic.to_excel(w, sheet_name="Sicramalar", index=False)
            hf_t.to_excel(w, sheet_name="Haftalik", index=False)
            df.to_excel(w, sheet_name="Tum_Veri", index=False)
            aylik.to_excel(w, sheet_name="Aylik")
            yillik.to_excel(w, sheet_name="Yillik")
        st.download_button("Excel İndir (Tüm Analiz)", buf.getvalue(), "usdtry_analiz.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("""
<div style="text-align:center; color:#1e2d4a; font-size:0.7rem; padding:30px 0 10px 0;
            border-top:1px solid #0d1220; margin-top:30px;
            font-family:'DM Mono',monospace; letter-spacing:0.1em;">
    USDTRY ANALYSIS PLATFORM · STREAMLIT + PLOTLY · EVDS API
</div>
""", unsafe_allow_html=True)
