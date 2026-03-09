import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import ssl
import io
from requests.adapters import HTTPAdapter

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
.forward-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 12px 0; }
.forward-card { background: #0d1220; border: 1px solid #1e2d4a; border-radius: 8px; padding: 16px; }
.forward-title { font-family: 'DM Mono', monospace; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: #4a6080; margin-bottom: 10px; }
.forward-big { font-family: 'DM Mono', monospace; font-size: 1.3rem; font-weight: 500; color: #e8f0ff; margin-bottom: 4px; }
.forward-detail { font-size: 0.72rem; color: #3a5070; line-height: 1.6; }
.forward-accent { color: #4a9eff; }
.spread-card {
    background: #0d1220; border: 1px solid #1e2d4a; border-radius: 10px;
    padding: 18px 16px; position: relative; overflow: hidden;
}
.spread-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #f6ad55, #b794f4);
}
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
.stInfo { background: #0d1a2e; border: 1px solid #1e4a8a; border-radius: 6px; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
.filter-banner {
    background: #0d1a2e; border: 1px solid #1e4a8a; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 16px;
    font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #4a9eff;
    line-height: 1.8;
}
.filter-tag {
    display: inline-block; background: rgba(246,173,85,0.12); color: #f6ad55;
    border: 1px solid rgba(246,173,85,0.3); border-radius: 4px;
    padding: 1px 7px; margin: 0 3px; font-size: 0.72rem;
}
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
    bgcolor='rgba(13,18,32,0.9)',
    bordercolor='#1e2d4a',
    borderwidth=1,
    font=dict(size=11),
    orientation='v',
    x=1.01,
    xanchor='left',
    y=0.5,
    yanchor='middle',
)

EVDS_API_KEY = "EDS05ZLAlI"

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

# ─── TCMB EVDS API ───────────────────────────────────────────────────────────
class _LegacySSL(HTTPAdapter):
    def init_poolmanager(self, *a, **kw):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.options |= 0x4
        kw["ssl_context"] = ctx
        super().init_poolmanager(*a, **kw)

def _evds_session():
    s = requests.Session()
    s.mount("https://", _LegacySSL())
    s.headers.update({"key": EVDS_API_KEY})
    return s

def _evds_cek_blok(session, bas, bit):
    SERILER = "TP.DK.USD.A.YTL-TP.DK.USD.S.YTL-TP.DK.EUR.A.YTL-TP.DK.EUR.S.YTL"
    BASE    = "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
    params  = f"series={SERILER}&startDate={bas}&endDate={bit}&type=json&frequency=1&formulas=&aggregationTypes="
    r = session.get(BASE + params, timeout=30)
    if r.status_code != 200 or not r.text.strip():
        return None
    try:
        data = r.json()
        df = pd.DataFrame(data["items"])
        if "UNIXTIME" in df.columns:
            df.drop(columns=["UNIXTIME"], inplace=True)
        df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True, errors="coerce")
        return df.dropna(subset=["Tarih"])
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def evds_ham_veri_cek():
    session = _evds_session()
    parcalar = []
    bugun = pd.Timestamp.today()
    yil = 2000

    while yil <= bugun.year:
        bas = f"01-01-{yil}"
        bit = f"31-12-{yil + 1}" if yil + 1 <= bugun.year else bugun.strftime("%d-%m-%Y")
        parca = _evds_cek_blok(session, bas, bit)
        if parca is not None and len(parca) > 0:
            parcalar.append(parca)
        yil += 2

    if not parcalar:
        st.error("❌ Hiç veri çekilemedi. API anahtarını kontrol edin: https://evds3.tcmb.gov.tr")
        return None

    df = pd.concat(parcalar, ignore_index=True)
    df = df.drop_duplicates(subset=["Tarih"])

    col_map = {c: c.replace(".", "_").replace("-", "_") for c in df.columns if c != "Tarih"}
    df = df.rename(columns=col_map)

    for col in df.columns:
        if col != "Tarih":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values("Tarih").reset_index(drop=True)


def evds_veri_cek(baslangic="01-01-2000", bitis=None):
    df = evds_ham_veri_cek()
    if df is None:
        return None
    bas_dt = pd.to_datetime(baslangic, dayfirst=True)
    bit_dt = pd.to_datetime(bitis, dayfirst=True) if bitis else pd.Timestamp.today()
    mask = (df["Tarih"] >= bas_dt) & (df["Tarih"] <= bit_dt)
    return df[mask].reset_index(drop=True)


def _temizle_kur_serisi(seri: pd.Series, tarihler: pd.Series) -> pd.Series:
    s = seri.copy().reset_index(drop=True)
    t = tarihler.reset_index(drop=True)

    trl_mask = (t < "2005-01-01") & (s > 100)
    s[trl_mask] = s[trl_mask] / 1_000_000

    medyan = s.median()
    if medyan > 0:
        aykiri = (s > medyan * 20) | (s < medyan / 20)
        s[aykiri & (s > medyan * 20)] = s[aykiri & (s > medyan * 20)] / 1000
        s[aykiri & (s < medyan / 20)] = s[aykiri & (s < medyan / 20)] * 1000

    pct_chg = s.pct_change().abs()
    imkansiz = pct_chg > 0.50
    if imkansiz.any():
        s[imkansiz] = np.nan
        s = s.ffill().bfill()

    rolling_med = s.rolling(window=30, center=True, min_periods=5).median()
    rolling_std = s.rolling(window=30, center=True, min_periods=5).std()
    z_score = (s - rolling_med) / (rolling_std + 1e-9)
    aykiri_z = z_score.abs() > 4
    if aykiri_z.any():
        s[aykiri_z] = np.nan
        s = s.ffill().bfill()

    return s


def veri_isle_api(df_raw, doviz="USD", tur="Alis"):
    suffix = "A" if tur == "Alis" else "S"
    candidates = [
        f"TP_DK_{doviz}_{suffix}",
        f"TP_DK_{doviz}_{suffix}_YTL",
    ]
    col_name = next((c for c in candidates if c in df_raw.columns), None)

    if col_name is None:
        available = [c for c in df_raw.columns if c != "Tarih"]
        st.error(f"Kolon bulunamadı. Aranan: {candidates}\nMevcut kolonlar: {available}")
        return None

    df = df_raw[["Tarih", col_name]].copy()
    df.columns = ["Tarih", "Dolar_Kuru"]
    df = df.dropna(subset=["Dolar_Kuru"])
    df = df.sort_values("Tarih").reset_index(drop=True)

    df["Dolar_Kuru"] = _temizle_kur_serisi(df["Dolar_Kuru"], df["Tarih"])

    df["Onceki_Kur"]    = df["Dolar_Kuru"].shift(1)
    df["Onceki_Tarih"]  = df["Tarih"].shift(1)
    df["Gun_Farki"]     = (df["Tarih"] - df["Onceki_Tarih"]).dt.days
    df["Yuzde_Degisim"] = (df["Dolar_Kuru"] / df["Onceki_Kur"] - 1) * 100
    df["TL_Degisim"]    = df["Dolar_Kuru"] - df["Onceki_Kur"]
    df = df.dropna()

    df["Yil"]     = df["Tarih"].dt.year
    df["Ay"]      = df["Tarih"].dt.month
    df["Gun"]     = df["Tarih"].dt.day
    df["Ay_Adi"]  = df["Tarih"].dt.strftime("%B")
    df["Gun_Adi"] = df["Tarih"].dt.strftime("%A")
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


def spread_hesapla(df_raw, doviz="USD"):
    a_candidates = [f"TP_DK_{doviz}_A", f"TP_DK_{doviz}_A_YTL"]
    s_candidates = [f"TP_DK_{doviz}_S", f"TP_DK_{doviz}_S_YTL"]

    a_col = next((c for c in a_candidates if c in df_raw.columns), None)
    s_col = next((c for c in s_candidates if c in df_raw.columns), None)

    if not a_col or not s_col:
        return None

    sp = df_raw[["Tarih", a_col, s_col]].dropna().copy()
    sp = sp.sort_values("Tarih").reset_index(drop=True)
    sp = sp.rename(columns={a_col: f"TP_DK_{doviz}_A", s_col: f"TP_DK_{doviz}_S"})

    a_key = f"TP_DK_{doviz}_A"
    s_key = f"TP_DK_{doviz}_S"

    sp[a_key] = _temizle_kur_serisi(sp[a_key], sp["Tarih"]).values
    sp[s_key] = _temizle_kur_serisi(sp[s_key], sp["Tarih"]).values

    sp["Spread_TL"]  = sp[s_key] - sp[a_key]
    sp["Spread_Pct"] = (sp["Spread_TL"] / sp[a_key]) * 100

    sp.loc[sp["Spread_TL"] < 0, "Spread_TL"]   = np.nan
    sp.loc[sp["Spread_Pct"] < 0, "Spread_Pct"] = np.nan
    sp["Spread_TL"]  = sp["Spread_TL"].ffill()
    sp["Spread_Pct"] = sp["Spread_Pct"].ffill()

    return sp


def forward_analysis(df, threshold, periods):
    df_r = df.reset_index(drop=True)
    mask = df_r["Abs_Degisim"] >= threshold
    event_positions = df_r.index[mask].tolist()
    results = {}
    for p in periods:
        changes = []
        for pos in event_positions:
            future_pos = pos + p
            if future_pos < len(df_r):
                fwd = (df_r.iloc[future_pos]["Dolar_Kuru"] / df_r.iloc[pos]["Dolar_Kuru"] - 1) * 100
                changes.append(fwd)
        if changes:
            arr = np.array(changes)
            results[p] = {
                "mean":    float(np.mean(arr)),
                "median":  float(np.median(arr)),
                "pos_pct": float((arr > 0).mean() * 100),
                "p10":     float(np.percentile(arr, 10)),
                "p25":     float(np.percentile(arr, 25)),
                "p75":     float(np.percentile(arr, 75)),
                "p90":     float(np.percentile(arr, 90)),
                "std":     float(np.std(arr, ddof=1)),
                "n":       int(len(arr)),
                "raw":     arr.tolist()
            }
    return results


# ─── HAFTALIK VERİ (7 TAKVİM GÜNÜ: Pzt→Paz) ─────────────────────────────────
def haftalik_veri_hesapla(df):
    """
    Haftalık periyot: ISO hafta numarası bazında (Pazartesi → Pazar).
    Haftanın ilk işlem günü açılış kuru, son işlem günü kapanış kuru kullanılır.
    Değişim = (kapanış / açılış - 1) * 100
    """
    df_h = df.copy()
    df_h["ISOYil"]   = df_h["Tarih"].dt.isocalendar().year.astype(int)
    df_h["ISOHafta"] = df_h["Tarih"].dt.isocalendar().week.astype(int)

    _hf_ilk = df_h.groupby(["ISOYil","ISOHafta"]).agg(
        AcilisTarih=("Tarih", "min"),
        AcilisKur=("Dolar_Kuru", "first")
    ).reset_index()

    _hf_son = df_h.groupby(["ISOYil","ISOHafta"]).agg(
        KapanisTarih=("Tarih", "max"),
        KapanisKur=("Dolar_Kuru", "last")
    ).reset_index()

    hf = _hf_ilk.merge(_hf_son, on=["ISOYil","ISOHafta"])

    # Haftalık değişim: (Kapanış / Açılış - 1) * 100
    hf["HaftaDegisim"] = (hf["KapanisKur"] / hf["AcilisKur"] - 1) * 100
    hf["XTarih"]       = hf["KapanisTarih"]

    # Gösterim için aralık etiketi (Pazartesi–Pazar takvim aralığı)
    hf["HaftaBaslangic"] = hf["AcilisTarih"].apply(
        lambda t: t - pd.Timedelta(days=t.weekday())  # Pazartesi
    )
    hf["HaftaBitis"] = hf["HaftaBaslangic"] + pd.Timedelta(days=6)  # Pazar

    hf["Aralik"] = (
        hf["HaftaBaslangic"].dt.strftime("%d.%m") + "–" +
        hf["HaftaBitis"].dt.strftime("%d.%m.%y") +
        " (Pzt–Paz)"
    )
    hf["IslemAralik"] = (
        hf["AcilisTarih"].dt.strftime("%d.%m") + "–" +
        hf["KapanisTarih"].dt.strftime("%d.%m.%y") +
        " (işlem)"
    )

    hf["AbsDegisim"] = hf["HaftaDegisim"].abs()
    hf = hf.dropna(subset=["HaftaDegisim"]).reset_index(drop=True)
    hf["_acs_str"] = hf["AcilisKur"].apply(tr_fmt_kur)
    hf["_kap_str"] = hf["KapanisKur"].apply(tr_fmt_kur)
    hf["_hf_str"]  = hf["HaftaDegisim"].apply(tr_fmt_pct)

    return hf


# ─── AYLIK VERİ (Ay başı → Ay sonu) ─────────────────────────────────────────
def aylik_veri_hesapla(df):
    """
    Aylık periyot: Her ayın ilk işlem günü → son işlem günü.
    Değişim = (ay sonu kuru / ay başı kuru - 1) * 100
    """
    df_a = df.copy()
    df_a["Yil"] = df_a["Tarih"].dt.year
    df_a["Ay"]  = df_a["Tarih"].dt.month

    _ay_ilk = df_a.groupby(["Yil","Ay"]).agg(
        AcilisTarih=("Tarih", "min"),
        AcilisKur=("Dolar_Kuru", "first")
    ).reset_index()

    _ay_son = df_a.groupby(["Yil","Ay"]).agg(
        KapanisTarih=("Tarih", "max"),
        KapanisKur=("Dolar_Kuru", "last")
    ).reset_index()

    ay = _ay_ilk.merge(_ay_son, on=["Yil","Ay"])
    ay["AyDegisim"] = (ay["KapanisKur"] / ay["AcilisKur"] - 1) * 100
    ay["AbsDegisim"] = ay["AyDegisim"].abs()
    ay["XTarih"] = ay["KapanisTarih"]
    ay["AyAdi"] = ay["Ay"].map(TR_AY_UZUN)
    ay["Aralik"] = ay["AyAdi"] + " " + ay["Yil"].astype(str)
    ay = ay.dropna(subset=["AyDegisim"]).reset_index(drop=True)
    ay["_acs_str"] = ay["AcilisKur"].apply(tr_fmt_kur)
    ay["_kap_str"] = ay["KapanisKur"].apply(tr_fmt_kur)
    ay["_ay_str"]  = ay["AyDegisim"].apply(tr_fmt_pct)

    return ay


# ─── ÇEYREKLİK VERİ (Çeyrek başı → Çeyrek sonu) ─────────────────────────────
def ceyreklik_veri_hesapla(df):
    """
    Çeyreklik periyot: Her çeyreğin ilk işlem günü → son işlem günü.
    Q1: Ocak–Mart, Q2: Nisan–Haziran, Q3: Temmuz–Eylül, Q4: Ekim–Aralık
    Değişim = (çeyrek sonu kuru / çeyrek başı kuru - 1) * 100
    """
    df_c = df.copy()
    df_c["Yil"]    = df_c["Tarih"].dt.year
    df_c["Ceyrek"] = df_c["Tarih"].dt.quarter

    _c_ilk = df_c.groupby(["Yil","Ceyrek"]).agg(
        AcilisTarih=("Tarih", "min"),
        AcilisKur=("Dolar_Kuru", "first")
    ).reset_index()

    _c_son = df_c.groupby(["Yil","Ceyrek"]).agg(
        KapanisTarih=("Tarih", "max"),
        KapanisKur=("Dolar_Kuru", "last")
    ).reset_index()

    cey = _c_ilk.merge(_c_son, on=["Yil","Ceyrek"])
    cey["CeyrekDegisim"] = (cey["KapanisKur"] / cey["AcilisKur"] - 1) * 100
    cey["AbsDegisim"] = cey["CeyrekDegisim"].abs()
    cey["XTarih"] = cey["KapanisTarih"]
    cey["CeyrekAdi"] = "Q" + cey["Ceyrek"].astype(str) + " " + cey["Yil"].astype(str)

    # Çeyrek ay aralığı
    _ceyrek_aylar = {1: "Oca–Mar", 2: "Nis–Haz", 3: "Tem–Eyl", 4: "Eki–Ara"}
    cey["Aralik"] = cey.apply(
        lambda r: f"Q{int(r['Ceyrek'])} {int(r['Yil'])} ({_ceyrek_aylar[int(r['Ceyrek'])]})", axis=1
    )
    cey = cey.dropna(subset=["CeyrekDegisim"]).reset_index(drop=True)
    cey["_acs_str"] = cey["AcilisKur"].apply(tr_fmt_kur)
    cey["_kap_str"] = cey["KapanisKur"].apply(tr_fmt_kur)
    cey["_cey_str"] = cey["CeyrekDegisim"].apply(tr_fmt_pct)

    return cey


# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 8px 0 4px 0;">
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                letter-spacing:0.2em; color:#1b6cf2; margin-bottom:6px;">
        ◈ TCMB EVDS · GÜNLÜK SIÇRAMA & İLERİ ANALİZ
    </div>
    <h1 style="font-size:2rem; font-weight:700; color:#e8f0ff; margin:0; line-height:1.1; letter-spacing:-0.02em;">
        Döviz Kuru Analiz Platformu
    </h1>
    <p style="color:#3a5070; font-size:0.85rem; margin:6px 0 0 0;">
        TCMB EVDS'den canlı veri · USD & EUR kur analizi · Spread takibi · İleri dönem etkisi
    </p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:16px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ Veri Ayarları</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    doviz_sec = st.selectbox("Döviz", ["USD", "EUR"], index=0)
    tur_sec   = st.selectbox("Fiyat Türü", ["Alis", "Satis"],
                              format_func=lambda x: "Alış" if x == "Alis" else "Satış", index=0)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#4a6080;
        text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">Tarih Aralığı</div>""",
        unsafe_allow_html=True)
    baslangic_dt = st.date_input(
        "Başlangıç Tarihi",
        value=datetime.date(2000, 1, 1),
        min_value=datetime.date(2000, 1, 1),
        max_value=datetime.date.today(),
        format="DD.MM.YYYY",
    )
    bitis_dt = st.date_input(
        "Bitiş Tarihi",
        value=datetime.date.today(),
        min_value=datetime.date(2000, 1, 2),
        max_value=datetime.date.today(),
        format="DD.MM.YYYY",
    )

    baslangic_tarih = baslangic_dt.strftime("%d-%m-%Y")
    bitis_tarih     = bitis_dt.strftime("%d-%m-%Y")

    if st.button("🔄 Veriyi Yenile", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ Parametre Kontrolü</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    esik            = st.slider("Günlük Sıçrama Eşiği (%)", 0.0, 10.0, 2.0, 0.1)
    gosterim_sec    = st.selectbox("Gösterilecek Sıçrama Sayısı", [10, 20, 30, 50, 75, 100, "Tümü"], index=2)
    yon             = st.radio("Sıçrama Yönü", ["Tümü", "Yalnız Pozitif ↑", "Yalnız Negatif ↓"])

    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ Etiket Ayarı</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    etiket_quantile = st.slider("Günlük — Etiketlenecek Dilim (%)", 10, 100, 40, 5)

    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ Haftalık / Gün Analizi</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.7rem;color:#4a9eff;font-family:'DM Mono',monospace;
        background:rgba(27,108,242,0.08);border:1px solid rgba(27,108,242,0.2);border-radius:4px;
        padding:6px 10px;margin-bottom:10px;">
        📅 Haftalık = Pazartesi açılış → Pazar kapanış (7 takvim günü)
    </div>""", unsafe_allow_html=True)
    haftalik_esik   = st.slider("Haftalık Sıçrama Eşiği (%)", 0.0, 20.0, 3.0, 0.5)
    haftalik_etiket = st.slider("Haftalık — Etiketlenecek Dilim (%)", 10, 100, 40, 5)
    haftalik_yon    = st.radio("Haftalık Yön", ["Tümü", "Yalnız Pozitif ↑", "Yalnız Negatif ↓"], key="haftalik_yon")
    gun_filtre      = st.multiselect("Gün Filtresi", ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"], default=[])

    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.15em;color:#1b6cf2;padding:20px 0 12px 0;border-bottom:1px solid #1e2d4a;">
        ◈ İleri Analiz</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    fwd_threshold   = st.slider("Tetikleyici Eşik (%)", 0.0, 15.0, 3.0, 0.5)

    st.markdown("""<div style="font-size:0.72rem;color:#3a5070;margin-top:20px;line-height:1.9;
        border-top:1px solid #1e2d4a;padding-top:12px;">
        Kaynak: <span style="color:#4a9eff;font-family:'DM Mono',monospace;">TCMB EVDS</span><br>
        API: <span style="color:#4a9eff;font-family:'DM Mono',monospace;">evds2.tcmb.gov.tr</span><br>
        Cache: <span style="color:#4a9eff;font-family:'DM Mono',monospace;">60 dakika</span>
    </div>""", unsafe_allow_html=True)

# ─── VERİ ÇEKME ──────────────────────────────────────────────────────────────
with st.spinner("🌐 TCMB EVDS'den 2000–bugün verisi çekiliyor (yıl yıl, ~26 istek)..."):
    df_raw = evds_veri_cek(baslangic=baslangic_tarih, bitis=bitis_tarih)

if df_raw is None:
    st.error("Veri çekilemedi. Lütfen API bağlantınızı kontrol edin ve sayfayı yenileyin.")
    st.stop()

with st.spinner(f"{'EUR' if doviz_sec == 'EUR' else 'USD'} verisi işleniyor..."):
    df = veri_isle_api(df_raw, doviz_sec, tur_sec)

if df is None:
    st.stop()

doviz_label = f"{doviz_sec}/TRY {'Alış' if tur_sec == 'Alis' else 'Satış'}"
st.success(f"✅ {doviz_label} verisi yüklendi · {df['Tarih'].min().strftime('%d.%m.%Y')} – {df['Tarih'].max().strftime('%d.%m.%Y')} · {len(df):,} gün", icon=None)

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

# ─── KPI CARDS ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">◈ Genel İstatistikler</div>', unsafe_allow_html=True)
son_kur  = df["Dolar_Kuru"].iloc[-1]
son_degis = df["Yuzde_Degisim"].iloc[-1]
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-label">Son Kur ({doviz_label})</div>
    <div class="metric-value metric-neu">{fkur(son_kur, 4)} ₺</div>
    <div class="metric-sub">{df['Tarih'].iloc[-1].strftime('%d.%m.%Y')} · {fpct(son_degis,2)} günlük</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Ort. Günlük Değ.</div>
    <div class="metric-value">{fpct(df['Yuzde_Degisim'].mean(),3)}</div>
    <div class="metric-sub">std ± {fpct(df['Yuzde_Degisim'].std(),3)}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Pozitif / Negatif</div>
    <div class="metric-value"><span class="metric-pos">{poz_say}</span> <span style="color:#1e2d4a">/</span> <span class="metric-neg">{neg_say}</span></div>
    <div class="metric-sub">gün · {df['Tarih'].min().year}–{df['Tarih'].max().year}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Toplam Sıçrama (≥%{esik})</div>
    <div class="metric-value metric-neu">{len(sicramalar):,}</div>
    <div class="metric-sub">günlerin {fpct(oran,1)}'i</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">En Büyük / En Küçük</div>
    <div class="metric-value"><span class="metric-pos">+{fpct(max_j,2)}</span></div>
    <div class="metric-sub"><span class="metric-neg">{fpct(min_j,2)}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── HAFTALIK VERİ (7 TAKVİM GÜNÜ) ──────────────────────────────────────────
hf_global = haftalik_veri_hesapla(df)

# ─── AYLIK VERİ ──────────────────────────────────────────────────────────────
ay_global = aylik_veri_hesapla(df)

# ─── ÇEYREKLİK VERİ ──────────────────────────────────────────────────────────
cey_global = ceyreklik_veri_hesapla(df)

# ─── SPREAD VERİSİ ───────────────────────────────────────────────────────────
sp_df = spread_hesapla(df_raw, doviz_sec)

# ─── TABS ────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 GÜNLÜK", "📆 HAFTALIK", "🗓 AYLIK & YILLIK",
    "📈 KÜMÜLATİF & PERFORMANS", "🔭 İLERİ ANALİZ & DAĞILIM",
    "📋 TABLOLAR & SPREAD"
])

with tab1:
    st.markdown(f'<div class="section-label">◈ {doviz_label} Kuru & Sıçrama Noktaları</div>', unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df["Tarih"], y=df["Dolar_Kuru"], mode="lines", name=doviz_label,
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
            marker=dict(color=color, size=s["Abs_Degisim"]*2.5,
                        line=dict(color=color, width=3), opacity=0.9),
            customdata=list(zip(s["_h"], s["_pct"], s["_ok"], s["_k"])),
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>%{{customdata[3]}} ₺ ← %{{customdata[2]}} ₺<br><b style='color:{tpl_color}'>%{{customdata[1]}}</b><extra></extra>"
        ))

    tv_k, tt_k = safe_ticks(df["Dolar_Kuru"].min(), df["Dolar_Kuru"].max(), n=8, decimals=2, is_kur=True)
    apply_base(fig1, height=560,
        title=dict(text=f"{doviz_label}  ·  Eşik %{esik}  ·  Top {gosterim_sec}", font=dict(size=13, color="#4a6080", family="DM Mono, monospace"), x=0),
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
        if is_pos:
            ethr  = s["Yuzde_Degisim"].quantile(1 - etiket_quantile / 100)
            s["_lbl"] = s.apply(lambda r: f"{r['Tarih'].strftime('%d.%m.%y')} {tr_fmt_pct(r['Yuzde_Degisim'],1)}"
                                if r["Yuzde_Degisim"] >= ethr else "", axis=1)
        else:
            ethr  = s["Yuzde_Degisim"].quantile(etiket_quantile / 100)
            s["_lbl"] = s.apply(lambda r: f"{r['Tarih'].strftime('%d.%m.%y')} {tr_fmt_pct(r['Yuzde_Degisim'],1)}"
                                if r["Yuzde_Degisim"] <= ethr else "", axis=1)
        fig2.add_trace(go.Scatter(
            x=s["Tarih"], y=s["Yuzde_Degisim"], mode="markers+text", name=name,
            marker=dict(color=color, size=s["Abs_Degisim"]*1.8+5, symbol=sym,
                        line=dict(color=color, width=1), opacity=0.9),
            text=s["_lbl"], textposition=tpos,
            textfont=dict(size=8, color=color, family="DM Mono, monospace"),
            customdata=list(zip(s["Hover_Tarih"], s["_ok"], s["_k"], s["_pct"])),
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>%{{customdata[1]}} → %{{customdata[2]}} ₺<br><b style='color:{tpl_color}'>%{{customdata[3]}}</b><extra></extra>"
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
            sign = "+" if is_pos else ""
            icon = "↑" if is_pos else "↓"
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

    esik_s_t1 = str(esik).replace(".", ",")
    yon_label_t1 = {
        "Tümü":             "Tümü",
        "Yalnız Pozitif ↑": "Yalnız ↑ Pozitif",
        "Yalnız Negatif ↓": "Yalnız ↓ Negatif",
    }
    st.markdown(
        f'<div class="section-label">◈ Günlük Sıçrama Tablosu '
        f'<span style="color:#f6ad55;font-size:0.8rem;font-weight:400;">'
        f'· Eşik ≥%{esik_s_t1} · {yon_label_t1.get(yon, yon)} · {gosterim_sec} kayıt'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    tbl_t1 = top_sic.copy().reset_index(drop=True)
    tbl_t1.index = tbl_t1.index + 1
    tbl_show_t1 = pd.DataFrame({
        "#":           tbl_t1.index,
        "Tarih":       tbl_t1["Tarih"].dt.strftime("%d.%m.%Y"),
        "Yıl":         tbl_t1["Yil"],
        "Ay":          tbl_t1["Ay_Adi"],
        "Gün":         tbl_t1["Gun_Adi"].map(TR_GUN),
        "Kur (₺)":     tbl_t1["Dolar_Kuru"].apply(tr_fmt_kur),
        "Önceki (₺)":  tbl_t1["Onceki_Kur"].apply(tr_fmt_kur),
        "Değişim %":   tbl_t1["Yuzde_Degisim"].apply(tr_fmt_pct),
        "TL Fark":     tbl_t1["TL_Degisim"].apply(lambda x: tr_fmt_kur(x, 4)),
        "Gün Farkı":   tbl_t1["Gun_Farki"].astype(int),
    })

    st.markdown(
        f"<div style='font-size:0.75rem;color:#4a6080;font-family:DM Mono,monospace;"
        f"margin-bottom:8px;'>Toplam <b style='color:#f6ad55'>{len(tbl_show_t1)}</b> kayıt listeleniyor</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(tbl_show_t1, use_container_width=True, height=400)

    dl_col1, dl_col2, _ = st.columns([1, 1, 4])
    with dl_col1:
        csv_t1 = tbl_show_t1.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇ CSV İndir",
            csv_t1,
            f"gunluk_sicramalar_esik{esik_s_t1}.csv",
            "text/csv",
            use_container_width=True,
        )
    with dl_col2:
        buf_t1 = io.BytesIO()
        with pd.ExcelWriter(buf_t1, engine="openpyxl") as w:
            tbl_show_t1.to_excel(w, sheet_name="Gunluk_Sicramalar", index=False)
        st.download_button(
            "⬇ Excel İndir",
            buf_t1.getvalue(),
            f"gunluk_sicramalar_esik{esik_s_t1}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

with tab2:
    GUN_COLORS = {"Pazartesi":"#4a9eff","Salı":"#b794f4","Çarşamba":"#f6ad55","Perşembe":"#00d4aa","Cuma":"#ff4d6a"}
    ALL_DAYS_TR = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma"]
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
            hovertemplate=f"<b>{gun_tr}</b> — %{{x|%d.%m.%Y}}<br>Değişim: <b>%{{customdata[0]}}</b><br>Kur: %{{customdata[2]}} → %{{customdata[1]}} ₺<extra></extra>"
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
        sub = df[df["Gun_Adi_TR"] == gun_tr]
        ort  = sub["Yuzde_Degisim"].mean()
        std  = sub["Yuzde_Degisim"].std()
        maks = sub["Yuzde_Degisim"].max()
        mins = sub["Yuzde_Degisim"].min()
        poz  = (sub["Yuzde_Degisim"] > 0).mean() * 100
        color = GUN_COLORS.get(gun_tr, "#4a9eff")
        sign = "+" if ort >= 0 else ""
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
        sub = df[df["Gun_Adi_TR"] == gun_tr]
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

    # ════ HAFTALIK DEĞİŞİM (7 TAKVİM GÜNÜ: Pzt→Paz) ══════════════════════
    st.markdown("""
    <div class="section-label">◈ Haftalık Değişim — Pazartesi Açılış → Pazar Kapanış (7 Takvim Günü)
        <span style="color:#4a9eff;font-size:0.75rem;font-weight:400;margin-left:8px;">
        · ISO hafta bazlı · ilk işlem günü açılış → son işlem günü kapanış
        </span>
    </div>""", unsafe_allow_html=True)

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
        def mk_lbl(r):
            cond = r["HaftaDegisim"] >= thr if is_pos else r["HaftaDegisim"] <= thr
            return f"{r['IslemAralik']} {tr_fmt_pct(r['HaftaDegisim'],1)}" if cond else ""
        sub["_lbl"] = sub.apply(mk_lbl, axis=1)
        return sub

    hf_pos_sc = hf_lbl_col(hf_pos_sc, True)
    hf_neg_sc = hf_lbl_col(hf_neg_sc, False)

    fig_hw = go.Figure()
    fig_hw.add_trace(go.Scatter(
        x=hf["XTarih"], y=hf["HaftaDegisim"], mode="lines", name="Haftalık Δ",
        line=dict(color="#2a4a7a", width=1), opacity=0.6,
        customdata=list(zip(hf["Aralik"], hf["IslemAralik"], hf["_acs_str"], hf["_kap_str"], hf["_hf_str"])),
        hovertemplate="<b>%{customdata[0]}</b><br>İşlem: %{customdata[1]}<br>Açılış: %{customdata[2]} ₺ → Kapanış: %{customdata[3]} ₺<br>%{customdata[4]}<extra></extra>"
    ))
    for subset, color, name, tpos, sym, tpl_color in [
        (hf_pos_sc, "#00d4aa", "↑ Pozitif", "top right",    "triangle-up",   "#00d4aa"),
        (hf_neg_sc, "#ff4d6a", "↓ Negatif", "bottom right", "triangle-down", "#ff4d6a"),
    ]:
        if len(subset) == 0:
            continue
        s = subset.copy()
        fig_hw.add_trace(go.Scatter(
            x=s["XTarih"], y=s["HaftaDegisim"], mode="markers+text", name=name,
            marker=dict(color=color, size=s["AbsDegisim"]*1.8+5, symbol=sym,
                        line=dict(color=color, width=2), opacity=0.9),
            text=s["_lbl"], textposition=tpos,
            textfont=dict(size=8, color=color, family="DM Mono, monospace"),
            customdata=list(zip(s["Aralik"], s["IslemAralik"], s["_acs_str"], s["_kap_str"], s["_hf_str"])),
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>İşlem: %{{customdata[1]}}<br>Açılış: %{{customdata[2]}} ₺ → Kapanış: %{{customdata[3]}} ₺<br><b style='color:{tpl_color}'>%{{customdata[4]}}</b><extra></extra>"
        ))

    tv_hf, tt_hf = safe_ticks(hf["HaftaDegisim"].min(), hf["HaftaDegisim"].max(), n=10, decimals=1, suffix="%")
    he_str = str(haftalik_esik).replace(".", ",")
    fig_hw.add_hline(y=haftalik_esik,  line_dash="dash", line_color="rgba(0,212,170,0.5)",  line_width=1,
                     annotation_text=f"+{he_str}%", annotation_font_color="#00d4aa", annotation_font_size=10)
    fig_hw.add_hline(y=-haftalik_esik, line_dash="dash", line_color="rgba(255,77,106,0.5)", line_width=1,
                     annotation_text=f"−{he_str}%", annotation_font_color="#ff4d6a", annotation_font_size=10)
    fig_hw.add_hline(y=0, line_color="#2a4a7a", line_width=1)
    apply_base(fig_hw, height=520,
        title=dict(text=f"HAFTALIK DEĞİŞİM (Pzt Açılış→Paz Kapanış, 7 Gün) · Eşik ±%{haftalik_esik} · Etiket top %{haftalik_etiket}",
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
        <div class="metric-sub">Pzt açılış→Paz kapanış ort.</div></div>
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

    # ════ AYLIK DEĞİŞİM BAR CHART ════════════════════════════════════════
    st.markdown("""
    <div class="section-label">◈ Aylık Değişim — Ay Başı → Ay Sonu
        <span style="color:#4a9eff;font-size:0.75rem;font-weight:400;margin-left:8px;">
        · Her ayın ilk işlem günü açılış → son işlem günü kapanış
        </span>
    </div>""", unsafe_allow_html=True)

    ay = ay_global.copy()
    ay["renk"] = ay["AyDegisim"].apply(lambda x: "#00d4aa" if x >= 0 else "#ff4d6a")
    fig_ay_bar = go.Figure()
    fig_ay_bar.add_trace(go.Bar(
        x=ay["XTarih"], y=ay["AyDegisim"],
        marker_color=ay["renk"].values, opacity=0.85,
        customdata=list(zip(ay["Aralik"], ay["_acs_str"], ay["_kap_str"], ay["_ay_str"])),
        hovertemplate="<b>%{customdata[0]}</b><br>Açılış: %{customdata[1]} ₺ → Kapanış: %{customdata[2]} ₺<br>Değişim: <b>%{customdata[3]}</b><extra></extra>"
    ))
    fig_ay_bar.add_hline(y=0, line_color="#2a4a7a", line_width=1)
    tv_ay, tt_ay = safe_ticks(ay["AyDegisim"].min(), ay["AyDegisim"].max(), n=8, decimals=1, suffix="%")
    apply_base(fig_ay_bar, height=380,
        title=dict(text="AYLIK DEĞİŞİM (Ay Başı→Ay Sonu) · Her ayın ilk işlem günü → son işlem günü",
                   font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y", tickfont=dict(size=10, color="#4a6080")),
        yaxis={**yt(tv_ay, tt_ay, {"gridcolor":"#131c2e","tickfont":dict(size=10,color="#4a6080"), "ticksuffix":"%"})},
        showlegend=False, hovermode="closest")
    st.plotly_chart(fig_ay_bar, use_container_width=True)

    ay_ort  = ay["AyDegisim"].mean()
    ay_maks = ay["AyDegisim"].max()
    ay_mins = ay["AyDegisim"].min()
    ay_poz  = (ay["AyDegisim"] > 0).sum()
    ay_neg  = (ay["AyDegisim"] < 0).sum()
    sign_ay = "+" if ay_ort >= 0 else ""
    st.markdown(f"""
    <div class="metric-row" style="grid-template-columns: repeat(5, 1fr);">
      <div class="metric-card" style="border-top:2px solid #4a9eff;">
        <div class="metric-label">Aylık Ort.</div>
        <div class="metric-value metric-{'pos' if ay_ort>=0 else 'neg'}">{sign_ay}{f'{ay_ort:.3f}'.replace('.',',')}%</div>
        <div class="metric-sub">Ay başı→ay sonu ort.</div></div>
      <div class="metric-card" style="border-top:2px solid #00d4aa;">
        <div class="metric-label">Pozitif Ay</div>
        <div class="metric-value metric-pos">{ay_poz}</div></div>
      <div class="metric-card" style="border-top:2px solid #ff4d6a;">
        <div class="metric-label">Negatif Ay</div>
        <div class="metric-value metric-neg">{ay_neg}</div></div>
      <div class="metric-card">
        <div class="metric-label">En İyi Ay</div>
        <div class="metric-value metric-pos">+{f'{ay_maks:.2f}'.replace('.',',')}%</div></div>
      <div class="metric-card">
        <div class="metric-label">En Kötü Ay</div>
        <div class="metric-value metric-neg">{f'{ay_mins:.2f}'.replace('.',',')}%</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ════ ÇEYREKLİK DEĞİŞİM BAR CHART ════════════════════════════════════
    st.markdown("""
    <div class="section-label">◈ Çeyreklik Değişim — Çeyrek Başı → Çeyrek Sonu
        <span style="color:#4a9eff;font-size:0.75rem;font-weight:400;margin-left:8px;">
        · Q1: Oca–Mar · Q2: Nis–Haz · Q3: Tem–Eyl · Q4: Eki–Ara
        </span>
    </div>""", unsafe_allow_html=True)

    cey = cey_global.copy()
    cey["renk"] = cey["CeyrekDegisim"].apply(lambda x: "#00d4aa" if x >= 0 else "#ff4d6a")
    fig_cey_bar = go.Figure()
    fig_cey_bar.add_trace(go.Bar(
        x=cey["XTarih"], y=cey["CeyrekDegisim"],
        marker_color=cey["renk"].values, opacity=0.85,
        customdata=list(zip(cey["Aralik"], cey["_acs_str"], cey["_kap_str"], cey["_cey_str"])),
        hovertemplate="<b>%{customdata[0]}</b><br>Açılış: %{customdata[1]} ₺ → Kapanış: %{customdata[2]} ₺<br>Değişim: <b>%{customdata[3]}</b><extra></extra>"
    ))
    fig_cey_bar.add_hline(y=0, line_color="#2a4a7a", line_width=1)
    tv_cey, tt_cey = safe_ticks(cey["CeyrekDegisim"].min(), cey["CeyrekDegisim"].max(), n=8, decimals=1, suffix="%")
    apply_base(fig_cey_bar, height=380,
        title=dict(text="ÇEYREKLİK DEĞİŞİM (Çeyrek Başı→Çeyrek Sonu) · Q1=Oca–Mar, Q2=Nis–Haz, Q3=Tem–Eyl, Q4=Eki–Ara",
                   font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e", tickformat="%Y", tickfont=dict(size=10, color="#4a6080")),
        yaxis={**yt(tv_cey, tt_cey, {"gridcolor":"#131c2e","tickfont":dict(size=10,color="#4a6080"), "ticksuffix":"%"})},
        showlegend=False, hovermode="closest")
    st.plotly_chart(fig_cey_bar, use_container_width=True)

    cey_ort  = cey["CeyrekDegisim"].mean()
    cey_maks = cey["CeyrekDegisim"].max()
    cey_mins = cey["CeyrekDegisim"].min()
    cey_poz  = (cey["CeyrekDegisim"] > 0).sum()
    cey_neg  = (cey["CeyrekDegisim"] < 0).sum()
    sign_cey = "+" if cey_ort >= 0 else ""
    st.markdown(f"""
    <div class="metric-row" style="grid-template-columns: repeat(5, 1fr);">
      <div class="metric-card" style="border-top:2px solid #b794f4;">
        <div class="metric-label">Çeyreklik Ort.</div>
        <div class="metric-value metric-{'pos' if cey_ort>=0 else 'neg'}">{sign_cey}{f'{cey_ort:.3f}'.replace('.',',')}%</div>
        <div class="metric-sub">Çeyrek başı→çeyrek sonu ort.</div></div>
      <div class="metric-card" style="border-top:2px solid #00d4aa;">
        <div class="metric-label">Pozitif Çeyrek</div>
        <div class="metric-value metric-pos">{cey_poz}</div></div>
      <div class="metric-card" style="border-top:2px solid #ff4d6a;">
        <div class="metric-label">Negatif Çeyrek</div>
        <div class="metric-value metric-neg">{cey_neg}</div></div>
      <div class="metric-card">
        <div class="metric-label">En İyi Çeyrek</div>
        <div class="metric-value metric-pos">+{f'{cey_maks:.2f}'.replace('.',',')}%</div></div>
      <div class="metric-card">
        <div class="metric-label">En Kötü Çeyrek</div>
        <div class="metric-value metric-neg">{f'{cey_mins:.2f}'.replace('.',',')}%</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

with tab3:
    if "Gun_Adi_TR" not in df.columns:
        df["Gun_Adi_TR"] = df["Gun_Adi"].map(TR_GUN)
    aktif_gunler_t3 = gun_filtre if gun_filtre else ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma"]

    st.markdown('<div class="section-label">◈ Aylık Getiri (21 Gün) & Volatilite</div>', unsafe_allow_html=True)
    col_am1, col_am2 = st.columns(2)
    with col_am1:
        aylik_g = df.dropna(subset=["Aylik_Getiri"]).copy()
        aylik_g_filt = aylik_g[aylik_g["Gun_Adi_TR"].isin(aktif_gunler_t3)] if gun_filtre else aylik_g.copy()
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
        df["_v20"] = df["Vol_20"].apply(lambda x: tr_fmt_pct(x, 3) if pd.notna(x) else "")
        df["_v60"] = df["Vol_60"].apply(lambda x: tr_fmt_pct(x, 3) if pd.notna(x) else "")
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
    text_matrix = np.where(
        np.isnan(ay_pivot.values), "",
        np.vectorize(lambda v: f"{f'{v:.2f}'.replace('.', ',')}%")(ay_pivot.values)
    )
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

    # ════ AYLIK ISI HARİTASI (Gerçek ay başı→sonu) ════════════════════
    st.markdown("""
    <div class="section-label">◈ Yıl–Ay Aylık Getiri Isı Haritası (Ay Başı→Ay Sonu)
        <span style="color:#4a9eff;font-size:0.75rem;font-weight:400;margin-left:8px;">
        · Her ayın ilk işlem günü açılış → son işlem günü kapanış
        </span>
    </div>""", unsafe_allow_html=True)

    ay_heat_df = ay_global.copy()
    ay_heat_pivot = ay_heat_df.pivot(index="Yil", columns="Ay", values="AyDegisim")
    ay_heat_pivot.columns = [TR_AY.get(c, str(c)) for c in ay_heat_pivot.columns]
    ay_heat_text = np.where(
        np.isnan(ay_heat_pivot.values), "",
        np.vectorize(lambda v: f"{f'{v:.1f}'.replace('.', ',')}%")(ay_heat_pivot.values)
    )
    fig_ay_heat = go.Figure(go.Heatmap(
        z=ay_heat_pivot.values, x=ay_heat_pivot.columns.tolist(),
        y=ay_heat_pivot.index.astype(str).tolist(),
        colorscale=[[0,"#ff4d6a"],[0.5,"#0d1220"],[1,"#00d4aa"]], zmid=0,
        text=ay_heat_text, texttemplate="%{text}", textfont=dict(size=9, family="DM Mono, monospace"),
        hovertemplate="<b>%{y} — %{x}</b><br>Ay getirisi: <b>%{text}</b><extra></extra>",
        colorbar=dict(tickfont=dict(size=9, color="#4a6080"))
    ))
    apply_base(fig_ay_heat, height=500,
        title=dict(text="YIL–AY GETİRİ ISISI (Ay Başı→Ay Sonu)", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(side="bottom", tickfont=dict(size=11, color="#4a6080")),
        yaxis=dict(tickfont=dict(size=11, color="#4a6080"), autorange="reversed"))
    st.plotly_chart(fig_ay_heat, use_container_width=True)

    # ════ ÇEYREKLİK ISI HARİTASI ════════════════════════════════════════
    st.markdown("""
    <div class="section-label">◈ Çeyreklik Getiri Isı Haritası (Çeyrek Başı→Çeyrek Sonu)
        <span style="color:#b794f4;font-size:0.75rem;font-weight:400;margin-left:8px;">
        · Q1=Oca–Mar · Q2=Nis–Haz · Q3=Tem–Eyl · Q4=Eki–Ara
        </span>
    </div>""", unsafe_allow_html=True)

    cey_heat = cey_global.copy()
    cey_heat_pivot = cey_heat.pivot(index="Yil", columns="Ceyrek", values="CeyrekDegisim")
    cey_heat_pivot.columns = [f"Q{int(c)}" for c in cey_heat_pivot.columns]
    cey_heat_text = np.where(
        np.isnan(cey_heat_pivot.values), "",
        np.vectorize(lambda v: f"{f'{v:.1f}'.replace('.', ',')}%")(cey_heat_pivot.values)
    )
    fig_cey_heat = go.Figure(go.Heatmap(
        z=cey_heat_pivot.values, x=cey_heat_pivot.columns.tolist(),
        y=cey_heat_pivot.index.astype(str).tolist(),
        colorscale=[[0,"#ff4d6a"],[0.5,"#0d1220"],[1,"#00d4aa"]], zmid=0,
        text=cey_heat_text, texttemplate="%{text}", textfont=dict(size=10, family="DM Mono, monospace"),
        hovertemplate="<b>%{y} %{x}</b><br>Çeyrek getirisi: <b>%{text}</b><extra></extra>",
        colorbar=dict(tickfont=dict(size=9, color="#4a6080"))
    ))
    apply_base(fig_cey_heat, height=500,
        title=dict(text="ÇEYREKLİK GETİRİ ISISI (Q1=Oca–Mar, Q2=Nis–Haz, Q3=Tem–Eyl, Q4=Eki–Ara)",
                   font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        xaxis=dict(side="bottom", tickfont=dict(size=13, color="#4a6080")),
        yaxis=dict(tickfont=dict(size=11, color="#4a6080"), autorange="reversed"))
    st.plotly_chart(fig_cey_heat, use_container_width=True)

# ════════════ TAB 4 — KÜMÜLATİF & PERFORMANS ════════════
with tab4:

    st.markdown("""<style>
    .perf-scorecard {
        background:#0d1220;border:1px solid #1e2d4a;border-radius:12px;
        padding:20px 18px;position:relative;overflow:hidden;
    }
    .perf-scorecard::before {
        content:'';position:absolute;top:0;left:0;right:0;height:2px;
        background:linear-gradient(90deg,#1b6cf2,#00d4aa,#b794f4);
    }
    .perf-scorecard-title {
        font-family:'DM Mono',monospace;font-size:0.6rem;text-transform:uppercase;
        letter-spacing:0.18em;color:#3a5070;margin-bottom:14px;
    }
    .perf-big{font-family:'DM Mono',monospace;font-size:2rem;font-weight:500;line-height:1;}
    .perf-mid{font-family:'DM Mono',monospace;font-size:1.05rem;font-weight:500;}
    .perf-sm {font-family:'DM Mono',monospace;font-size:0.85rem;font-weight:500;}
    .perf-sub{font-size:0.7rem;color:#3a5070;margin-top:5px;font-family:'DM Mono',monospace;line-height:1.7;}
    .perf-badge{display:inline-block;font-family:'DM Mono',monospace;font-size:0.62rem;
        padding:2px 8px;border-radius:3px;margin-top:8px;}
    .perf-badge-pos{background:rgba(0,212,170,0.1);color:#00d4aa;border:1px solid rgba(0,212,170,0.25);}
    .perf-badge-neg{background:rgba(255,77,106,0.1);color:#ff4d6a;border:1px solid rgba(255,77,106,0.25);}
    .perf-badge-neu{background:rgba(74,158,255,0.1);color:#4a9eff;border:1px solid rgba(74,158,255,0.25);}
    .perf-divider{border:none;border-top:1px solid #1e2d4a;margin:9px 0;}
    .perf-row{display:flex;justify-content:space-between;align-items:center;margin:4px 0;}
    .perf-row-label{font-family:'DM Mono',monospace;font-size:0.63rem;color:#4a6080;}
    .perf-row-val  {font-family:'DM Mono',monospace;font-size:0.72rem;color:#c9d4e8;}
    .streak-box{background:#0d1220;border:1px solid #1e2d4a;border-radius:8px;padding:14px 16px;margin-bottom:10px;}
    .regime-high{background:rgba(255,77,106,0.07);border:1px solid rgba(255,77,106,0.2);}
    .regime-low {background:rgba(0,212,170,0.07);border:1px solid rgba(0,212,170,0.2);}
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">◈ Periyot & Frekans Seçimi</div>', unsafe_allow_html=True)
    sel_c1, sel_c2, sel_c3 = st.columns([2, 2, 3])
    with sel_c1:
        frekans = st.selectbox("Frekans",
            ["Günlük","Haftalık (7 gün)","Aylık","Çeyreklik","Yıllık"], index=1, key="cum_frekans")
    with sel_c2:
        bas_yil = int(df["Tarih"].min().year)
        bit_yil = int(df["Tarih"].max().year)
        yil_aralik = st.select_slider("Yıl Aralığı",
            options=list(range(bas_yil, bit_yil+1)),
            value=(bas_yil, bit_yil), key="cum_yil")
    with sel_c3:
        grafik_katmanlar = st.multiselect("Kümülatif Grafik Katmanları",
            ["Kümülatif Değişim %","Yuvarlanmalı Ort.","Volatilite Bandı"],
            default=["Kümülatif Değişim %","Yuvarlanmalı Ort."], key="cum_layers")

    # Yıllıklaştırma faktörleri
    ANNUALIZE = {"Günlük":252, "Haftalık (7 gün)":52, "Aylık":12, "Çeyreklik":4, "Yıllık":1}
    ann_factor = ANNUALIZE[frekans]

    # Periyot verisini hazırla — gerçek periyot bazlı hesaplamalar
    df_cum_filter = df[(df["Yil"] >= yil_aralik[0]) & (df["Yil"] <= yil_aralik[1])].copy()

    if frekans == "Günlük":
        periyot_df = df_cum_filter[["Tarih","Dolar_Kuru","Yuzde_Degisim","Yil"]].copy()
        periyot_df.columns = ["Tarih","Kur","Degisim","Yil"]
        x_fmt, adet_label = "%b %Y", "Günlük Gözlem"

    elif frekans == "Haftalık (7 gün)":
        # Gerçek haftalık veri: Pzt açılış → Paz kapanış
        hf_c = hf_global[
            (hf_global["AcilisTarih"].dt.year >= yil_aralik[0]) &
            (hf_global["KapanisTarih"].dt.year <= yil_aralik[1])].copy()
        periyot_df = pd.DataFrame({
            "Tarih":   hf_c["KapanisTarih"].values,
            "Kur":     hf_c["KapanisKur"].values,
            "Degisim": hf_c["HaftaDegisim"].values,
            "Yil":     hf_c["KapanisTarih"].dt.year.values,
        })
        x_fmt, adet_label = "%b %Y", "Haftalık Gözlem (7 takvim günü)"

    elif frekans == "Aylık":
        # Gerçek aylık veri: Ay başı → Ay sonu
        ay_c = ay_global[
            (ay_global["Yil"] >= yil_aralik[0]) &
            (ay_global["Yil"] <= yil_aralik[1])].copy()
        periyot_df = pd.DataFrame({
            "Tarih":   ay_c["KapanisTarih"].values,
            "Kur":     ay_c["KapanisKur"].values,
            "Degisim": ay_c["AyDegisim"].values,
            "Yil":     ay_c["Yil"].values,
        })
        x_fmt, adet_label = "%Y", "Aylık Gözlem (Ay Başı→Sonu)"

    elif frekans == "Çeyreklik":
        # Gerçek çeyreklik veri: Çeyrek başı → Çeyrek sonu
        cey_c = cey_global[
            (cey_global["Yil"] >= yil_aralik[0]) &
            (cey_global["Yil"] <= yil_aralik[1])].copy()
        periyot_df = pd.DataFrame({
            "Tarih":   cey_c["KapanisTarih"].values,
            "Kur":     cey_c["KapanisKur"].values,
            "Degisim": cey_c["CeyrekDegisim"].values,
            "Yil":     cey_c["Yil"].values,
        })
        x_fmt, adet_label = "%Y", "Çeyreklik Gözlem (Çeyrek Başı→Sonu)"

    else:  # Yıllık
        df_cum_y = df_cum_filter.copy()
        df_cum_y["Yil"] = df_cum_y["Tarih"].dt.year
        yil_g = df_cum_y.groupby("Yil").agg(
            AcilisTarih=("Tarih", "min"), AcilisKur=("Dolar_Kuru", "first"),
            KapanisTarih=("Tarih", "max"), KapanisKur=("Dolar_Kuru", "last")
        ).reset_index()
        yil_g["YilDegisim"] = (yil_g["KapanisKur"] / yil_g["AcilisKur"] - 1) * 100
        periyot_df = pd.DataFrame({
            "Tarih":   yil_g["KapanisTarih"].values,
            "Kur":     yil_g["KapanisKur"].values,
            "Degisim": yil_g["YilDegisim"].values,
            "Yil":     yil_g["Yil"].values,
        })
        x_fmt, adet_label = "%Y", "Yıllık Gözlem (Yıl Başı→Sonu)"

    periyot_df = periyot_df.sort_values("Tarih").reset_index(drop=True)

    # Kümülatif — bileşik (kur bazlı)
    kur0 = periyot_df["Kur"].iloc[0]
    periyot_df["Kumülatif"] = (periyot_df["Kur"] / kur0 - 1) * 100

    # Drawdown
    rolling_max = periyot_df["Kumülatif"].cummax()
    periyot_df["Drawdown"] = periyot_df["Kumülatif"] - rolling_max

    # MA
    ma_win = min(20, max(3, len(periyot_df)//10))
    periyot_df["MA"] = periyot_df["Kumülatif"].rolling(ma_win).mean()

    # Volatilite bandı
    periyot_df["Vol"] = periyot_df["Degisim"].rolling(ma_win).std()
    periyot_df["Band_ust"] = periyot_df["Kumülatif"] + periyot_df["Vol"] * 2
    periyot_df["Band_alt"] = periyot_df["Kumülatif"] - periyot_df["Vol"] * 2

    # Temel istatistikler
    n            = len(periyot_df)
    r            = periyot_df["Degisim"].dropna()
    ort          = r.mean()
    std          = r.std(ddof=1)
    toplam_get   = periyot_df["Kumülatif"].iloc[-1]
    max_dd       = periyot_df["Drawdown"].min()
    poz          = int((r > 0).sum())
    neg          = int((r < 0).sum())
    poz_oran     = poz / n * 100 if n > 0 else 0

    # CAGR
    n_yil = (periyot_df["Tarih"].iloc[-1] - periyot_df["Tarih"].iloc[0]).days / 365.25
    kur_son = periyot_df["Kur"].iloc[-1]
    cagr = ((kur_son / kur0) ** (1 / max(n_yil, 0.01)) - 1) * 100 if n_yil > 0 else 0.0

    # Sharpe / Sortino / Calmar
    ann_ort = ort * ann_factor
    ann_std = std * (ann_factor ** 0.5)
    sharpe  = ann_ort / ann_std if ann_std > 0 else 0.0
    neg_r   = r[r < 0]
    downside_std = neg_r.std(ddof=1) * (ann_factor ** 0.5) if len(neg_r) > 1 else 1e-9
    sortino = ann_ort / downside_std if downside_std > 0 else 0.0
    calmar = cagr / abs(max_dd) if abs(max_dd) > 0.001 else 0.0

    son_degisim = periyot_df["Degisim"].iloc[-1]
    pct_rank    = float((r <= son_degisim).mean() * 100)

    # Streak analizi
    def _streak_analiz(seri):
        streaks_pos, streaks_neg = [], []
        cur_val, cur_len = None, 0
        for v in seri:
            sign = 1 if v > 0 else (-1 if v < 0 else 0)
            if sign == cur_val:
                cur_len += 1
            else:
                if cur_val == 1:  streaks_pos.append(cur_len)
                if cur_val == -1: streaks_neg.append(cur_len)
                cur_val, cur_len = sign, 1
        if cur_val == 1:  streaks_pos.append(cur_len)
        if cur_val == -1: streaks_neg.append(cur_len)
        return (max(streaks_pos) if streaks_pos else 0,
                max(streaks_neg) if streaks_neg else 0,
                streaks_pos, streaks_neg)

    max_pos_streak, max_neg_streak, all_pos_str, all_neg_str = _streak_analiz(r.values)
    avg_pos_streak = np.mean(all_pos_str) if all_pos_str else 0
    avg_neg_streak = np.mean(all_neg_str) if all_neg_str else 0

    # Mevsimsellik
    if frekans in ["Günlük","Haftalık (7 gün)","Aylık"]:
        df_mevs = df_cum_filter.copy()
        mevs = df_mevs.groupby("Ay")["Yuzde_Degisim"].mean()
    else:
        mevs = pd.Series(dtype=float)

    # Volatilite rejimi
    periyot_df["Vol20"] = periyot_df["Degisim"].rolling(20, min_periods=5).std()
    vol_median = periyot_df["Vol20"].median()
    periyot_df["Rejim"] = periyot_df["Vol20"].apply(
        lambda x: "Yüksek Vol" if (pd.notna(x) and x > vol_median) else "Düşük Vol")

    # USD–EUR korelasyon
    usd_d = veri_isle_api(df_raw, "USD", tur_sec)
    eur_d = veri_isle_api(df_raw, "EUR", tur_sec)
    if usd_d is not None and eur_d is not None:
        kor_df = pd.merge(
            usd_d[["Tarih","Yuzde_Degisim"]].rename(columns={"Yuzde_Degisim":"USD"}),
            eur_d[["Tarih","Yuzde_Degisim"]].rename(columns={"Yuzde_Degisim":"EUR"}),
            on="Tarih", how="inner"
        ).dropna()
        kor_global = kor_df["USD"].corr(kor_df["EUR"])
        kor_rolling = kor_df.set_index("Tarih")[["USD","EUR"]].rolling(60).corr().unstack()["USD"]["EUR"].reset_index()
        kor_rolling.columns = ["Tarih","Korelasyon"]
    else:
        kor_global = None
        kor_rolling = None

    # Formatlar
    ilk_kur_s = fkur(kur0)
    son_kur_s = fkur(kur_son)
    tarih_bas = periyot_df["Tarih"].iloc[0].strftime("%d.%m.%Y")
    tarih_son = periyot_df["Tarih"].iloc[-1].strftime("%d.%m.%Y")
    s_ = lambda v: "+" if v >= 0 else ""
    f2 = lambda v: f'{v:.2f}'.replace('.',',')
    f3 = lambda v: f'{v:.3f}'.replace('.',',')
    f1 = lambda v: f'{v:.1f}'.replace('.',',')

    # Scorecard frekans etiketi
    _frekans_kisa = {"Günlük":"Gün","Haftalık (7 gün)":"Hft","Aylık":"Ay","Çeyreklik":"Çey","Yıllık":"Yıl"}
    frekans_kisa = _frekans_kisa.get(frekans, frekans[:3])

    # ════ SCORECARD SATIRI ════════════════════════════════════════════════
    st.markdown('<div class="section-label">◈ Performans Özeti</div>', unsafe_allow_html=True)
    sc1,sc2,sc3,sc4,sc5 = st.columns(5)

    with sc1:
        cagr_c = "#00d4aa" if cagr>=0 else "#ff4d6a"
        st.markdown(f"""<div class="perf-scorecard">
        <div class="perf-scorecard-title">◈ Kümülatif Getiri</div>
        <div class="perf-big" style="color:{'#00d4aa' if toplam_get>=0 else '#ff4d6a'}">
            {s_(toplam_get)}{f1(toplam_get)}%</div>
        <div class="perf-sub">Bileşik · {tarih_bas} – {tarih_son}<br>
            {ilk_kur_s} → {son_kur_s} ₺</div>
        <hr class="perf-divider">
        <div class="perf-row">
            <span class="perf-row-label">CAGR</span>
            <span class="perf-row-val" style="color:{cagr_c}">{s_(cagr)}{f2(cagr)}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Süre</span>
            <span class="perf-row-val">{n_yil:.1f} yıl</span>
        </div>
        <span class="perf-badge {'perf-badge-pos' if toplam_get>=0 else 'perf-badge-neg'}">
            {frekans} · {n} gözlem</span>
        </div>""", unsafe_allow_html=True)

    with sc2:
        st.markdown(f"""<div class="perf-scorecard">
        <div class="perf-scorecard-title">◈ Dağılım</div>
        <div style="display:flex;gap:10px;align-items:flex-end;margin-bottom:6px;">
            <div><div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:#3a5070;margin-bottom:3px;">POZİTİF</div>
                <div class="perf-big" style="color:#00d4aa;font-size:1.7rem;">{poz}</div></div>
            <div style="color:#1e2d4a;font-size:1.3rem;padding-bottom:2px;">/</div>
            <div><div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:#3a5070;margin-bottom:3px;">NEGATİF</div>
                <div class="perf-big" style="color:#ff4d6a;font-size:1.7rem;">{neg}</div></div>
        </div>
        <div class="perf-sub">{adet_label} · Toplam {n}</div>
        <div style="margin-top:9px;background:#131c2e;border-radius:4px;height:6px;overflow:hidden;">
            <div style="width:{min(poz_oran,100):.1f}%;background:linear-gradient(90deg,#00d4aa,#1b6cf2);height:100%;"></div>
        </div>
        <div class="perf-sub" style="margin-top:4px;">Pozitif oran: %{f1(poz_oran)}</div>
        <hr class="perf-divider">
        <div class="perf-row">
            <span class="perf-row-label">Son Değişim</span>
            <span class="perf-row-val" style="color:{'#00d4aa' if son_degisim>=0 else '#ff4d6a'}">{s_(son_degisim)}{f2(son_degisim)}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Pct. Rank</span>
            <span class="perf-row-val">%{f1(pct_rank)}</span>
        </div>
        </div>""", unsafe_allow_html=True)

    with sc3:
        st.markdown(f"""<div class="perf-scorecard">
        <div class="perf-scorecard-title">◈ Getiri İstatistikleri</div>
        <div class="perf-mid" style="color:{'#00d4aa' if ort>=0 else '#ff4d6a'}">
            {s_(ort)}{f3(ort)}%</div>
        <div class="perf-sub">Ort. {frekans.lower()} değişim</div>
        <hr class="perf-divider">
        <div class="perf-row">
            <span class="perf-row-label">Std Sapma ({frekans_kisa})</span>
            <span class="perf-row-val">±{f3(std)}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Yıllık Std</span>
            <span class="perf-row-val">±{f3(ann_std)}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">En İyi</span>
            <span class="perf-row-val" style="color:#00d4aa">+{f2(r.max())}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">En Kötü</span>
            <span class="perf-row-val" style="color:#ff4d6a">{f2(r.min())}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Çarpıklık</span>
            <span class="perf-row-val">{f2(float(r.skew()))}</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Basıklık</span>
            <span class="perf-row-val">{f2(float(r.kurtosis()))}</span>
        </div>
        </div>""", unsafe_allow_html=True)

    with sc4:
        sh_c  = "#00d4aa" if sharpe>0  else "#ff4d6a"
        so_c  = "#00d4aa" if sortino>0 else "#ff4d6a"
        ca_c  = "#00d4aa" if calmar>0  else "#ff4d6a"
        st.markdown(f"""<div class="perf-scorecard">
        <div class="perf-scorecard-title">◈ Risk Oranları</div>
        <div class="perf-row" style="margin-bottom:6px;">
            <span class="perf-row-label">Sharpe (yıllık, rf=0)</span>
            <span class="perf-row-val" style="color:{sh_c};font-size:0.85rem;">{f2(sharpe)}</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Sortino</span>
            <span class="perf-row-val" style="color:{so_c}">{f2(sortino)}</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Calmar</span>
            <span class="perf-row-val" style="color:{ca_c}">{f2(calmar)}</span>
        </div>
        <hr class="perf-divider">
        <div class="perf-row">
            <span class="perf-row-label">Max Drawdown</span>
            <span class="perf-row-val" style="color:#ff4d6a">{f2(max_dd)}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Downside Std</span>
            <span class="perf-row-val">±{f2(downside_std)}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">VaR %95 (hist.)</span>
            <span class="perf-row-val" style="color:#f6ad55">{f2(float(np.percentile(r,5)))}%</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">CVaR %95</span>
            <span class="perf-row-val" style="color:#f6ad55">{f2(float(r[r <= np.percentile(r,5)].mean()))}%</span>
        </div>
        </div>""", unsafe_allow_html=True)

    with sc5:
        yil_perf_sc = periyot_df.groupby("Yil")["Degisim"].agg(ort="mean", adet="count").reset_index()
        en_iyi  = yil_perf_sc.loc[yil_perf_sc["ort"].idxmax()]
        en_kotu = yil_perf_sc.loc[yil_perf_sc["ort"].idxmin()]
        st.markdown(f"""<div class="perf-scorecard">
        <div class="perf-scorecard-title">◈ Streak & Ekstremler</div>
        <div class="perf-row">
            <span class="perf-row-label">Max Poz. Seri</span>
            <span class="perf-row-val" style="color:#00d4aa">{max_pos_streak} {frekans_kisa}</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Max Neg. Seri</span>
            <span class="perf-row-val" style="color:#ff4d6a">{max_neg_streak} {frekans_kisa}</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Ort. Poz. Seri</span>
            <span class="perf-row-val">{avg_pos_streak:.1f}</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">Ort. Neg. Seri</span>
            <span class="perf-row-val">{avg_neg_streak:.1f}</span>
        </div>
        <hr class="perf-divider">
        <div class="perf-row">
            <span class="perf-row-label">En İyi Yıl</span>
            <span class="perf-row-val" style="color:#00d4aa">{int(en_iyi['Yil'])} (+{f2(en_iyi['ort'])}%)</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">En Kötü Yıl</span>
            <span class="perf-row-val" style="color:#ff4d6a">{int(en_kotu['Yil'])} ({f2(en_kotu['ort'])}%)</span>
        </div>
        <div class="perf-row">
            <span class="perf-row-label">{'USD-EUR Kor.' if kor_global is not None else ''}</span>
            <span class="perf-row-val" style="color:#b794f4">{f2(kor_global) if kor_global is not None else '—'}</span>
        </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════ GRAFİK 1 — Kümülatif + Drawdown ════════════════════════════════
    st.markdown(
        f'<div class="section-label">◈ Kümülatif Getiri & Drawdown — {frekans} '
        f'<span style="color:#4a9eff;font-size:0.8rem;font-weight:400;">'
        f'· {yil_aralik[0]}–{yil_aralik[1]} · {n} gözlem · CAGR {s_(cagr)}{f2(cagr)}%</span></div>',
        unsafe_allow_html=True)

    fig_cum = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.68, 0.32], vertical_spacing=0.04)

    if "Volatilite Bandı" in grafik_katmanlar:
        xb = pd.concat([periyot_df["Tarih"], periyot_df["Tarih"][::-1]]).reset_index(drop=True)
        yb = pd.concat([periyot_df["Band_ust"], periyot_df["Band_alt"][::-1]]).reset_index(drop=True)
        fig_cum.add_trace(go.Scatter(
            x=xb, y=yb, fill="toself",
            fillcolor="rgba(74,158,255,0.05)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Vol Bandı ±2σ", hoverinfo="skip"), row=1, col=1)

    if "Kümülatif Değişim %" in grafik_katmanlar:
        fig_cum.add_trace(go.Scatter(
            x=periyot_df["Tarih"], y=periyot_df["Kumülatif"],
            mode="lines", name="Kümülatif %",
            line=dict(color="#4a9eff", width=2),
            fill="tozeroy", fillcolor="rgba(74,158,255,0.06)",
            customdata=list(zip(
                periyot_df["Kur"].apply(tr_fmt_kur),
                periyot_df["Degisim"].apply(lambda x: tr_fmt_pct(x,2)),
                periyot_df["Kumülatif"].apply(lambda x: tr_fmt_pct(x,2))
            )),
            hovertemplate="<b>%{x|%d.%m.%Y}</b><br>Kur: %{customdata[0]} ₺<br>"
                          f"{frekans} Δ: <b>%{{customdata[1]}}</b><br>"
                          "Kümülatif: <b>%{customdata[2]}</b><extra></extra>"),
            row=1, col=1)

    if "Yuvarlanmalı Ort." in grafik_katmanlar:
        fig_cum.add_trace(go.Scatter(
            x=periyot_df["Tarih"], y=periyot_df["MA"],
            mode="lines", name=f"MA{ma_win}",
            line=dict(color="#f6ad55", width=1.4, dash="dot"),
            hovertemplate="%{x|%d.%m.%Y}<br>MA: <b>%{y:.2f}%</b><extra></extra>"),
            row=1, col=1)

    fig_cum.add_trace(go.Scatter(
        x=periyot_df["Tarih"], y=periyot_df["Drawdown"],
        mode="lines", name="Drawdown",
        line=dict(color="#ff4d6a", width=1),
        fill="tozeroy", fillcolor="rgba(255,77,106,0.12)",
        hovertemplate="%{x|%d.%m.%Y}<br>Drawdown: <b>%{y:.2f}%</b><extra></extra>"),
        row=2, col=1)

    fig_cum.add_hline(y=0, line_color="#2a4a7a", line_width=1, row=1, col=1)
    fig_cum.add_hline(y=0, line_color="#2a4a7a", line_width=1, row=2, col=1)

    fig_cum.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,32,0.9)",
        font=dict(color="#c9d4e8", family="DM Sans, sans-serif"), height=560,
        title=dict(text=f"KÜMÜLATİF & DRAWDOWN — {doviz_label} — {frekans.upper()}",
                   font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
        legend={**LEGEND_RIGHT}, margin=dict(l=50,r=120,t=50,b=40),
        hoverlabel=dict(bgcolor="#0d1220", font_size=12, font_color="#e8f0ff"),
        xaxis2=dict(gridcolor="#131c2e", tickformat=x_fmt, tickfont=dict(size=10,color="#4a6080")),
        xaxis=dict(gridcolor="#131c2e", tickfont=dict(size=10,color="#4a6080")),
        yaxis=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10,color="#4a6080")),
        yaxis2=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10,color="#4a6080")),
        hovermode="x unified"
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    # ════ GRAFİK 2 — Bar + Yıl bazlı matris ══════════════════════════════
    col_g2a, col_g2b = st.columns([3, 2])

    with col_g2a:
        st.markdown(
            f'<div class="section-label">◈ {frekans} Değişim + Kümülatif Birikim</div>',
            unsafe_allow_html=True)
        periyot_df["_rc"] = periyot_df["Degisim"].apply(lambda x: "#00d4aa" if x>=0 else "#ff4d6a")

        fig_bar = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.52, 0.48], vertical_spacing=0.04,
            subplot_titles=[
                f"{frekans} Periyot Değişimi",
                "Kümülatif Birikim (başlangıçtan bugüne, bileşik)"
            ]
        )
        fig_bar.add_trace(go.Bar(
            x=periyot_df["Tarih"], y=periyot_df["Degisim"],
            marker_color=periyot_df["_rc"].values, marker_line_width=0, opacity=0.85,
            name=f"{frekans} Δ",
            customdata=list(zip(
                periyot_df["Degisim"].apply(lambda x: tr_fmt_pct(x,2)),
                periyot_df["Kur"].apply(tr_fmt_kur),
                periyot_df["Kumülatif"].apply(lambda x: tr_fmt_pct(x,2))
            )),
            hovertemplate="<b>%{x|%d.%m.%Y}</b><br>"
                          f"{frekans} Δ: <b>%{{customdata[0]}}</b><br>"
                          "Kur: %{customdata[1]} ₺<br>"
                          "Kümülatif: %{customdata[2]}<extra></extra>"
        ), row=1, col=1)
        fig_bar.add_hline(y=0, line_color="#2a4a7a", line_width=1, row=1, col=1)

        fig_bar.add_trace(go.Scatter(
            x=periyot_df["Tarih"], y=periyot_df["Kumülatif"],
            mode="lines", name="Kümülatif %",
            line=dict(color="#4a9eff", width=2),
            fill="tozeroy", fillcolor="rgba(74,158,255,0.08)",
            customdata=list(zip(
                periyot_df["Kumülatif"].apply(lambda x: tr_fmt_pct(x,2)),
                periyot_df["Kur"].apply(tr_fmt_kur)
            )),
            hovertemplate="<b>%{x|%d.%m.%Y}</b><br>"
                          "Kümülatif: <b>%{customdata[0]}</b><br>"
                          "Kur: %{customdata[1]} ₺<extra></extra>"
        ), row=2, col=1)
        fig_bar.add_hline(y=0, line_color="#2a4a7a", line_width=1, row=2, col=1)

        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,32,0.9)",
            font=dict(color="#c9d4e8", family="DM Sans, sans-serif"), height=500,
            legend={**LEGEND_RIGHT}, margin=dict(l=50,r=80,t=50,b=40),
            hoverlabel=dict(bgcolor="#0d1220", font_size=12, font_color="#e8f0ff"),
            xaxis=dict(gridcolor="#131c2e", tickformat=x_fmt, tickfont=dict(size=10,color="#4a6080")),
            xaxis2=dict(gridcolor="#131c2e", tickformat=x_fmt, tickfont=dict(size=10,color="#4a6080")),
            yaxis=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10,color="#4a6080")),
            yaxis2=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10,color="#4a6080")),
            showlegend=False, hovermode="x unified"
        )
        fig_bar.update_annotations(font=dict(size=9, color="#4a6080", family="DM Mono, monospace"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2b:
        st.markdown('<div class="section-label">◈ Yıl Bazlı Kartlar</div>', unsafe_allow_html=True)
        yil_perf_full = periyot_df.groupby("Yil").agg(
            Adet=("Degisim","count"), Ort_Pct=("Degisim","mean"),
            En_Iyi=("Degisim","max"), En_Kotu=("Degisim","min"),
            Std=("Degisim","std"),
            Poz_Adet=("Degisim", lambda x: (x>0).sum()),
        ).reset_index()
        yil_perf_full["Poz_Oran"] = (yil_perf_full["Poz_Adet"]/yil_perf_full["Adet"]*100).round(1)

        for _, yr in yil_perf_full.sort_values("Yil", ascending=False).iterrows():
            ort_c = "#00d4aa" if yr["Ort_Pct"]>=0 else "#ff4d6a"
            sign  = "+" if yr["Ort_Pct"]>=0 else ""
            st.markdown(f"""
            <div style="background:#0d1220;border:1px solid #1e2d4a;border-left:3px solid {ort_c};
                        border-radius:6px;padding:10px 12px;margin-bottom:7px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-family:'DM Mono',monospace;font-size:0.78rem;color:#c9d4e8;font-weight:500;">{int(yr['Yil'])}</span>
                    <span style="font-family:'DM Mono',monospace;font-size:0.85rem;color:{ort_c};font-weight:500;">{sign}{f2(yr['Ort_Pct'])}%</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:4px;">
                    <span style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#3a5070;">{int(yr['Adet'])} gözlem · %{yr['Poz_Oran']:.0f} poz</span>
                    <span style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#3a5070;">±{f2(yr['Std'])}%</span>
                </div>
                <div style="margin-top:5px;background:#131c2e;border-radius:3px;height:3px;overflow:hidden;">
                    <div style="width:{yr['Poz_Oran']:.1f}%;background:{ort_c};height:100%;opacity:0.7;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    # ════ GRAFİK 3 — Yıl Üstüne Yıl ════════════════════════════════════
    st.markdown('<div class="section-label">◈ Yıl İçi Kümülatif — Yıl Üstüne Yıl</div>', unsafe_allow_html=True)
    YILLAR = sorted(periyot_df["Yil"].unique())
    YCOLOR = ["#4a9eff","#00d4aa","#f6ad55","#b794f4","#ff4d6a",
              "#60a5fa","#34d399","#fbbf24","#a78bfa","#fb7185",
              "#38bdf8","#4ade80","#facc15","#c084fc","#f43f5e"]
    fig_yoy = go.Figure()
    for i, yil in enumerate(YILLAR):
        sub = periyot_df[periyot_df["Yil"]==yil].copy().reset_index(drop=True)
        if len(sub)<2: continue
        sub["YilKum"] = (sub["Kur"] / sub["Kur"].iloc[0] - 1) * 100
        color = YCOLOR[i % len(YCOLOR)]
        fig_yoy.add_trace(go.Scatter(
            x=sub.index, y=sub["YilKum"], mode="lines", name=str(yil),
            line=dict(color=color, width=1.5), opacity=0.85,
            customdata=list(zip(
                sub["Tarih"].dt.strftime("%d.%m.%Y"),
                sub["Kur"].apply(tr_fmt_kur),
                sub["YilKum"].apply(lambda x: tr_fmt_pct(x,2))
            )),
            hovertemplate=f"<b>{yil}</b> — %{{customdata[0]}}<br>"
                          "Kur: %{customdata[1]} ₺<br>"
                          "Yıl içi kümülatif: <b>%{customdata[2]}</b><extra></extra>"
        ))
    fig_yoy.add_hline(y=0, line_color="#2a4a7a", line_width=1, line_dash="dash")
    apply_base(fig_yoy, height=460,
        title=dict(text=f"YIL İÇİ KÜMÜLATİF ({frekans.upper()}) — YIL ÜZERİNE YIL",
                   font=dict(size=11,color="#4a6080",family="DM Mono, monospace"), x=0),
        xaxis=dict(gridcolor="#131c2e", title=dict(text=f"{frekans} sırası",font=dict(size=10,color="#4a6080")),
                   tickfont=dict(size=10,color="#4a6080")),
        yaxis=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10,color="#4a6080")),
        hovermode="closest",
        legend=dict(bgcolor="rgba(13,18,32,0.9)",bordercolor="#1e2d4a",borderwidth=1,
                    font=dict(size=10),orientation="v",x=1.01,xanchor="left",y=0.5,yanchor="middle"))
    st.plotly_chart(fig_yoy, use_container_width=True)

    # ════ GRAFİK 4 — Mevsimsellik ═════════════════════════════════════════
    if len(mevs) > 0:
        st.markdown('<div class="section-label">◈ Mevsimsellik — Ay Bazlı Ortalama Günlük Getiri</div>', unsafe_allow_html=True)
        ay_ort_genel = df_cum_filter["Yuzde_Degisim"].mean()
        mevs_df = mevs.reset_index()
        mevs_df.columns = ["Ay","OrtGetiri"]
        mevs_df["AyAdi"] = mevs_df["Ay"].map(TR_AY_UZUN)
        mevs_df["FarkGenel"] = mevs_df["OrtGetiri"] - ay_ort_genel
        mevs_df["_renk"] = mevs_df["FarkGenel"].apply(lambda x: "#00d4aa" if x>=0 else "#ff4d6a")
        mevs_df["_ort_s"] = mevs_df["OrtGetiri"].apply(lambda x: tr_fmt_pct(x,3))
        mevs_df["_fark_s"] = mevs_df["FarkGenel"].apply(lambda x: tr_fmt_pct(x,3))

        fig_mevs = go.Figure()
        fig_mevs.add_trace(go.Bar(
            x=mevs_df["AyAdi"], y=mevs_df["OrtGetiri"],
            marker_color=mevs_df["_renk"].values, marker_line_width=0, opacity=0.85,
            customdata=list(zip(mevs_df["_ort_s"], mevs_df["_fark_s"])),
            hovertemplate="<b>%{x}</b><br>Ort. günlük: <b>%{customdata[0]}</b><br>"
                          "Genel ort. farkı: <b>%{customdata[1]}</b><extra></extra>"
        ))
        fig_mevs.add_hline(y=ay_ort_genel, line_dash="dash", line_color="#f6ad55", line_width=1.5,
                           annotation_text=f"Genel ort. {tr_fmt_pct(ay_ort_genel,3)}",
                           annotation_font_color="#f6ad55", annotation_font_size=10)
        fig_mevs.add_hline(y=0, line_color="#2a4a7a", line_width=1)
        tv_m, tt_m = safe_ticks(mevs_df["OrtGetiri"].min(), mevs_df["OrtGetiri"].max(), n=8, decimals=3, suffix="%")
        apply_base(fig_mevs, height=360,
            title=dict(text="MEVSİMSELLİK — AY BAZLI ORT. GÜNLÜK GETİRİ",
                       font=dict(size=11,color="#4a6080",family="DM Mono, monospace"), x=0),
            xaxis=dict(gridcolor="#131c2e", tickfont=dict(size=10,color="#4a6080")),
            yaxis={**yt(tv_m, tt_m, {"gridcolor":"#131c2e","tickfont":dict(size=10,color="#4a6080")})},
            showlegend=False, hovermode="closest")
        st.plotly_chart(fig_mevs, use_container_width=True)

    # ════ GRAFİK 5 — Regime Detection ════════════════════════════════════
    st.markdown('<div class="section-label">◈ Volatilite Rejimi — Yüksek / Düşük</div>', unsafe_allow_html=True)

    periyot_nona = periyot_df.dropna(subset=["Vol20"]).copy()
    regime_high = periyot_nona[periyot_nona["Rejim"]=="Yüksek Vol"]
    regime_low  = periyot_nona[periyot_nona["Rejim"]=="Düşük Vol"]

    fig_reg = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.6,0.4], vertical_spacing=0.04)

    fig_reg.add_trace(go.Scatter(
        x=periyot_df["Tarih"], y=periyot_df["Kur"],
        mode="lines", name="Kur",
        line=dict(color="#2a4a7a", width=1.5),
        hovertemplate="%{x|%d.%m.%Y}<br>Kur: <b>%{y:.4f} ₺</b><extra></extra>"),
        row=1, col=1)

    in_high = False
    x_start = None
    for _, row_r in periyot_nona.iterrows():
        if row_r["Rejim"]=="Yüksek Vol" and not in_high:
            x_start = row_r["Tarih"]; in_high=True
        elif row_r["Rejim"]!="Yüksek Vol" and in_high:
            fig_reg.add_vrect(x0=x_start, x1=row_r["Tarih"],
                fillcolor="rgba(255,77,106,0.07)", layer="below", line_width=0, row=1, col=1)
            in_high=False
    if in_high and x_start is not None:
        fig_reg.add_vrect(x0=x_start, x1=periyot_nona["Tarih"].iloc[-1],
            fillcolor="rgba(255,77,106,0.07)", layer="below", line_width=0, row=1, col=1)

    fig_reg.add_trace(go.Scatter(
        x=periyot_nona["Tarih"], y=periyot_nona["Vol20"],
        mode="lines", name=f"Vol (20 periyot)",
        line=dict(color="#b794f4", width=1.5),
        hovertemplate="%{x|%d.%m.%Y}<br>Vol: <b>%{y:.3f}%</b><extra></extra>"),
        row=2, col=1)
    fig_reg.add_hline(y=float(vol_median), line_dash="dash",
                      line_color="#f6ad55", line_width=1.2,
                      annotation_text=f"Medyan {float(vol_median):.3f}%",
                      annotation_font_color="#f6ad55", annotation_font_size=9, row=2, col=1)

    fig_reg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,32,0.9)",
        font=dict(color="#c9d4e8",family="DM Sans, sans-serif"), height=520,
        title=dict(text="VOLATİLİTE REJİMİ — YÜKSEK (kırmızı şerit) / DÜŞÜK",
                   font=dict(size=11,color="#4a6080",family="DM Mono, monospace"), x=0),
        legend={**LEGEND_RIGHT}, margin=dict(l=50,r=120,t=50,b=40),
        hoverlabel=dict(bgcolor="#0d1220",font_size=12,font_color="#e8f0ff"),
        xaxis=dict(gridcolor="#131c2e",tickfont=dict(size=10,color="#4a6080")),
        xaxis2=dict(gridcolor="#131c2e",tickformat=x_fmt,tickfont=dict(size=10,color="#4a6080")),
        yaxis=dict(gridcolor="#131c2e",tickfont=dict(size=10,color="#4a6080")),
        yaxis2=dict(gridcolor="#131c2e",ticksuffix="%",tickfont=dict(size=10,color="#4a6080")),
        hovermode="x unified"
    )
    st.plotly_chart(fig_reg, use_container_width=True)

    reg_col1, reg_col2 = st.columns(2)
    for rcol, rdf, rlabel, rcolor in [
        (reg_col1, regime_high, "Yüksek Volatilite Rejimi", "#ff4d6a"),
        (reg_col2, regime_low,  "Düşük Volatilite Rejimi",  "#00d4aa"),
    ]:
        with rcol:
            rd = rdf["Degisim"]
            st.markdown(f"""
            <div class="perf-scorecard" style="border-top:2px solid {rcolor};">
                <div class="perf-scorecard-title" style="color:{rcolor};">◈ {rlabel}</div>
                <div class="perf-row"><span class="perf-row-label">Gözlem</span>
                    <span class="perf-row-val">{len(rd)}</span></div>
                <div class="perf-row"><span class="perf-row-label">Ort. Getiri</span>
                    <span class="perf-row-val" style="color:{rcolor};">{s_(rd.mean())}{f3(rd.mean())}%</span></div>
                <div class="perf-row"><span class="perf-row-label">Std Sapma</span>
                    <span class="perf-row-val">±{f3(rd.std())}%</span></div>
                <div class="perf-row"><span class="perf-row-label">Pozitif Oran</span>
                    <span class="perf-row-val">%{f1((rd>0).mean()*100)}</span></div>
                <div class="perf-row"><span class="perf-row-label">En İyi</span>
                    <span class="perf-row-val" style="color:#00d4aa;">+{f2(rd.max())}%</span></div>
                <div class="perf-row"><span class="perf-row-label">En Kötü</span>
                    <span class="perf-row-val" style="color:#ff4d6a;">{f2(rd.min())}%</span></div>
            </div>""", unsafe_allow_html=True)

    # ════ GRAFİK 6 — Korelasyon ══════════════════════════════════════════
    if kor_rolling is not None and len(kor_rolling.dropna()) > 10:
        st.markdown('<div class="section-label">◈ USD/TRY — EUR/TRY Korelasyon (60 Günlük Yuvarlanmalı)</div>', unsafe_allow_html=True)
        kor_plot = kor_rolling.dropna().copy()
        fig_kor = go.Figure()
        fig_kor.add_trace(go.Scatter(
            x=kor_plot["Tarih"], y=kor_plot["Korelasyon"],
            mode="lines", name="60G Korelasyon",
            line=dict(color="#4a9eff", width=1.5),
            fill="tozeroy", fillcolor="rgba(74,158,255,0.06)",
            hovertemplate="%{x|%d.%m.%Y}<br>Korelasyon: <b>%{y:.4f}</b><extra></extra>"
        ))
        fig_kor.add_hline(y=float(kor_global), line_dash="dash", line_color="#f6ad55", line_width=1.2,
                          annotation_text=f"Tarihsel ort. {kor_global:.4f}",
                          annotation_font_color="#f6ad55", annotation_font_size=9)
        fig_kor.add_hline(y=0, line_color="#2a4a7a", line_width=1)
        apply_base(fig_kor, height=360,
            title=dict(text=f"USD/TRY — EUR/TRY GÜNLÜK GETİRİ KORELASYONU · Tarihsel ort: {kor_global:.4f}",
                       font=dict(size=11,color="#4a6080",family="DM Mono, monospace"), x=0),
            xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y", tickfont=dict(size=10,color="#4a6080")),
            yaxis=dict(gridcolor="#131c2e", range=[-0.1,1.05], tickfont=dict(size=10,color="#4a6080")),
            hovermode="x unified", showlegend=False)
        st.plotly_chart(fig_kor, use_container_width=True)

    # ════ GRAFİK 7 — Streak Analizi ══════════════════════════════════════
    st.markdown('<div class="section-label">◈ Streak Analizi — Ardışık Pozitif / Negatif Seriler</div>', unsafe_allow_html=True)

    str_col1, str_col2 = st.columns(2)

    def _streak_hist(streaks, color, title, label):
        if not streaks:
            return go.Figure()
        s_arr = np.array(streaks)
        counts = pd.Series(s_arr).value_counts().sort_index()
        mean_val = float(np.mean(s_arr))
        x_labels = counts.index.astype(str).tolist()
        x_numeric = [int(v) for v in counts.index]
        mean_pos  = min(range(len(x_numeric)), key=lambda i: abs(x_numeric[i] - mean_val))

        fig_s = go.Figure(go.Bar(
            x=x_labels, y=counts.values,
            marker_color=color, marker_line_width=0, opacity=0.85,
            hovertemplate=f"{label}: <b>%{{x}}</b><br>Frekans: <b>%{{y}}</b><extra></extra>"
        ))
        fig_s.add_shape(
            type="line", xref="x", yref="paper",
            x0=x_labels[mean_pos], x1=x_labels[mean_pos],
            y0=0, y1=1,
            line=dict(color="#f6ad55", width=1.2, dash="dash")
        )
        fig_s.add_annotation(
            x=x_labels[mean_pos], xref="x",
            y=1, yref="paper",
            text=f"Ort. {mean_val:.1f}",
            font=dict(color="#f6ad55", size=9, family="DM Mono, monospace"),
            showarrow=False, yanchor="bottom", xanchor="left",
            bgcolor="rgba(13,18,32,0.7)"
        )
        apply_base(fig_s, height=300,
            title=dict(text=title, font=dict(size=11,color="#4a6080",family="DM Mono, monospace"), x=0),
            xaxis=dict(gridcolor="#131c2e", tickfont=dict(size=10,color="#4a6080"),
                       title=dict(text=f"Ardışık {frekans.lower()} sayısı", font=dict(size=9,color="#4a6080"))),
            yaxis=dict(gridcolor="#131c2e", tickfont=dict(size=10,color="#4a6080"),
                       title=dict(text="Frekans", font=dict(size=9,color="#4a6080"))),
            showlegend=False)
        return fig_s

    with str_col1:
        fig_sp = _streak_hist(all_pos_str, "#00d4aa",
                              f"POZİTİF SERİ DAĞILIMI · Max {max_pos_streak}",
                              f"Ardışık pozitif {frekans.lower()}")
        st.plotly_chart(fig_sp, use_container_width=True)

    with str_col2:
        fig_sn = _streak_hist(all_neg_str, "#ff4d6a",
                              f"NEGATİF SERİ DAĞILIMI · Max {max_neg_streak}",
                              f"Ardışık negatif {frekans.lower()}")
        st.plotly_chart(fig_sn, use_container_width=True)

    # ════ GRAFİK 8 — Momentum ════════════════════════════════════════════
    st.markdown('<div class="section-label">◈ Momentum — Kısa / Uzun Vade Çaprazlama</div>', unsafe_allow_html=True)

    m_win_k = max(5,  min(20,  n//10))
    m_win_u = max(20, min(60,  n//3))
    periyot_df["Mom_K"] = periyot_df["Kur"].rolling(m_win_k).mean()
    periyot_df["Mom_U"] = periyot_df["Kur"].rolling(m_win_u).mean()

    fig_mom = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.65, 0.35], vertical_spacing=0.04)
    fig_mom.add_trace(go.Scatter(
        x=periyot_df["Tarih"], y=periyot_df["Kur"], mode="lines",
        name="Kur", line=dict(color="#2a4a7a", width=1.5),
        hovertemplate="%{x|%d.%m.%Y}<br>%{y:.4f} ₺<extra></extra>"), row=1, col=1)
    fig_mom.add_trace(go.Scatter(
        x=periyot_df["Tarih"], y=periyot_df["Mom_K"], mode="lines",
        name=f"MA{m_win_k} (hızlı)", line=dict(color="#00d4aa", width=1.3),
        hovertemplate=f"MA{m_win_k}: %{{y:.4f}} ₺<extra></extra>"), row=1, col=1)
    fig_mom.add_trace(go.Scatter(
        x=periyot_df["Tarih"], y=periyot_df["Mom_U"], mode="lines",
        name=f"MA{m_win_u} (yavaş)", line=dict(color="#f6ad55", width=1.3, dash="dot"),
        hovertemplate=f"MA{m_win_u}: %{{y:.4f}} ₺<extra></extra>"), row=1, col=1)

    periyot_df["Mom_Bar"] = periyot_df["Mom_K"] - periyot_df["Mom_U"]
    periyot_df["_mb_c"] = periyot_df["Mom_Bar"].apply(lambda x: "#00d4aa" if x>=0 else "#ff4d6a")
    fig_mom.add_trace(go.Bar(
        x=periyot_df["Tarih"], y=periyot_df["Mom_Bar"],
        marker_color=periyot_df["_mb_c"].values, marker_line_width=0, opacity=0.7,
        name="Momentum Farkı",
        hovertemplate="%{x|%d.%m.%Y}<br>Fark: <b>%{y:.4f}</b><extra></extra>"), row=2, col=1)
    fig_mom.add_hline(y=0, line_color="#2a4a7a", line_width=1, row=2, col=1)

    fig_mom.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,32,0.9)",
        font=dict(color="#c9d4e8",family="DM Sans, sans-serif"), height=520,
        title=dict(text=f"MOMENTUM — MA{m_win_k} / MA{m_win_u} ÇAPRAZLAMA",
                   font=dict(size=11,color="#4a6080",family="DM Mono, monospace"), x=0),
        legend={**LEGEND_RIGHT}, margin=dict(l=50,r=120,t=50,b=40),
        hoverlabel=dict(bgcolor="#0d1220",font_size=12,font_color="#e8f0ff"),
        xaxis=dict(gridcolor="#131c2e",tickfont=dict(size=10,color="#4a6080")),
        xaxis2=dict(gridcolor="#131c2e",tickformat=x_fmt,tickfont=dict(size=10,color="#4a6080")),
        yaxis=dict(gridcolor="#131c2e",tickfont=dict(size=10,color="#4a6080")),
        yaxis2=dict(gridcolor="#131c2e",tickfont=dict(size=10,color="#4a6080")),
        hovermode="x unified"
    )
    st.plotly_chart(fig_mom, use_container_width=True)

    # ════ İNDİR ═══════════════════════════════════════════════════════════
    st.markdown('<div class="section-label">◈ Performans Verisini İndir</div>', unsafe_allow_html=True)
    dl_c1, dl_c2, _ = st.columns([1,1,4])

    perf_exp = periyot_df[["Tarih","Yil","Kur","Degisim","Kumülatif","Drawdown"]].copy()
    perf_exp.columns = ["Tarih","Yil","Kur","Degisim_%","Kumülatif_%","Drawdown_%"]
    perf_exp["Tarih"] = perf_exp["Tarih"].dt.strftime("%d.%m.%Y")

    with dl_c1:
        csv_pf = perf_exp.to_csv(index=False).encode("utf-8-sig")
        st.download_button(f"⬇ CSV ({frekans})", csv_pf,
            f"performans_{frekans.lower()}_{yil_aralik[0]}_{yil_aralik[1]}.csv",
            "text/csv", use_container_width=True)
    with dl_c2:
        buf_pf = io.BytesIO()
        with pd.ExcelWriter(buf_pf, engine="openpyxl") as w:
            perf_exp.to_excel(w, sheet_name="Kumulatif", index=False)
            yil_perf_full.to_excel(w, sheet_name="Yil_Bazli", index=False)
            if len(mevs)>0:
                mevs_df[["AyAdi","OrtGetiri","FarkGenel"]].to_excel(w, sheet_name="Mevsimsellik", index=False)
        st.download_button(f"⬇ Excel ({frekans})", buf_pf.getvalue(),
            f"performans_{frekans.lower()}_{yil_aralik[0]}_{yil_aralik[1]}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

st.markdown("""
<div style="text-align:center; color:#1e2d4a; font-size:0.7rem; padding:30px 0 10px 0;
            border-top:1px solid #0d1220; margin-top:30px;
            font-family:'DM Mono',monospace; letter-spacing:0.1em;">
    TCMB EVDS · USDTRY / EURTRY ANALİZ PLATFORMU · STREAMLIT + PLOTLY
</div>
""", unsafe_allow_html=True)

with tab5:
    st.markdown(f'<div class="section-label">◈ Büyük Sıçramalardan Sonra Ne Oluyor? (≥%{fwd_threshold})</div>', unsafe_allow_html=True)
    periods = [1, 5, 10, 21, 63]
    period_labels = {1:"1G", 5:"5G (1Hf)", 10:"10G (2Hf)", 21:"21G (1Ay)", 63:"63G (3Ay)"}
    fwd = forward_analysis(df, fwd_threshold, periods)

    if not fwd:
        st.warning(f"%{fwd_threshold} eşiğinde yeterli sıçrama bulunamadı.")
    else:
        cards_html = ""
        for p in periods:
            if p in fwd:
                r = fwd[p]
                mean_cls = "metric-pos" if r["mean"] >= 0 else "metric-neg"
                sign = "+" if r["mean"] >= 0 else ""
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
        fig_box = go.Figure()
        colors_box = ["#4a9eff","#00d4aa","#f6ad55","#b794f4","#ff4d6a"]
        for i, p in enumerate(periods):
            if p in fwd:
                c = colors_box[i]
                rr, gg, bb = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
                fig_box.add_trace(go.Box(y=fwd[p]["raw"], name=period_labels[p], marker_color=c,
                    boxpoints="outliers", line_width=1.5, fillcolor=f"rgba({rr},{gg},{bb},0.1)",
                    hovertemplate="%{y:.3f}%<extra></extra>"))
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
            hovertemplate="%{x}<br>Pozitif oran: <b>%{y:.1f}%</b><extra></extra>"
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
        means_21, counts_21 = [], []
        for thr in thresholds:
            f_tmp = forward_analysis(df, thr, [21])
            if 21 in f_tmp and f_tmp[21]["n"] >= 5:
                means_21.append(f_tmp[21]["mean"])
                counts_21.append(f_tmp[21]["n"])
            else:
                means_21.append(np.nan)
                counts_21.append(0)
        fig_sens = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sens.add_trace(go.Scatter(x=thresholds, y=means_21, mode="lines+markers", name="Ort. 21G Getiri",
            line=dict(color="#4a9eff", width=2), marker=dict(size=6),
            hovertemplate="Eşik: %{x:.1f}%<br>Ort. 21G: <b>%{y:.2f}%</b><extra></extra>"), secondary_y=False)
        fig_sens.add_trace(go.Bar(x=thresholds, y=counts_21, name="Örnek Sayısı",
            marker_color="rgba(74,158,255,0.15)",
            hovertemplate="Eşik: %{x:.1f}%<br>n: %{y}<extra></extra>"), secondary_y=True)
        fig_sens.add_hline(y=0, line_color="#1e2d4a", line_width=1)
        fig_sens.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,32,0.9)",
            font=dict(color="#c9d4e8", family="DM Sans, sans-serif"), height=400,
            title=dict(text="EŞİK HASSASIYETI — 21G ORTALAMA GETİRİ", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            legend={**LEGEND_RIGHT},
            margin=dict(l=50, r=120, t=50, b=40),
            hoverlabel=dict(bgcolor="#0d1220", font_size=12, font_color="#e8f0ff"),
            xaxis=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10, color="#4a6080")),
            yaxis=dict(gridcolor="#131c2e", ticksuffix="%", tickfont=dict(size=10, color="#4a6080")),
            yaxis2=dict(gridcolor="#0d1220", tickfont=dict(size=9, color="#3a5070"), title=dict(text="n", font=dict(color="#3a5070")))
        )
        st.plotly_chart(fig_sens, use_container_width=True)

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
        pivot = sicramalar.groupby(["Yil","Ay"]).size().unstack(fill_value=0)
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

# ════════════ TAB 6 — TABLOLAR & SPREAD ════════════
with tab6:
    st.markdown(f'<div class="section-label">◈ {doviz_sec}/TRY Alış–Satış Spread Analizi</div>', unsafe_allow_html=True)

    if sp_df is None or len(sp_df) == 0:
        st.warning("Spread verisi hesaplanamadı. Hem alış hem satış kolonları gereklidir.")
    else:
        sp_ort  = sp_df["Spread_TL"].mean()
        sp_maks = sp_df["Spread_TL"].max()
        sp_son  = sp_df["Spread_TL"].iloc[-1]
        sp_pct  = sp_df["Spread_Pct"].mean()

        st.markdown(f"""
        <div class="metric-row" style="grid-template-columns: repeat(4, 1fr);">
          <div class="spread-card">
            <div class="metric-label">Son Spread (TL)</div>
            <div class="metric-value metric-neu">{fkur(sp_son, 4)} ₺</div>
            <div class="metric-sub">{sp_df['Tarih'].iloc[-1].strftime('%d.%m.%Y')}</div>
          </div>
          <div class="spread-card">
            <div class="metric-label">Ort. Spread (TL)</div>
            <div class="metric-value">{fkur(sp_ort, 4)} ₺</div>
            <div class="metric-sub">Tarihsel ortalama</div>
          </div>
          <div class="spread-card">
            <div class="metric-label">Maks Spread (TL)</div>
            <div class="metric-value metric-neg">{fkur(sp_maks, 4)} ₺</div>
            <div class="metric-sub">En yüksek spread</div>
          </div>
          <div class="spread-card">
            <div class="metric-label">Ort. Spread (%)</div>
            <div class="metric-value metric-pos">{fpct(sp_pct, 4)}</div>
            <div class="metric-sub">Alış kuru üzerinden</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        sp_df["_sp_str"]  = sp_df["Spread_TL"].apply(lambda x: tr_fmt_kur(x, 4))
        sp_df["_spp_str"] = sp_df["Spread_Pct"].apply(lambda x: tr_fmt_pct(x, 4))

        fig_sp1 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                row_heights=[0.6, 0.4], vertical_spacing=0.06)

        a_col = f"TP_DK_{doviz_sec}_A"
        s_col = f"TP_DK_{doviz_sec}_S"
        fig_sp1.add_trace(go.Scatter(
            x=sp_df["Tarih"], y=sp_df[a_col], mode="lines", name="Alış",
            line=dict(color="#4a9eff", width=1.2),
            hovertemplate="%{x|%d.%m.%Y}<br>Alış: <b>%{y:.4f} ₺</b><extra></extra>"
        ), row=1, col=1)
        fig_sp1.add_trace(go.Scatter(
            x=sp_df["Tarih"], y=sp_df[s_col], mode="lines", name="Satış",
            line=dict(color="#ff4d6a", width=1.2),
            fill="tonexty", fillcolor="rgba(255,77,106,0.05)",
            hovertemplate="%{x|%d.%m.%Y}<br>Satış: <b>%{y:.4f} ₺</b><extra></extra>"
        ), row=1, col=1)
        fig_sp1.add_trace(go.Scatter(
            x=sp_df["Tarih"], y=sp_df["Spread_TL"], mode="lines", name="Spread (TL)",
            line=dict(color="#f6ad55", width=1),
            fill="tozeroy", fillcolor="rgba(246,173,85,0.08)",
            customdata=list(zip(sp_df["_sp_str"], sp_df["_spp_str"])),
            hovertemplate="%{x|%d.%m.%Y}<br>Spread: <b>%{customdata[0]} ₺</b> (%{customdata[1]})<extra></extra>"
        ), row=2, col=1)

        fig_sp1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,32,0.9)",
            font=dict(color="#c9d4e8", family="DM Sans, sans-serif"), height=540,
            title=dict(text=f"{doviz_sec}/TRY ALIŞ–SATIŞ & SPREAD", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            legend={**LEGEND_RIGHT},
            margin=dict(l=50, r=120, t=50, b=40),
            hoverlabel=dict(bgcolor="#0d1220", font_size=12, font_color="#e8f0ff"),
            xaxis2=dict(gridcolor="#131c2e", tickformat="%b %Y", tickfont=dict(size=10, color="#4a6080")),
            xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y", tickfont=dict(size=10, color="#4a6080")),
            yaxis=dict(gridcolor="#131c2e", tickfont=dict(size=10, color="#4a6080")),
            yaxis2=dict(gridcolor="#131c2e", tickfont=dict(size=10, color="#4a6080")),
            hovermode="x unified"
        )
        st.plotly_chart(fig_sp1, use_container_width=True)

        st.markdown('<div class="section-label">◈ Spread % & Yuvarlanmalı Ortalama</div>', unsafe_allow_html=True)
        sp_df["Spread_MA20"] = sp_df["Spread_Pct"].rolling(20).mean()
        sp_df["Spread_MA60"] = sp_df["Spread_Pct"].rolling(60).mean()

        fig_sp2 = go.Figure()
        fig_sp2.add_trace(go.Scatter(
            x=sp_df["Tarih"], y=sp_df["Spread_Pct"], mode="lines", name="Spread %",
            line=dict(color="#b794f4", width=0.8), opacity=0.5,
            hovertemplate="%{x|%d.%m.%Y}<br>%{y:.4f}%<extra></extra>"
        ))
        fig_sp2.add_trace(go.Scatter(
            x=sp_df["Tarih"], y=sp_df["Spread_MA20"], mode="lines", name="20G MA",
            line=dict(color="#f6ad55", width=1.5),
            hovertemplate="%{x|%d.%m.%Y}<br>20G MA: <b>%{y:.4f}%</b><extra></extra>"
        ))
        fig_sp2.add_trace(go.Scatter(
            x=sp_df["Tarih"], y=sp_df["Spread_MA60"], mode="lines", name="60G MA",
            line=dict(color="#4a9eff", width=1.5, dash="dot"),
            hovertemplate="%{x|%d.%m.%Y}<br>60G MA: <b>%{y:.4f}%</b><extra></extra>"
        ))
        apply_base(fig_sp2, height=420,
            title=dict(text="SPREAD % — YUVARLANMALI ORTALAMA", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
            xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y"),
            yaxis=dict(gridcolor="#131c2e", ticksuffix="%"),
            hovermode="x unified")
        st.plotly_chart(fig_sp2, use_container_width=True)

        st.markdown('<div class="section-label">◈ USD vs EUR Spread Karşılaştırması</div>', unsafe_allow_html=True)
        sp_usd = spread_hesapla(df_raw, "USD")
        sp_eur = spread_hesapla(df_raw, "EUR")

        if sp_usd is not None and sp_eur is not None:
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(
                x=sp_usd["Tarih"], y=sp_usd["Spread_Pct"], mode="lines", name="USD Spread %",
                line=dict(color="#4a9eff", width=1.2),
                hovertemplate="%{x|%d.%m.%Y}<br>USD Spread: <b>%{y:.4f}%</b><extra></extra>"
            ))
            fig_comp.add_trace(go.Scatter(
                x=sp_eur["Tarih"], y=sp_eur["Spread_Pct"], mode="lines", name="EUR Spread %",
                line=dict(color="#f6ad55", width=1.2),
                hovertemplate="%{x|%d.%m.%Y}<br>EUR Spread: <b>%{y:.4f}%</b><extra></extra>"
            ))
            apply_base(fig_comp, height=400,
                title=dict(text="USD vs EUR SPREAD % KARŞILAŞTIRMASI", font=dict(size=11, color="#4a6080", family="DM Mono, monospace"), x=0),
                xaxis=dict(gridcolor="#131c2e", tickformat="%b %Y"),
                yaxis=dict(gridcolor="#131c2e", ticksuffix="%"),
                hovermode="x unified")
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("USD ve EUR spread karşılaştırması için her iki dövizin alış/satış verisi gereklidir.")

    # ── Yön etiketi ───────────────────────────────────────────────────────
    yon_label = {
        "Tümü":              "Tümü",
        "Yalnız Pozitif ↑":  "Yalnız ↑ Pozitif",
        "Yalnız Negatif ↓":  "Yalnız ↓ Negatif",
    }

    # ── Filtre banner ─────────────────────────────────────────────────────
    esik_s   = str(esik).replace(".", ",")
    hf_esik_s = str(haftalik_esik).replace(".", ",")
    st.markdown(f"""
    <div class="filter-banner">
        🔎 &nbsp;Aktif Filtreler &nbsp;·&nbsp;
        Günlük Eşik: <span class="filter-tag">≥ %{esik_s}</span>
        Yön: <span class="filter-tag">{yon_label.get(yon, yon)}</span>
        Gösterim: <span class="filter-tag">{gosterim_sec}</span>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        Haftalık Eşik: <span class="filter-tag">≥ %{hf_esik_s}</span>
        Haftalık Yön: <span class="filter-tag">{yon_label.get(haftalik_yon, haftalik_yon)}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Günlük sıçrama tablosu ────────────────────────────────────────────
    st.markdown(
        f'<div class="section-label">◈ Sıçrama Tablosu '
        f'<span style="color:#f6ad55;font-size:0.8rem;font-weight:400;">'
        f'· Eşik ≥%{esik_s} · {yon_label.get(yon, yon)} · {gosterim_sec} kayıt'
        f'</span></div>',
        unsafe_allow_html=True
    )
    tbl = top_sic.copy().reset_index(drop=True)
    tbl.index = tbl.index + 1
    tbl_show = pd.DataFrame({
        "#":           tbl.index,
        "Tarih":       tbl["Tarih"].dt.strftime("%d.%m.%Y"),
        "Yıl":         tbl["Yil"],
        "Ay":          tbl["Ay_Adi"],
        "Gün Adı":     tbl["Gun_Adi"].map(TR_GUN),
        "Kur":         tbl["Dolar_Kuru"].apply(tr_fmt_kur),
        "Önceki Kur":  tbl["Onceki_Kur"].apply(tr_fmt_kur),
        "Değişim %":   tbl["Yuzde_Degisim"].apply(tr_fmt_pct),
        "TL Δ":        tbl["TL_Degisim"].apply(lambda x: tr_fmt_kur(x, 4)),
        "Gün Farkı":   tbl["Gun_Farki"].astype(int),
    })
    st.markdown(
        f"<div style='font-size:0.75rem;color:#4a6080;font-family:DM Mono,monospace;"
        f"margin-bottom:8px;'>Toplam <b style='color:#f6ad55'>{len(tbl_show)}</b> kayıt</div>",
        unsafe_allow_html=True
    )
    st.dataframe(tbl_show, use_container_width=True, height=420)

    # ── Aylık & Yıllık özetler ────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div class="section-label">◈ Aylık Özet '
            f'<span style="color:#f6ad55;font-size:0.8rem;font-weight:400;">'
            f'· Eşik ≥%{esik_s} · {yon_label.get(yon, yon)}'
            f'</span></div>',
            unsafe_allow_html=True
        )
        aylik_ozet = (
            sicramalar
            .groupby("Ay_Adi")["Abs_Degisim"]
            .agg(["count", "mean", "max", "min"])
            .round(3)
        )
        aylik_ozet.columns = ["Toplam", "Ort. %", "Maks %", "Min %"]
        st.dataframe(aylik_ozet, use_container_width=True)

    with c2:
        st.markdown(
            f'<div class="section-label">◈ Yıllık Özet '
            f'<span style="color:#f6ad55;font-size:0.8rem;font-weight:400;">'
            f'· Eşik ≥%{esik_s} · {yon_label.get(yon, yon)}'
            f'</span></div>',
            unsafe_allow_html=True
        )
        yillik_ozet = sicramalar.groupby("Yil").agg(
            Toplam    = ("Abs_Degisim",     "count"),
            Ort_Pct   = ("Abs_Degisim",     "mean"),
            Pozitif   = ("Yuzde_Degisim",   lambda x: (x > 0).sum()),
            Negatif   = ("Yuzde_Degisim",   lambda x: (x < 0).sum()),
            Maks      = ("Abs_Degisim",     "max"),
        ).round(3)
        yillik_ozet.columns = ["Toplam", "Ort. %", "Pozitif", "Negatif", "Maks %"]
        st.dataframe(yillik_ozet, use_container_width=True)

    # ── Haftalık tablo (7 takvim günü) ───────────────────────────────────
    st.markdown(
        f'<div class="section-label">◈ Haftalık Değişim Tablosu (Pzt Açılış → Paz Kapanış, 7 Gün) '
        f'<span style="color:#f6ad55;font-size:0.8rem;font-weight:400;">'
        f'· Eşik ≥%{hf_esik_s} · {yon_label.get(haftalik_yon, haftalik_yon)}'
        f'</span></div>',
        unsafe_allow_html=True
    )

    if haftalik_yon == "Yalnız Pozitif ↑":
        hf_tablo = hf_global[hf_global["HaftaDegisim"] >= haftalik_esik].copy()
    elif haftalik_yon == "Yalnız Negatif ↓":
        hf_tablo = hf_global[hf_global["HaftaDegisim"] <= -haftalik_esik].copy()
    else:
        hf_tablo = hf_global[hf_global["HaftaDegisim"].abs() >= haftalik_esik].copy()

    def _hf_df_hazirla(kaynak):
        t = kaynak.copy()
        t2 = pd.DataFrame({
            "Yıl":         t["AcilisTarih"].dt.year,
            "Hafta (Pzt–Paz)": t["Aralik"],
            "İşlem Aralığı":   t["IslemAralik"],
            "Açılış Kuru":     t["AcilisKur"].apply(tr_fmt_kur),
            "Kapanış Kuru":    t["KapanisKur"].apply(tr_fmt_kur),
            "Değişim %":       t["HaftaDegisim"].apply(tr_fmt_pct),
            "Yön":             t["HaftaDegisim"].apply(lambda x: "↑" if x > 0 else "↓"),
        })
        return t2.sort_values("Hafta (Pzt–Paz)", ascending=False).reset_index(drop=True)

    hf_t        = _hf_df_hazirla(hf_tablo)
    hf_t_tumumu = _hf_df_hazirla(hf_global)

    st.markdown(
        f"<div style='font-size:0.75rem;color:#4a6080;font-family:DM Mono,monospace;"
        f"margin-bottom:8px;'>Filtreli: <b style='color:#f6ad55'>{len(hf_t)}</b> hafta "
        f"&nbsp;·&nbsp; Toplam: <b style='color:#4a9eff'>{len(hf_t_tumumu)}</b> hafta</div>",
        unsafe_allow_html=True
    )
    st.dataframe(hf_t, use_container_width=True, height=420)

    # ── Aylık tablo ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">◈ Aylık Değişim Tablosu (Ay Başı → Ay Sonu)
        <span style="color:#4a9eff;font-size:0.75rem;font-weight:400;margin-left:8px;">
        · Her ayın ilk işlem günü açılış → son işlem günü kapanış
        </span>
    </div>""", unsafe_allow_html=True)

    ay_tablo = ay_global.sort_values(["Yil","Ay"], ascending=False).copy()
    ay_tablo_show = pd.DataFrame({
        "Yıl":         ay_tablo["Yil"],
        "Ay":          ay_tablo["AyAdi"],
        "Açılış Tarihi": ay_tablo["AcilisTarih"].dt.strftime("%d.%m.%Y"),
        "Kapanış Tarihi": ay_tablo["KapanisTarih"].dt.strftime("%d.%m.%Y"),
        "Açılış Kuru": ay_tablo["AcilisKur"].apply(tr_fmt_kur),
        "Kapanış Kuru": ay_tablo["KapanisKur"].apply(tr_fmt_kur),
        "Değişim %":   ay_tablo["AyDegisim"].apply(tr_fmt_pct),
        "Yön":         ay_tablo["AyDegisim"].apply(lambda x: "↑" if x > 0 else "↓"),
    }).reset_index(drop=True)
    st.dataframe(ay_tablo_show, use_container_width=True, height=420)

    # ── Çeyreklik tablo ───────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">◈ Çeyreklik Değişim Tablosu (Çeyrek Başı → Çeyrek Sonu)
        <span style="color:#b794f4;font-size:0.75rem;font-weight:400;margin-left:8px;">
        · Q1=Oca–Mar · Q2=Nis–Haz · Q3=Tem–Eyl · Q4=Eki–Ara
        </span>
    </div>""", unsafe_allow_html=True)

    cey_tablo = cey_global.sort_values(["Yil","Ceyrek"], ascending=False).copy()
    cey_tablo_show = pd.DataFrame({
        "Yıl":          cey_tablo["Yil"],
        "Çeyrek":       cey_tablo["Aralik"],
        "Açılış Tarihi": cey_tablo["AcilisTarih"].dt.strftime("%d.%m.%Y"),
        "Kapanış Tarihi": cey_tablo["KapanisTarih"].dt.strftime("%d.%m.%Y"),
        "Açılış Kuru":  cey_tablo["AcilisKur"].apply(tr_fmt_kur),
        "Kapanış Kuru": cey_tablo["KapanisKur"].apply(tr_fmt_kur),
        "Değişim %":    cey_tablo["CeyrekDegisim"].apply(tr_fmt_pct),
        "Yön":          cey_tablo["CeyrekDegisim"].apply(lambda x: "↑" if x > 0 else "↓"),
    }).reset_index(drop=True)
    st.dataframe(cey_tablo_show, use_container_width=True, height=420)

    # ── Haftalık indirme ──────────────────────────────────────────────────
    st.markdown(
        '<div class="section-label">◈ Tüm Veriyi İndir</div>',
        unsafe_allow_html=True
    )

    hf_dl1, hf_dl2, _ = st.columns([1, 1, 4])
    with hf_dl1:
        csv_hf_tum = hf_t_tumumu.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇ Haftalık CSV",
            csv_hf_tum,
            "haftalik_7gun_tum_veri.csv",
            "text/csv",
            use_container_width=True,
        )
    with hf_dl2:
        buf_hf = io.BytesIO()
        with pd.ExcelWriter(buf_hf, engine="openpyxl") as w:
            hf_t_tumumu.to_excel(w, sheet_name="Haftalik_Tum_7gun", index=False)
            hf_t.to_excel(       w, sheet_name="Haftalik_Filtreli", index=False)
            ay_tablo_show.to_excel(w, sheet_name="Aylik_Tum", index=False)
            cey_tablo_show.to_excel(w, sheet_name="Ceyreklik_Tum", index=False)
        st.download_button(
            "⬇ Tüm Periyotlar Excel",
            buf_hf.getvalue(),
            "tum_periyot_veri.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # ── Genel dışa aktar ──────────────────────────────────────────────────
    st.markdown('<div class="section-label">◈ Tüm Analizi Dışa Aktar</div>', unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        csv = top_sic.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇ Sıçramalar CSV", csv, "sicramalar.csv", "text/csv", use_container_width=True)
    with dc2:
        _cum_gun = df[["Tarih","Yil","Dolar_Kuru","Yuzde_Degisim"]].copy()
        _cum_gun = _cum_gun.sort_values("Tarih").reset_index(drop=True)
        _cum_gun["Kumülatif_%"] = (_cum_gun["Dolar_Kuru"] / _cum_gun["Dolar_Kuru"].iloc[0] - 1) * 100
        _cum_gun["Drawdown_%"] = _cum_gun["Kumülatif_%"] - _cum_gun["Kumülatif_%"].cummax()
        _cum_gun["Tarih"] = _cum_gun["Tarih"].dt.strftime("%d.%m.%Y")
        _cum_gun = _cum_gun.rename(columns={"Dolar_Kuru":"Kur","Yuzde_Degisim":"Degisim_%"})

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            top_sic.to_excel(       w, sheet_name="Sicramalar",         index=False)
            hf_t_tumumu.to_excel(   w, sheet_name="Haftalik_7gun_Tum",  index=False)
            hf_t.to_excel(          w, sheet_name="Haftalik_Filtreli",  index=False)
            ay_tablo_show.to_excel( w, sheet_name="Aylik_Tum",          index=False)
            cey_tablo_show.to_excel(w, sheet_name="Ceyreklik_Tum",      index=False)
            df.to_excel(            w, sheet_name="Tum_Gunluk_Veri",    index=False)
            _cum_gun.to_excel(      w, sheet_name="Kumulatif_Gunluk",   index=False)
            aylik_ozet.to_excel(    w, sheet_name="Aylik_Sicrama_Ozet")
            yillik_ozet.to_excel(   w, sheet_name="Yillik_Sicrama_Ozet")
            if sp_df is not None:
                sp_df.to_excel(     w, sheet_name="Spread",             index=False)
        st.download_button(
            "⬇ Excel İndir (Tüm Analiz)",
            buf.getvalue(),
            "doviz_analiz_tam.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
