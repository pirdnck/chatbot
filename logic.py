import streamlit as st
from fsm import LivestockFSM

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Berkah Ternak Hub", page_icon="🌾", layout="wide")

# --- 2. PREMIUM & CLEAN CSS STYLING ---
st.markdown("""
<style>
    /* Latar belakang hangat dan bersih (tidak monoton/kontras tajam) */
    .stApp {
        background-color: #FAF8F5;
    }
    /* Mengubah warna teks utama */
    h1, h2, h3, p {
        color: #2C4A3E !important;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Tombol Utama Estetik Hijau Sage */
    .stButton>button {
        border-radius: 6px;
        background-color: #2C4A3E;
        color: #FFFFFF;
        border: none;
        padding: 6px 16px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #3D6656;
        color: #FFFFFF;
        transform: translateY(-1px);
    }
    /* Card Produk Minimalis */
    .product-card {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #EAE7E2;
        margin-bottom: 12px;
    }
    /* Status Badge FSM */
    .state-badge {
        background-color: #E6EDE9;
        color: #2C4A3E;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. INisialisasi SESSION STATE ---
if 'bot' not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()  # Start FSM
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# --- 4. HEADER MINIMALIS ---
st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>🌾 Berkah Ternak Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 15px; color: #667A71; margin-bottom: 25px;'>Belanja Produk Peternakan Lokal dengan Asisten Pintar</p>", unsafe_allow_html=True)

# --- 5. TATA LETAK UTAMA (2 Kolom Bersih) ---
col_katalog, col_chat = st.columns([1, 1], gap="large")

# ==========================================
# === KOLOM KIRI: KATALOG BELANJA SIMPEL ===
# ==========================================
with col_katalog:
    st.markdown("### 🛒 Pilihan Produk Segar")
    st.caption("Klik tombol untuk menambahkan langsung ke keranjang belanja Anda.")
    st.write("")
    
    menu_items = st.session_state.bot.nlp.menu_data
    
    for key, data in menu_items.items():
        # Membungkus item ke dalam kontainer minimalis
        st.markdown(f"""
        <div class="product-card">
            <span style="font-size: 20px;">{data['emoji']}</span> <b>{key.capitalize()}</b> — <span style="color:#667A71;">{data['desc']}</span>
            <div style="font-size: 16px; font-weight: bold; margin-top: 5px; color: #2C4A3E;">Rp {data['price']:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tombol aksi tepat di bawah card produk
        if st.button(f"Tambah {key.capitalize()}", key=f"add_{key}"):
            st.session_state.history.append({"role": "user", "content": f"Beli 1 {key}"})
            st.session_state.bot.step(f"pesan 1 {key}")
            st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
            st.rerun()
        st.write("")

# ==========================================
# === KOLOM KANAN: CHAT ASISTEN & RINGKASAN ===
# ==========================================
with col_chat:
    st.markdown("### 💬 Interaksi Asisten")
    
    # Kotak Chat Ringan
    chat_box = st.container(height=300)
    with chat_box:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    if prompt := st.chat_input("Ketik di sini... (Contoh: 'pesan 2 susu', 'bayar')"):
        st.session_state.history.append({"role": "user", "content": prompt})
        st.session_state.bot.step(prompt)
        st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
        st.rerun()
        
    st.divider()
    
    # Ringkasan Status & Kontrol Cepat di Bagian Bawah Chat
    st.markdown("#### Rincian Belanja")
    total_tagihan = st.session_state.bot.calculate_total()
    
    if st.session_state.bot.cart:
        for item in st.session_state.bot.cart:
            st.markdown(f"- {item['emoji']} **{item['item'].capitalize()}** ({item['qty']}x) : Rp {item['price']*item['qty']:,}")
        st.markdown(f"**Total Akhir: Rp {total_tagihan:,}**")
        
        # Tombol pintas cerdas tergantung pada State saat ini
        if st.session_state.bot.state.name == "ORDERING":
            if st.button("🛍️ Selesai & Lanjut Checkout", use_container_width=True):
                st.session_state.history.append({"role": "user", "content": "Selesai belanja"})
                st.session_state.bot.step("checkout")
                st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                st.rerun()
        elif st.session_state.bot.state.name == "CONFIRMATION":
            if st.button("💳 Konfirmasi & Bayar Sekarang", use_container_width=True):
                st.session_state.history.append({"role": "user", "content": "Bayar"})
                st.session_state.bot.step("checkout")
                st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                st.rerun()
    else:
        st.info("Keranjang belanja masih kosong.")
        
    st.write("")
    # Informasi Indikator State Otomata yang minimalis
    st.markdown(f"Status Sistem FSM: <span class='state-badge'>{st.session_state.bot.state.name}</span>", unsafe_allow_html=True)
    
    if st.button("🔄 Bersihkan Sesi", type="secondary"):
        st.session_state.clear()
        st.rerun()