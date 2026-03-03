import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from datetime import datetime
from typing import Optional, Tuple, Dict, List, Any, Union

# =============================================================================
# KONFİGÜRASYON & SABİTLER
# =============================================================================
st.set_page_config(
    page_title="USDTRY Analiz Platformu | Profesyonel",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema Sabitleri
class Theme:
    BG_PRIMARY = "#080c14"
    BG_SECONDARY = "#0d1220"
    BORDER = "#1e2d4a"
    TEXT_PRIMARY = "#e8f0ff"
    TEXT_SECONDARY = "#c9d4e8"
    TEXT_MUTED = "#4a6080"
    ACCENT_BLUE = "#1b6cf2"
    ACCENT_BLUE_LIGHT = "#4a9eff"
    ACCENT_GREEN = "#00d4aa"
    ACCENT_RED = "#ff4d6a"
    ACCENT_PURPLE = "#b794f4"
    ACCENT_ORANGE = "#f6ad55"

# Türkçe Ay ve Gün Sabitleri
TR_AY = {1: 'Oca', 2: 'Şub', 3: 'Mar', 4: 'Nis', 5: 'May', 6: 'Haz',
         7: 'Tem', 8: 'Ağu', 9: 'Eyl', 10: 'Eki', 11: 'Kas', 12: 'Ara'}
TR_AY_UZUN = {1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
              7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'}
TR_GUN = {'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba',
          'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar'}
GUN_RENKLERI = {
    'Pazartesi': Theme.ACCENT_BLUE_LIGHT,
    'Salı': Theme.ACCENT_PURPLE,
    'Çarşamba': Theme.ACCENT_ORANGE,
    'Perşembe': Theme.ACCENT_GREEN,
    'Cuma': Theme.ACCENT_RED
}

# Plotly Tema Konfigürasyonu - PNG için optimize edildi
PLOTLY_BASE = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(13,18,32,0.9)',
    'font': {'color': Theme.TEXT_SECONDARY, 'family': 'DM Sans, sans-serif', 'size': 12},
    'hoverlabel': {
        'bgcolor': Theme.BG_SECONDARY,
        'font_size': 12,
        'font_color': Theme.TEXT_PRIMARY,
        'bordercolor': Theme.BORDER
    },
    'xaxis': {
        'gridcolor': '#131c2e',
        'gridwidth': 1,
        'tickfont': {'size': 11, 'color': Theme.TEXT_MUTED},
        'zeroline': False,
        'title_font': {'size': 12, 'color': Theme.TEXT_MUTED}
    },
    'yaxis': {
        'gridcolor': '#131c2e',
        'gridwidth': 1,
        'tickfont': {'size': 11, 'color': Theme.TEXT_MUTED},
        'zeroline': False,
        'title_font': {'size': 12, 'color': Theme.TEXT_MUTED}
    },
    'legend': {
        'bgcolor': 'rgba(13,18,32,0.8)',
        'bordercolor': Theme.BORDER,
        'borderwidth': 1,
        'font': {'size': 11},
        'orientation': 'h',
        'yanchor': 'bottom',
        'y': 1.02,
        'xanchor': 'left',
        'x': 0
    },
    'margin': {'l': 60, 'r': 30, 't': 70, 'b': 50},
    'title': {
        'font': {'size': 14, 'color': Theme.TEXT_MUTED, 'family': 'DM Mono, monospace'}
    }
}

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================
def tr_fmt_kur(val: Union[float, int, str], decimals: int = 4) -> str:
    """Türkçe formatlı kur değeri döndürür."""
    try:
        return f"{float(val):.{decimals}f}".replace('.', ',')
    except (ValueError, TypeError):
        return str(val)

def tr_fmt_pct(val: Union[float, int, str], decimals: int = 3, show_sign: bool = True) -> str:
    """Türkçe formatlı yüzde değeri döndürür."""
    try:
        v = float(val)
        sign = "+" if show_sign and v >= 0 else ""
        return f"{sign}{v:.{decimals}f}".replace('.', ',') + "%"
    except (ValueError, TypeError):
        return str(val)

def parse_sayi(s: Any) -> str:
    """Excel'den gelen sayısal değerleri parser eder."""
    if pd.isna(s):
        return str(s)
    s = str(s).strip()
    if '.' in s and ',' in s:
        if s.rfind('.') > s.rfind(','):
            s = s.replace(',', '')
        else:
            s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    return s

def safe_ticks(vmin: float, vmax: float, n: int = 8, decimals: int = 2, 
               suffix: str = '', is_kur: bool = False) -> Tuple[Optional[List[float]], Optional[List[str]]]:
    """Güvenli tick hesaplayıcı."""
    try:
        vmin = float(vmin)
        vmax = float(vmax)
        
        if not (np.isfinite(vmin) and np.isfinite(vmax)):
            return None, None
        
        if vmax <= vmin:
            vmax = vmin + 1.0
        
        raw_step = (vmax - vmin) / max(n, 1)
        if raw_step <= 0 or not np.isfinite(raw_step):
            return None, None
        
        mag = 10 ** np.floor(np.log10(raw_step))
        step = np.ceil(raw_step / mag) * mag
        
        if step <= 0 or not np.isfinite(step):
            return None, None
        
        start = np.floor(vmin / step) * step
        ticks = np.arange(start, vmax + step * 1.05, step)
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

def apply_base(fig: go.Figure, **kwargs) -> go.Figure:
    """Plotly grafiğine base temayı uygular."""
    cfg = {**PLOTLY_BASE, **kwargs}
    
    for k in ['xaxis', 'yaxis', 'font', 'hoverlabel', 'legend', 'margin', 'title']:
        if k in kwargs:
            base_val = PLOTLY_BASE.get(k, {})
            if isinstance(base_val, dict) and isinstance(kwargs[k], dict):
                cfg[k] = {**base_val, **kwargs[k]}
    
    fig.update_layout(**cfg)
    fig.update_layout(autosize=True)
    
    return fig

def create_section_header(title: str, icon: str = "◈") -> None:
    """Bölüm başlığı oluşturur."""
    st.markdown(f"""
    <div class="section-label">
        {icon} {title}
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# VERİ İŞLEME FONKSİYONLARI
# =============================================================================
@st.cache_data
def veri_isle(raw_data: bytes) -> Tuple[pd.DataFrame, int]:
    """EVDS'den gelen Excel verisini işler ve temizler."""
    try:
        df = pd.read_excel(io.BytesIO(raw_data), sheet_name='EVDS')
    except Exception as e:
        st.error(f"Excel okuma hatası: {e}")
        st.stop()
    
    df.columns = ['Tarih', 'Dolar_Kuru']
    n0 = len(df)
    df = df.dropna()
    cleaned = n0 - len(df)
    
    df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y', errors='coerce')
    df = df.dropna(subset=['Tarih'])
    df = df.sort_values('Tarih').reset_index(drop=True)
    
    df['Dolar_Kuru'] = df['Dolar_Kuru'].apply(
        lambda x: parse_sayi(x) if isinstance(x, str) else x
    )
    df['Dolar_Kuru'] = pd.to_numeric(df['Dolar_Kuru'], errors='coerce')
    df = df.dropna(subset=['Dolar_Kuru'])
    
    medyan = df['Dolar_Kuru'].median()
    if medyan > 0:
        aykiri = (df['Dolar_Kuru'] > medyan * 10) | (df['Dolar_Kuru'] < medyan / 10)
        if aykiri.any():
            df.loc[aykiri, 'Dolar_Kuru'] = df.loc[aykiri, 'Dolar_Kuru'] / 1000
    
    df['Onceki_Kur'] = df['Dolar_Kuru'].shift(1)
    df['Onceki_Tarih'] = df['Tarih'].shift(1)
    df['Gun_Farki'] = (df['Tarih'] - df['Onceki_Tarih']).dt.days
    df['Yuzde_Degisim'] = (df['Dolar_Kuru'] / df['Onceki_Kur'] - 1) * 100
    df['TL_Degisim'] = df['Dolar_Kuru'] - df['Onceki_Kur']
    df = df.dropna()
    
    df['Yil'] = df['Tarih'].dt.year
    df['Ay'] = df['Tarih'].dt.month
    df['Gun'] = df['Tarih'].dt.day
    df['Ay_Adi'] = df['Tarih'].dt.strftime('%B')
    df['Gun_Adi'] = df['Tarih'].dt.strftime('%A')
    df['Gun_Adi_TR'] = df['Gun_Adi'].map(TR_GUN)
    df['Abs_Degisim'] = df['Yuzde_Degisim'].abs()
    df['Hover_Tarih'] = df.apply(
        lambda r: f"{int(r['Tarih'].day)} {TR_AY_UZUN.get(r['Tarih'].month, '')} {int(r['Tarih'].year)}", 
        axis=1
    )
    
    df_idx = df.set_index('Tarih')
    df['Haftalik_Degisim'] = df_idx['Dolar_Kuru'].pct_change(5).values * 100
    df['Aylik_Degisim'] = df_idx['Dolar_Kuru'].pct_change(21).values * 100
    df['3Ay_Degisim'] = df_idx['Dolar_Kuru'].pct_change(63).values * 100
    
    df['Vol_20'] = df['Yuzde_Degisim'].rolling(20).std()
    df['Vol_60'] = df['Yuzde_Degisim'].rolling(60).std()
    
    df['_kur_str'] = df['Dolar_Kuru'].apply(tr_fmt_kur)
    df['_onc_kur_str'] = df['Onceki_Kur'].apply(tr_fmt_kur)
    df['_pct_str'] = df['Yuzde_Degisim'].apply(lambda x: tr_fmt_pct(x, 3))
    
    return df, cleaned

@st.cache_data
def forward_analysis(df: pd.DataFrame, threshold: float, periods: List[int]) -> Dict[int, Dict]:
    """Büyük sıçramalar sonrası ileri dönem değişimlerini analiz eder."""
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

def calculate_weekly_data(df: pd.DataFrame) -> pd.DataFrame:
    """Haftalık (Pazartesi-Cuma) verilerini hesaplar."""
    df['ISOYil'] = df['Tarih'].dt.isocalendar().year.astype(int)
    df['ISOHafta'] = df['Tarih'].dt.isocalendar().week.astype(int)
    
    _hf_ilk = df.groupby(['ISOYil', 'ISOHafta']).agg(
        PztTarih=('Tarih', 'min'),
        PztKur=('Dolar_Kuru', 'first')
    ).reset_index()
    
    _hf_son = df.groupby(['ISOYil', 'ISOHafta']).agg(
        CumTarih=('Tarih', 'max'),
        CumKur=('Dolar_Kuru', 'last')
    ).reset_index()
    
    hf = _hf_ilk.merge(_hf_son, on=['ISOYil', 'ISOHafta'])
    hf['HaftaDegisim'] = (hf['CumKur'] / hf['PztKur'] - 1) * 100
    hf['XTarih'] = hf['CumTarih']
    hf['Aralik'] = hf['PztTarih'].dt.strftime('%d.%m') + '–' + hf['CumTarih'].dt.strftime('%d.%m.%y')
    hf['AbsDegisim'] = hf['HaftaDegisim'].abs()
    hf = hf.dropna(subset=['HaftaDegisim']).reset_index(drop=True)
    hf['_pzt_str'] = hf['PztKur'].apply(tr_fmt_kur)
    hf['_cum_str'] = hf['CumKur'].apply(tr_fmt_kur)
    hf['_hf_str'] = hf['HaftaDegisim'].apply(tr_fmt_pct)
    
    return hf

# =============================================================================
# CSS STİLLERİ
# =============================================================================
def inject_custom_css() -> None:
    """Özel CSS stillerini enjekte eder."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,300&display=swap');
    
    * {{
        font-family: 'DM Sans', sans-serif;
        box-sizing: border-box;
    }}
    
    html, body, .stApp {{
        background: {Theme.BG_PRIMARY};
        color: {Theme.TEXT_SECONDARY};
    }}
    
    .stApp {{
        background: {Theme.BG_PRIMARY};
    }}
    
    section[data-testid="stSidebar"] {{
        background: {Theme.BG_SECONDARY} !important;
        border-right: 1px solid {Theme.BORDER};
    }}
    
    section[data-testid="stSidebar"] * {{
        color: {Theme.TEXT_SECONDARY};
    }}
    
    /* Radio butonları yatay */
    div.row-widget.stRadio > div {{
        flex-direction: row;
        gap: 30px;
    }}
    
    /* Butonlar */
    .stButton > button {{
        background: linear-gradient(135deg, {Theme.ACCENT_BLUE}, #0f4abf);
        color: white;
        border: none;
        border-radius: 6px;
        font-family: 'DM Mono', monospace;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(27,108,242,0.4);
    }}
    
    .stDownloadButton > button {{
        background: transparent;
        color: {Theme.ACCENT_BLUE_LIGHT};
        border: 1px solid {Theme.BORDER};
        border-radius: 6px;
        font-family: 'DM Mono', monospace;
        font-size: 0.8rem;
    }}
    
    .stDownloadButton > button:hover {{
        border-color: {Theme.ACCENT_BLUE_LIGHT};
        background: rgba(74,158,255,0.05);
    }}
    
    /* Metric Kartları */
    .metric-row {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
        margin: 16px 0;
    }}
    
    .metric-card {{
        background: {Theme.BG_SECONDARY};
        border: 1px solid {Theme.BORDER};
        border-radius: 10px;
        padding: 18px 16px;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, {Theme.ACCENT_BLUE}, {Theme.ACCENT_GREEN});
    }}
    
    .metric-card:hover {{
        border-color: #2a4a7a;
    }}
    
    .metric-label {{
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        color: {Theme.TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 10px;
    }}
    
    .metric-value {{
        font-family: 'DM Mono', monospace;
        font-size: 1.5rem;
        font-weight: 500;
        color: {Theme.TEXT_PRIMARY};
        line-height: 1;
        margin-bottom: 6px;
    }}
    
    .metric-sub {{
        font-size: 0.72rem;
        color: #3a5070;
    }}
    
    .metric-pos {{ color: {Theme.ACCENT_GREEN} !important; }}
    .metric-neg {{ color: {Theme.ACCENT_RED} !important; }}
    .metric-neu {{ color: {Theme.ACCENT_BLUE_LIGHT} !important; }}
    
    /* Section Label */
    .section-label {{
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: {Theme.TEXT_MUTED};
        padding: 24px 0 8px 0;
        border-bottom: 1px solid {Theme.BORDER};
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .section-label::after {{
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, {Theme.BORDER}, transparent);
    }}
    
    /* Jump Cards */
    .jump-card {{
        background: {Theme.BG_SECONDARY};
        border: 1px solid {Theme.BORDER};
        border-radius: 8px;
        padding: 14px;
        transition: all 0.2s;
        position: relative;
        overflow: hidden;
    }}
    
    .jump-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        border-color: #2a4a7a;
    }}
    
    .jump-card.pos {{ border-top: 2px solid {Theme.ACCENT_GREEN}; }}
    .jump-card.neg {{ border-top: 2px solid {Theme.ACCENT_RED}; }}
    
    .jump-rank {{
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        color: #3a5070;
        margin-bottom: 8px;
    }}
    
    .jump-date {{
        font-family: 'DM Mono', monospace;
        font-size: 0.85rem;
        color: {Theme.TEXT_SECONDARY};
        margin-bottom: 4px;
    }}
    
    .jump-pct {{
        font-family: 'DM Mono', monospace;
        font-size: 1.6rem;
        font-weight: 500;
        line-height: 1.1;
    }}
    
    .jump-pct.pos {{ color: {Theme.ACCENT_GREEN}; }}
    .jump-pct.neg {{ color: {Theme.ACCENT_RED}; }}
    
    .jump-meta {{
        font-size: 0.7rem;
        color: #3a5070;
        margin-top: 6px;
        font-family: 'DM Mono', monospace;
    }}
    
    /* Forward Grid */
    .forward-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 12px 0;
    }}
    
    .forward-card {{
        background: {Theme.BG_SECONDARY};
        border: 1px solid {Theme.BORDER};
        border-radius: 8px;
        padding: 16px;
    }}
    
    .forward-title {{
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {Theme.TEXT_MUTED};
        margin-bottom: 10px;
    }}
    
    .forward-big {{
        font-family: 'DM Mono', monospace;
        font-size: 1.3rem;
        font-weight: 500;
        color: {Theme.TEXT_PRIMARY};
        margin-bottom: 4px;
    }}
    
    .forward-detail {{
        font-size: 0.72rem;
        color: #3a5070;
        line-height: 1.6;
    }}
    
    .forward-accent {{
        color: {Theme.ACCENT_BLUE_LIGHT};
    }}
    
    /* Upload Box */
    .upload-box {{
        background: {Theme.BG_SECONDARY};
        border: 1px dashed {Theme.BORDER};
        border-radius: 12px;
        padding: 60px 40px;
        text-align: center;
        margin: 40px auto;
        max-width: 600px;
    }}
    
    .upload-icon {{
        font-size: 3rem;
        margin-bottom: 16px;
        color: {Theme.ACCENT_BLUE_LIGHT};
    }}
    
    .upload-title {{
        font-family: 'DM Mono', monospace;
        font-size: 1rem;
        color: {Theme.ACCENT_BLUE_LIGHT};
        margin-bottom: 8px;
    }}
    
    .upload-desc {{
        font-size: 0.85rem;
        color: #3a5070;
        line-height: 1.7;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {Theme.BG_SECONDARY};
        border-bottom: 1px solid {Theme.BORDER};
        gap: 0;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        color: {Theme.TEXT_MUTED};
        padding: 12px 24px;
        background: transparent;
        border: none;
        text-transform: uppercase;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {Theme.ACCENT_BLUE_LIGHT} !important;
        border-bottom: 2px solid {Theme.ACCENT_BLUE_LIGHT} !important;
        background: transparent !important;
    }}
    
    /* DataFrames */
    div[data-testid="stDataFrame"] {{
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid {Theme.BORDER};
    }}
    
    /* Hide Menu */
    #MainMenu, footer {{ visibility: hidden; }}
    
    /* Container */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# HEADER BİLEŞENİ
# =============================================================================
def render_header() -> None:
    """Sayfa başlığını render eder."""
    st.markdown(f"""
    <div style="padding: 8px 0 4px 0;">
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.2em; color:{Theme.ACCENT_BLUE}; margin-bottom:6px;">
            ◈ USDTRY · GÜNLÜK SIÇRAMA & İLERİ ANALİZ · PROFESYONEL
        </div>
        <h1 style="font-size:2rem; font-weight:700; color:{Theme.TEXT_PRIMARY}; margin:0; 
                   line-height:1.1; letter-spacing:-0.02em;">
            Dolar Kuru Analiz Platformu
        </h1>
        <p style="color:#3a5070; font-size:0.85rem; margin:6px 0 0 0;">
            Günlük sıçramaları keşfedin · Haftalık & aylık trendleri takip edin · İleri dönem etkisini analiz edin
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# KPI KARTLARI
# =============================================================================
def render_kpi_cards(df: pd.DataFrame, sicramalar: pd.DataFrame, esik: float) -> None:
    """Ana KPI kartlarını render eder."""
    poz_say = (df['Yuzde_Degisim'] > 0).sum()
    neg_say = (df['Yuzde_Degisim'] < 0).sum()
    oran = len(sicramalar) / len(df) * 100 if len(df) > 0 else 0
    max_j = df['Yuzde_Degisim'].max() if len(df) > 0 else 0
    min_j = df['Yuzde_Degisim'].min() if len(df) > 0 else 0
    
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Toplam Gün</div>
            <div class="metric-value metric-neu">{len(df):,}</div>
            <div class="metric-sub">{df['Tarih'].min().year} – {df['Tarih'].max().year}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Ort. Günlük Değ.</div>
            <div class="metric-value">{tr_fmt_pct(df['Yuzde_Degisim'].mean(), 3)}</div>
            <div class="metric-sub">std ± {tr_fmt_pct(df['Yuzde_Degisim'].std(), 3)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Pozitif / Negatif</div>
            <div class="metric-value">
                <span class="metric-pos">{poz_say}</span> 
                <span style="color:#1e2d4a">/</span> 
                <span class="metric-neg">{neg_say}</span>
            </div>
            <div class="metric-sub">gün</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Toplam Sıçrama (≥%{esik:.1f})</div>
            <div class="metric-value metric-neu">{len(sicramalar):,}</div>
            <div class="metric-sub">günlerin {tr_fmt_pct(oran, 1)}'i</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">En Büyük / En Küçük</div>
            <div class="metric-value"><span class="metric-pos">+{tr_fmt_pct(max_j, 2, False)}</span></div>
            <div class="metric-sub"><span class="metric-neg">{tr_fmt_pct(min_j, 2, False)}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_jump_cards(sicramalar: pd.DataFrame) -> None:
    """En büyük sıçramaları kart olarak render eder."""
    if len(sicramalar) == 0:
        return
        
    top10 = sicramalar.head(10)
    
    for row_df in [top10.iloc[:5], top10.iloc[5:10]]:
        cols = st.columns(5)
        for i, (_, r) in enumerate(row_df.iterrows()):
            is_pos = r['Yuzde_Degisim'] > 0
            sign = "+" if is_pos else ""
            icon = "↑" if is_pos else "↓"
            global_rank = list(top10.index).index(r.name) + 1
            
            with cols[i]:
                st.markdown(f"""
                <div class="jump-card {'pos' if is_pos else 'neg'}">
                    <div class="jump-rank">#{global_rank} {icon}</div>
                    <div class="jump-date">{r['Tarih'].strftime('%d.%m.%Y')}</div>
                    <div class="jump-pct {'pos' if is_pos else 'neg'}">
                        {sign}{r['Yuzde_Degisim']:.2f}%
                    </div>
                    <div class="jump-meta">{TR_GUN.get(r['Gun_Adi'], r['Gun_Adi'])}</div>
                    <div class="jump-meta">{tr_fmt_kur(r['Onceki_Kur'])} → {tr_fmt_kur(r['Dolar_Kuru'])} ₺</div>
                    <div class="jump-meta">+{int(r['Gun_Farki'])} gün arayla</div>
                </div>
                """, unsafe_allow_html=True)

# =============================================================================
# GRAFİK OLUŞTURUCULAR
# =============================================================================
def create_price_chart(df: pd.DataFrame, esik: float, gosterim_sec: Any) -> go.Figure:
    """Fiyat grafiğini oluşturur."""
    fig = go.Figure()
    
    # Ana fiyat serisi
    fig.add_trace(go.Scatter(
        x=df['Tarih'],
        y=df['Dolar_Kuru'],
        mode='lines',
        name='USD/TRY',
        line=dict(color=Theme.BORDER, width=1.5),
        customdata=list(zip(df['Hover_Tarih'], df['_kur_str'])),
        hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]} ₺<extra></extra>'
    ))
    
    # Sıçramaları bul
    sicramalar = df[df['Abs_Degisim'] >= esik].copy()
    if len(sicramalar) > 0:
        # Pozitif sıçramalar
        pos_j = sicramalar[sicramalar['Yuzde_Degisim'] > 0]
        if len(pos_j) > 0:
            fig.add_trace(go.Scatter(
                x=pos_j['Tarih'],
                y=pos_j['Dolar_Kuru'],
                mode='markers',
                name='↑ Pozitif Sıçrama',
                marker=dict(
                    color=Theme.ACCENT_GREEN,
                    size=pos_j['Abs_Degisim'] * 2.5,
                    line=dict(color=Theme.ACCENT_GREEN, width=2),
                    opacity=0.8
                ),
                customdata=list(zip(
                    pos_j['Hover_Tarih'],
                    pos_j['_pct_str'],
                    pos_j['_onc_kur_str'],
                    pos_j['_kur_str']
                )),
                hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[3]} ₺ ← %{customdata[2]} ₺<br>' +
                             f'<b style="color:{Theme.ACCENT_GREEN}">%{{customdata[1]}}</b><extra></extra>'
            ))
        
        # Negatif sıçramalar
        neg_j = sicramalar[sicramalar['Yuzde_Degisim'] < 0]
        if len(neg_j) > 0:
            fig.add_trace(go.Scatter(
                x=neg_j['Tarih'],
                y=neg_j['Dolar_Kuru'],
                mode='markers',
                name='↓ Negatif Sıçrama',
                marker=dict(
                    color=Theme.ACCENT_RED,
                    size=neg_j['Abs_Degisim'] * 2.5,
                    line=dict(color=Theme.ACCENT_RED, width=2),
                    opacity=0.8
                ),
                customdata=list(zip(
                    neg_j['Hover_Tarih'],
                    neg_j['_pct_str'],
                    neg_j['_onc_kur_str'],
                    neg_j['_kur_str']
                )),
                hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[3]} ₺ ← %{customdata[2]} ₺<br>' +
                             f'<b style="color:{Theme.ACCENT_RED}">%{{customdata[1]}}</b><extra></extra>'
            ))
    
    # Tick ayarları
    tv_k, tt_k = safe_ticks(df['Dolar_Kuru'].min(), df['Dolar_Kuru'].max(), 
                             n=8, decimals=2, is_kur=True)
    
    apply_base(
        fig,
        height=560,
        title=dict(
            text=f"USD/TRY · Eşik %{esik} · Top {gosterim_sec}",
            x=0
        ),
        xaxis=dict(
            tickformat='%b %Y',
            title="Tarih"
        ),
        yaxis=dict(
            tickvals=tv_k if tv_k else None,
            ticktext=tt_k if tt_k else None,
            title="USD/TRY"
        )
    )
    
    return fig

