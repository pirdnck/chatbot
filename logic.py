import streamlit as st
from fsm import LivestockFSM

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Berkah Ternak Smart Hub", 
    page_icon="🌾", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS: IMPORT MATERIAL ICONS & STYLING PREMIUM ---
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

<style>
    /* Mengatur tema warna latar belakang yang sejuk dan bersih */
    .stApp {
        background-color: #F9FAFB;
    }
    
    /* Font & Warna Teks Utama (Deep Forest Green) */
    h1, h2, h3 {
        color: #1B332C !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    p, span, label {
        color: #4A5568 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Tombol Utama Hijau Minimalis */
    .stButton>button {
        border-radius: 8px !important;
        background-color: #1B332C !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif;
        width: 100%;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .stButton>button:hover {
        background-color: #2A4D43 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(27,51,44,0.15);
    }
    
    /* Tombol Reset (Sekunder) */
    div[data-testid="stMarkdownContainer"] + div .stButton>button[kind="secondary"] {
        background-color: #EDF2F7 !important;
        color: #4A5568 !important;
    }

    /* Desain Grid Card Produk Baru dengan Vektor Ikon */
    .product-box {
        background-color: #FFFFFF;
        padding: 24px 16px;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        margin-bottom: 15px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .product-box:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-color: #CBD5E1;
    }
    
    /* Pengaturan Style Ikon Vektor */
    .custom-icon {
        font-family: 'Material Icons Round';
        font-size: 40px;
        color: #2E5A44; /* Warna hijau ikon ikonik */
        background-color: #F0F7F4;
        padding: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-bottom: 12px;
    }
    
    .product-title {
        font-size: 18px;
        font-weight: 700;
        color: #1B332C;
        margin-bottom: 4px;
    }
    .product-price {
        font-size: 16px;
        color: #2E5A44;
        font-weight: 700;
        margin-bottom: 12px;
    }

    /* Badge Status Logika Otomata */
    .fsm-status {
        display: inline-block;
        background-color: #EDF7F2;
        color: #1B332C;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #C6E4D3;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MAP STRUKTUR IKON KUSTOM UNTUK ETALASE ---
# Kita memetakan kata kunci produk ke nama ikon resmi di Google Material Icons
icon_mapping = {
    "susu": "local_cafe",       # Representasi segelas susu/minuman segar
    "telur": "egg",             # Ikon telur murni
    "daging": "set_meal",       # Komponen daging/makanan segar
    "madu": "恵み" or "hive"    # Jika hive tidak keluar, gunakan 'eco' atau 'local_honeypot'
}
# Cadangan ikon yang aman dan pasti ter-render di semua OS:
safe_icons = {
    "susu": "opacity",          # Tetesan cairan murni
    "telur": "egg",             # Bentuk telur
    "daging": "restaurant",     # Garpu & Pisau kuliner daging
    "madu": "local_florist"     # Nektar bunga alami
}

# --- 4. INISIALISASI SESSION STATE ---
if 'bot' not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()  
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# --- 5. TOP BANNER ---
st.markdown("<h1 style='text-align: center; margin-top: 10px;'>🌾 Berkah Ternak Smart Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 15px; color: #6B7280; margin-bottom: 35px;'>Platform belanja hasil peternakan lokal dengan asisten AI berbasis otomata</p>", unsafe_allow_html=True)

# --- 6. TATA LETAK UTAMA (2 KOLOM SEIMBANG) ---
col_menu, col_interaction = st.columns([11, 9], gap="large")

# ==========================================
# KOLOM KIRI: ETALASE DENGAN IKON VEKTOR (GRID)
# ==========================================
with col_menu:
    st.markdown("### 🛒 Produk Pilihan Langsung dari Kandang")
    st.write("Klik produk untuk langsung dimasukkan ke dalam rincian nota.")
    st.write("")
    
    menu_items = st.session_state.bot.nlp.menu_data
    keys = list(menu_items.keys())
    
    for i in range(0, len(keys), 2):
        row_cols = st.columns(2)
        
        # Grid Item Kiri
        with row_cols[0]:
            k1 = keys[i]
            d1 = menu_items[k1]
            icon1 = safe_icons.get(k1, "shopping_basket")
            
            st.markdown(f"""
            <div class="product-box">
                <div class="custom-icon"><span class="material-icons-round" style="font-size:36px; vertical-align:middle;">{icon1}</span></div>
                <div class="product-title">{k1.capitalize()}</div>
                <div style="font-size: 13px; color: #6B7280; margin-bottom: 8px;">{d1['desc']}</div>
                <div class="product-price">Rp {d1['price']:,}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Pesan {k1.capitalize()}", key=f"btn_{k1}"):
                st.session_state.history.append({"role": "user", "content": f"Beli 1 {k1}"})
                st.session_state.bot.step(f"pesan 1 {k1}")
                st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                st.rerun()
                
        # Grid Item Kanan
        if i + 1 < len(keys):
            with row_cols[1]:
                k2 = keys[i+1]
                d2 = menu_items[k2]
                icon2 = safe_icons.get(k2, "shopping_basket")
                
                st.markdown(f"""
                <div class="product-box">
                    <div class="custom-icon"><span class="material-icons-round" style="font-size:36px; vertical-align:middle;">{icon2}</span></div>
                    <div class="product-title">{k2.capitalize()}</div>
                    <div style="font-size: 13px; color: #6B7280; margin-bottom: 8px;">{d2['desc']}</div>
                    <div class="product-price">Rp {d2['price']:,}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Pesan {k2.capitalize()}", key=f"btn_{k2}"):
                    st.session_state.history.append({"role": "user", "content": f"Beli 1 {k2}"})
                    st.session_state.bot.step(f"pesan 1 {k2}")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
        st.write("")

# ==========================================
# KOLOM KANAN: CHATBOT INTERAKTIF & NOTA BELANJA
# ==========================================
with col_interaction:
    st.markdown("### 💬 Konsultasi & Pemesanan")
    
    # Box Obrolan Chatbot
    chat_container = st.container(height=300)
    with chat_container:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Deteksi Input Chat Toko Kuliah
    if prompt := st.chat_input("Ketik pesan di sini... (cth: 'beli 2 telur', 'selesai')"):
        st.session_state.history.append({"role": "user", "content": prompt})
        st.session_state.bot.step(prompt)
        st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
        st.rerun()
        
    st.write("")
    
    # Ringkasan Nota Belanja Terintegrasi Dinamis
    with st.container(border=True):
        st.markdown("📋 **Rincian Ringkasan Nota**")
        
        if st.session_state.bot.cart:
            for item in st.session_state.bot.cart:
                subtotal = item['price'] * item['qty']
                # Mengambil simbol penanda untuk list nota belanja yang seragam
                st.markdown(f"🔹 **{item['item'].capitalize()}** ({item['qty']}x) — `Rp {subtotal:,}`")
            
            st.divider()
            total_tagihan = st.session_state.bot.calculate_total()
            st.metric(label="Total Tagihan Belanja", value=f"Rp {total_tagihan:,}")
            
            # Mengubah Aksi Tombol Cepat Menyesuaikan Alur Berjalan State FSM
            current_state = st.session_state.bot.state.name
            if current_state == "ORDERING":
                if st.button("🚀 Selesai & Ajukan Pesanan", key="action_checkout"):
                    st.session_state.history.append({"role": "user", "content": "Selesai"})
                    st.session_state.bot.step("checkout")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
            elif current_state == "CONFIRMATION":
                if st.button("💳 Konfirmasi & Bayar Sekarang", key="action_pay"):
                    st.session_state.history.append({"role": "user", "content": "Ya"})
                    st.session_state.bot.step("ya")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
        else:
            st.caption("Belum ada produk yang Anda pilih saat ini.")
            
        # Pelaporan Komponen State untuk Kebutuhan Demo Dosen
        state_sekarang = st.session_state.bot.state.name
        st.markdown(f"""
        <div style='text-align: right;'>
            <span class='fsm-status'>⚙️ Current State: {state_sekarang}</span>
        </div>
        """, unsafe_allow_html=True)

    # Tombol Refresh Sesi Aplikasi Keseluruhan
    if st.button("🔄 Bersihkan Riwayat", key="global_reset", type="secondary"):
        st.session_state.clear()
        st.rerun()