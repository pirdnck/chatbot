import streamlit as st
from fsm import LivestockFSM

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Berkah Ternak Hub v2", page_icon="🌾", layout="wide")

# --- 2. JALUR WARNA CUSTOM (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #F4F7F0; }
    h1, h2, h3 { color: #2E4A23 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button {
        border-radius: 8px; background-color: #2E4A23; color: white;
        transition: all 0.3s ease; border: none;
    }
    .stButton>button:hover { background-color: #426B34; transform: translateY(-2px); color: white; }
    .status-box {
        padding: 15px; border-radius: 10px; background-color: #E6EFE2;
        border-left: 5px solid #2E4A23; margin-bottom: 15px;
    }
    .badge-promo {
        background-color: #FCE8E6; color: #CC3333; padding: 4px 8px;
        border-radius: 20px; font-size: 11px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALIZATION SESSION STATE ---
if 'bot' not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()  
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# --- 4. SIDEBAR: MONITOR STATUS FSM (Bagus untuk Ujian/Demo Dosen!) ---
with st.sidebar:
    st.markdown("### 📊 Engine Dashboard")
    st.caption("Alur logika otomata (FSM) yang sedang berjalan di belakang sistem.")
    
    # Visual Tracking State
    current_state = st.session_state.bot.state.name
    st.markdown(f"<div class='status-box'><b>State Aktif Saat Ini:</b><br><code style='font-size:16px;'>{current_state}</code></div>", unsafe_allow_html=True)
    
    # Progress Bar Alur Belanja
    state_mapping = {"IDLE": 25, "ORDERING": 50, "CONFIRMATION": 75, "PAYMENT": 100}
    st.progress(state_mapping.get(current_state, 25))
    
    st.divider()
    st.markdown("### 💡 Tips Interaksi")
    st.info("Anda bisa memesan via tombol katalog di kanan atau mengetik langsung kalimat bebas (NLP Regex) di kolom chat.")
    
    if st.button("🔄 Reset & Mulai Ulang", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.rerun()

# --- 5. HEADER UTAMA ---
st.markdown("<h1 style='text-align: center;'>👨‍🌾 Berkah Ternak Smart Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #556B2F; font-size: 16px;'>Sistem Pintar Belanja Hasil Peternakan Lokal Berbasis Teori Bahasa & Otomata</p>", unsafe_allow_html=True)
st.divider()

# --- 6. LAYOUT UTAMA ---
col_katalog, col_chat = st.columns([11, 9], gap="large")

# ===============================================
# === KOLOM KIRI: KATALOG & PROMO INTERAKTIF ===
# ===============================================
with col_katalog:
    st.subheader("🥦 Produk Segar Langsung dari Kandang")
    
    # Grid Produk Eceran
    menu_items = st.session_state.bot.nlp.menu_data
    grid_cols = st.columns(2)
    for index, (key, data) in enumerate(menu_items.items()):
        with grid_cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"### {data['emoji']} {key.capitalize()}")
                st.caption(data['desc'])
                st.write(f"**Harga:** Rp {data['price']:,} / satuan")
                
                if st.button(f"🛒 Tambah {key.capitalize()}", key=f"btn_{key}", use_container_width=True):
                    st.session_state.history.append({"role": "user", "content": f"Beli 1 {key} via katalog"})
                    st.session_state.bot.step(f"pesan 1 {key}")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()

    st.write("")
    st.subheader("🛍️ Paket Hemat Spesial Hari Ini")
    
    # Grid Paket Bundle Promo
    bundle_items = st.session_state.bot.nlp.bundles
    grid_bundles = st.columns(2)
    for index, (b_name, b_info) in enumerate(bundle_items.items()):
        with grid_bundles[index % 2]:
            with st.container(border=True):
                st.markdown(f"### 📦 {b_name.upper()}")
                st.markdown(f"<span class='badge-promo'>{b_info['desc']}</span>", unsafe_allow_html=True)
                st.write(f"**Harga Paket:** Rp {b_info['price']:,}")
                
                if st.button(f"⚡ Ambil {b_name.capitalize()}", key=f"btn_{b_name}", use_container_width=True):
                    st.session_state.history.append({"role": "user", "content": f"Ambil {b_name}"})
                    st.session_state.bot.step(b_name)
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()

# ===============================================
# === KOLOM KANAN: CHATBOT & STRUK BELANJA ===
# ===============================================
with col_chat:
    tab_asisten, tab_keranjang = st.tabs(["💬 Chat Asisten Pintar", "🧺 Isi Keranjang Saya"])
    
    # --- SUB-TAB: CHAT ---
    with tab_asisten:
        chat_box = st.container(height=380)
        with chat_box:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
        if prompt := st.chat_input("Ketik pesan Anda di sini... (cth: 'pesan paket sarapan', 'bayar')"):
            st.session_state.history.append({"role": "user", "content": prompt})
            st.session_state.bot.step(prompt)
            st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
            st.rerun()

    # --- SUB-TAB: RINGKASAN KERANJANG/STRUK ---
    with tab_keranjang:
        st.markdown("### 📋 Nota Rincian Belanja")
        if st.session_state.bot.cart:
            for i, item in enumerate(st.session_state.bot.cart):
                sub = item['price'] * item['qty']
                st.markdown(f"**{i+1}. {item['emoji']} {item['item'].capitalize()}** x `{item['qty']}`")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; Subtotal: Rp {sub:,}")
            
            st.divider()
            
            # Tampilan Finansial Struk
            subtotal_akhir = st.session_state.bot.calculate_subtotal()
            diskon_akhir = st.session_state.bot.discount
            total_akhir = st.session_state.bot.calculate_total()
            
            st.text(f"Subtotal Produk : Rp {subtotal_akhir:,}")
            st.text(f"Potongan Kupon   : -Rp {diskon_akhir:,}")
            st.metric("Total Tagihan Bersih", f"Rp {total_akhir:,}")
            
            # Tombol shortcut aksi cepat untuk meningkatkan UX
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🧹 Kosongkan Keranjang", use_container_width=True, type="secondary"):
                    st.session_state.history.append({"role": "user", "content": "Kosongkan keranjang"})
                    st.session_state.bot.step("kosongkan")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
            with col_b2:
                if st.button("🚀 Checkout & Bayar", use_container_width=True):
                    st.session_state.history.append({"role": "user", "content": "Bayar"})
                    st.session_state.bot.step("bayar")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()
        else:
            st.info("Keranjang belanjaan Anda masih kosong. Pilih produk segar di menu kiri!")