def create_daily_change_chart(df: pd.DataFrame, esik: float, etiket_quantile: int) -> go.Figure:
    """Günlük değişim grafiğini oluşturur."""
    fig = go.Figure()
    
    # Ana değişim serisi
    fig.add_trace(go.Scatter(
        x=df['Tarih'],
        y=df['Yuzde_Degisim'],
        mode='lines',
        name='Günlük Δ',
        line=dict(color=Theme.BORDER, width=1),
        opacity=0.6,
        customdata=list(zip(df['Hover_Tarih'], df['_pct_str'])),
        hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>'
    ))
    
    # Sıçramaları bul
    sicramalar = df[df['Abs_Degisim'] >= esik].copy()
    if len(sicramalar) > 0:
        # Pozitif sıçramalar
        pos_j = sicramalar[sicramalar['Yuzde_Degisim'] > 0].copy()
        if len(pos_j) > 0:
            ethr_pos = pos_j['Yuzde_Degisim'].quantile(1 - etiket_quantile / 100)
            pos_j['_lbl'] = pos_j.apply(
                lambda r: f"{r['Tarih'].strftime('%d.%m')} {tr_fmt_pct(r['Yuzde_Degisim'], 1)}"
                if r['Yuzde_Degisim'] >= ethr_pos else "",
                axis=1
            )
            
            fig.add_trace(go.Scatter(
                x=pos_j['Tarih'],
                y=pos_j['Yuzde_Degisim'],
                mode='markers+text',
                name='↑ Pozitif Sıçrama',
                marker=dict(
                    color=Theme.ACCENT_GREEN,
                    size=pos_j['Abs_Degisim'] * 1.8 + 5,
                    symbol='triangle-up',
                    line=dict(color=Theme.ACCENT_GREEN, width=1),
                    opacity=0.9
                ),
                text=pos_j['_lbl'],
                textposition='top center',
                textfont=dict(size=8, color=Theme.ACCENT_GREEN, family='DM Mono, monospace'),
                customdata=list(zip(pos_j['Hover_Tarih'], pos_j['_onc_kur_str'], 
                                   pos_j['_kur_str'], pos_j['_pct_str'])),
                hovertemplate=f'<b>%{{customdata[0]}}</b><br>%{{customdata[1]}} → %{{customdata[2]}} ₺<br>' +
                             f'<b style="color:{Theme.ACCENT_GREEN}">%{{customdata[3]}}</b><extra></extra>'
            ))
        
        # Negatif sıçramalar
        neg_j = sicramalar[sicramalar['Yuzde_Degisim'] < 0].copy()
        if len(neg_j) > 0:
            ethr_neg = neg_j['Yuzde_Degisim'].quantile(etiket_quantile / 100)
            neg_j['_lbl'] = neg_j.apply(
                lambda r: f"{r['Tarih'].strftime('%d.%m')} {tr_fmt_pct(r['Yuzde_Degisim'], 1)}"
                if r['Yuzde_Degisim'] <= ethr_neg else "",
                axis=1
            )
            
            fig.add_trace(go.Scatter(
                x=neg_j['Tarih'],
                y=neg_j['Yuzde_Degisim'],
                mode='markers+text',
                name='↓ Negatif Sıçrama',
                marker=dict(
                    color=Theme.ACCENT_RED,
                    size=neg_j['Abs_Degisim'] * 1.8 + 5,
                    symbol='triangle-down',
                    line=dict(color=Theme.ACCENT_RED, width=1),
                    opacity=0.9
                ),
                text=neg_j['_lbl'],
                textposition='bottom center',
                textfont=dict(size=8, color=Theme.ACCENT_RED, family='DM Mono, monospace'),
                customdata=list(zip(neg_j['Hover_Tarih'], neg_j['_onc_kur_str'], 
                                   neg_j['_kur_str'], neg_j['_pct_str'])),
                hovertemplate=f'<b>%{{customdata[0]}}</b><br>%{{customdata[1]}} → %{{customdata[2]}} ₺<br>' +
                             f'<b style="color:{Theme.ACCENT_RED}">%{{customdata[3]}}</b><extra></extra>'
            ))
    
    # Eşik çizgileri
    esik_str = str(esik).replace('.', ',')
    fig.add_hline(
        y=esik,
        line_dash="dash",
        line_color=f'rgba(0,212,170,0.5)',
        line_width=1,
        annotation_text=f"+{esik_str}%",
        annotation_font_color=Theme.ACCENT_GREEN,
        annotation_font_size=10
    )
    fig.add_hline(
        y=-esik,
        line_dash="dash",
        line_color=f'rgba(255,77,106,0.5)',
        line_width=1,
        annotation_text=f"−{esik_str}%",
        annotation_font_color=Theme.ACCENT_RED,
        annotation_font_size=10
    )
    fig.add_hline(y=0, line_color=Theme.BORDER, line_width=1)
    
    # Tick ayarları
    tv_p, tt_p = safe_ticks(df['Yuzde_Degisim'].min(), df['Yuzde_Degisim'].max(),
                             n=10, decimals=1, suffix='%')
    
    apply_base(
        fig,
        height=500,
        title=dict(
            text=f"GÜNLÜK DEĞİŞİM · Eşik ±%{esik} · Etiket top %{etiket_quantile}",
            x=0
        ),
        xaxis=dict(
            tickformat='%b %Y',
            title="Tarih"
        ),
        yaxis=dict(
            tickvals=tv_p if tv_p else None,
            ticktext=tt_p if tt_p else None,
            title="Değişim (%)"
        )
    )
    
    return fig

