import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import calendar
from datetime import datetime

# Sayfa yapılandırması
st.set_page_config(
    page_title="Dolar Kuru Günlük Sıçrama Analizi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile profesyonel görünüm
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
        margin-bottom: 1rem;
        padding: 1rem;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #2D3748;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
        border: 1px solid #E2E8F0;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .stat-label {
        font-size: 1rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2D3748;
    }
    
    .stat-unit {
        font-size: 1rem;
        color: #A0AEC0;
        margin-left: 0.25rem;
    }
    
    .positive {
        color: #48BB78;
        font-weight: 600;
    }
    
    .negative {
        color: #F56565;
        font-weight: 600;
    }
    
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2D3748;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
    }
    
    .sicrama-karti {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    
    .sicrama-karti:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .kontrol-panel {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<h1 class="main-header">📊 DOLAR KURU GÜNLÜK SIÇRAMA ANALİZİ</h1>', unsafe_allow_html=True)
st.markdown("Excel dosyanızı yükleyin, günlük sıçramaları keşfedin!")

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <img src="https://img.icons8.com/fluency/96/000000/line-chart.png" style="width: 80px;">
        <h2 style="color: #2D3748; margin-top: 0.5rem;">Analiz Paneli</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Dosya yükleme
    uploaded_file = st.file_uploader(
        "📂 Excel dosyası yükleyin",
        type=['xlsx', 'xls'],
        help="İlk sütun: Tarih, İkinci sütun: Dolar Kuru"
    )
    
    if uploaded_file is not None:
        st.success("✅ Dosya başarıyla yüklendi!")
        
        st.markdown("---")
        st.markdown("### ⚙️ GÜNLÜK SIÇRAMA AYARLARI")
        
        # Eşik değeri
        esik = st.slider(
            "🎯 Sıçrama Eşiği (%)",
            min_value=0.5, max_value=10.0, value=2.0, step=0.5,
            help="Bu değerin üzerindeki günlük değişimler sıçrama olarak kabul edilir"
        )
        
        # Gösterilecek sıçrama sayısı
        gosterim_sayisi = st.selectbox(
            "📊 Gösterilecek Sıçrama Sayısı",
            options=[10, 20, 30, 50, 75, 100, "Tümü"],
            index=2,
            help="En büyük kaç günlük sıçrama gösterilsin?"
        )
        
        # Sıçrama yönü filtresi
        yon_filtre = st.radio(
            "🔄 Sıçrama Yönü",
            options=["Tümü", "Sadece Pozitif", "Sadece Negatif"],
            index=0,
            horizontal=True
        )
        
        st.markdown("---")
        st.markdown("### 📈 GRAFİK AYARLARI")
        
        # Grafik tipi
        grafik_tipi = st.selectbox(
            "Grafik Tipi",
            options=["Dağılım (Scatter)", "Çizgi + Nokta", "Sadece Noktalar"],
            index=0
        )
        
        # Renk teması
        renk_temasi = st.selectbox(
            "🎨 Renk Teması",
            options=["Profesyonel", "Canlı", "Pastel", "Karanlık"],
            index=0
        )
        
        # Analiz butonu
        analiz_btn = st.button(
            "🚀 GÜNLÜK SIÇRAMA ANALİZİ",
            type="primary",
            use_container_width=True
        )

# Ana içerik
if uploaded_file is not None and analiz_btn:
    
    with st.spinner("🔍 Günlük sıçramalar analiz ediliyor..."):
        try:
            # Excel okuma
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_name = excel_file.sheet_names[0]
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # Sütunları düzenle
            if len(df.columns) >= 2:
                df = df.iloc[:, :2].copy()
                df.columns = ['Tarih', 'Dolar_Kuru']
            else:
                st.error("❌ Excel dosyasında en az 2 sütun olmalı!")
                st.stop()
            
            # Veri temizliği
            df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
            df['Dolar_Kuru'] = pd.to_numeric(df['Dolar_Kuru'], errors='coerce')
            df = df.dropna().sort_values('Tarih').reset_index(drop=True)
            
            if len(df) == 0:
                st.error("❌ Hiç geçerli veri bulunamadı!")
                st.stop()
            
            # GÜNLÜK DEĞİŞİM HESAPLAMA (bir önceki işlem gününe göre)
            df['Onceki_Kur'] = df['Dolar_Kuru'].shift(1)
            df['Onceki_Tarih'] = df['Tarih'].shift(1)
            df['Gun_Farki'] = (df['Tarih'] - df['Onceki_Tarih']).dt.days
            df['Yuzde_Degisim'] = (df['Dolar_Kuru'] / df['Onceki_Kur'] - 1) * 100
            df['TL_Degisim'] = df['Dolar_Kuru'] - df['Onceki_Kur']
            df = df.dropna().reset_index(drop=True)
            
            # Günlük veriler için tarih özellikleri
            df['Yil'] = df['Tarih'].dt.year
            df['Ay'] = df['Tarih'].dt.month
            df['Gun'] = df['Tarih'].dt.day
            df['Ay_Adi'] = df['Tarih'].dt.strftime('%B')
            df['Gun_Adi'] = df['Tarih'].dt.strftime('%A')
            df['Hafta'] = df['Tarih'].dt.isocalendar().week
            df['Yil_Ay'] = df['Tarih'].dt.strftime('%Y-%m')
            df['Abs_Degisim'] = abs(df['Yuzde_Degisim'])
            
            # GÜNLÜK SIÇRAMA TESPİTİ
            df['Sicrama'] = df['Abs_Degisim'] >= esik
            
            # Sıçrama tipini belirle
            df['Sicrama_Tipi'] = 'Normal'
            df.loc[df['Yuzde_Degisim'] > esik, 'Sicrama_Tipi'] = 'Pozitif'
            df.loc[df['Yuzde_Degisim'] < -esik, 'Sicrama_Tipi'] = 'Negatif'
            
            # Sıçramaları filtrele (yön filtresine göre)
            if yon_filtre == "Sadece Pozitif":
                sicramalar = df[df['Yuzde_Degisim'] > esik].copy()
            elif yon_filtre == "Sadece Negatif":
                sicramalar = df[df['Yuzde_Degisim'] < -esik].copy()
            else:
                sicramalar = df[df['Sicrama']].copy()
            
            # Sıçramaları büyüklüğe göre sırala
            sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
            
            # Gösterim sayısını ayarla
            toplam_sicrama = len(sicramalar)
            if gosterim_sayisi != "Tümü":
                sicramalar = sicramalar.head(gosterim_sayisi)
            
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            st.stop()
    
    # ========== KONTROL PANELİ ==========
    st.markdown('<div class="kontrol-panel">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="stat-label">Toplam Gün</div>
            <div class="metric-value">{len(df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="stat-label">Eşik Değeri</div>
            <div class="metric-value">%{esik}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="stat-label">Toplam Sıçrama</div>
            <div class="metric-value">{toplam_sicrama}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="stat-label">Gösterilen</div>
            <div class="metric-value">{len(sicramalar)}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== GÜNLÜK SIÇRAMA GRAFİĞİ ==========
    st.markdown('<h2 class="sub-header">📈 GÜNLÜK SIÇRAMALAR</h2>', unsafe_allow_html=True)
    
    # Renk teması
    if renk_temasi == "Profesyonel":
        renk_trend = '#4299E1'
        renk_pozitif = '#48BB78'
        renk_negatif = '#F56565'
        renk_normal = '#CBD5E0'
    elif renk_temasi == "Canlı":
        renk_trend = '#FF6B6B'
        renk_pozitif = '#4ECDC4'
        renk_negatif = '#FFE66D'
        renk_normal = '#95A5A6'
    elif renk_temasi == "Pastel":
        renk_trend = '#6C5B7B'
        renk_pozitif = '#99B898'
        renk_negatif = '#F8A5A5'
        renk_normal = '#BDC3C7'
    else:
        renk_trend = '#2C3E50'
        renk_pozitif = '#27AE60'
        renk_negatif = '#C0392B'
        renk_normal = '#7F8C8D'
    
    # Ana grafik - Günlük sıçramalar
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4],
        subplot_titles=(f'GÜNLÜK DOLAR KURU VE {len(sicramalar)} BÜYÜK SIÇRAMA', 
                       f'GÜNLÜK YÜZDE DEĞİŞİMLER (Eşik: %{esik})')
    )
    
    # 1. Üst grafik - Dolar kuru ve sıçramalar
    fig.add_trace(
        go.Scatter(
            x=df['Tarih'], y=df['Dolar_Kuru'],
            mode='lines',
            name='Dolar Kuru',
            line=dict(color=renk_trend, width=1.5),
            opacity=0.7,
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Sıçramaları ekle (büyüklüklerine göre boyutlandır)
    poz_sicra = sicramalar[sicramalar['Yuzde_Degisim'] > 0]
    neg_sicra = sicramalar[sicramalar['Yuzde_Degisim'] < 0]
    
    if len(poz_sicra) > 0:
        fig.add_trace(
            go.Scatter(
                x=poz_sicra['Tarih'], y=poz_sicra['Dolar_Kuru'],
                mode='markers',
                name=f'Pozitif Sıçrama ({len(poz_sicra)})',
                marker=dict(
                    color=renk_pozitif,
                    size=poz_sicra['Abs_Degisim']*3,
                    line=dict(color='white', width=1),
                    symbol='circle'
                ),
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: +%{text:.2f}%<extra></extra>',
                text=poz_sicra['Yuzde_Degisim']
            ),
            row=1, col=1
        )
    
    if len(neg_sicra) > 0:
        fig.add_trace(
            go.Scatter(
                x=neg_sicra['Tarih'], y=neg_sicra['Dolar_Kuru'],
                mode='markers',
                name=f'Negatif Sıçrama ({len(neg_sicra)})',
                marker=dict(
                    color=renk_negatif,
                    size=neg_sicra['Abs_Degisim']*3,
                    line=dict(color='white', width=1),
                    symbol='circle'
                ),
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{text:.2f}%<extra></extra>',
                text=neg_sicra['Yuzde_Degisim']
            ),
            row=1, col=1
        )
    
    # 2. Alt grafik - Günlük yüzde değişimler
    # Tüm günler (arka plan)
    fig.add_trace(
        go.Scatter(
            x=df['Tarih'], y=df['Yuzde_Degisim'],
            mode='markers',
            name='Tüm Günler',
            marker=dict(
                color=renk_normal,
                size=3,
                opacity=0.3
            ),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: %{y:.2f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Sıçramaları vurgula
    if len(poz_sicra) > 0:
        fig.add_trace(
            go.Scatter(
                x=poz_sicra['Tarih'], y=poz_sicra['Yuzde_Degisim'],
                mode='markers',
                name='Pozitif Sıçrama',
                marker=dict(
                    color=renk_pozitif,
                    size=poz_sicra['Abs_Degisim']*1.5,
                    line=dict(color='white', width=0.5)
                ),
                showlegend=False,
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: +%{y:.2f}%<extra></extra>'
            ),
            row=2, col=1
        )
    
    if len(neg_sicra) > 0:
        fig.add_trace(
            go.Scatter(
                x=neg_sicra['Tarih'], y=neg_sicra['Yuzde_Degisim'],
                mode='markers',
                name='Negatif Sıçrama',
                marker=dict(
                    color=renk_negatif,
                    size=neg_sicra['Abs_Degisim']*1.5,
                    line=dict(color='white', width=0.5)
                ),
                showlegend=False,
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: %{y:.2f}%<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Eşik çizgileri
    fig.add_hline(y=esik, line_dash="dash", line_color=renk_pozitif, 
                  annotation_text=f"+{esik}%", annotation_position="top left",
                  row=2, col=1)
    fig.add_hline(y=-esik, line_dash="dash", line_color=renk_negatif,
                  annotation_text=f"-{esik}%", annotation_position="bottom left",
                  row=2, col=1)
    fig.add_hline(y=0, line_color='gray', line_width=0.5, row=2, col=1)
    
    # Layout düzenlemeleri
    fig.update_layout(
        height=700,
        template='plotly_white',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(title_text="", row=1, col=1)
    fig.update_xaxes(title_text="Tarih", row=2, col=1)
    
    fig.update_yaxes(title_text="Dolar Kuru (TL)", row=1, col=1)
    fig.update_yaxes(title_text="Değişim (%)", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ========== GÜNLÜK SIÇRAMA LİSTESİ ==========
    st.markdown('<h2 class="sub-header">📋 GÜNLÜK SIÇRAMA LİSTESİ</h2>', unsafe_allow_html=True)
    
    # Filtreleme seçenekleri
    col1, col2, col3 = st.columns(3)
    with col1:
        yil_filtre = st.multiselect("Yıl Filtresi", options=sorted(sicramalar['Yil'].unique()))
    with col2:
        ay_filtre = st.multiselect("Ay Filtresi", options=range(1, 13), format_func=lambda x: calendar.month_name[x])
    with col3:
        siralama = st.selectbox("Sıralama", options=["Büyükten Küçüğe", "Küçükten Büyüğe", "Tarihe Göre"])
    
    # Filtre uygula
    filtered_sicramalar = sicramalar.copy()
    if yil_filtre:
        filtered_sicramalar = filtered_sicramalar[filtered_sicramalar['Yil'].isin(yil_filtre)]
    if ay_filtre:
        filtered_sicramalar = filtered_sicramalar[filtered_sicramalar['Ay'].isin(ay_filtre)]
    
    # Sıralama
    if siralama == "Büyükten Küçüğe":
        filtered_sicramalar = filtered_sicramalar.sort_values('Abs_Degisim', ascending=False)
    elif siralama == "Küçükten Büyüğe":
        filtered_sicramalar = filtered_sicramalar.sort_values('Abs_Degisim', ascending=True)
    else:
        filtered_sicramalar = filtered_sicramalar.sort_values('Tarih', ascending=False)
    
    # Tablo için hazırlık
    tablo_df = filtered_sicramalar[[
        'Tarih', 'Gun', 'Ay_Adi', 'Yil', 'Gun_Adi',
        'Dolar_Kuru', 'Onceki_Kur', 'Yuzde_Degisim', 'TL_Degisim', 'Gun_Farki'
    ]].copy()
    
    tablo_df['Tarih'] = tablo_df['Tarih'].dt.strftime('%d.%m.%Y')
    tablo_df['Dolar_Kuru'] = tablo_df['Dolar_Kuru'].round(4)
    tablo_df['Onceki_Kur'] = tablo_df['Onceki_Kur'].round(4)
    tablo_df['Yuzde_Degisim'] = tablo_df['Yuzde_Degisim'].round(2)
    tablo_df['TL_Degisim'] = tablo_df['TL_Degisim'].round(4)
    tablo_df['Yon'] = tablo_df['Yuzde_Degisim'].apply(lambda x: '📈' if x > 0 else '📉')
    
    tablo_df.insert(0, '#', range(1, len(tablo_df) + 1))
    
    # Tabloyu göster
    st.dataframe(
        tablo_df,
        column_config={
            '#': st.column_config.NumberColumn("No", width=50),
            'Tarih': "Tarih",
            'Gun': "Gün",
            'Ay_Adi': "Ay",
            'Yil': "Yıl",
            'Gun_Adi': "Gün Adı",
            'Dolar_Kuru': "Yeni Kur (TL)",
            'Onceki_Kur': "Önceki Kur",
            'Yuzde_Degisim': "Değişim %",
            'TL_Degisim': "TL Değişim",
            'Gun_Farki': "Gün Farkı",
            'Yon': ""
        },
        use_container_width=True,
        height=500
    )
    
    # ========== EN BÜYÜK GÜNLÜK SIÇRAMALAR ==========
    st.markdown('<h2 class="sub-header">⚡ EN BÜYÜK 10 GÜNLÜK SIÇRAMA</h2>', unsafe_allow_html=True)
    
    top_10 = sicramalar.head(10)
    
    # 5 kolonlu kart gösterimi
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_10.iterrows()):
        with cols[i % 5]:
            renk = '#48BB78' if row['Yuzde_Degisim'] > 0 else '#F56565'
            yon = '📈' if row['Yuzde_Degisim'] > 0 else '📉'
            
            st.markdown(f"""
            <div class="sicrama-karti" style="border-left-color: {renk};">
                <div style="font-size: 1.2rem; font-weight: 700;">#{i+1} {yon}</div>
                <div style="font-size: 1rem; color: #4A5568;">{row['Tarih'].strftime('%d.%m.%Y')}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {renk};">%{row['Yuzde_Degisim']:+.2f}</div>
                <div style="font-size: 0.9rem; color: #718096;">{row['Gun_Adi']}, {row['Ay_Adi']}</div>
                <div style="font-size: 0.9rem;">{row['Onceki_Kur']:.4f} → {row['Dolar_Kuru']:.4f} TL</div>
                <div style="font-size: 0.8rem; color: #A0AEC0;">{row['Gun_Farki']} gün sonra</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== ZAMAN BAZLI ANALİZLER (İkincil) ==========
    st.markdown('<h2 class="sub-header">📊 ZAMAN BAZLI ANALİZLER</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Günlere Göre Dağılım", "📆 Aylara Göre Dağılım", "📈 Trend Analizi"])
    
    with tab1:
        # Haftanın günlerine göre dağılım
        gun_sirasi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        gun_adlari_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        
        if len(sicramalar) > 0:
            haftalik_df = sicramalar.groupby('Gun_Adi').size().reindex(gun_sirasi).reset_index()
            haftalik_df.columns = ['Gün', 'Sayı']
            haftalik_df['Gün_TR'] = gun_adlari_tr
            haftalik_df = haftalik_df.fillna(0)
            
            fig_gun = px.bar(
                haftalik_df, 
                x='Gün_TR', 
                y='Sayı',
                title='Haftanın Günlerine Göre Sıçrama Sayıları',
                color='Sayı',
                color_continuous_scale='Viridis',
                labels={'Sayı': 'Sıçrama Sayısı', 'Gün_TR': 'Gün'}
            )
            fig_gun.update_layout(height=400)
            st.plotly_chart(fig_gun, use_container_width=True)
            
            # İstatistikler
            col1, col2, col3 = st.columns(3)
            with col1:
                max_gun = haftalik_df.loc[haftalik_df['Sayı'].idxmax()]
                st.info(f"📊 En çok sıçrama: **{max_gun['Gün_TR']}** ({int(max_gun['Sayı'])} sıçrama)")
            with col2:
                min_gun = haftalik_df.loc[haftalik_df[haftalik_df['Sayı'] > 0]['Sayı'].idxmin()]
                st.info(f"📉 En az sıçrama: **{min_gun['Gün_TR']}** ({int(min_gun['Sayı'])} sıçrama)")
            with col3:
                hafta_ici = haftalik_df.iloc[:5]['Sayı'].sum()
                hafta_sonu = haftalik_df.iloc[5:]['Sayı'].sum()
                st.info(f"📅 Hafta içi: {int(hafta_ici)} | Hafta sonu: {int(hafta_sonu)}")
        else:
            st.warning("Bu eşikte sıçrama verisi yok")
    
    with tab2:
        # Aylara göre dağılım
        if len(sicramalar) > 0:
            aylik_df = sicramalar.groupby('Ay').size().reset_index(name='Sayı')
            aylik_df['Ay_Adi'] = aylik_df['Ay'].apply(lambda x: calendar.month_name[x])
            
            fig_ay = px.bar(
                aylik_df, 
                x='Ay_Adi', 
                y='Sayı',
                title='Aylara Göre Sıçrama Sayıları',
                color='Sayı',
                color_continuous_scale='Plasma',
                labels={'Sayı': 'Sıçrama Sayısı', 'Ay_Adi': 'Ay'}
            )
            fig_ay.update_layout(height=400)
            st.plotly_chart(fig_ay, use_container_width=True)
            
            # En yüksek ay
            max_ay = aylik_df.loc[aylik_df['Sayı'].idxmax()]
            st.success(f"🌟 En çok sıçrama olan ay: **{max_ay['Ay_Adi']}** ({int(max_ay['Sayı'])} sıçrama)")
        else:
            st.warning("Bu eşikte sıçrama verisi yok")
    
    with tab3:
        # Günlük sıçrama trendi
        if len(sicramalar) > 0:
            # Yıllara göre sıçrama sayıları
            yillik_df = sicramalar.groupby('Yil').size().reset_index(name='Sayı')
            
            fig_trend = px.line(
                yillik_df, 
                x='Yil', 
                y='Sayı',
                markers=True,
                title='Yıllara Göre Günlük Sıçrama Sayıları',
                labels={'Sayı': 'Sıçrama Sayısı', 'Yil': 'Yıl'}
            )
            fig_trend.update_layout(height=400)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Kümülatif sıçrama
            df['Kumulatif_Sicrama'] = df['Sicrama'].cumsum()
            
            fig_kum = px.line(
                df, 
                x='Tarih', 
                y='Kumulatif_Sicrama',
                title='Kümülatif Günlük Sıçrama Sayısı',
                labels={'Kumulatif_Sicrama': 'Toplam Sıçrama', 'Tarih': 'Tarih'}
            )
            fig_kum.update_layout(height=400)
            st.plotly_chart(fig_kum, use_container_width=True)
        else:
            st.warning("Bu eşikte sıçrama verisi yok")
    
    # ========== İNDİRME BUTONU ==========
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if len(sicramalar) > 0:
            csv = sicramalar.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 GÜNLÜK SIÇRAMA VERİLERİNİ İNDİR ({len(sicramalar)} kayıt)",
                data=csv,
                file_name=f'dolar_gunluk_sicrama_{esik}percent_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )
    
    st.balloons()
    st.success(f"✅ Günlük sıçrama analizi tamamlandı! Toplam {len(df)} gün içinde {toplam_sicrama} sıçrama tespit edildi.")

else:
    # Hoş geldiniz ekranı
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://img.icons8.com/fluency/96/000000/line-chart.png", width=150)
        
        st.markdown("""
        <div style="text-align: center; background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
            <h2 style="color: #2D3748;">📊 Günlük Sıçrama Analizine Hoş Geldiniz</h2>
            <p style="color: #718096; font-size: 1.1rem; margin: 1.5rem 0;">
                Excel dosyanızı yükleyin, dolar kurundaki <b>günlük sıçramaları</b> 
                profesyonel grafiklerle keşfedin!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2rem;">
            <div style="background: #EBF4FF; padding: 1rem; border-radius: 10px;">
                <b>📊 Ayarlanabilir Sıçrama Sayısı</b><br>
                10, 20, 30, 50, 100 veya tümü
            </div>
            <div style="background: #F0FFF4; padding: 1rem; border-radius: 10px;">
                <b>🎯 Eşik Değeri</b><br>
                %0.5 ile %10 arası ayarlanabilir
            </div>
            <div style="background: #FFF5F5; padding: 1rem; border-radius: 10px;">
                <b>🔄 Yön Filtresi</b><br>
                Pozitif/Negatif/Tümü
            </div>
            <div style="background: #FFFAF0; padding: 1rem; border-radius: 10px;">
                <b>📋 Detaylı Tablo</b><br>
                Filtreleme ve sıralama
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #FEEBC8; border-radius: 10px;">
            <p style="margin: 0; color: #7B341E;">
                <b>💡 İpucu:</b> Farklı eşik değerleri ve sıçrama sayıları deneyerek 
                günlük volatiliteyi keşfedin!
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 1rem;">
    📊 Dolar Kuru Günlük Sıçrama Analizi | Her gün için detaylı sıçrama analizi
</div>
""", unsafe_allow_html=True)
