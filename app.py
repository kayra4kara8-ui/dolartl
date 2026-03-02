import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

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
    .positive {
        color: #2ECC71;
        font-weight: bold;
    }
    .negative {
        color: #E74C3C;
        font-weight: bold;
    }
    .top-list {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .top-item {
        padding: 0.5rem;
        border-bottom: 1px solid #dee2e6;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<h1 class="main-header">📈 DOLAR KURU GÜNLÜK SIÇRAMA ANALİZİ</h1>', unsafe_allow_html=True)
st.markdown("Excel dosyanızı yükleyin, en büyük 30 sıçramayı görün!")

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
        
        # Gösterilecek sıçrama sayısı
        gosterim_sayisi = st.number_input("📊 Gösterilecek sıçrama sayısı", 
                                          min_value=5, max_value=100, value=30, step=5)
        
        # Analiz butonu
        analiz_btn = st.button("🚀 ANALİZİ ÇALIŞTIR", type="primary", use_container_width=True)

# Ana içerik
if uploaded_file is not None and analiz_btn:
    
    # Veriyi yükle ve işle
    with st.spinner("Veri analiz ediliyor..."):
        try:
            # Excel'i oku
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_name = excel_file.sheet_names[0]
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # Sütun isimlerini al
            if len(df.columns) >= 2:
                tarih_sutunu = df.columns[0]
                kur_sutunu = df.columns[1]
                df = df[[tarih_sutunu, kur_sutunu]].copy()
                df.columns = ['Tarih', 'Dolar_Kuru']
            else:
                st.error("Excel dosyasında en az 2 sütun olmalı!")
                st.stop()
            
            # Tarih dönüşümü
            df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
            df['Dolar_Kuru'] = pd.to_numeric(df['Dolar_Kuru'], errors='coerce')
            
            # Boş değerleri temizle
            df = df.dropna().sort_values('Tarih').reset_index(drop=True)
            
            if len(df) == 0:
                st.error("Hiç geçerli veri bulunamadı!")
                st.stop()
            
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
            
            # Eşik üzerindeki sıçramalar
            sicramalar = df[df['Abs_Degisim'] >= esik].copy()
            sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
            
            # İLK 30 (veya seçilen sayı) EN BÜYÜK SIÇRAMA
            top_sicramalar = sicramalar.head(gosterim_sayisi).copy()
            
        except Exception as e:
            st.error(f"❌ Dosya okuma hatası: {str(e)}")
            st.stop()
    
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
        st.metric("📊 Toplam Sıçrama", f"{len(sicramalar)} (>{esik}%)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("📅 Veri Aralığı", f"{df['Tarih'].min().strftime('%Y')}-{df['Tarih'].max().strftime('%Y')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # İLK 30 SIÇRAMA TABLOSU (DETAYLI)
    st.markdown(f'<h2 class="sub-header">🏆 EN BÜYÜK {gosterim_sayisi} SIÇRAMA</h2>', unsafe_allow_html=True)
    
    # Tabloyu hazırla
    top_tablo = top_sicramalar[[
        'Tarih', 'Gun', 'Ay', 'Yil', 'Gun_Adi', 'Ay_Adi',
        'Dolar_Kuru', 'Onceki_Kur', 'Yuzde_Degisim', 'Gun_Farki'
    ]].copy()
    
    top_tablo['Tarih'] = top_tablo['Tarih'].dt.strftime('%d.%m.%Y')
    top_tablo['Dolar_Kuru'] = top_tablo['Dolar_Kuru'].round(4)
    top_tablo['Onceki_Kur'] = top_tablo['Onceki_Kur'].round(4)
    top_tablo['Yuzde_Degisim'] = top_tablo['Yuzde_Degisim'].round(2)
    top_tablo['Yon'] = top_tablo['Yuzde_Degisim'].apply(lambda x: '📈' if x > 0 else '📉')
    
    # Sıra numarası ekle
    top_tablo.insert(0, 'Sıra', range(1, len(top_tablo) + 1))
    
    # Detaylı tablo göster
    st.dataframe(
        top_tablo[[
            'Sıra', 'Tarih', 'Gun', 'Ay', 'Yil', 'Gun_Adi', 'Ay_Adi',
            'Dolar_Kuru', 'Onceki_Kur', 'Yuzde_Degisim', 'Yon', 'Gun_Farki'
        ]],
        column_config={
            'Sıra': 'No',
            'Tarih': 'Tarih',
            'Gun': 'Gün',
            'Ay': 'Ay',
            'Yil': 'Yıl',
            'Gun_Adi': 'Gün Adı',
            'Ay_Adi': 'Ay Adı',
            'Dolar_Kuru': 'Yeni Kur (TL)',
            'Onceki_Kur': 'Önceki Kur',
            'Yuzde_Degisim': 'Değişim %',
            'Yon': 'Yön',
            'Gun_Farki': 'Gün Farkı'
        },
        use_container_width=True,
        height=500
    )
    
    # GRAFİK
    st.markdown('<h2 class="sub-header">📈 GÖRSELLEŞTİRME</h2>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    # Dolar kuru trendi
    fig.add_trace(go.Scatter(
        x=df['Tarih'], y=df['Dolar_Kuru'],
        mode='lines',
        name='Dolar Kuru',
        line=dict(color='#3498DB', width=2),
        hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<extra></extra>'
    ))
    
    # İlk 30 sıçramayı işaretle
    poz = top_sicramalar[top_sicramalar['Yuzde_Degisim'] > 0]
    neg = top_sicramalar[top_sicramalar['Yuzde_Degisim'] < 0]
    
    if len(poz) > 0:
        fig.add_trace(go.Scatter(
            x=poz['Tarih'], y=poz['Dolar_Kuru'],
            mode='markers',
            name=f'Pozitif (İlk {len(poz)})',
            marker=dict(color='#2ECC71', size=12, line=dict(color='white', width=1)),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{text}',
            text=[f"%{x:+.2f}" for x in poz['Yuzde_Degisim']]
        ))
    
    if len(neg) > 0:
        fig.add_trace(go.Scatter(
            x=neg['Tarih'], y=neg['Dolar_Kuru'],
            mode='markers',
            name=f'Negatif (İlk {len(neg)})',
            marker=dict(color='#E74C3C', size=12, line=dict(color='white', width=1)),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{text}',
            text=[f"%{x:+.2f}" for x in neg['Yuzde_Degisim']]
        ))
    
    fig.update_layout(
        title=f'DOLAR KURU - EN BÜYÜK {gosterim_sayisi} SIÇRAMA',
        xaxis_title='Tarih',
        yaxis_title='Dolar Kuru (TL)',
        height=500,
        template='plotly_white',
        hovermode='x'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # İLK 30'UN DETAYLI LİSTESİ (KART ŞEKLİNDE)
    st.markdown(f'<h2 class="sub-header">📋 İLK {gosterim_sayisi} SIÇRAMA DETAYI</h2>', unsafe_allow_html=True)
    
    # 3 kolonlu grid
    cols = st.columns(3)
    
    for idx, (_, row) in enumerate(top_sicramalar.iterrows()):
        col_idx = idx % 3
        with cols[col_idx]:
            # Renk belirle
            if row['Yuzde_Degisim'] > 0:
                renk = "#2ECC71"
                yon_ikon = "📈"
            else:
                renk = "#E74C3C"
                yon_ikon = "📉"
            
            # Kart HTML
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                border-left: 5px solid {renk};
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            ">
                <h4 style="margin:0; color:{renk};">#{idx+1} - {row['Tarih'].strftime('%d.%m.%Y')} {yon_ikon}</h4>
                <p style="margin:5px 0;">
                    <b>📅 Gün:</b> {row['Gun']} {row['Gun_Adi']}<br>
                    <b>📆 Ay:</b> {row['Ay']} - {row['Ay_Adi']}<br>
                    <b>📅 Yıl:</b> {row['Yil']}<br>
                    <b>💰 Yeni Kur:</b> {row['Dolar_Kuru']:.4f} TL<br>
                    <b>💵 Önceki Kur:</b> {row['Onceki_Kur']:.4f} TL<br>
                    <b>📊 Değişim:</b> <span style="color:{renk}; font-weight:bold;">%{row['Yuzde_Degisim']:+.2f}</span><br>
                    <b>⏱️ Gün Farkı:</b> {row['Gun_Farki']} gün
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # İSTATİSTİKLER
    st.markdown('<h2 class="sub-header">📊 İLK 30 ANALİZİ</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        poz_sayisi = len(top_sicramalar[top_sicramalar['Yuzde_Degisim'] > 0])
        neg_sayisi = len(top_sicramalar[top_sicramalar['Yuzde_Degisim'] < 0])
        st.metric("📈 Pozitif Sıçrama", poz_sayisi)
        st.metric("📉 Negatif Sıçrama", neg_sayisi)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("📊 Ortalama Değişim", f"%{top_sicramalar['Yuzde_Degisim'].mean():+.2f}")
        st.metric("📈 En Yüksek", f"%{top_sicramalar['Yuzde_Degisim'].max():+.2f}")
        st.metric("📉 En Düşük", f"%{top_sicramalar['Yuzde_Degisim'].min():+.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("📅 Ortalama Gün Farkı", f"{top_sicramalar['Gun_Farki'].mean():.1f} gün")
        st.metric("📆 En Çok Hangi Ay", f"{top_sicramalar['Ay'].mode()[0]}. Ay")
        st.metric("📅 En Çok Hangi Yıl", f"{top_sicramalar['Yil'].mode()[0]}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Yıllara göre dağılım
    st.markdown('<h2 class="sub-header">📅 YILLARA GÖRE DAĞILIM (İlk 30)</h2>', unsafe_allow_html=True)
    
    yillik_df = top_sicramalar.groupby('Yil').size().reset_index(name='Sayı')
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=yillik_df['Yil'],
        y=yillik_df['Sayı'],
        marker_color='#3498DB',
        text=yillik_df['Sayı'],
        textposition='outside'
    ))
    
    fig2.update_layout(
        title='İlk 30 Sıçramanın Yıllara Göre Dağılımı',
        xaxis_title='Yıl',
        yaxis_title='Sıçrama Sayısı',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # İndirme butonu
    csv = top_sicramalar.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 İlk {gosterim_sayisi} Sıçramayı İndir (CSV)",
        data=csv,
        file_name=f'dolar_ilk_{gosterim_sayisi}_sicrama.csv',
        mime='text/csv',
    )
    
    st.balloons()
    st.success(f"✅ Analiz tamamlandı! En büyük {gosterim_sayisi} sıçrama listelendi.")

else:
    # Hoş geldiniz mesajı
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Emblem-money.svg/200px-Emblem-money.svg.png", width=200)
        
        st.markdown("""
        ### 📥 Nasıl Kullanılır?
        
        1. **Excel dosyanızı yükleyin** (sol menüden)
        2. **Eşik değerini ayarlayın** (varsayılan: %2)
        3. **Gösterilecek sıçrama sayısını seçin** (varsayılan: 30)
        4. **Analiz butonuna tıklayın**
        5. **İlk 30 sıçramayı detaylı görün!**
        
        ### 📊 Bu Analizde Görecekleriniz:
        - 🏆 **En büyük 30 sıçrama** (tarih, gün, ay, yıl detaylı)
        - 📈 **Grafikte işaretlenmiş sıçramalar**
        - 📋 **Her sıçrama için kart görünümü**
        - 📊 **İstatistiksel analiz**
        - 📅 **Yıllara göre dağılım**
        
        ### 📁 Excel Formatı
        - **İlk sütun**: Tarih (01-01-2016, 01.01.2016)
        - **İkinci sütun**: Dolar Kuru (2.9181)
        """)

# Footer
st.markdown("---")
st.markdown("📊 **Dolar Kuru Sıçrama Analizi** | En büyük 30 sıçramayı keşfedin!")