def create_daily_by_day_chart(df: pd.DataFrame, aktif_gunler: List[str]) -> go.Figure:
    """Gün bazlı değişim grafiği oluşturur."""
    fig = go.Figure()
    
    # Arkaplan çizgisi
    fig.add_trace(go.Scatter(
        x=df['Tarih'],
        y=df['Yuzde_Degisim'],
        mode='lines',
        line=dict(color=Theme.BORDER, width=0.7),
        opacity=0.5,
        hoverinfo='skip',
        showlegend=False
    ))
    
    for gun_tr in aktif_gunler:
        sub = df[df['Gun_Adi_TR'] == gun_tr].copy()
        if len(sub) == 0:
            continue
            
        color = GUN_RENKLERI.get(gun_tr, Theme.TEXT_SECONDARY)
        
        fig.add_trace(go.Scatter(
            x=sub['Tarih'],
            y=sub['Yuzde_Degisim'],
            mode='markers',
            name=gun_tr,
            marker=dict(
                color=color,
                size=6,
                opacity=0.8,
                line=dict(color='rgba(0,0,0,0.3)', width=0.5)
            ),
            customdata=list(zip(
                sub['_pct_str'],
                sub['_kur_str'],
                sub['_onc_kur_str']
            )),
            hovertemplate=f'<b>{gun_tr}</b> — %{{x|%d.%m.%Y}}<br>' +
                         'Değişim: <b>%{customdata[0]}</b><br>' +
                         'Kur: %{customdata[2]} → %{customdata[1]} ₺<extra></extra>'
        ))
    
    fig.add_hline(y=0, line_color=Theme.BORDER, line_width=1)
    
    tv_gd, tt_gd = safe_ticks(
        df['Yuzde_Degisim'].min(),
        df['Yuzde_Degisim'].max(),
        n=10, decimals=1, suffix='%'
    )
    
    apply_base(
        fig,
        height=460,
        title=dict(
            text=f"GÜN BAZLI DEĞİŞİM — {', '.join(aktif_gunler)}",
            x=0
        ),
        xaxis=dict(
            tickformat='%b %Y',
            title="Tarih"
        ),
        yaxis=dict(
            tickvals=tv_gd if tv_gd else None,
            ticktext=tt_gd if tt_gd else None,
            title="Değişim (%)"
        )
    )
    
    return fig

