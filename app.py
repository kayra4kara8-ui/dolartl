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
    page_title="Dolar Kuru Profesyonel Analiz",
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
    
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #667eea30;
    }
    
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
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
    
    .highlight {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<h1 class="main-header">📊 DOLAR KURU PROFESYONEL SIÇRAMA ANALİZİ</h1>', unsafe_allow_html=True)

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
        st.markdown("### ⚙️ ANALİZ PARAMETRELERİ")
        
        # Eşik değeri
        esik = st.slider(
            "🎯 Sıçrama Eşiği (%)",
            min_value=0.5, max_value=10.0, value=2.0, step=0.5,
            help="Bu değerin üzerindeki değişimler sıçrama olarak kabul edilir"
        )
        
        # Gösterim sayısı
        gosterim_sayisi = st.selectbox(
            "📊 Gösterilecek Sıçrama Sayısı",
            options=[10, 20, 30, 50, 75, 100, "Tümü"],
            index=2,
            help="En büyük kaç sıçrama gösterilsin?"
        )
        
        # Renk teması
        renk_temasi = st.selectbox(
            "🎨 Renk Teması",
            options=["Profesyonel", "Canlı", "Pastel", "Karanlık"],
            index=0
        )
        
        # Analiz butonu
        analiz_btn = st.button(
            "🚀 ANALİZİ ÇALIŞTIR",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="background: #EBF4FF; padding: 1rem; border-radius: 10px;">
            <p style="color: #1E4F8A; margin: 0; font-size: 0.9rem;">
                💡 <b>İpucu:</b> Farklı eşik değerleri deneyerek 
                sıçramaların şiddetini keşfedin!
            </p>
        </div>
        """, unsafe_allow_html=True)

# Ana içerik
if uploaded_file is not None and analiz_btn:
    
    with st.spinner("🔍 Veriler analiz ediliyor..."):
        try:
            # Excel okuma
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_name = excel_file.sheet_names[0]
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # Sütunları düzenle
            if len(df.columns) >= 2:
                df.columns = ['Tarih', 'Dolar_Kuru'][:len(df.columns)]
                df = df.iloc[:, :2].copy()
                df.columns = ['Tarih', 'Dolar_Kuru']
            else:
                st.error("❌ Excel dosyasında en az 2 sütun olmalı!")
                st.stop()
            
            # Veri temizliği
            df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
            df['Dolar_Kuru'] = pd.to_numeric(df['Dolar_Kuru'], errors='coerce')
            df = df.dropna().sort_values('Tarih').reset_index(drop=True)
            
            # Günlük değişim hesapla
            df['Onceki_Kur'] = df['Dolar_Kuru'].shift(1)
            df['Onceki_Tarih'] = df['Tarih'].shift(1)
            df['Gun_Farki'] = (df['Tarih'] - df['Onceki_Tarih']).dt.days
            df['Yuzde_Degisim'] = (df['Dolar_Kuru'] / df['Onceki_Kur'] - 1) * 100
            df['TL_Degisim'] = df['Dolar_Kuru'] - df['Onceki_Kur']
            df = df.dropna().reset_index(drop=True)
            
            # Tarih özellikleri
            df['Yil'] = df['Tarih'].dt.year
            df['Ay'] = df['Tarih'].dt.month
            df['Gun'] = df['Tarih'].dt.day
            df['Ay_Adi'] = df['Tarih'].dt.strftime('%B')
            df['Gun_Adi'] = df['Tarih'].dt.strftime('%A')
            df['Hafta'] = df['Tarih'].dt.isocalendar().week
            df['Yil_Ay'] = df['Tarih'].dt.strftime('%Y-%m')
            df['Abs_Degisim'] = abs(df['Yuzde_Degisim'])
            
            # Sıçrama tespiti
            df['Sicrama'] = df['Abs_Degisim'] >= esik
            df['Sicrama_Tipi'] = np.where(
                df['Yuzde_Degisim'] > esik, 'Pozitif',
                np.where(df['Yuzde_Degisim'] < -esik, 'Negatif', 'Normal')
            )
            
            # Sıçramaları filtrele
            sicramalar = df[df['Sicrama']].copy()
            sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
            
            # Gösterim sayısını ayarla
            if gosterim_sayisi != "Tümü":
                sicramalar = sicramalar.head(gosterim_sayisi)
            
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            st.stop()
    
    # ========== ÜST İSTATİSTİKLER ==========
    st.markdown('<h2 class="sub-header">📊 GENEL GÖRÜNÜM</h2>', unsafe_allow_html=True)
    
    # Ana metrikler
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Toplam İşlem Günü</div>
            <div class="stat-value">{:,}</div>
            <div class="stat-unit">gün</div>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Ortalama Değişim</div>
            <div class="stat-value">%{:.2f}</div>
            <div class="stat-unit">günlük</div>
        </div>
        """.format(df['Yuzde_Degisim'].mean()), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Toplam Sıçrama</div>
            <div class="stat-value">{}</div>
            <div class="stat-unit">(>{}%)</div>
        </div>
        """.format(len(df[df['Sicrama']]), esik), unsafe_allow_html=True)
    
    with col4:
        poz = len(df[df['Yuzde_Degisim'] > esik])
        neg = len(df[df['Yuzde_Degisim'] < -esik])
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Pozitif / Negatif</div>
            <div class="stat-value"><span class="positive">{}</span> / <span class="negative">{}</span></div>
            <div class="stat-unit">sıçrama</div>
        </div>
        """.format(poz, neg), unsafe_allow_html=True)
    
    # ========== ANA GRAFİK ==========
    st.markdown('<h2 class="sub-header">📈 DOLAR KURU VE SIÇRAMA ANALİZİ</h2>', unsafe_allow_html=True)
    
    # Renk teması
    if renk_temasi == "Profesyonel":
        renk_trend = '#4299E1'
        renk_pozitif = '#48BB78'
        renk_negatif = '#F56565'
        renk_arkaplan = 'white'
    elif renk_temasi == "Canlı":
        renk_trend = '#FF6B6B'
        renk_pozitif = '#4ECDC4'
        renk_negatif = '#FFE66D'
        renk_arkaplan = '#F7F9FC'
    elif renk_temasi == "Pastel":
        renk_trend = '#6C5B7B'
        renk_pozitif = '#99B898'
        renk_negatif = '#F8A5A5'
        renk_arkaplan = '#F9F9F9'
    else:
        renk_trend = '#2C3E50'
        renk_pozitif = '#27AE60'
        renk_negatif = '#C0392B'
        renk_arkaplan = '#2C3E50'
    
    # Subplot oluştur
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=('DOLAR KURU TRENDİ', 'GÜNLÜK YÜZDE DEĞİŞİM', 'SIÇRAMA VOLATİLİTESİ')
    )
    
    # 1. Dolar kuru trendi
    fig.add_trace(
        go.Scatter(
            x=df['Tarih'], y=df['Dolar_Kuru'],
            mode='lines',
            name='Dolar Kuru',
            line=dict(color=renk_trend, width=2),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Sıçramaları ekle
    poz_sicra = sicramalar[sicramalar['Yuzde_Degisim'] > 0]
    neg_sicra = sicramalar[sicramalar['Yuzde_Degisim'] < 0]
    
    if len(poz_sicra) > 0:
        fig.add_trace(
            go.Scatter(
                x=poz_sicra['Tarih'], y=poz_sicra['Dolar_Kuru'],
                mode='markers',
                name='Pozitif Sıçrama',
                marker=dict(
                    color=renk_pozitif,
                    size=poz_sicra['Abs_Degisim']*2,
                    line=dict(color='white', width=1),
                    symbol='circle'
                ),
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{text}',
                text=[f"+%{x:.2f}" for x in poz_sicra['Yuzde_Degisim']]
            ),
            row=1, col=1
        )
    
    if len(neg_sicra) > 0:
        fig.add_trace(
            go.Scatter(
                x=neg_sicra['Tarih'], y=neg_sicra['Dolar_Kuru'],
                mode='markers',
                name='Negatif Sıçrama',
                marker=dict(
                    color=renk_negatif,
                    size=neg_sicra['Abs_Degisim']*2,
                    line=dict(color='white', width=1),
                    symbol='circle'
                ),
                hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{text}',
                text=[f"%{x:.2f}" for x in neg_sicra['Yuzde_Degisim']]
            ),
            row=1, col=1
        )
    
    # 2. Günlük yüzde değişim
    fig.add_trace(
        go.Scatter(
            x=df['Tarih'], y=df['Yuzde_Degisim'],
            mode='markers',
            name='Günlük Değişim',
            marker=dict(
                color='lightgray',
                size=3,
                opacity=0.5
            ),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: %{y:.2f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Eşik çizgileri
    fig.add_hline(y=esik, line_dash="dash", line_color=renk_pozitif, 
                  annotation_text=f"+{esik}%", row=2, col=1)
    fig.add_hline(y=-esik, line_dash="dash", line_color=renk_negatif,
                  annotation_text=f"-{esik}%", row=2, col=1)
    
    # 3. 30 günlük volatilite
    df['Volatilite_30'] = df['Yuzde_Degisim'].rolling(window=30).std()
    
    fig.add_trace(
        go.Scatter(
            x=df['Tarih'], y=df['Volatilite_30'],
            mode='lines',
            name='30 Günlük Volatilite',
            line=dict(color='#9F7AEA', width=2),
            fill='tozeroy',
            fillcolor='#9F7AEA20',
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Volatilite: %{y:.2f}%<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Sıçrama günlerini işaretle
    sicrama_gunleri = sicramalar['Tarih'].tolist()
    sicrama_vol = df[df['Tarih'].isin(sicrama_gunleri)]['Volatilite_30']
    
    fig.add_trace(
        go.Scatter(
            x=sicrama_gunleri, y=sicrama_vol,
            mode='markers',
            name='Sıçrama Günleri',
            marker=dict(color='#F6AD55', size=8, line=dict(color='white', width=1)),
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Layout düzenlemeleri
    fig.update_layout(
        height=800,
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
    fig.update_xaxes(title_text="", row=2, col=1)
    fig.update_xaxes(title_text="Tarih", row=3, col=1)
    
    fig.update_yaxes(title_text="Dolar Kuru (TL)", row=1, col=1)
    fig.update_yaxes(title_text="Değişim (%)", row=2, col=1)
    fig.update_yaxes(title_text="Volatilite (%)", row=3, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ========== SIÇRAMA DETAYLARI ==========
    st.markdown('<h2 class="sub-header">🔥 EN BÜYÜK SIÇRAMALAR</h2>', unsafe_allow_html=True)
    
    # Tablo ve kartlar
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Detaylı tablo
        tablo_df = sicramalar[[
            'Tarih', 'Gun', 'Ay_Adi', 'Yil', 'Gun_Adi',
            'Dolar_Kuru', 'Onceki_Kur', 'Yuzde_Degisim', 'TL_Degisim', 'Gun_Farki'
        ]].copy()
        
        tablo_df['Tarih'] = tablo_df['Tarih'].dt.strftime('%d.%m.%Y')
        tablo_df['Dolar_Kuru'] = tablo_df['Dolar_Kuru'].round(4)
        tablo_df['Onceki_Kur'] = tablo_df['Onceki_Kur'].round(4)
        tablo_df['Yuzde_Degisim'] = tablo_df['Yuzde_Degisim'].round(2)
        tablo_df['TL_Degisim'] = tablo_df['TL_Degisim'].round(4)
        tablo_df['Yon'] = tablo_df['Yuzde_Degisim'].apply(
            lambda x: '📈' if x > 0 else '📉'
        )
        
        tablo_df.insert(0, '#', range(1, len(tablo_df) + 1))
        
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
            height=400
        )
    
    with col2:
        # Özet istatistikler
        st.markdown("""
        <div style="background: white; border-radius: 15px; padding: 1.5rem; box-shadow: 0 5px 20px rgba(0,0,0,0.05);">
            <h3 style="color: #2D3748; margin-top: 0;">📊 Özet İstatistikler</h3>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(sicramalar)}</div>
            <div class="metric-label">Toplam Sıçrama</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            poz_say = len(sicramalar[sicramalar['Yuzde_Degisim'] > 0])
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value" style="color: #48BB78;">{poz_say}</div>
                <div class="metric-label">Pozitif</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            neg_say = len(sicramalar[sicramalar['Yuzde_Degisim'] < 0])
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value" style="color: #F56565;">{neg_say}</div>
                <div class="metric-label">Negatif</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">%{sicramalar['Yuzde_Degisim'].mean():+.2f}</div>
            <div class="metric-label">Ortalama Sıçrama</div>
        </div>
        
        <div class="metric-box">
            <div class="metric-value">%{sicramalar['Yuzde_Degisim'].max():+.2f}</div>
            <div class="metric-label">En Yüksek</div>
        </div>
        
        <div class="metric-box">
            <div class="metric-value">%{sicramalar['Yuzde_Degisim'].min():+.2f}</div>
            <div class="metric-label">En Düşük</div>
        </div>
        
        <div class="metric-box">
            <div class="metric-value">{sicramalar['Gun_Farki'].mean():.1f}</div>
            <div class="metric-label">Ort. Gün Farkı</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ========== ZAMAN BAZLI ANALİZLER ==========
    st.markdown('<h2 class="sub-header">📅 ZAMAN BAZLI ANALİZLER</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📆 Aylık Dağılım", 
        "📅 Yıllık Dağılım",
        "📊 Haftalık Pattern",
        "📈 Trend Analizi"
    ])
    
    with tab1:
        # Aylık sıçrama dağılımı
        aylik_df = sicramalar.groupby('Ay').agg({
            'Yuzde_Degisim': ['count', 'mean', 'max', 'min']
        }).round(2)
        aylik_df.columns = ['Sayı', 'Ortalama', 'Maks', 'Min']
        aylik_df['Ay_Adi'] = [calendar.month_name[i] for i in range(1, 13)]
        aylik_df = aylik_df.reset_index()
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig_ay = px.bar(
                aylik_df, x='Ay_Adi', y='Sayı',
                title='Aylara Göre Sıçrama Sayıları',
                color='Sayı',
                color_continuous_scale='Viridis',
                labels={'Sayı': 'Sıçrama Sayısı', 'Ay_Adi': 'Ay'}
            )
            fig_ay.update_layout(height=400)
            st.plotly_chart(fig_ay, use_container_width=True)
        
        with col2:
            st.dataframe(
                aylik_df[['Ay_Adi', 'Sayı', 'Ortalama', 'Maks', 'Min']],
                column_config={
                    'Ay_Adi': 'Ay',
                    'Sayı': 'Sıçrama',
                    'Ortalama': 'Ort. %',
                    'Maks': 'Maks %',
                    'Min': 'Min %'
                },
                use_container_width=True
            )
    
    with tab2:
        # Yıllık sıçrama dağılımı
        yillik_df = sicramalar.groupby('Yil').agg({
            'Yuzde_Degisim': ['count', 'mean', 'max', 'min']
        }).round(2)
        yillik_df.columns = ['Sayı', 'Ortalama', 'Maks', 'Min']
        yillik_df = yillik_df.reset_index()
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig_yil = px.bar(
                yillik_df, x='Yil', y='Sayı',
                title='Yıllara Göre Sıçrama Sayıları',
                color='Sayı',
                color_continuous_scale='Plasma',
                labels={'Sayı': 'Sıçrama Sayısı', 'Yil': 'Yıl'}
            )
            fig_yil.update_layout(height=400)
            st.plotly_chart(fig_yil, use_container_width=True)
        
        with col2:
            st.dataframe(
                yillik_df,
                column_config={
                    'Yil': 'Yıl',
                    'Sayı': 'Sıçrama',
                    'Ortalama': 'Ort. %',
                    'Maks': 'Maks %',
                    'Min': 'Min %'
                },
                use_container_width=True
            )
    
    with tab3:
        # Haftalık pattern
        gun_sirasi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        gun_adlari_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        
        haftalik_df = sicramalar.groupby('Gun_Adi').size().reindex(gun_sirasi).reset_index()
        haftalik_df.columns = ['Gün', 'Sayı']
        haftalik_df['Gün_TR'] = gun_adlari_tr
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig_gun = px.bar(
                haftalik_df, x='Gün_TR', y='Sayı',
                title='Haftanın Günlerine Göre Sıçrama Sayıları',
                color='Sayı',
                color_continuous_scale='Hot',
                labels={'Sayı': 'Sıçrama Sayısı', 'Gün_TR': 'Gün'}
            )
            fig_gun.update_layout(height=400)
            st.plotly_chart(fig_gun, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style="background: white; border-radius: 15px; padding: 1.5rem; box-shadow: 0 5px 20px rgba(0,0,0,0.05);">
                <h4 style="color: #2D3748; margin-top: 0;">📊 Günlük Pattern Analizi</h4>
            """, unsafe_allow_html=True)
            
            max_gun = haftalik_df.loc[haftalik_df['Sayı'].idxmax()]
            min_gun = haftalik_df.loc[haftalik_df['Sayı'].idxmin()]
            
            st.markdown(f"""
            <p><b>En çok sıçrama:</b> {max_gun['Gün_TR']} ({max_gun['Sayı']} sıçrama)</p>
            <p><b>En az sıçrama:</b> {min_gun['Gün_TR']} ({min_gun['Sayı']} sıçrama)</p>
            <p><b>Hafta içi ort:</b> {haftalik_df.iloc[:5]['Sayı'].mean():.1f} sıçrama/gün</p>
            <p><b>Hafta sonu ort:</b> {haftalik_df.iloc[5:]['Sayı'].mean():.1f} sıçrama/gün</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        # Trend analizi
        df['Kumulatif_Sicrama'] = df['Sicrama'].cumsum()
        
        fig_trend = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=('Kümülatif Sıçrama Sayısı', 'Aylık Ortalama Değişim')
        )
        
        fig_trend.add_trace(
            go.Scatter(
                x=df['Tarih'], y=df['Kumulatif_Sicrama'],
                mode='lines',
                name='Kümülatif Sıçrama',
                line=dict(color='#9F7AEA', width=2),
                fill='tozeroy'
            ),
            row=1, col=1
        )
        
        # Aylık ortalama
        aylik_ort = df.groupby('Yil_Ay')['Yuzde_Degisim'].mean().reset_index()
        aylik_ort['Tarih'] = pd.to_datetime(aylik_ort['Yil_Ay'] + '-01')
        
        fig_trend.add_trace(
            go.Bar(
                x=aylik_ort['Tarih'], y=aylik_ort['Yuzde_Degisim'],
                name='Aylık Ortalama',
                marker_color='#48BB78',
                marker_line_color='white'
            ),
            row=2, col=1
        )
        
        fig_trend.add_hline(y=0, line_dash="dash", line_color='gray', row=2, col=1)
        
        fig_trend.update_layout(height=500, showlegend=False)
        fig_trend.update_xaxes(title_text="", row=1, col=1)
        fig_trend.update_xaxes(title_text="Tarih", row=2, col=1)
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # ========== EN ŞİDDETLİ GÜNLER ==========
    st.markdown('<h2 class="sub-header">⚡ EN ŞİDDETLİ 10 SIÇRAMA</h2>', unsafe_allow_html=True)
    
    top_10 = sicramalar.head(10)
    
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_10.iterrows()):
        with cols[i % 5]:
            renk = '#48BB78' if row['Yuzde_Degisim'] > 0 else '#F56565'
            yon = '📈' if row['Yuzde_Degisim'] > 0 else '📉'
            
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 10px;
                padding: 1rem;
                margin: 0.5rem 0;
                border-left: 5px solid {renk};
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            ">
                <div style="font-size: 1.2rem; font-weight: 700;">#{i+1} {yon}</div>
                <div style="font-size: 1rem; color: #4A5568;">{row['Tarih'].strftime('%d.%m.%Y')}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {renk};">%{row['Yuzde_Degisim']:+.2f}</div>
                <div style="font-size: 0.9rem; color: #718096;">{row['Gun_Adi']}, {row['Ay_Adi']} {row['Yil']}</div>
                <div style="font-size: 0.9rem;">{row['Onceki_Kur']:.4f} → {row['Dolar_Kuru']:.4f} TL</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== İNDİRME BUTONU ==========
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        csv = sicramalar.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 TÜM SIÇRAMA VERİLERİNİ İNDİR (CSV)",
            data=csv,
            file_name=f'dolar_sicrama_analizi_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
            use_container_width=True
        )
    
    st.balloons()
    st.success(f"✅ Analiz tamamlandı! Toplam {len(df)} gün içinde {len(sicramalar)} sıçrama tespit edildi.")

else:
    # Hoş geldiniz ekranı
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://img.icons8.com/fluency/96/000000/line-chart.png", width=150)
        
        st.markdown("""
        <div style="text-align: center; background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
            <h2 style="color: #2D3748;">📊 Profesyonel Sıçrama Analizine Hoş Geldiniz</h2>
            <p style="color: #718096; font-size: 1.1rem; margin: 1.5rem 0;">
                Excel dosyanızı yükleyin, dolar kurundaki günlük sıçramaları 
                profesyonel grafiklerle keşfedin!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2rem;">
            <div style="background: #EBF4FF; padding: 1rem; border-radius: 10px;">
                <b>📈 4 Farklı Grafik</b><br>
                Trend, Değişim, Volatilite
            </div>
            <div style="background: #F0FFF4; padding: 1rem; border-radius: 10px;">
                <b>📅 Zaman Analizi</b><br>
                Aylık, Yıllık, Haftalık
            </div>
            <div style="background: #FFF5F5; padding: 1rem; border-radius: 10px;">
                <b>⚡ En Şiddetliler</b><br>
                Top 10 sıçrama kartları
            </div>
            <div style="background: #FFFAF0; padding: 1rem; border-radius: 10px;">
                <b>📊 Detaylı Tablo</b><br>
                Tüm sıçramalar listesi
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 1rem;">
    📊 Dolar Kuru Profesyonel Sıçrama Analizi | Günlük değişimleri keşfedin
</div>
""", unsafe_allow_html=True)
