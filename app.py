import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import calendar

# Sayfa yapılandırması
st.set_page_config(
    page_title="Dolar Kuru Günlük Sıçrama Analizi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Profesyonel CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        border: 1px solid #e2e8f0;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    .stat-unit {
        font-size: 0.9rem;
        color: #a0aec0;
    }
    
    .positive {
        color: #48bb78;
        font-weight: 600;
    }
    
    .negative {
        color: #f56565;
        font-weight: 600;
    }
    
    .info-box {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .metric-badge {
        background: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .jump-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid;
        transition: transform 0.2s;
    }
    
    .jump-card:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<div class="main-title">📈 DOLAR KURU GÜNLÜK SIÇRAMA ANALİZİ</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ ANALİZ PANELİ")
    st.markdown("---")
    
    # Dosya yükleme
    uploaded_file = st.file_uploader(
        "📂 Excel dosyası yükleyin",
        type=['xlsx', 'xls'],
        help="İlk sütun: Tarih, İkinci sütun: Dolar Kuru"
    )
    
    if uploaded_file:
        st.success("✅ Dosya yüklendi!")
        st.markdown("---")
        
        # Analiz parametreleri
        st.markdown("### 🎯 SIÇRAMA PARAMETRELERİ")
        
        esik = st.slider(
            "Eşik değeri (%)",
            min_value=0.5, max_value=10.0, value=2.0, step=0.5,
            help="Bu değerin üzerindeki günlük değişimler sıçrama kabul edilir"
        )
        
        # Gösterilecek sıçrama sayısı
        gosterim = st.selectbox(
            "Gösterilecek en büyük sıçrama sayısı",
            options=[10, 20, 30, 40, 50],
            index=2,
            help="En büyük kaç sıçrama işaretlensin?"
        )
        
        # Sıçrama yönü
        yon = st.radio(
            "Sıçrama yönü",
            options=["Tümü", "Sadece pozitif 📈", "Sadece negatif 📉"],
            horizontal=True
        )
        
        # Grafik tipi
        st.markdown("### 📊 GRAFİK TİPİ")
        grafik_tipi = st.selectbox(
            "Grafik görünümü",
            options=["Line + Nokta", "Sadece Line", "Sadece Noktalar"]
        )
        
        analiz_btn = st.button(
            "🚀 ANALİZİ ÇALIŞTIR",
            type="primary",
            use_container_width=True
        )

# Ana içerik
if uploaded_file and analiz_btn:
    
    with st.spinner("📊 Günlük sıçramalar analiz ediliyor..."):
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
            
            # NaN değerleri temizle
            df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
            df['Dolar_Kuru'] = pd.to_numeric(df['Dolar_Kuru'], errors='coerce')
            
            # NaN değerleri olan satırları temizle
            initial_len = len(df)
            df = df.dropna().sort_values('Tarih').reset_index(drop=True)
            cleaned_len = len(df)
            
            # Günlük değişim hesapla (bir önceki veri olan güne göre)
            df['Onceki_Kur'] = df['Dolar_Kuru'].shift(1)
            df['Onceki_Tarih'] = df['Tarih'].shift(1)
            df['Gun_Farki'] = (df['Tarih'] - df['Onceki_Tarih']).dt.days
            df['Yuzde_Degisim'] = (df['Dolar_Kuru'] / df['Onceki_Kur'] - 1) * 100
            df['TL_Degisim'] = df['Dolar_Kuru'] - df['Onceki_Kur']
            
            # İlk satırı temizle (NaN)
            df = df.dropna().reset_index(drop=True)
            
            # Günlük veriler için ek bilgiler
            df['Yil'] = df['Tarih'].dt.year
            df['Ay'] = df['Tarih'].dt.month
            df['Gun'] = df['Tarih'].dt.day
            df['Ay_Adi'] = df['Tarih'].dt.strftime('%B')
            df['Gun_Adi'] = df['Tarih'].dt.strftime('%A')
            df['Abs_Degisim'] = abs(df['Yuzde_Degisim'])
            
            # Sıçrama tespiti
            df['Sicrama'] = df['Abs_Degisim'] >= esik
            
            # Yön filtresine göre sıçramaları seç
            if yon == "Sadece pozitif 📈":
                sicramalar = df[df['Yuzde_Degisim'] >= esik].copy()
            elif yon == "Sadece negatif 📉":
                sicramalar = df[df['Yuzde_Degisim'] <= -esik].copy()
            else:
                sicramalar = df[df['Sicrama']].copy()
            
            # En büyük sıçramaları sırala
            sicramalar = sicramalar.sort_values('Abs_Degisim', ascending=False)
            top_sicramalar = sicramalar.head(gosterim)
            
            # İstatistikler
            poz_say = len(df[df['Yuzde_Degisim'] > 0])
            neg_say = len(df[df['Yuzde_Degisim'] < 0])
            poz_sicra = len(sicramalar[sicramalar['Yuzde_Degisim'] > 0])
            neg_sicra = len(sicramalar[sicramalar['Yuzde_Degisim'] < 0])
            
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            st.stop()
    
    # Bilgi mesajı
    if initial_len > cleaned_len:
        st.info(f"📌 {initial_len - cleaned_len} adet NaN (boş) değer temizlendi.")
    
    # İstatistik kartları
    st.markdown('<div class="section-title">📊 GÜNLÜK İSTATİSTİKLER</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Toplam Gün</div>
            <div class="stat-value">{len(df):,}</div>
            <div class="stat-unit">işlem günü</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Ort. Günlük Değişim</div>
            <div class="stat-value">%{df['Yuzde_Degisim'].mean():.2f}</div>
            <div class="stat-unit">±%{df['Yuzde_Degisim'].std():.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Pozitif/Negatif Gün</div>
            <div class="stat-value"><span class="positive">{poz_say}</span> / <span class="negative">{neg_say}</span></div>
            <div class="stat-unit">gün</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Toplam Sıçrama</div>
            <div class="stat-value">{len(sicramalar)}</div>
            <div class="stat-unit">>{esik}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Sıçrama Oranı</div>
            <div class="stat-value">%{len(sicramalar)/len(df)*100:.1f}</div>
            <div class="stat-unit">günlerin</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ANA GRAFİK - LINE GRAFİK
    st.markdown('<div class="section-title">📈 GÜNLÜK DOLAR KURU VE SIÇRAMALAR</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    # Ana line grafik
    fig.add_trace(go.Scatter(
        x=df['Tarih'],
        y=df['Dolar_Kuru'],
        mode='lines',
        name='Dolar Kuru',
        line=dict(color='#4299E1', width=2),
        hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Dolar Kuru: %{y:.4f} TL<extra></extra>'
    ))
    
    # En büyük sıçramaları işaretle
    poz_top = top_sicramalar[top_sicramalar['Yuzde_Degisim'] > 0]
    neg_top = top_sicramalar[top_sicramalar['Yuzde_Degisim'] < 0]
    
    if len(poz_top) > 0:
        fig.add_trace(go.Scatter(
            x=poz_top['Tarih'],
            y=poz_top['Dolar_Kuru'],
            mode='markers',
            name=f'Pozitif Sıçrama (Top {len(poz_top)})',
            marker=dict(
                symbol='circle',
                size=poz_top['Abs_Degisim']*3,
                color='#48BB78',
                line=dict(color='white', width=1)
            ),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: +%{customdata:.2f}%<extra></extra>',
            customdata=poz_top['Yuzde_Degisim']
        ))
    
    if len(neg_top) > 0:
        fig.add_trace(go.Scatter(
            x=neg_top['Tarih'],
            y=neg_top['Dolar_Kuru'],
            mode='markers',
            name=f'Negatif Sıçrama (Top {len(neg_top)})',
            marker=dict(
                symbol='circle',
                size=neg_top['Abs_Degisim']*3,
                color='#F56565',
                line=dict(color='white', width=1)
            ),
            hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Kur: %{y:.4f} TL<br>Değişim: %{customdata:.2f}%<extra></extra>',
            customdata=neg_top['Yuzde_Degisim']
        ))
    
    # Layout düzenlemeleri
    fig.update_layout(
        title=dict(
            text=f'DOLAR KURU - EN BÜYÜK {gosterim} GÜNLÜK SIÇRAMA (Eşik: %{esik})',
            font=dict(size=16, weight=600)
        ),
        xaxis=dict(
            title='Tarih',
            tickformat='%Y',
            gridcolor='#E2E8F0'
        ),
        yaxis=dict(
            title='Dolar Kuru (TL)',
            gridcolor='#E2E8F0'
        ),
        hovermode='x unified',
        template='plotly_white',
        height=600,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # GÜNLÜK DEĞİŞİM GRAFİĞİ
    st.markdown('<div class="section-title">📊 GÜNLÜK YÜZDE DEĞİŞİMLER</div>', unsafe_allow_html=True)
    
    fig2 = go.Figure()
    
    # Tüm değişimler (ince çizgi)
    fig2.add_trace(go.Scatter(
        x=df['Tarih'],
        y=df['Yuzde_Degisim'],
        mode='lines',
        name='Günlük Değişim',
        line=dict(color='#CBD5E0', width=1),
        opacity=0.7,
        hovertemplate='<b>%{x|%d.%m.%Y}</b><br>Değişim: %{y:.2f}%<extra></extra>'
    ))
    
    # En büyük sıçramalar
    if len(poz_top) > 0:
        fig2.add_trace(go.Scatter(
            x=poz_top['Tarih'],
            y=poz_top['Yuzde_Degisim'],
            mode='markers',
            name=f'Pozitif Sıçrama',
            marker=dict(
                size=10,
                color='#48BB78',
                line=dict(color='white', width=1)
            ),
            showlegend=False
        ))
    
    if len(neg_top) > 0:
        fig2.add_trace(go.Scatter(
            x=neg_top['Tarih'],
            y=neg_top['Yuzde_Degisim'],
            mode='markers',
            name=f'Negatif Sıçrama',
            marker=dict(
                size=10,
                color='#F56565',
                line=dict(color='white', width=1)
            ),
            showlegend=False
        ))
    
    # Eşik çizgileri
    fig2.add_hline(
        y=esik,
        line_dash='dash',
        line_color='#48BB78',
        annotation_text=f'+{esik}%',
        annotation_position='top left'
    )
    fig2.add_hline(
        y=-esik,
        line_dash='dash',
        line_color='#F56565',
        annotation_text=f'-{esik}%',
        annotation_position='bottom left'
    )
    fig2.add_hline(y=0, line_color='black', line_width=0.5)
    
    fig2.update_layout(
        title=f'GÜNLÜK YÜZDE DEĞİŞİMLER VE {esik}% EŞİĞİ',
        xaxis=dict(title='Tarih', tickformat='%Y'),
        yaxis=dict(title='Değişim (%)', gridcolor='#E2E8F0'),
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # EN BÜYÜK SIÇRAMALAR TABLOSU
    st.markdown(f'<div class="section-title">🏆 EN BÜYÜK {gosterim} GÜNLÜK SIÇRAMA</div>', unsafe_allow_html=True)
    
    # Tablo için veri hazırlama
    tablo_df = top_sicramalar[[
        'Tarih', 'Gun', 'Ay_Adi', 'Yil', 'Gun_Adi',
        'Dolar_Kuru', 'Onceki_Kur', 'Yuzde_Degisim', 'TL_Degisim', 'Gun_Farki'
    ]].copy()
    
    tablo_df['Tarih'] = tablo_df['Tarih'].dt.strftime('%d.%m.%Y')
    tablo_df['Dolar_Kuru'] = tablo_df['Dolar_Kuru'].round(4)
    tablo_df['Onceki_Kur'] = tablo_df['Onceki_Kur'].round(4)
    tablo_df['Yuzde_Degisim'] = tablo_df['Yuzde_Degisim'].round(2)
    tablo_df['TL_Degisim'] = tablo_df['TL_Degisim'].round(4)
    
    tablo_df.insert(0, '#', range(1, len(tablo_df) + 1))
    
    # Renkli gösterim için
    def renklendir(val):
        if val > 0:
            return f'<span class="positive">%{val:+.2f}</span>'
        elif val < 0:
            return f'<span class="negative">%{val:+.2f}</span>'
        return f'%{val:.2f}'
    
    tablo_df['Değişim'] = tablo_df['Yuzde_Degisim'].apply(renklendir)
    
    st.dataframe(
        tablo_df[[
            '#', 'Tarih', 'Gun', 'Ay_Adi', 'Yil', 'Gun_Adi',
            'Dolar_Kuru', 'Onceki_Kur', 'Değişim', 'TL_Degisim', 'Gun_Farki'
        ]],
        column_config={
            '#': 'No',
            'Tarih': 'Tarih',
            'Gun': 'Gün',
            'Ay_Adi': 'Ay',
            'Yil': 'Yıl',
            'Gun_Adi': 'Gün Adı',
            'Dolar_Kuru': 'Yeni Kur (TL)',
            'Onceki_Kur': 'Önceki Kur',
            'Değişim': 'Değişim',
            'TL_Degisim': 'TL Değişim',
            'Gun_Farki': 'Gün Farkı'
        },
        use_container_width=True,
        height=500
    )
    
    # EN BÜYÜK 10 KART
    st.markdown('<div class="section-title">⚡ EN BÜYÜK 10 GÜNLÜK SIÇRAMA</div>', unsafe_allow_html=True)
    
    top_10 = top_sicramalar.head(10)
    
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_10.iterrows()):
        with cols[i % 5]:
            renk = '#48BB78' if row['Yuzde_Degisim'] > 0 else '#F56565'
            yon = '📈' if row['Yuzde_Degisim'] > 0 else '📉'
            
            st.markdown(f"""
            <div class="jump-card" style="border-left-color: {renk};">
                <div style="font-size: 1.2rem; font-weight: 700;">#{i+1} {yon}</div>
                <div style="color: #4a5568;">{row['Tarih'].strftime('%d.%m.%Y')}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {renk};">%{row['Yuzde_Degisim']:+.2f}</div>
                <div style="font-size: 0.9rem; color: #718096;">{row['Gun_Adi']}</div>
                <div style="font-size: 0.9rem;">{row['Onceki_Kur']:.4f} → {row['Dolar_Kuru']:.4f}</div>
                <div style="font-size: 0.8rem; color: #a0aec0;">{row['Gun_Farki']} gün sonra</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ZAMAN ANALİZLERİ
    st.markdown('<div class="section-title">📅 ZAMAN BAZLI ANALİZLER</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📆 Aylık Dağılım", "📊 Günlük Pattern", "📈 Yıllık Trend"])
    
    with tab1:
        # Aylık sıçrama dağılımı
        aylik_df = sicramalar.groupby('Ay').size().reset_index(name='Sayı')
        aylik_df['Ay_Adi'] = aylik_df['Ay'].apply(lambda x: calendar.month_abbr[x])
        
        fig_ay = px.bar(
            aylik_df,
            x='Ay_Adi',
            y='Sayı',
            title='Aylara Göre Günlük Sıçrama Sayıları',
            color='Sayı',
            color_continuous_scale='Viridis',
            labels={'Sayı': 'Sıçrama Sayısı', 'Ay_Adi': 'Ay'}
        )
        fig_ay.update_layout(height=400)
        st.plotly_chart(fig_ay, use_container_width=True)
    
    with tab2:
        # Haftanın günlerine göre dağılım
        gun_sirasi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        gun_adlari_tr = ['Pts', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
        
        haftalik_df = sicramalar.groupby('Gun_Adi').size().reindex(gun_sirasi).reset_index()
        haftalik_df.columns = ['Gun', 'Sayı']
        haftalik_df['Gun_TR'] = gun_adlari_tr
        haftalik_df = haftalik_df.fillna(0)
        
        fig_gun = px.bar(
            haftalik_df,
            x='Gun_TR',
            y='Sayı',
            title='Haftanın Günlerine Göre Sıçrama Sayıları',
            color='Sayı',
            color_continuous_scale='Plasma',
            labels={'Sayı': 'Sıçrama Sayısı', 'Gun_TR': 'Gün'}
        )
        fig_gun.update_layout(height=400)
        st.plotly_chart(fig_gun, use_container_width=True)
    
    with tab3:
        # Yıllık trend
        yillik_df = sicramalar.groupby('Yil').size().reset_index(name='Sayı')
        
        fig_yil = px.line(
            yillik_df,
            x='Yil',
            y='Sayı',
            markers=True,
            title='Yıllara Göre Günlük Sıçrama Sayıları',
            labels={'Sayı': 'Sıçrama Sayısı', 'Yil': 'Yıl'}
        )
        fig_yil.update_layout(height=400)
        st.plotly_chart(fig_yil, use_container_width=True)
    
    # İndirme butonu
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        csv = top_sicramalar.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 EN BÜYÜK {gosterim} SIÇRAMAYI İNDİR (CSV)",
            data=csv,
            file_name=f'dolar_top_{gosterim}_sicrama.csv',
            mime='text/csv',
            use_container_width=True
        )
    
    st.balloons()
    st.success(f"✅ Analiz tamamlandı! {len(df)} günlük veri içinde {len(sicramalar)} sıçrama tespit edildi.")

else:
    # Hoş geldiniz ekranı
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <img src="https://img.icons8.com/fluency/96/000000/line-chart.png" style="width: 120px;">
            <h2 style="color: #2d3748; margin-top: 1rem;">Günlük Sıçrama Analizine Hoş Geldiniz</h2>
            <p style="color: #718096; font-size: 1.1rem; margin: 1.5rem 0;">
                Excel dosyanızı yükleyin, dolar kurundaki en büyük günlük sıçramaları 
                profesyonel grafiklerle keşfedin.
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 2rem 0;">
            <div style="background: #f7fafc; padding: 1.5rem; border-radius: 10px;">
                <h4 style="margin: 0 0 0.5rem 0;">📈 Line Grafik</h4>
                <p style="color: #718096; margin: 0;">Dolar kuru trendi üzerinde en büyük sıçramalar işaretlenir</p>
            </div>
            <div style="background: #f7fafc; padding: 1.5rem; border-radius: 10px;">
                <h4 style="margin: 0 0 0.5rem 0;">🎯 Ayarlanabilir</h4>
                <p style="color: #718096; margin: 0;">10,20,30,40,50 en büyük sıçrama seçeneği</p>
            </div>
            <div style="background: #f7fafc; padding: 1.5rem; border-radius: 10px;">
                <h4 style="margin: 0 0 0.5rem 0;">🧹 NaN Temizleme</h4>
                <p style="color: #718096; margin: 0;">Boş değerler otomatik temizlenir</p>
            </div>
            <div style="background: #f7fafc; padding: 1.5rem; border-radius: 10px;">
                <h4 style="margin: 0 0 0.5rem 0;">📊 Detaylı Tablo</h4>
                <p style="color: #718096; margin: 0;">Gün, ay, yıl, gün adı, değişim miktarı</p>
            </div>
        </div>
        
        <div style="background: #ebf8ff; padding: 1rem; border-radius: 10px; text-align: center;">
            <p style="color: #2c5282; margin: 0;">
                💡 İpucu: Farklı eşik değerleri ve sıçrama sayıları deneyin!
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #a0aec0; padding: 1rem;">
    Dolar Kuru Günlük Sıçrama Analizi v1.0 | NaN değerler temizlenir | Line grafik odaklı
</div>
""", unsafe_allow_html=True)