def render_day_stats_cards(df: pd.DataFrame, aktif_gunler: List[str]) -> None:
    """Gün bazlı istatistik kartlarını render eder."""
    if not aktif_gunler:
        return
        
    kart_cols = st.columns(len(aktif_gunler))
    
    for i, gun_tr in enumerate(aktif_gunler):
        sub = df[df['Gun_Adi_TR'] == gun_tr]
        if len(sub) == 0:
            with kart_cols[i]:
                st.markdown(f"""
                <div class="metric-card" style="border-top: 2px solid {Theme.TEXT_MUTED};">
                    <div class="metric-label">{gun_tr}</div>
                    <div class="metric-value">Veri yok</div>
                </div>
                """, unsafe_allow_html=True)
            continue
            
        ort = sub['Yuzde_Degisim'].mean()
        std = sub['Yuzde_Degisim'].std()
        maks = sub['Yuzde_Degisim'].max()
        mins = sub['Yuzde_Degisim'].min()
        poz = (sub['Yuzde_Degisim'] > 0).mean() * 100
        color = GUN_RENKLERI.get(gun_tr, Theme.ACCENT_BLUE_LIGHT)
        sign = "+" if ort >= 0 else ""
        
        with kart_cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 2px solid {color};">
                <div class="metric-label" style="color:{color};">{gun_tr}</div>
                <div class="metric-value {'metric-pos' if ort>=0 else 'metric-neg'}">
                    {sign}{ort:.3f}%
                </div>
                <div class="metric-sub">Ort. günlük değişim</div>
                <div style="margin-top:10px;font-size:0.72rem;color:#3a5070;
                            font-family:'DM Mono',monospace;line-height:1.8;">
                    <span style="color:#4a6080">Std:</span> 
                    <span style="color:{color}">±{std:.3f}%</span><br>
                    <span style="color:#4a6080">Max:</span> 
                    <span style="color:{Theme.ACCENT_GREEN}">+{maks:.2f}%</span><br>
                    <span style="color:#4a6080">Min:</span> 
                    <span style="color:{Theme.ACCENT_RED}">{mins:.2f}%</span><br>
                    <span style="color:#4a6080">Poz. oran:</span> 
                    <span style="color:{color}">%{poz:.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_violin_chart(df: pd.DataFrame, gunler: List[str]) -> go.Figure:
    """Violin grafiği oluşturur."""
    fig = go.Figure()
    
    for gun_tr in gunler:
        sub = df[df['Gun_Adi_TR'] == gun_tr]
        if len(sub) == 0:
            continue
            
        color = GUN_RENKLERI.get(gun_tr, Theme.ACCENT_BLUE_LIGHT)
        rr, gg, bb = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        
        fig.add_trace(go.Violin(
            y=sub['Yuzde_Degisim'],
            name=gun_tr,
            line_color=color,
            fillcolor=f'rgba({rr},{gg},{bb},0.12)',
            meanline_visible=True,
            box_visible=True,
            points='outliers',
            hovertemplate=f'<b>{gun_tr}</b><br>%{{y:.3f}}%<extra></extra>'
        ))
    
    fig.add_hline(y=0, line_color=Theme.BORDER, line_dash='dash', line_width=1)
    
    tv_gd, tt_gd = safe_ticks(
        df['Yuzde_Degisim'].min(),
        df['Yuzde_Degisim'].max(),
        n=10, decimals=1, suffix='%'
    )
    
    apply_base(
        fig,
        height=460,
        title=dict(
            text="GÜN BAZLI DEĞİŞİM — VİOLİN",
            x=0
        ),
        yaxis=dict(
            tickvals=tv_gd if tv_gd else None,
            ticktext=tt_gd if tt_gd else None,
            title="Değişim (%)"
        )
    )
    
    return fig

def create_weekly_chart(hf: pd.DataFrame, esik: float, etiket: int) -> go.Figure:
    """Haftalık değişim grafiği oluşturur."""
    fig = go.Figure()
    
    # Ana seri
    fig.add_trace(go.Scatter(
        x=hf['XTarih'],
        y=hf['HaftaDegisim'],
        mode='lines',
        name='Haftalık Δ',
        line=dict(color=Theme.BORDER, width=1),
        opacity=0.6,
        customdata=list(zip(hf['Aralik'], hf['_pzt_str'], hf['_cum_str'], hf['_hf_str'])),
        hovertemplate='<b>%{customdata[0]}</b><br>' +
                     'Pzt: %{customdata[1]} ₺ → Cum: %{customdata[2]} ₺<br>' +
                     '%{customdata[3]}<extra></extra>'
    ))
    
    # Sıçramaları bul
    sicramalar = hf[hf['HaftaDegisim'].abs() >= esik].copy()
    if len(sicramalar) > 0:
        # Pozitif sıçramalar
        hf_pos = sicramalar[sicramalar['HaftaDegisim'] > 0].copy()
        if len(hf_pos) > 0:
            thr_pos = hf_pos['HaftaDegisim'].quantile(1 - etiket/100)
            hf_pos['_lbl'] = hf_pos.apply(
                lambda r: f"{r['Aralik']} {tr_fmt_pct(r['HaftaDegisim'], 1)}"
                if r['HaftaDegisim'] >= thr_pos else "",
                axis=1
            )
            
            fig.add_trace(go.Scatter(
                x=hf_pos['XTarih'],
                y=hf_pos['HaftaDegisim'],
                mode='markers+text',
                name='↑ Pozitif Sıçrama',
                marker=dict(
                    color=Theme.ACCENT_GREEN,
                    size=hf_pos['AbsDegisim'] * 1.8 + 5,
                    symbol='triangle-up',
                    line=dict(color=Theme.ACCENT_GREEN, width=2),
                    opacity=0.9
                ),
                text=hf_pos['_lbl'],
                textposition='top center',
                textfont=dict(size=8, color=Theme.ACCENT_GREEN, family='DM Mono, monospace'),
                customdata=list(zip(hf_pos['Aralik'], hf_pos['_pzt_str'], 
                                   hf_pos['_cum_str'], hf_pos['_hf_str'])),
                hovertemplate=f'<b>%{{customdata[0]}}</b><br>' +
                             f'Pzt: %{{customdata[1]}} ₺ → Cum: %{{customdata[2]}} ₺<br>' +
                             f'<b style="color:{Theme.ACCENT_GREEN}">%{{customdata[3]}}</b><extra></extra>'
            ))
        
        # Negatif sıçramalar
        hf_neg = sicramalar[sicramalar['HaftaDegisim'] < 0].copy()
        if len(hf_neg) > 0:
            thr_neg = hf_neg['HaftaDegisim'].quantile(etiket/100)
            hf_neg['_lbl'] = hf_neg.apply(
                lambda r: f"{r['Aralik']} {tr_fmt_pct(r['HaftaDegisim'], 1)}"
                if r['HaftaDegisim'] <= thr_neg else "",
                axis=1
            )
            
            fig.add_trace(go.Scatter(
                x=hf_neg['XTarih'],
                y=hf_neg['HaftaDegisim'],
                mode='markers+text',
                name='↓ Negatif Sıçrama',
                marker=dict(
                    color=Theme.ACCENT_RED,
                    size=hf_neg['AbsDegisim'] * 1.8 + 5,
                    symbol='triangle-down',
                    line=dict(color=Theme.ACCENT_RED, width=2),
                    opacity=0.9
                ),
                text=hf_neg['_lbl'],
                textposition='bottom center',
                textfont=dict(size=8, color=Theme.ACCENT_RED, family='DM Mono, monospace'),
                customdata=list(zip(hf_neg['Aralik'], hf_neg['_pzt_str'], 
                                   hf_neg['_cum_str'], hf_neg['_hf_str'])),
                hovertemplate=f'<b>%{{customdata[0]}}</b><br>' +
                             f'Pzt: %{{customdata[1]}} ₺ → Cum: %{{customdata[2]}} ₺<br>' +
                             f'<b style="color:{Theme.ACCENT_RED}">%{{customdata[3]}}</b><extra></extra>'
            ))
    
    # Eşik çizgileri
    esik_str = str(esik).replace('.', ',')
    fig.add_hline(
        y=esik,
        line_dash="dash",
        line_color=f'rgba(0,212,170,0.5)',
        line_width=1,
        annotation_text=f"+{esik_str}%",
        annotation_font_color=Theme.ACCENT_GREEN,
        annotation_font_size=10
    )
    fig.add_hline(
        y=-esik,
        line_dash="dash",
        line_color=f'rgba(255,77,106,0.5)',
        line_width=1,
        annotation_text=f"−{esik_str}%",
        annotation_font_color=Theme.ACCENT_RED,
        annotation_font_size=10
    )
    fig.add_hline(y=0, line_color=Theme.BORDER, line_width=1)
    
    tv_hf, tt_hf = safe_ticks(
        hf['HaftaDegisim'].min(),
        hf['HaftaDegisim'].max(),
        n=10, decimals=1, suffix='%'
    )
    
    apply_base(
        fig,
        height=520,
        title=dict(
            text=f"HAFTALIK DEĞİŞİM (Pzt→Cum) · Eşik ±%{esik} · Etiket top %{etiket}",
            x=0
        ),
        xaxis=dict(
            tickformat='%b %Y',
            title="Tarih"
        ),
        yaxis=dict(
            tickvals=tv_hf if tv_hf else None,
            ticktext=tt_hf if tt_hf else None,
            title="Değişim (%)"
        )
    )
    
    return fig

def render_weekly_kpis(hf: pd.DataFrame, esik: float) -> None:
    """Haftalık KPI kartlarını render eder."""
    hf_ort = hf['HaftaDegisim'].mean()
    hf_maks = hf['HaftaDegisim'].max()
    hf_mins = hf['HaftaDegisim'].min()
    hf_pos_n = (hf['HaftaDegisim'] >= esik).sum()
    hf_neg_n = (hf['HaftaDegisim'] <= -esik).sum()
    sign_hf = "+" if hf_ort >= 0 else ""
    esik_str = str(esik).replace('.', ',')
    
    st.markdown(f"""
    <div class="metric-row" style="grid-template-columns: repeat(5, 1fr);">
        <div class="metric-card" style="border-top:2px solid {Theme.ACCENT_BLUE_LIGHT};">
            <div class="metric-label">Haftalık Ort.</div>
            <div class="metric-value metric-{'pos' if hf_ort>=0 else 'neg'}">
                {sign_hf}{hf_ort:.3f}%
            </div>
            <div class="metric-sub">Pzt→Cum ort.</div>
        </div>
        <div class="metric-card" style="border-top:2px solid {Theme.ACCENT_GREEN};">
            <div class="metric-label">≥ +%{esik_str} hafta</div>
            <div class="metric-value metric-pos">{hf_pos_n}</div>
            <div class="metric-sub">pozitif büyük hafta</div>
        </div>
        <div class="metric-card" style="border-top:2px solid {Theme.ACCENT_RED};">
            <div class="metric-label">≤ −%{esik_str} hafta</div>
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

def render_weekly_table(hf: pd.DataFrame) -> None:
    """Haftalık değişim tablosunu render eder."""
    hf_tablo = hf[['PztTarih', 'CumTarih', 'PztKur', 'CumKur', 'HaftaDegisim']].copy()
    hf_tablo['Hafta'] = hf_tablo['PztTarih'].dt.strftime('%d.%m.%Y') + ' – ' + \
                        hf_tablo['CumTarih'].dt.strftime('%d.%m.%Y')
    hf_tablo['Yıl'] = hf_tablo['PztTarih'].dt.year
    hf_tablo['Pzt Kur'] = hf_tablo['PztKur'].apply(tr_fmt_kur)
    hf_tablo['Cum Kur'] = hf_tablo['CumKur'].apply(tr_fmt_kur)
    hf_tablo['Değişim %'] = hf_tablo['HaftaDegisim'].apply(tr_fmt_pct)
    hf_tablo['Yön'] = hf_tablo['HaftaDegisim'].apply(lambda x: '↑' if x > 0 else '↓')
    
    hf_tablo = hf_tablo[['Yıl', 'Hafta', 'Pzt Kur', 'Cum Kur', 'Değişim %', 'Yön']]\
        .sort_values('Hafta', ascending=False)\
        .reset_index(drop=True)
    
    styled = style_dataframe(hf_tablo)
    st.dataframe(styled, use_container_width=True, height=420)

def create_monthly_change_chart(df: pd.DataFrame, aktif_gunler: List[str]) -> go.Figure:
    """Aylık değişim grafiği oluşturur."""
    aylik_g = df.dropna(subset=['Aylik_Degisim']).copy()
    
    if aktif_gunler:
        aylik_g = aylik_g[aylik_g['Gun_Adi_TR'].isin(aktif_gunler)]
    
    if len(aylik_g) == 0:
        return go.Figure()
    
    aylik_g['renk'] = aylik_g['Aylik_Degisim'].apply(
        lambda x: Theme.ACCENT_BLUE_LIGHT if x >= 0 else Theme.ACCENT_RED
    )
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=aylik_g['Tarih'],
        y=aylik_g['Aylik_Degisim'],
        marker_color=aylik_g['renk'].values,
        opacity=0.8,
        customdata=list(zip(
            aylik_g['Gun_Adi_TR'],
            aylik_g['Aylik_Degisim'].apply(lambda x: tr_fmt_pct(x, 2))
        )),
        hovertemplate='%{x|%d.%m.%Y} (%{customdata[0]})<br>' +
                     '21G: <b>%{customdata[1]}</b><extra></extra>'
    ))
    
    fig.add_hline(y=0, line_color=Theme.BORDER, line_width=1)
    
    tv_am, tt_am = safe_ticks(
        aylik_g['Aylik_Degisim'].min(),
        aylik_g['Aylik_Degisim'].max(),
        n=8, decimals=1, suffix='%'
    )
    
    apply_base(
        fig,
        height=340,
        title=dict(
            text="21 GÜNLÜK (AYLIK) DEĞİŞİM",
            x=0
        ),
        yaxis=dict(
            tickvals=tv_am if tv_am else None,
            ticktext=tt_am if tt_am else None,
            title="Değişim (%)"
        ),
        xaxis=dict(
            tickformat='%b %Y',
            title="Tarih"
        ),
        showlegend=False
    )
    
    return fig

def create_volatility_chart(df: pd.DataFrame) -> go.Figure:
    """Volatilite grafiği oluşturur."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Tarih'],
        y=df['Vol_20'],
        mode='lines',
        name='20G Vol',
        line=dict(color=Theme.ACCENT_BLUE_LIGHT, width=1.5),
        fill='tozeroy',
        fillcolor='rgba(74,158,255,0.05)',
        customdata=df['Vol_20'].apply(lambda x: tr_fmt_pct(x, 3) if pd.notna(x) else ""),
        hovertemplate='%{x|%d.%m.%Y}<br>20G: <b>%{customdata}</b><extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Tarih'],
        y=df['Vol_60'],
        mode='lines',
        name='60G Vol',
        line=dict(color=Theme.ACCENT_RED, width=1.2, dash='dot'),
        customdata=df['Vol_60'].apply(lambda x: tr_fmt_pct(x, 3) if pd.notna(x) else ""),
        hovertemplate='%{x|%d.%m.%Y}<br>60G: <b>%{customdata}</b><extra></extra>'
    ))
    
    vol_max = df['Vol_20'].dropna().max() if df['Vol_20'].dropna().shape[0] > 0 else 1.0
    tv_vol, tt_vol = safe_ticks(0, vol_max, n=6, decimals=2, suffix='%')
    
    apply_base(
        fig,
        height=340,
        title=dict(
            text="YUVARLANMALI VOLATİLİTE",
            x=0
        ),
        yaxis=dict(
            tickvals=tv_vol if tv_vol else None,
            ticktext=tt_vol if tt_vol else None,
            title="Volatilite (%)"
        ),
        xaxis=dict(
            tickformat='%b %Y',
            title="Tarih"
        )
    )
    
    return fig

