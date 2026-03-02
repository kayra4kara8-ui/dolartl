import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io

st.set_page_config(
    page_title="Dolar Kuru Sıçrama Analizi",
    page_icon="💹",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .main { background-color: #0f1117; color: #fff; }
    .stat-card {
        background: linear-gradient(135deg, #1a1f2e, #252b3b);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.2s;
        border: 1px solid #2d3748;
    }
    .stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); }
    .stat-title { color: #a0aec0; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { color: #fff; font-size: 1.6rem; font-weight: bold; margin: 8px 0; }
    .stat-sub { color: #718096; font-size: 0.75rem; }

    .jump-card {
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        background: #1a1f2e;
        border: 1px solid #2d3748;
        transition: all 0.2s;
    }
    .jump-card:hover { transform: scale(1.03); box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    .jump-positive { border-left: 4px solid #48bb78; }
    .jump-negative { border-left: 4px solid #f56565; }
    .jump-rank { font-size: 0.85rem; color: #a0aec0; }
    .jump-date { font-size: 0.9rem; color: #e2e8f0; font-weight: 600; }
    .jump-pct-pos { font-size: 1.4rem; font-weight: bold; color: #48bb78; }
    .jump-pct-neg { font-size: 1.4rem; font-weight: bold; color: #f56565; }
    .jump-detail { font-size: 0.75rem; color: #718096; margin-top: 4px; }

    .section-header {
        background: linear-gradient(90deg, #2d3748, #1a1f2e);
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 4px solid #4299e1;
        margin: 20px 0 10px 0;
    }
    
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    .stSelectbox label, .stSlider label, .stRadio label { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── RENK TEMAları ───────────────────────────────────────────────────────────
TEMALAR = {
    "🔵 Profesyonel": {
        "trend": "#4299E1",
        "pos": "#48BB78",
        "neg": "#F56565",
        "cum": "#9F7AEA",
        "yearly": "#F6AD55",
        "bg": "#0f1117",
        "card_bg": "#1a1f2e"
    },
    "🟠 Canlı": {
        "trend": "#F6AD55",
        "pos": "#38B2AC",
        "neg": "#F6E05E",
        "cum": "#ED8936",
        "yearly": "#68D391",
        "bg": "#1a0a00",
        "card_bg": "#2d1a00"
    },
    "🌸 Pastel": {
        "trend": "#B794F4",
        "pos": "#9AE6B4",
        "neg": "#FEB2B2",
        "cum": "#D6BCFA",
        "yearly": "#FBD38D",
        "bg": "#1a0a2e",
        "card_bg": "#2d1a4e"
    },
    "🌑 Karanlık": {
        "trend": "#90CDF4",
        "pos": "#68D391",
        "neg": "#FC8181",
        "cum": "#E9D8FD",
        "yearly": "#FBD38D",
        "bg": "#050505",
        "card_bg": "#111111"
    }
}

# ─── VERİ İŞLEME ─────────────────────────────────────────────────────────────
@st.cache_data
def veri_isle(uploaded_bytes):
    df = pd.read_excel(io.BytesIO(uploaded_bytes), sheet_name='EVDS')
    df.columns = ['Tarih', 'Dolar_Kuru']
    
    nan_before = df.shape[0]
    df = df.dropna()
    nan_cleaned = nan_before - df.shape[0]
    
    df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y', errors='coerce')
    df = df.dropna(subset=['Tarih'])
    df = df.sort_values('Tarih').reset_index(drop=True)
    
    df['Dolar_Kuru'] = pd.to_numeric(df['Dolar_Kuru'], errors='coerce')
    df = df.dropna(subset=['Dolar_Kuru'])
    
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
    df['Abs_Degisim'] = df['Yuzde_Degisim'].abs()
    
    return df, nan_cleaned

# ─── BAŞLIK ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 30px 0 10px 0;">
    <h1 style="font-size:2.5rem; font-weight:800; 
               background: linear-gradient(90deg, #4299E1, #9F7AEA, #48BB78);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        💹 DOLAR KURU SIÇRAMA ANALİZİ
    </h1>
    <p style="color:#718096; font-size:1rem;">Günlük bazda en büyük sıçramaları keşfedin</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    
    tema_secim = st.selectbox("🎨 Renk Teması", list(TEMALAR.keys()))
    tema = TEMALAR[tema_secim]
    
    esik = st.slider("📏 Eşik Değeri (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.1)
    
    gosterim_secenekleri = [10, 20, 30, 40, 50, 75, 100, "Tümü"]
    gosterim_sayisi = st.selectbox("🔢 Gösterilecek Sıçrama Sayısı", gosterim_secenekleri, index=2)
    
    yon = st.radio("📊 Sıçrama Yönü", ["Tümü", "Sadece Pozitif 📈", "Sadece Negatif 📉"])
    
    st.markdown("---")
    st.markdown("### 📁 Veri Yükle")
    uploaded_file = st.file_uploader("Excel dosyası (.xlsx)", type=['xlsx', 'xls'])

# ─── ANA İÇERİK ───────────────────────────────────────────────────────────────
if uploaded_file is None:
    st.markdown("""
    <div style="text-align:center; padding: 60px; background: #1a1f2e; 
                border-radius: 16px; border: 2px dashed #4299e1; margin: 30px;">
        <div style="font-size: 4rem;">📂</div>
        <h3 style="color: #4299e1;">Excel Dosyanızı Yükleyin</h3>
        <p style="color: #718096;">Sol panelden EVDS formatında Excel dosyanızı yükleyin</p>
        <div style="color: #4a5568; font-size: 0.9rem; margin-top: 20px;">
            <p>✅ Sayfa adı: <strong>EVDS</strong></p>
            <p>✅ Sütunlar: <strong>Tarih</strong> (DD-MM-YYYY) ve <strong>TP_DK_USD_A_YTL</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Veri yükleme
    with st.spinner("⏳ Veriler işleniyor..."):
        try:
            df, nan_cleaned = veri_isle(uploaded_file.read())
        except Exception as e:
            st.error(f"❌ Dosya okuma hatası: {e}")
            st.stop()
    
    if nan_cleaned > 0:
        st.info(f"📌 {nan_cleaned} adet boş (NaN) değer otomatik temizlendi")
    
    # Filtreleme
    if yon == "Sadece Pozitif 📈":
        sicramalar = df[df['Yuzde_Degisim'] >= esik].copy()
    elif yon == "Sadece Negatif 📉":
        sicramalar = df[df['Yuzde_Degisim'] <= -esik].copy()
    else:
        sicramalar = df[df['Abs_Degisim'] >= esik].copy()
    
    sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
    
    if gosterim_sayisi != "Tümü":
        top_sicramalar = sicramalar.head(int(gosterim_sayisi))
    else:
        top_sicramalar = sicramalar.copy()
    
    # ─── İSTATİSTİK KARTLARI ─────────────────────────────────────────────────
    poz_say = len(df[df['Yuzde_Degisim'] > 0])
    neg_say = len(df[df['Yuzde_Degisim'] < 0])
    oran = len(sicramalar) / len(df) * 100
    
    st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📊 Genel İstatistikler</h3></div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "📅 Toplam İşlem Günü", f"{len(df):,}", f"{df['Tarih'].min().year} - {df['Tarih'].max().year}"),
        (c2, "📈 Ortalama Değişim", f"%{df['Yuzde_Degisim'].mean():.2f}", f"± {df['Yuzde_Degisim'].std():.2f}"),
        (c3, "⬆️⬇️ Pozitif / Negatif", f"{poz_say} / {neg_say}", "gün"),
        (c4, "⚡ Toplam Sıçrama", f"{len(sicramalar):,}", f"> %{esik}"),
        (c5, "📊 Sıçrama Oranı", f"%{oran:.1f}", "günlerin yüzdesi"),
    ]
    for col, title, val, sub in cards:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-title">{title}</div>
                <div class="stat-value">{val}</div>
                <div class="stat-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── GRAFİK 1: ANA DOLAR KURU ────────────────────────────────────────────
    st.markdown(f'<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📈 Dolar Kuru Grafiği</h3></div>', unsafe_allow_html=True)
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['Tarih'], y=df['Dolar_Kuru'],
        mode='lines', name='Dolar Kuru',
        line=dict(color=tema['trend'], width=2),
        hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<extra></extra>'
    ))
    
    pos_j = top_sicramalar[top_sicramalar['Yuzde_Degisim'] > 0]
    neg_j = top_sicramalar[top_sicramalar['Yuzde_Degisim'] < 0]
    
    if len(pos_j) > 0:
        fig1.add_trace(go.Scatter(
            x=pos_j['Tarih'], y=pos_j['Dolar_Kuru'],
            mode='markers', name='Pozitif Sıçrama',
            marker=dict(
                color=tema['pos'], size=pos_j['Abs_Degisim'] * 3,
                line=dict(color='white', width=1), opacity=0.8
            ),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: +%{customdata:.2f}%<extra></extra>',
            customdata=pos_j['Yuzde_Degisim']
        ))
    
    if len(neg_j) > 0:
        fig1.add_trace(go.Scatter(
            x=neg_j['Tarih'], y=neg_j['Dolar_Kuru'],
            mode='markers', name='Negatif Sıçrama',
            marker=dict(
                color=tema['neg'], size=neg_j['Abs_Degisim'] * 3,
                line=dict(color='white', width=1), opacity=0.8
            ),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{customdata:.2f}%<extra></extra>',
            customdata=neg_j['Yuzde_Degisim']
        ))
    
    fig1.update_layout(
        title=f"DOLAR KURU - EN BÜYÜK {gosterim_sayisi} GÜNLÜK SIÇRAMA (Eşik: %{esik})",
        xaxis_title="Tarih", yaxis_title="Dolar Kuru (TL)",
        height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
        font=dict(color='#e2e8f0'), title_font_size=14,
        legend=dict(bgcolor='rgba(0,0,0,0.3)', bordercolor='#2d3748'),
        xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748')
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # ─── GRAFİK 2: GÜNLÜK YÜZDE DEĞİŞİMLER ─────────────────────────────────
    st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📉 Günlük Yüzde Değişimler</h3></div>', unsafe_allow_html=True)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df['Tarih'], y=df['Yuzde_Degisim'],
        mode='lines', name='Günlük Değişim',
        line=dict(color='#CBD5E0', width=1), opacity=0.5
    ))
    fig2.add_trace(go.Scatter(
        x=pos_j['Tarih'], y=pos_j['Yuzde_Degisim'],
        mode='markers', name='Pozitif Sıçrama',
        marker=dict(color=tema['pos'], size=8, symbol='triangle-up')
    ))
    fig2.add_trace(go.Scatter(
        x=neg_j['Tarih'], y=neg_j['Yuzde_Degisim'],
        mode='markers', name='Negatif Sıçrama',
        marker=dict(color=tema['neg'], size=8, symbol='triangle-down')
    ))
    fig2.add_hline(y=esik, line_dash="dash", line_color=tema['pos'], annotation_text=f"+{esik}%")
    fig2.add_hline(y=-esik, line_dash="dash", line_color=tema['neg'], annotation_text=f"-{esik}%")
    fig2.add_hline(y=0, line_color='white', line_width=0.5)
    fig2.update_layout(
        title=f"GÜNLÜK YÜZDE DEĞİŞİMLER VE %{esik} EŞİĞİ",
        height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
        font=dict(color='#e2e8f0'), xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748')
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # ─── KARTLAR: EN BÜYÜK 10 ────────────────────────────────────────────────
    st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">🎴 En Büyük 10 Sıçrama</h3></div>', unsafe_allow_html=True)
    
    top10 = sicramalar.head(10)
    cols_per_row = 5
    for row_start in range(0, min(10, len(top10)), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, (_, r) in enumerate(top10.iloc[row_start:row_start+cols_per_row].iterrows()):
            is_pos = r['Yuzde_Degisim'] > 0
            card_class = "jump-positive" if is_pos else "jump-negative"
            icon = "📈" if is_pos else "📉"
            pct_class = "jump-pct-pos" if is_pos else "jump-pct-neg"
            sign = "+" if is_pos else ""
            rank = row_start + i + 1
            with cols[i]:
                st.markdown(f"""
                <div class="jump-card {card_class}">
                    <div class="jump-rank">#{rank} {icon}</div>
                    <div class="jump-date">{r['Tarih'].strftime('%d.%m.%Y')}</div>
                    <div class="{pct_class}">{sign}{r['Yuzde_Degisim']:.2f}%</div>
                    <div class="jump-detail">{r['Gun_Adi']}</div>
                    <div class="jump-detail">{r['Onceki_Kur']:.4f} → {r['Dolar_Kuru']:.4f}</div>
                    <div class="jump-detail">{int(r['Gun_Farki'])} gün sonra</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── GRAFİKLER 3-8 ───────────────────────────────────────────────────────
    col_l, col_r = st.columns(2)
    
    with col_l:
        # GRAFİK 3: KÜMÜLATİF
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📈 Kümülatif Sıçrama</h3></div>', unsafe_allow_html=True)
        cum_df = sicramalar.sort_values('Tarih').reset_index(drop=True)
        cum_df['Kumulatif'] = range(1, len(cum_df)+1)
        fig3 = go.Figure(go.Scatter(
            x=cum_df['Tarih'], y=cum_df['Kumulatif'],
            fill='tozeroy', line=dict(color=tema['cum'], width=2),
            fillcolor=f"rgba(159,122,234,0.2)"
        ))
        fig3.update_layout(
            title="KÜMÜLATİF SIÇRAMA SAYISI", height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
            font=dict(color='#e2e8f0'), xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748')
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_r:
        # GRAFİK 4: AYLIK
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📅 Aylık Dağılım</h3></div>', unsafe_allow_html=True)
        ay_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
        ay_sayim = sicramalar.groupby('Ay_Adi').size().reindex(ay_order).fillna(0)
        fig4 = px.bar(x=ay_sayim.index, y=ay_sayim.values, color=ay_sayim.values,
                      color_continuous_scale='Viridis', labels={'x':'Ay','y':'Sıçrama Sayısı'})
        fig4.update_layout(
            title="AYLARA GÖRE SIÇRAMA SAYILARI", height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
            font=dict(color='#e2e8f0'), showlegend=False,
            xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748'), coloraxis_showscale=False
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    col_l2, col_r2 = st.columns(2)
    
    with col_l2:
        # GRAFİK 5: HAFTALIK PATTERN
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📆 Haftalık Pattern</h3></div>', unsafe_allow_html=True)
        gun_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        gun_sayim = sicramalar.groupby('Gun_Adi').size().reindex(gun_order).fillna(0)
        fig5 = px.bar(x=gun_sayim.index, y=gun_sayim.values, color=gun_sayim.values,
                      color_continuous_scale='Plasma')
        fig5.update_layout(
            title="HAFTANIN GÜNLERİNE GÖRE SIÇRAMA", height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
            font=dict(color='#e2e8f0'), showlegend=False,
            xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748'), coloraxis_showscale=False
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    with col_r2:
        # GRAFİK 6: YILLIK TREND
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📊 Yıllık Trend</h3></div>', unsafe_allow_html=True)
        yil_sayim = sicramalar.groupby('Yil').size().reset_index(name='Sayi')
        fig6 = go.Figure(go.Scatter(
            x=yil_sayim['Yil'], y=yil_sayim['Sayi'],
            mode='lines+markers',
            line=dict(color=tema['yearly'], width=2),
            marker=dict(color=tema['yearly'], size=10, line=dict(color='white', width=2))
        ))
        fig6.update_layout(
            title="YILLARA GÖRE SIÇRAMA SAYILARI", height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
            font=dict(color='#e2e8f0'), xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748')
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    col_l3, col_r3 = st.columns(2)
    
    with col_l3:
        # GRAFİK 7: BÜYÜKLÜK DAĞILIMI
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📊 Büyüklük Dağılımı</h3></div>', unsafe_allow_html=True)
        fig7 = go.Figure()
        fig7.add_trace(go.Histogram(
            x=sicramalar[sicramalar['Yuzde_Degisim']>0]['Yuzde_Degisim'],
            nbinsx=20, name='Pozitif', marker_color=tema['pos'], opacity=0.7
        ))
        fig7.add_trace(go.Histogram(
            x=sicramalar[sicramalar['Yuzde_Degisim']<0]['Yuzde_Degisim'],
            nbinsx=20, name='Negatif', marker_color=tema['neg'], opacity=0.7
        ))
        fig7.update_layout(
            title="SIÇRAMA BÜYÜKLÜKLERİNİN DAĞILIMI", barmode='overlay', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
            font=dict(color='#e2e8f0'), xaxis=dict(gridcolor='#2d3748'), yaxis=dict(gridcolor='#2d3748')
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col_r3:
        # GRAFİK 8: ISI HARİTASI
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">🗺️ Yıl-Ay Isı Haritası</h3></div>', unsafe_allow_html=True)
        pivot = sicramalar.groupby(['Yil','Ay']).size().unstack(fill_value=0)
        fig8 = go.Figure(go.Heatmap(
            z=pivot.values, x=pivot.columns.astype(str), y=pivot.index.astype(str),
            colorscale='RdYlGn', text=pivot.values,
            hovertemplate='Yıl: %{y}<br>Ay: %{x}<br>Sıçrama: %{z}<extra></extra>'
        ))
        fig8.update_layout(
            title="YIL-AY BAZINDA SIÇRAMA YOĞUNLUĞU", height=480,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,31,46,0.8)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig8, use_container_width=True)
    
    # ─── TABLO 1: EN BÜYÜK SIÇRAMALAR ────────────────────────────────────────
    st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📋 En Büyük Sıçramalar Tablosu</h3></div>', unsafe_allow_html=True)
    
    tablo1 = top_sicramalar.copy()
    tablo1 = tablo1.reset_index(drop=True)
    tablo1.index = tablo1.index + 1
    tablo1_show = pd.DataFrame({
        '#': tablo1.index,
        'Tarih': tablo1['Tarih'].dt.strftime('%d.%m.%Y'),
        'Gün': tablo1['Gun'],
        'Ay': tablo1['Ay_Adi'],
        'Yıl': tablo1['Yil'],
        'Gün Adı': tablo1['Gun_Adi'],
        'Yeni Kur': tablo1['Dolar_Kuru'].round(4),
        'Önceki Kur': tablo1['Onceki_Kur'].round(4),
        'Değişim %': tablo1['Yuzde_Degisim'].round(2),
        'TL Değişim': tablo1['TL_Degisim'].round(4),
        'Gün Farkı': tablo1['Gun_Farki'].astype(int),
    })
    st.dataframe(tablo1_show, use_container_width=True, height=400)
    
    # ─── TABLO 2 & 3 ─────────────────────────────────────────────────────────
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📅 Aylık Özet</h3></div>', unsafe_allow_html=True)
        aylik = sicramalar.groupby('Ay_Adi')['Abs_Degisim'].agg(['count','mean','max','min']).round(2)
        aylik.columns = ['Toplam','Ort. %','Max %','Min %']
        st.dataframe(aylik, use_container_width=True)
    
    with col_t2:
        st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">📊 Yıllık Özet</h3></div>', unsafe_allow_html=True)
        yillik = sicramalar.groupby('Yil').agg(
            Toplam=('Abs_Degisim','count'),
            Ort_Pct=('Abs_Degisim','mean'),
            Pozitif=('Yuzde_Degisim', lambda x: (x>0).sum()),
            Negatif=('Yuzde_Degisim', lambda x: (x<0).sum())
        ).round(2)
        yillik.columns = ['Toplam','Ort. %','Pozitif','Negatif']
        st.dataframe(yillik, use_container_width=True)
    
    # ─── İNDİRME ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><h3 style="margin:0; color:#e2e8f0;">💾 İndirme</h3></div>', unsafe_allow_html=True)
    
    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        csv_data = top_sicramalar.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 CSV İndir (Sıçramalar)", csv_data, "sicramalar.csv", "text/csv")
    
    with col_d2:
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
            top_sicramalar.to_excel(writer, sheet_name='Sicramalar', index=False)
            df.to_excel(writer, sheet_name='Tum_Veri', index=False)
            aylik.to_excel(writer, sheet_name='Aylik_Ozet')
            yillik.to_excel(writer, sheet_name='Yillik_Ozet')
        st.download_button("📊 Excel İndir (Tüm Analiz)", excel_buf.getvalue(),
                           "dolar_analiz.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with col_d3:
        st.info("💡 Grafikleri indirmek için grafiğin üzerindeki kamera ikonuna tıklayın")

# Footer
st.markdown("""
<div style="text-align:center; color:#4a5568; font-size:0.75rem; padding: 30px 0; border-top: 1px solid #2d3748; margin-top: 30px;">
    💹 Dolar Kuru Sıçrama Analizi | Powered by Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
