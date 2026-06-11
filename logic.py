import streamlit as st
from fsm import LivestockFSM

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Berkah Ternak Smart Hub", 
    page_icon="🌾", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS: MEROMBAK TOTAL TAMPILAN KAKU ---
st.markdown("""
<style>
    /* Mengatur latar belakang aplikasi yang bersih dan premium */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Font & Warna Teks Utama (Hijau Peternakan Modern) */
    h1, h2, h3 {
        color: #1E352F !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    p, span, label {
        color: #4A5568 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Transformasi Tombol Menjadi Modern & Elegan */
    .stButton>button {
        border-radius: 8px !important;
        background-color: #1E352F !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        background-color: #2D4F46 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Tombol Tipe Sekunder (Batal/Reset) */
    div[data-testid="stMarkdownContainer"] + div .stButton>button[kind="secondary"] {
        background-color: #EDF2F7 !important;
        color: #4A5568 !important;
    }

    /* Desain Grid Card Produk ala E-Commerce */
    .product-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        text-align: center;
    }
    .product-emoji {
        font-size: 32px;
        margin-bottom: 10px;
    }
    .product-title {
        font-size: 18px;
        font-weight: bold;
        color: #1E352F;
        margin-bottom: 5px;
    }
    .product-price {
        font-size: 16px;
        color: #2F855A;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Badge Status FSM yang Indah */
    .fsm-status {
        display: inline-block;
        background-color: #E6FFFA;
        color: #234E52;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid #B2F5EA;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. INISIALISASI SESSION STATE BOT ---
if 'bot' not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()  # Jalankan state IDLE awal
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# --- 4. BANNER TOP HEADER ---
st.markdown("<h1 style='text-align: center; margin-top: 10px;'>🌾 Berkah Ternak Smart Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 16px; color: #718096; margin-bottom: 30px;'>Belanja hasil peternakan segar langsung dari genggaman Anda</p>", unsafe_allow_html=True)

# --- 5. TATA LETAK UTAMA (2 KOLOM SEIMBANG) ---
col_menu, col_interaction = st.columns([11, 9], gap="large")

# ==========================================
# KOLOM KIRI: KATALOG PRODUK VISUAL (GRID 2x2)
# ==========================================
with col_menu:
    st.markdown("### 🧺 Etalase Produk Segar Hari Ini")
    st.write("Klik produk untuk langsung menambahkan ke keranjang belanja.")
    
    # Ambil data menu dari engine.py
    menu_items = st.session_state.bot.nlp.menu_data
    
    # Membuat susunan Grid 2 Kolom menggunakan sub-columns
    keys = list(menu_items.keys())
    for i in range(0, len(keys), 2):
        row_cols = st.columns(2)
        
        # Item Pertama dalam Baris
        with row_cols[0]:
            k1 = keys[i]
            d1 = menu_items[k1]
            st.markdown(f"""
            <div class="product-box">
                <div class="product-emoji">{d1['emoji']}</div>
                <div class="product-title">{k1.capitalize()}</div>
                <div style="font-size: 12px; color: #718096; margin-bottom: 8px;">{d1['desc']}</div>
                <div class="product-price">Rp {d1['price']:,}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Tambah {k1.capitalize()}", key=f"btn_{k1}"):
                st.session_state.history.append({"role": "user", "content": f"Beli 1 {k1}"})
                st.session_state.bot.step(f"pesan 1 {k1}")
                st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                st.rerun()
                
        # Item Kedua dalam Baris (jika ada)
        if i + 1 < len(keys):
            with row_cols[1]:
                k2 = keys[i+1]
                d2 = menu_items[k2]
                st.markdown(f"""
                <div class="product-box">
                    <div class="product-emoji">{d2['emoji']}</div>
                    <div class="product-title">{k2.capitalize()}</div>
                    <div style="font-size: 12px; color: #718096; margin-bottom: 8px;">{d2['desc']}</div>
                    <div class="product-price">Rp {d2['price']:,}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Tambah {k2.capitalize()}", key=f"btn_{k2}"):
                    st.session_state.history.append({"role": "user", "content": f"Beli 1 {k2}"})
                    st.session_state.bot.step(f"pesan 1 {k2}")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
        st.write("")

# ==========================================
# KOLOM KANAN: CHATBOT & RINGKASAN STRUK (INTEGRATED)
# ==========================================
with col_interaction:
    st.markdown("### 💬 Asisten Virtual & Nota")
    
    # Ruang Obrolan Chatbot (Kompak & Ringan)
    chat_container = st.container(height=320)
    with chat_container:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Input Kolom Chat Kuliah
    if prompt := st.chat_input("Ketik pesan Anda... (contoh: 'pesan 2 susu', 'bayar')"):
        st.session_state.history.append({"role": "user", "content": prompt})
        st.session_state.bot.step(prompt)
        st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
        st.rerun()
        
    st.write("")
    
    # Rincian Nota Belanja Langsung Tampil di Bawah Chat (Sangat Informatif)
    with st.container(border=True):
        st.markdown("📋 **Rincian Nota Belanja**")
        
        if st.session_state.bot.cart:
            for item in st.session_state.bot.cart:
                subtotal = item['price'] * item['qty']
                st.markdown(f"- {item['emoji']} **{item['item'].capitalize()}** ({item['qty']}x) — `Rp {subtotal:,}`")
            
            st.divider()
            total_tagihan = st.session_state.bot.calculate_total()
            st.metric(label="Total yang Harus Dibayar", value=f"Rp {total_tagihan:,}")
            
            # Tombol Dinamis Pintar Berdasarkan State Saat Ini
            current_state = st.session_state.bot.state.name
            if current_state == "ORDERING":
                if st.button("🚀 Selesai & Ajukan Checkout", key="action_checkout"):
                    st.session_state.history.append({"role": "user", "content": "Selesai"})
                    st.session_state.bot.step("bayar")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
            elif current_state == "CONFIRMATION":
                if st.button("💳 Konfirmasi & Bayar Sekarang", key="action_pay"):
                    st.session_state.history.append({"role": "user", "content": "Ya"})
                    st.session_state.bot.step("ya")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
        else:
            st.caption("Belum ada item di dalam keranjang belanja Anda.")
            
        # Info Tambahan untuk Keperluan Demonstrasi Akademik TBO
        state_sekarang = st.session_state.bot.state.name
        st.markdown(f"""
        <div style='text-align: right;'>
            <span class='fsm-status'>🤖 FSM State: {state_sekarang}</span>
        </div>
        """, unsafe_allow_html=True)

    # Tombol Reset Sistem di bagian paling bawah
    if st.button("🔄 Reset Sesi Belanja", key="global_reset", type="secondary"):
        st.session_state.clear()
        st.rerun()