def create_monthly_heatmap(df: pd.DataFrame) -> go.Figure:
    """Yıl-Ay ısı haritası oluşturur."""
    ay_pivot = df.groupby(['Yil', 'Ay'])['Yuzde_Degisim'].mean().unstack(fill_value=np.nan)
    ay_pivot.columns = [TR_AY.get(c, str(c)) for c in ay_pivot.columns]
    
    text_matrix = np.where(
        np.isnan(ay_pivot.values),
        "",
        np.vectorize(lambda v: tr_fmt_pct(v, 2, False))(ay_pivot.values)
    )
    
    fig = go.Figure(go.Heatmap(
        z=ay_pivot.values,
        x=ay_pivot.columns.tolist(),
        y=ay_pivot.index.astype(str).tolist(),
        colorscale=[[0, Theme.ACCENT_RED], [0.5, Theme.BG_SECONDARY], [1, Theme.ACCENT_GREEN]],
        zmid=0,
        text=text_matrix,
        texttemplate="%{text}",
        textfont=dict(size=9, family='DM Mono, monospace', color=Theme.TEXT_PRIMARY),
        hovertemplate='<b>%{y} — %{x}</b><br>Ort. Günlük: <b>%{text}</b><extra></extra>',
        colorbar=dict(
            title="Ort. Değişim",
            tickfont=dict(size=9, color=Theme.TEXT_MUTED)
        )
    ))
    
    apply_base(
        fig,
        height=500,
        title=dict(
            text="YIL–AY ORTALAMA GÜNLÜK DEĞİŞİM",
            x=0
        ),
        xaxis=dict(
            side='bottom',
            tickfont=dict(size=11, color=Theme.TEXT_MUTED),
            title="Ay"
        ),
        yaxis=dict(
            tickfont=dict(size=11, color=Theme.TEXT_MUTED),
            autorange='reversed',
            title="Yıl"
        )
    )
    
    return fig

def create_cumulative_jumps_chart(sicramalar: pd.DataFrame) -> go.Figure:
    """Kümülatif sıçrama grafiği oluşturur."""
    if len(sicramalar) == 0:
        return go.Figure()
        
    cum_df = sicramalar.sort_values('Tarih').reset_index(drop=True)
    cum_df['Kumulatif'] = range(1, len(cum_df) + 1)
    
    fig = go.Figure(go.Scatter(
        x=cum_df['Tarih'],
        y=cum_df['Kumulatif'],
        fill='tozeroy',
        line=dict(color=Theme.ACCENT_BLUE_LIGHT, width=1.5),
        fillcolor='rgba(74,158,255,0.06)',
        hovertemplate='%{x|%d.%m.%Y}<br>Toplam: <b>%{y}</b> sıçrama<extra></extra>'
    ))
    
    apply_base(
        fig,
        height=380,
        title=dict(
            text="KÜMÜLATİF SIÇRAMA SAYISI",
            x=0
        ),
        xaxis=dict(
            tickformat='%b %Y',
            title="Tarih"
        ),
        yaxis=dict(
            title="Sıçrama Sayısı"
        )
    )
    
    return fig

