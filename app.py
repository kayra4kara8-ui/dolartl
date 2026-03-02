import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Sayfa yapılandırması
st.set_page_config(
    page_title="Dolar Kuru Sıçrama Analizi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile görsel iyileştirme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .big-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .positive {
        color: #2ECC71;
        font-weight: bold;
    }
    .negative {
        color: #E74C3C;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<h1 class="main-header">📈 DOLAR KURU GÜNLÜK SIÇRAMA ANALİZİ</h1>', unsafe_allow_html=True)
st.markdown("Excel dosyanızı yükleyin, anında grafikler ve tablolar oluştursun!")

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Emblem-money.svg/200px-Emblem-money.svg.png", width=100)
    st.markdown("## ⚙️ AYARLAR")
    
    # Dosya yükleme
    uploaded_file = st.file_uploader("📂 Excel dosyası yükleyin", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        st.success("✅ Dosya yüklendi!")
        
        # Eşik değeri
        esik = st.slider("🎯 Sıçrama eşiği (%)", min_value=0.5, max_value=20.0, value=2.0, step=0.5)
        
        # Gösterim sayısı
        gosterim_sayisi = st.number_input("📊 Tabloda gösterilecek sıçrama sayısı", 
                                          min_value=5, max_value=200, value=50, step=5)
        
        # Sıçrama yönü
        yon = st.radio("🔄 Sıçrama yönü", ["Her İki", "Pozitif", "Negatif"])
        
        # Renk teması
        renk_tema = st.selectbox("🎨 Renk teması", 
                                 ["Modern", "Klasik", "Pastel", "Canlı"])
        
        # Analiz butonu
        analiz_btn = st.button("🚀 ANALİZİ ÇALIŞTIR", type="primary", use_container_width=True)

# Ana içerik
if uploaded_file is not None and analiz_btn:
    
    # Veriyi yükle ve işle
    with st.spinner("Veri analiz ediliyor..."):
        df = pd.read_excel(uploaded_file, sheet_name='EVDS')
        df.columns = ['Tarih', 'Dolar_Kuru']
        df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y', errors='coerce')
        
        # Boş değerleri temizle
        df = df.dropna().sort_values('Tarih').reset_index(drop=True)
        
        # Günlük değişim hesapla
        df['Onceki_Kur'] = df['Dolar_Kuru'].shift(1)
        df['Onceki_Tarih'] = df['Tarih'].shift(1)
        df['Gun_Farki'] = (df['Tarih'] - df['Onceki_Tarih']).dt.days
        df['Yuzde_Degisim'] = (df['Dolar_Kuru'] / df['Onceki_Kur'] - 1) * 100
        df = df.dropna().reset_index(drop=True)
        
        # Tarih bilgileri
        df['Gun'] = df['Tarih'].dt.day
        df['Ay'] = df['Tarih'].dt.month
        df['Yil'] = df['Tarih'].dt.year
        df['Ay_Adi'] = df['Tarih'].dt.strftime('%B')
        df['Gun_Adi'] = df['Tarih'].dt.strftime('%A')
        df['Abs_Degisim'] = abs(df['Yuzde_Degisim'])
        
        # Yön filtresi
        if yon == "Pozitif":
            sicramalar = df[df['Yuzde_Degisim'] >= esik].copy()
        elif yon == "Negatif":
            sicramalar = df[df['Yuzde_Degisim'] <= -esik].copy()
        else:
            sicramalar = df[df['Abs_Degisim'] >= esik].copy()
        
        sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
        
        # Renk temasını ayarla
        if renk_tema == "Modern":
            renk_trend = '#3498DB'
            renk_pozitif = '#2ECC71'
            renk_negatif = '#E74C3C'
            renk_esik = '#F39C12'
        elif renk_tema == "Klasik":
            renk_trend = 'blue'
            renk_pozitif = 'green'
            renk_negatif = 'red'
            renk_esik = 'orange'
        elif renk_tema == "Pastel":
            renk_trend = '#6C5B7B'
            renk_pozitif = '#99B898'
            renk_negatif = '#F8A5A5'
            renk_esik = '#F7D794'
        else:
            renk_trend = '#F08A5D'
            renk_pozitif = '#4ECDC4'
            renk_negatif = '#FF6B6B'
            renk_esik = '#FFE66D'
    
    # İSTATİSTİK KARTLARI
    st.markdown('<h2 class="sub-header">📊 ÖZET İSTATİSTİKLER</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("📅 Toplam Gün", f"{len(df):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("📈 Ortalama Değişim", f"%{df['Yuzde_Degisim'].mean():.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("📊 Sıçrama Sayısı", f"{len(sicramalar)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("📅 Veri Aralığı", f"{df['Tarih'].min().strftime('%Y')}-{df['Tarih'].max().strftime('%Y')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # GRAFİKLER
    st.markdown('<h2 class="sub-header">📈 GÖRSELLEŞTİRMELER</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📉 Dolar Kuru & Sıçramalar", "📊 Değişim Analizi", "📅 Yıllık Dağılım"])
    
    with tab1:
        # Plotly ile interaktif grafik
        fig = go.Figure()
        
        # Dolar kuru trendi
        fig.add_trace(go.Scatter(
            x=df['Tarih'], y=df['Dolar_Kuru'],
            mode='lines',
            name='Dolar Kuru',
            line=dict(color=renk_trend, width=2),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<extra></extra>'
        ))
        
        # Pozitif sıçramalar
        poz = sicramalar[sicramalar['Yuzde_Degisim'] > 0]
        if len(poz) > 0:
            fig.add_trace(go.Scatter(
                x=poz['Tarih'], y=poz['Dolar_Kuru'],
                mode='markers',
                name=f'Pozitif Sıçrama ({len(poz)})',
                marker=dict(color=renk_pozitif, size=poz['Abs_Degisim']*2, 
                           line=dict(color='white', width=1)),
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{text}',
                text=[f"%{x:+.2f}" for x in poz['Yuzde_Degisim']]
            ))
        
        # Negatif sıçramalar
        neg = sicramalar[sicramalar['Yuzde_Degisim'] < 0]
        if len(neg) > 0:
            fig.add_trace(go.Scatter(
                x=neg['Tarih'], y=neg['Dolar_Kuru'],
                mode='markers',
                name=f'Negatif Sıçrama ({len(neg)})',
                marker=dict(color=renk_negatif, size=abs(neg['Yuzde_Degisim'])*2,
                           line=dict(color='white', width=1)),
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{text}',
                text=[f"%{x:+.2f}" for x in neg['Yuzde_Degisim']]
            ))
        
        fig.update_layout(
            title=f'DOLAR KURU - {esik}% ÜZERİNDEKİ SIÇRAMALAR (Toplam: {len(sicramalar)})',
            xaxis_title='Tarih',
            yaxis_title='Dolar Kuru (TL)',
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Yüzde değişim grafiği
            fig2 = go.Figure()
            
            # Tüm değişimler
            fig2.add_trace(go.Scatter(
                x=df['Tarih'], y=df['Yuzde_Degisim'],
                mode='markers',
                name='Tüm Değişimler',
                marker=dict(color='lightgray', size=3, opacity=0.5),
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: %{y:.2f}%<extra></extra>'
            ))
            
            # Sıçramalar
            if len(poz) > 0:
                fig2.add_trace(go.Scatter(
                    x=poz['Tarih'], y=poz['Yuzde_Degisim'],
                    mode='markers',
                    name='Pozitif Sıçrama',
                    marker=dict(color=renk_pozitif, size=10),
                    hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: %{y:+.2f}%<extra></extra>'
                ))
            
            if len(neg) > 0:
                fig2.add_trace(go.Scatter(
                    x=neg['Tarih'], y=neg['Yuzde_Degisim'],
                    mode='markers',
                    name='Negatif Sıçrama',
                    marker=dict(color=renk_negatif, size=10),
                    hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: %{y:+.2f}%<extra></extra>'
                ))
            
            # Eşik çizgileri
            fig2.add_hline(y=esik, line_dash="dash", line_color=renk_pozitif, 
                          annotation_text=f"+{esik}%", annotation_position="top left")
            fig2.add_hline(y=-esik, line_dash="dash", line_color=renk_negatif,
                          annotation_text=f"-{esik}%", annotation_position="bottom left")
            
            fig2.update_layout(
                title='GÜNLÜK YÜZDE DEĞİŞİMLER',
                xaxis_title='Tarih',
                yaxis_title='Değişim (%)',
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # Histogram
            fig3 = go.Figure()
            
            fig3.add_trace(go.Histogram(
                x=sicramalar['Yuzde_Degisim'],
                nbinsx=20,
                marker_color=[renk_pozitif if x > 0 else renk_negatif for x in sicramalar['Yuzde_Degisim']],
                name='Sıçramalar'
            ))
            
            fig3.update_layout(
                title='SIÇRAMA BÜYÜKLÜK DAĞILIMI',
                xaxis_title='Değişim (%)',
                yaxis_title='Frekans',
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
    
    with tab3:
        # Yıllık dağılım
        yillik_df = sicramalar.groupby('Yil').agg({
            'Yuzde_Degisim': ['count', 'mean', 'max', 'min']
        }).round(2)
        yillik_df.columns = ['Sayı', 'Ortalama', 'Maks', 'Min']
        yillik_df = yillik_df.reset_index()
        
        # Çubuk grafik
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=yillik_df['Yil'],
            y=yillik_df['Sayı'],
            marker_color=renk_trend,
            text=yillik_df['Sayı'],
            textposition='outside',
            name='Sıçrama Sayısı'
        ))
        
        fig4.update_layout(
            title='YILLARA GÖRE SIÇRAMA SAYILARI',
            xaxis_title='Yıl',
            yaxis_title='Sıçrama Sayısı',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig4, use_container_width=True)
        
        # Yıllık tablo
        st.dataframe(yillik_df, use_container_width=True)
    
    # SIÇRAMA TABLOSU
    st.markdown('<h2 class="sub-header">📋 SIÇRAMA LİSTESİ</h2>', unsafe_allow_html=True)
    
    # Tablo için veri hazırlama
    tablo_df = sicramalar.head(gosterim_sayisi)[
        ['Tarih', 'Gun', 'Ay', 'Yil', 'Dolar_Kuru', 'Onceki_Kur', 
         'Yuzde_Degisim', 'Gun_Farki']
    ].copy()
    
    tablo_df['Tarih'] = tablo_df['Tarih'].dt.strftime('%d.%m.%Y')
    tablo_df['Dolar_Kuru'] = tablo_df['Dolar_Kuru'].round(4)
    tablo_df['Onceki_Kur'] = tablo_df['Onceki_Kur'].round(4)
    tablo_df['Yuzde_Degisim'] = tablo_df['Yuzde_Degisim'].round(2)
    
    # Renkli gösterim için
    def renklendir(val):
        if val > 0:
            return f'<span class="positive">%{val:+.2f}</span>'
        elif val < 0:
            return f'<span class="negative">%{val:+.2f}</span>'
        return f'%{val:.2f}'
    
    tablo_df['Değişim'] = tablo_df['Yuzde_Degisim'].apply(renklendir)
    
    # Tabloyu göster
    st.markdown(f"**📊 {esik}% üzerindeki ilk {gosterim_sayisi} sıçrama**")
    st.dataframe(
        tablo_df[['Tarih', 'Gun', 'Ay', 'Yil', 'Dolar_Kuru', 'Onceki_Kur', 'Değişim', 'Gun_Farki']],
        column_config={
            'Tarih': 'Tarih',
            'Gun': 'Gün',
            'Ay': 'Ay',
            'Yil': 'Yıl',
            'Dolar_Kuru': 'Dolar Kuru (TL)',
            'Onceki_Kur': 'Önceki Kur',
            'Değişim': 'Değişim (%)',
            'Gun_Farki': 'Gün Farkı'
        },
        use_container_width=True,
        height=400
    )
    
    # İndirme butonu
    csv = sicramalar.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Tüm Sıçramaları İndir (CSV)",
        data=csv,
        file_name=f'dolar_sicramalar_{esik}percent.csv',
        mime='text/csv',
    )
    
    # Başarı mesajı
    st.balloons()
    st.success(f"✅ Analiz tamamlandı! {len(sicramalar)} sıçrama tespit edildi.")

else:
    # Hoş geldiniz mesajı
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Emblem-money.svg/200px-Emblem-money.svg.png", width=200)
        
        st.markdown("""
        ### 📥 Nasıl Kullanılır?
        
        1. **Excel dosyanızı yükleyin** (sol menüden)
        2. **Eşik değerini ayarlayın** (varsayılan: %2)
        3. **Analiz butonuna tıklayın**
        4. **Grafikleri ve tabloları inceleyin**
        
        ### 📊 Özellikler
        - 📈 İnteraktif grafikler
        - 📋 Detaylı sıçrama tablosu
        - 🎯 Ayarlanabilir eşik
        - 📥 CSV indirme
        - 🎨 Renk temaları
        
        ### 📁 Excel Formatı
        Dosyanızda şu sütunlar olmalı:
        - **Tarih** (format: 01-01-2016)
        - **TP_DK_USD_A_YTL** (dolar kuru)
        """)
        
        st.info("💡 Örnek dosya kullanmak isterseniz, yukarıdaki 'data.xlsx' dosyasını yükleyin!")

# Footer
st.markdown("---")
st.markdown("📊 **Dolar Kuru Sıçrama Analizi** | Günlük değişimleri keşfedin!")