def create_monthly_jumps_chart(sicramalar: pd.DataFrame) -> go.Figure:
    """Aylık sıçrama grafiği oluşturur."""
    if len(sicramalar) == 0:
        return go.Figure()
        
    ay_order_tr = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                   'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
    
    sicramalar['Ay_Adi_TR'] = sicramalar['Ay'].map(TR_AY_UZUN)
    ay_sayim = sicramalar.groupby('Ay_Adi_TR').size().reindex(ay_order_tr).fillna(0)
    
    fig = go.Figure(go.Bar(
        x=ay_sayim.index,
        y=ay_sayim.values,
        marker=dict(
            color=ay_sayim.values,
            colorscale=[[0, Theme.BORDER], [1, Theme.ACCENT_BLUE_LIGHT]],
            line=dict(color='rgba(255,255,255,0.05)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>%{y} sıçrama<extra></extra>'
    ))
    
    apply_base(
        fig,
        height=350,
        title=dict(
            text="AYLARA GÖRE SIÇRAMA SAYISI",
            x=0
        ),
        xaxis=dict(
            title="Ay"
        ),
        yaxis=dict(
            title="Sıçrama Sayısı"
        ),
        showlegend=False
    )
    
    return fig

def create_magnitude_distribution_chart(sicramalar: pd.DataFrame) -> go.Figure:
    """Sıçrama büyüklük dağılımı grafiği oluşturur."""
    if len(sicramalar) == 0:
        return go.Figure()
        
    fig = go.Figure()
    
    pozitif = sicramalar[sicramalar['Yuzde_Degisim'] > 0]
    if len(pozitif) > 0:
        fig.add_trace(go.Histogram(
            x=pozitif['Yuzde_Degisim'],
            nbinsx=25,
            name='↑ Pozitif',
            marker_color=Theme.ACCENT_GREEN,
            opacity=0.7,
            hovertemplate='%{x:.1f}% — %{y} adet<extra></extra>'
        ))
    
    negatif = sicramalar[sicramalar['Yuzde_Degisim'] < 0]
    if len(negatif) > 0:
        fig.add_trace(go.Histogram(
            x=negatif['Yuzde_Degisim'],
            nbinsx=25,
            name='↓ Negatif',
            marker_color=Theme.ACCENT_RED,
            opacity=0.7,
            hovertemplate='%{x:.1f}% — %{y} adet<extra></extra>'
        ))
    
    apply_base(
        fig,
        height=380,
        barmode='overlay',
        title=dict(
            text="SIÇRAMA BÜYÜKLÜKLERİ DAĞILIMI",
            x=0
        ),
        xaxis=dict(
            ticksuffix='%',
            title="Değişim (%)"
        ),
        yaxis=dict(
            title="Frekans"
        )
    )
    
    return fig

def create_density_heatmap(sicramalar: pd.DataFrame) -> go.Figure:
    """Yoğunluk ısı haritası oluşturur."""
    if len(sicramalar) == 0:
        return go.Figure()
        
    pivot = sicramalar.groupby(['Yil', 'Ay']).size().unstack(fill_value=0)
    ay_labels = [TR_AY.get(c, str(c)) for c in pivot.columns]
    
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=ay_labels,
        y=pivot.index.astype(str),
        colorscale=[[0, Theme.BG_SECONDARY], [0.5, Theme.ACCENT_BLUE], [1, Theme.ACCENT_GREEN]],
        text=pivot.values,
        texttemplate="%{text}",
        textfont=dict(size=9, color=Theme.TEXT_PRIMARY, family='DM Mono, monospace'),
        hovertemplate='<b>%{y} — %{x}</b><br>%{z} sıçrama<extra></extra>',
        colorbar=dict(
            title="Sıçrama Sayısı",
            tickfont=dict(size=9, color=Theme.TEXT_MUTED)
        )
    ))
    
    apply_base(
        fig,
        height=350,
        title=dict(
            text="YIL–AY SIÇRAMA YOĞUNLUĞU",
            x=0
        ),
        xaxis=dict(
            side='bottom',
            tickfont=dict(size=11, color=Theme.TEXT_MUTED),
            title="Ay"
        ),
        yaxis=dict(
            tickfont=dict(size=11, color=Theme.TEXT_MUTED),
            autorange='reversed',
            title="Yıl"
        )
    )
    
    return fig

def create_weekly_pattern_chart(sicramalar: pd.DataFrame) -> go.Figure:
    """Haftalık pattern grafiği oluşturur."""
    if len(sicramalar) == 0:
        return go.Figure()
        
    gun_order_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    sicramalar['Gun_Adi_TR'] = sicramalar['Gun_Adi'].map(TR_GUN)
    gun_sayim = sicramalar.groupby('Gun_Adi_TR').size().reindex(gun_order_tr).fillna(0)
    
    fig = go.Figure(go.Bar(
        x=gun_sayim.index,
        y=gun_sayim.values,
        marker=dict(
            color=gun_sayim.values,
            colorscale=[[0, Theme.BORDER], [1, Theme.ACCENT_PURPLE]],
            line=dict(color='rgba(255,255,255,0.05)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>%{y} sıçrama<extra></extra>'
    ))
    
    apply_base(
        fig,
        height=340,
        title=dict(
            text="HAFTANIN GÜNLERİNE GÖRE SIÇRAMA SAYISI",
            x=0
        ),
        xaxis=dict(
            title="Gün"
        ),
        yaxis=dict(
            title="Sıçrama Sayısı"
        ),
        showlegend=False
    )
    
    return fig

def create_forward_boxplot(fwd: Dict, periods: List[int], 
                          period_labels: Dict) -> go.Figure:
    """Forward analiz box plot oluşturur."""
    fig = go.Figure()
    colors_box = [Theme.ACCENT_BLUE_LIGHT, Theme.ACCENT_GREEN, 
                  Theme.ACCENT_ORANGE, Theme.ACCENT_PURPLE, Theme.ACCENT_RED]
    
    for i, p in enumerate(periods):
        if p in fwd and len(fwd[p]['raw']) > 0:
            c = colors_box[i % len(colors_box)]
            rr, gg, bb = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
            
            fig.add_trace(go.Box(
                y=fwd[p]['raw'],
                name=period_labels[p],
                marker_color=c,
                boxpoints='outliers',
                line_width=1.5,
                fillcolor=f'rgba({rr},{gg},{bb},0.1)',
                hovertemplate='%{y:.3f}%<extra></extra>'
            ))
    
    fig.add_hline(y=0, line_color=Theme.BORDER, line_width=1, line_dash='dash')
    
    apply_base(
        fig,
        height=480,
        title=dict(
            text="SIÇRAMA SONRASI DEĞİŞİM DAĞILIMI",
            x=0
        ),
        yaxis=dict(
            ticksuffix='%',
            title="Değişim (%)"
        )
    )
    
    return fig

def create_win_rate_chart(fwd: Dict, periods: List[int], 
                          period_labels: Dict) -> go.Figure:
    """Kazanma oranı grafiği oluşturur."""
    pos_rates = []
    period_names = []
    
    for p in periods:
        if p in fwd:
            pos_rates.append(fwd[p]['pos_pct'])
            period_names.append(period_labels[p])
    
    if not pos_rates:
        return go.Figure()
    
    fig = go.Figure(go.Bar(
        x=period_names,
        y=pos_rates,
        marker_color=[Theme.ACCENT_GREEN if v >= 50 else Theme.ACCENT_RED for v in pos_rates],
        text=[f"%{v:.0f}" for v in pos_rates],
        textposition='outside',
        textfont=dict(size=11, color=Theme.TEXT_SECONDARY, family='DM Mono, monospace'),
        hovertemplate='%{x}<br>Pozitif oran: <b>%{y:.1f}%</b><extra></extra>'
    ))
    
    fig.add_hline(
        y=50,
        line_dash='dash',
        line_color=Theme.BORDER,
        line_width=1,
        annotation_text="50%",
        annotation_font_color=Theme.TEXT_MUTED
    )
    
    apply_base(
        fig,
        height=360,
        title=dict(
            text="DÖNEM SONU POZİTİF KAPANIŞ ORANI",
            x=0
        ),
        yaxis=dict(
            ticksuffix='%',
            range=[0, 105],
            title="Pozitif Oran (%)"
        ),
        showlegend=False
    )
    
    return fig

def create_threshold_sensitivity(df: pd.DataFrame) -> go.Figure:
    """Eşik hassasiyeti grafiği oluşturur."""
    thresholds = np.arange(1.0, 12.0, 0.5)
    means_21, counts_21 = [], []
    
    for thr in thresholds:
        f = forward_analysis(df, thr, [21])
        if 21 in f and f[21]['n'] >= 5:
            means_21.append(f[21]['mean'])
            counts_21.append(f[21]['n'])
        else:
            means_21.append(np.nan)
            counts_21.append(0)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=thresholds,
            y=means_21,
            mode='lines+markers',
            name='Ort. 21G Değişim',
            line=dict(color=Theme.ACCENT_BLUE_LIGHT, width=2),
            marker=dict(size=6),
            hovertemplate='Eşik: %{x:.1f}%<br>Ort. 21G: <b>%{y:.2f}%</b><extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=thresholds,
            y=counts_21,
            name='Örnek Sayısı',
            marker_color='rgba(74,158,255,0.15)',
            hovertemplate='Eşik: %{x:.1f}%<br>n: %{y}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.add_hline(y=0, line_color=Theme.BORDER, line_width=1)
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(13,18,32,0.9)',
        font=dict(color=Theme.TEXT_SECONDARY, family='DM Sans, sans-serif', size=11),
        height=400,
        title=dict(
            text="EŞİK HASSASİYETİ — 21G ORTALAMA DEĞİŞİM",
            font=dict(size=13, color=Theme.TEXT_MUTED, family='DM Mono, monospace'),
            x=0
        ),
        legend=dict(
            bgcolor='rgba(13,18,32,0.8)',
            bordercolor=Theme.BORDER,
            font=dict(size=10)
        ),
        hoverlabel=dict(
            bgcolor=Theme.BG_SECONDARY,
            font_size=11,
            font_color=Theme.TEXT_PRIMARY
        ),
        xaxis=dict(
            title="Eşik (%)",
            gridcolor='#131c2e',
            ticksuffix='%'
        ),
        yaxis=dict(
            title="Ortalama Değişim (%)",
            gridcolor='#131c2e',
            ticksuffix='%'
        ),
        yaxis2=dict(
            title="Örnek Sayısı",
            gridcolor='#0d1220',
            tickfont=dict(size=9, color='#3a5070')
        ),
        margin=dict(l=60, r=40, t=60, b=50)
    )
    
    return fig

def create_jumps_table(top_sic: pd.DataFrame) -> pd.DataFrame:
    """Sıçrama tablosu oluşturur."""
    if len(top_sic) == 0:
        return pd.DataFrame()
        
    tbl = top_sic.copy().reset_index(drop=True)
    tbl.index = tbl.index + 1
    
    return pd.DataFrame({
        '#': tbl.index,
        'Tarih': tbl['Tarih'].dt.strftime('%d.%m.%Y'),
        'Yıl': tbl['Yil'],
        'Ay': tbl['Ay_Adi'],
        'Gün Adı': tbl['Gun_Adi'],
        'Kur': tbl['Dolar_Kuru'].apply(tr_fmt_kur),
        'Önceki Kur': tbl['Onceki_Kur'].apply(tr_fmt_kur),
        'Değişim %': tbl['Yuzde_Degisim'].apply(tr_fmt_pct),
        'TL Δ': tbl['TL_Degisim'].apply(lambda x: tr_fmt_kur(x, 4)),
        'Gün Farkı': tbl['Gun_Farki'].astype(int),
    })

def create_monthly_summary(sicramalar: pd.DataFrame) -> pd.DataFrame:
    """Aylık özet tablosu oluşturur."""
    if len(sicramalar) == 0:
        return pd.DataFrame()
        
    aylik = sicramalar.groupby('Ay_Adi')['Abs_Degisim'].agg(['count', 'mean', 'max', 'min']).round(3)
    aylik.columns = ['Toplam', 'Ort. %', 'Maks %', 'Min %']
    return aylik

def create_yearly_summary(sicramalar: pd.DataFrame) -> pd.DataFrame:
    """Yıllık özet tablosu oluşturur."""
    if len(sicramalar) == 0:
        return pd.DataFrame()
        
    yillik = sicramalar.groupby('Yil').agg(
        Toplam=('Abs_Degisim', 'count'),
        Ort_Pct=('Abs_Degisim', 'mean'),
        Pozitif=('Yuzde_Degisim', lambda x: (x > 0).sum()),
        Negatif=('Yuzde_Degisim', lambda x: (x < 0).sum()),
        Maks=('Abs_Degisim', 'max')
    ).round(3)
    yillik.columns = ['Toplam', 'Ort. %', 'Pozitif', 'Negatif', 'Maks %']
    return yillik

def create_weekly_summary_table(hf: pd.DataFrame) -> pd.DataFrame:
    """Haftalık özet tablosu oluşturur."""
    if len(hf) == 0:
        return pd.DataFrame()
        
    hf_t = hf[['PztTarih', 'CumTarih', 'PztKur', 'CumKur', 'HaftaDegisim']].copy()
    hf_t.insert(0, 'Hafta', hf_t['PztTarih'].dt.strftime('%d.%m.%Y') + ' – ' + 
                hf_t['CumTarih'].dt.strftime('%d.%m.%Y'))
    hf_t.insert(0, 'Yıl', hf_t['PztTarih'].dt.year)
    hf_t['Pzt Kur'] = hf_t['PztKur'].apply(tr_fmt_kur)
    hf_t['Cum Kur'] = hf_t['CumKur'].apply(tr_fmt_kur)
    hf_t['Değişim %'] = hf_t['HaftaDegisim'].apply(tr_fmt_pct)
    hf_t['Yön'] = hf_t['HaftaDegisim'].apply(lambda x: '↑' if x > 0 else '↓')
    
    hf_t = hf_t[['Yıl', 'Hafta', 'Pzt Kur', 'Cum Kur', 'Değişim %', 'Yön']]\
        .sort_values('Hafta', ascending=False)\
        .reset_index(drop=True)
    hf_t.index = hf_t.index + 1
    
    return hf_t

def render_export_buttons(top_sic: pd.DataFrame, hf_t: pd.DataFrame, 
                         df: pd.DataFrame, aylik: pd.DataFrame, 
                         yillik: pd.DataFrame) -> None:
    """Dışa aktar butonlarını render eder."""
    col1, col2 = st.columns(2)
    
    with col1:
        if len(top_sic) > 0:
            csv = top_sic.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 CSV İndir (Sıçramalar)",
                csv,
                "sicramalar.csv",
                "text/csv"
            )
    
    with col2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            if len(top_sic) > 0:
                top_sic.to_excel(w, sheet_name='Sicramalar', index=False)
            if len(hf_t) > 0:
                hf_t.to_excel(w, sheet_name='Haftalik', index=False)
            df.to_excel(w, sheet_name='Tum_Veri', index=False)
            if len(aylik) > 0:
                aylik.to_excel(w, sheet_name='Aylik')
            if len(yillik) > 0:
                yillik.to_excel(w, sheet_name='Yillik')
        
        st.download_button(
            "📥 Excel İndir (Tüm Analiz)",
            buf.getvalue(),
            "usdtry_analiz.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def style_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame'e stil uygular."""
    def color_row(val):
        if isinstance(val, str) and val.endswith('%'):
            try:
                num = float(val.replace(',', '.').replace('%', '').replace('+', ''))
                if num > 0:
                    return f'color: {Theme.ACCENT_GREEN}'
                elif num < 0:
                    return f'color: {Theme.ACCENT_RED}'
            except Exception:
                pass
        return ''
    
    subset = ['Değişim %'] if 'Değişim %' in df.columns else []
    
    styled = (df.style
        .applymap(color_row, subset=subset)
        .set_properties(**{
            'background-color': Theme.BG_SECONDARY,
            'color': '#8aa0bf',
            'border': f'1px solid {Theme.BORDER}',
            'font-family': 'DM Mono, monospace',
            'font-size': '12px'
        })
        .set_table_styles([
            {
                'selector': 'th',
                'props': [
                    ('background-color', Theme.BG_PRIMARY),
                    ('color', Theme.TEXT_MUTED),
                    ('font-family', 'DM Mono, monospace'),
                    ('font-size', '11px'),
                    ('text-transform', 'uppercase'),
                    ('letter-spacing', '0.08em'),
                    ('border', f'1px solid {Theme.BORDER}'),
                    ('padding', '8px 12px')
                ]
            },
            {
                'selector': 'td',
                'props': [('padding', '6px 12px')]
            },
            {
                'selector': 'tr:hover td',
                'props': [('background-color', '#131c2e')]
            }
        ]))
    
    return styled

# =============================================================================
# SIDEBAR BİLEŞENİ
# =============================================================================
def render_sidebar() -> Tuple[float, Any, int, float, int, List[str], float, Any]:
    """Sidebar kontrollerini render eder."""
    with st.sidebar:
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.15em; color:{Theme.ACCENT_BLUE}; padding:16px 0 12px 0;
                    border-bottom:1px solid {Theme.BORDER};">
            ◈ Parametre Kontrolü
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Ana parametreler
        esik = st.slider(
            "📊 Günlük Sıçrama Eşiği (%)",
            min_value=0.5,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="Bu eşiğin üzerindeki günlük değişimler 'sıçrama' olarak kabul edilir."
        )
        
        gosterim_sec = st.selectbox(
            "📋 Gösterilecek Sıçrama Sayısı",
            options=[10, 20, 30, 50, 75, 100, "Tümü"],
            index=2,
            help="Tablolarda ve grafiklerde kaç sıçramanın gösterileceği."
        )
        
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.15em; color:{Theme.ACCENT_BLUE}; padding:20px 0 12px 0;
                    border-bottom:1px solid {Theme.BORDER};">
            ◈ Etiket Ayarı
        </div>
        """, unsafe_allow_html=True)
        
        etiket_quantile = st.slider(
            "🏷️ Etiketlenecek Dilim (%)",
            min_value=10,
            max_value=100,
            value=40,
            step=5,
            help="En büyük sıçramaların yüzde kaçının grafikte etiketleneceği."
        )
        
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.15em; color:{Theme.ACCENT_BLUE}; padding:20px 0 12px 0;
                    border-bottom:1px solid {Theme.BORDER};">
            ◈ Haftalık Analiz
        </div>
        """, unsafe_allow_html=True)
        
        haftalik_esik = st.slider(
            "📈 Haftalık Sıçrama Eşiği (%)",
            min_value=0.0,
            max_value=20.0,
            value=3.0,
            step=0.5,
            help="Haftalık değişimler için sıçrama eşiği."
        )
        
        haftalik_etiket = st.slider(
            "🏷️ Haftalık Etiket Dilimi (%)",
            min_value=10,
            max_value=100,
            value=40,
            step=5,
            key="haftalik_etiket"
        )
        
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.15em; color:{Theme.ACCENT_BLUE}; padding:20px 0 12px 0;
                    border-bottom:1px solid {Theme.BORDER};">
            ◈ Gün Filtresi
        </div>
        """, unsafe_allow_html=True)
        
        gun_filtre = st.multiselect(
            "📅 Gün Filtresi",
            options=["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"],
            default=[],
            help="Analiz edilecek günleri filtreleyin."
        )
        
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.15em; color:{Theme.ACCENT_BLUE}; padding:20px 0 12px 0;
                    border-bottom:1px solid {Theme.BORDER};">
            ◈ İleri Analiz
        </div>
        """, unsafe_allow_html=True)
        
        fwd_threshold = st.slider(
            "🔮 Tetikleyici Eşik (%)",
            min_value=0.5,
            max_value=15.0,
            value=3.0,
            step=0.5,
            help="İleri analiz için kullanılacak sıçrama eşiği."
        )
        
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                    letter-spacing:0.15em; color:{Theme.ACCENT_BLUE}; padding:20px 0 12px 0;
                    border-bottom:1px solid {Theme.BORDER};">
            ◈ Veri Kaynağı
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📂 Excel Dosyası (.xlsx)",
            type=['xlsx', 'xls'],
            help="EVDS'den indirilen Excel dosyasını yükleyin."
        )
        
        st.markdown(f"""
        <div style="font-size:0.72rem; color:#3a5070; margin-top:8px; line-height:1.7;">
            Sayfa: <span style="color:{Theme.ACCENT_BLUE_LIGHT}; font-family:'DM Mono',monospace;">EVDS</span><br>
            Sütun 1: <span style="color:{Theme.ACCENT_BLUE_LIGHT}; font-family:'DM Mono',monospace;">Tarih (DD-MM-YYYY)</span><br>
            Sütun 2: <span style="color:{Theme.ACCENT_BLUE_LIGHT}; font-family:'DM Mono',monospace;">TP_DK_USD_A_YTL</span>
        </div>
        """, unsafe_allow_html=True)
        
        return (esik, gosterim_sec, etiket_quantile, haftalik_esik, 
                haftalik_etiket, gun_filtre, fwd_threshold, uploaded_file)

# =============================================================================
# TAB İÇERİKLERİ
# =============================================================================
def render_tab1(df: pd.DataFrame, esik: float, gosterim_sec: Any, etiket_quantile: int) -> None:
    """Günlük Analiz tab'ını render eder."""
    create_section_header("Dolar Kuru & Sıçrama Noktaları")
    
    # Fiyat grafiği
    fig1 = create_price_chart(df, esik, gosterim_sec)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Günlük değişim grafiği
    create_section_header("Günlük Değişim")
    fig2 = create_daily_change_chart(df, esik, etiket_quantile)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top 10 kartları
    sicramalar = df[df['Abs_Degisim'] >= esik].copy()
    if len(sicramalar) > 0:
        create_section_header("En Büyük 10 Sıçrama")
        render_jump_cards(sicramalar)

def render_tab2(df: pd.DataFrame, hf_global: pd.DataFrame, gun_filtre: List[str],
                haftalik_esik: float, haftalik_etiket: int) -> None:
    """Haftalık & Aylık Analiz tab'ını render eder."""
    ALL_DAYS_TR = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
    aktif_gunler = gun_filtre if gun_filtre else ALL_DAYS_TR
    
    # Gün bazlı scatter
    create_section_header("Günlük Değişim — Gün Bazlı Karşılaştırma")
    fig_gd = create_daily_by_day_chart(df, aktif_gunler)
    st.plotly_chart(fig_gd, use_container_width=True)
    
    # Gün istatistik kartları
    create_section_header("Gün Bazlı İstatistikler")
    render_day_stats_cards(df, aktif_gunler)
    
    # Violin grafiği
    create_section_header("Dağılım Karşılaştırması (Violin)")
    fig_vio = create_violin_chart(df, ALL_DAYS_TR)
    st.plotly_chart(fig_vio, use_container_width=True)
    
    # Haftalık değişim
    create_section_header("Haftalık Değişim — Pazartesi → Cuma")
    fig_hw = create_weekly_chart(hf_global, haftalik_esik, haftalik_etiket)
    st.plotly_chart(fig_hw, use_container_width=True)
    
    # Haftalık KPI'lar
    if len(hf_global) > 0:
        render_weekly_kpis(hf_global, haftalik_esik)
        
        # Haftalık tablo
        create_section_header("Haftalık Değişim Tablosu")
        render_weekly_table(hf_global)
    
    # Aylık değişim ve volatilite
    col_am1, col_am2 = st.columns(2)
    with col_am1:
        create_section_header("Aylık Değişim (21 Gün)")
        fig_am = create_monthly_change_chart(df, aktif_gunler)
        if fig_am.data:
            st.plotly_chart(fig_am, use_container_width=True)
    
    with col_am2:
        create_section_header("Yuvarlanmalı Volatilite")
        fig_vol = create_volatility_chart(df)
        st.plotly_chart(fig_vol, use_container_width=True)
    
    # Yıl-Ay ısı haritası
    create_section_header("Yıl–Ay Ortalama Günlük Değişim (Isı Haritası)")
    fig_heat = create_monthly_heatmap(df)
    st.plotly_chart(fig_heat, use_container_width=True)

def render_tab3(df: pd.DataFrame, fwd_threshold: float) -> None:
    """İleri Analiz tab'ını render eder."""
    create_section_header(f"Büyük Sıçramalardan Sonra Ne Oluyor? (≥%{fwd_threshold})")
    
    periods = [1, 5, 10, 21, 63]
    period_labels = {1: '1G', 5: '5G (1Hf)', 10: '10G (2Hf)', 
                     21: '21G (1Ay)', 63: '63G (3Ay)'}
    
    fwd = forward_analysis(df, fwd_threshold, periods)
    
    if not fwd:
        st.warning(f"%{fwd_threshold} eşiğinde yeterli sıçrama bulunamadı.")
        return
    
    # Forward kartları
    cards_html = ""
    for p in periods:
        if p in fwd:
            r = fwd[p]
            if r['n'] > 0:
                mean_cls = "metric-pos" if r['mean'] >= 0 else "metric-neg"
                sign = "+" if r['mean'] >= 0 else ""
                
                cards_html += f"""
                <div class="forward-card">
                    <div class="forward-title">{period_labels[p]} Sonra</div>
                    <div class="forward-big {mean_cls}">{sign}{r['mean']:.2f}%</div>
                    <div class="forward-detail">
                        <span style="color:#4a6080">Medyan:</span> 
                        <span class="forward-accent">{'+' if r['median']>=0 else ''}{r['median']:.2f}%</span><br>
                        <span style="color:#4a6080">Pozitif oran:</span> 
                        <span class="forward-accent">%{r['pos_pct']:.0f}</span><br>
                        <span style="color:#4a6080">IQR:</span> 
                        <span class="forward-accent">{r['p25']:.2f}% — {r['p75']:.2f}%</span><br>
                        <span style="color:#4a6080">Örnek:</span> 
                        <span class="forward-accent">{r['n']}</span>
                    </div>
                </div>"""
    
    if cards_html:
        st.markdown(f'<div class="forward-grid">{cards_html}</div>', unsafe_allow_html=True)
    
    # Box plot
    create_section_header("Dağılım (Box Plot)")
    fig_box = create_forward_boxplot(fwd, periods, period_labels)
    if fig_box.data:
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Pozitif kapanış oranı
    create_section_header("Pozitif Kapanış Oranı (Her Dönem)")
    fig_win = create_win_rate_chart(fwd, periods, period_labels)
    if fig_win.data:
        st.plotly_chart(fig_win, use_container_width=True)
    
    # Eşik hassasiyeti
    create_section_header("Eşik Hassasiyeti (21G Ort. Değişim vs Tetikleyici Eşik)")
    fig_sens = create_threshold_sensitivity(df)
    st.plotly_chart(fig_sens, use_container_width=True)

def render_tab4(df: pd.DataFrame, sicramalar: pd.DataFrame) -> None:
    """Dağılım & Isıtma tab'ını render eder."""
    if len(sicramalar) == 0:
        st.info("Sıçrama verisi bulunamadı.")
        return
        
    col_l, col_r = st.columns(2)
    
    with col_l:
        # Kümülatif sıçrama sayısı
        create_section_header("Kümülatif Sıçrama Sayısı")
        fig3 = create_cumulative_jumps_chart(sicramalar)
        st.plotly_chart(fig3, use_container_width=True)
        
        # Aylara göre sıçrama
        create_section_header("Aylara Göre Sıçrama")
        fig4 = create_monthly_jumps_chart(sicramalar)
        st.plotly_chart(fig4, use_container_width=True)
    
    with col_r:
        # Büyüklük dağılımı
        create_section_header("Büyüklük Dağılımı")
        fig7 = create_magnitude_distribution_chart(sicramalar)
        st.plotly_chart(fig7, use_container_width=True)
        
        # Yıl-Ay yoğunluk haritası
        create_section_header("Yıl–Ay Yoğunluk Haritası")
        fig8 = create_density_heatmap(sicramalar)
        st.plotly_chart(fig8, use_container_width=True)
    
    # Haftalık pattern
    create_section_header("Haftalık Pattern")
    fig5 = create_weekly_pattern_chart(sicramalar)
    st.plotly_chart(fig5, use_container_width=True)

def render_tab5(df: pd.DataFrame, top_sic: pd.DataFrame, hf_global: pd.DataFrame,
                sicramalar: pd.DataFrame) -> None:
    """Tablolar tab'ını render eder."""
    # Sıçrama tablosu
    if len(top_sic) > 0:
        create_section_header("Sıçrama Tablosu")
        tbl_show = create_jumps_table(top_sic)
        st.dataframe(tbl_show, use_container_width=True, height=420)
    
    # Özet tablolar
    col1, col2 = st.columns(2)
    
    with col1:
        create_section_header("Aylık Özet")
        aylik = create_monthly_summary(sicramalar)
        if len(aylik) > 0:
            st.dataframe(aylik, use_container_width=True)
    
    with col2:
        create_section_header("Yıllık Özet")
        yillik = create_yearly_summary(sicramalar)
        if len(yillik) > 0:
            st.dataframe(yillik, use_container_width=True)
    
    # Haftalık tablo
    if len(hf_global) > 0:
        create_section_header("Haftalık Değişim Tablosu (Pzt → Cum)")
        hf_t = create_weekly_summary_table(hf_global)
        if len(hf_t) > 0:
            st.dataframe(hf_t, use_container_width=True, height=420)
    
    # Dışa aktar
    create_section_header("Dışa Aktar")
    aylik = create_monthly_summary(sicramalar)
    yillik = create_yearly_summary(sicramalar)
    hf_t = create_weekly_summary_table(hf_global) if len(hf_global) > 0 else pd.DataFrame()
    render_export_buttons(top_sic, hf_t, df, aylik, yillik)

# =============================================================================
# ANA UYGULAMA
# =============================================================================
def main():
    """Ana uygulama fonksiyonu."""
    inject_custom_css()
    render_header()
    
    (esik, gosterim_sec, etiket_quantile, haftalik_esik, 
     haftalik_etiket, gun_filtre, fwd_threshold, uploaded_file) = render_sidebar()
    
    if uploaded_file is None:
        st.markdown(f"""
        <div class="upload-box">
            <div class="upload-icon">◈</div>
            <div class="upload-title">EVDS Excel Dosyanızı Yükleyin</div>
            <div class="upload-desc">
                Sol panelden .xlsx dosyanızı seçin<br><br>
                Beklenen format: <strong>EVDS</strong> sayfası<br>
                Tarih: <strong>DD-MM-YYYY</strong> · Kur: <strong>TP_DK_USD_A_YTL</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    with st.spinner("Veriler işleniyor..."):
        try:
            df, nan_cleaned = veri_isle(uploaded_file.read())
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")
            st.stop()
    
    if nan_cleaned > 0:
        st.info(f"ℹ {nan_cleaned} boş satır temizlendi.")
    
    # Sıçramaları filtrele
    sicramalar = df[df['Abs_Degisim'] >= esik].copy()
    sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
    
    if gosterim_sec != "Tümü":
        top_sic = sicramalar.head(int(gosterim_sec)).copy()
    else:
        top_sic = sicramalar.copy()
    
    # Haftalık veriyi hesapla
    hf_global = calculate_weekly_data(df)
    
    # KPI kartlarını render et
    render_kpi_cards(df, sicramalar, esik)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 GÜNLÜK ANALİZ",
        "📈 HAFTALIK & AYLIK",
        "🔮 İLERİ ANALİZ",
        "📉 DAĞILIM & ISITMA",
        "📋 TABLOLAR"
    ])
    
    with tab1:
        render_tab1(df, esik, gosterim_sec, etiket_quantile)
    
    with tab2:
        render_tab2(df, hf_global, gun_filtre, haftalik_esik, haftalik_etiket)
    
    with tab3:
        render_tab3(df, fwd_threshold)
    
    with tab4:
        render_tab4(df, sicramalar)
    
    with tab5:
        render_tab5(df, top_sic, hf_global, sicramalar)
    
    st.markdown(f"""
    <div style="text-align:center; color:{Theme.BORDER}; font-size:0.7rem; padding:30px 0 10px 0;
                border-top:1px solid {Theme.BG_SECONDARY}; margin-top:30px;
                font-family:'DM Mono',monospace; letter-spacing:0.1em;">
        USDTRY ANALYSIS PLATFORM · PROFESYONEL · STREAMLIT + PLOTLY
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
