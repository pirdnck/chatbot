import streamlit as st
from fsm import LivestockFSM

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Berkah Ternak Hub", page_icon="🚜", layout="wide")

# --- 2. CUSTOM STYLING (CSS) ---
# Membuat tampilan card, metrik, dan tombol jauh lebih modern
st.markdown("""
<style>
    .stApp {
        background-color: #f9fbf7;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #2e4a23;
        font-weight: bold;
    }
    .product-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e6ebd3;
        margin-bottom: 20px;
    }
    .badge {
        background-color: #eaf2dc;
        color: #3b5c28;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALIZATION SESSION STATE ---
if 'bot' not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()  # Start FSM
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# --- 4. HEADER UTAMA ---
st.markdown("<h1 style='text-align: center; color: #2e4a23;'>🚜 Berkah Ternak Smart Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7c65; font-size: 16px;'>Produk Segar dari Peternakan Lokal, Dipesan dengan Logika Pintar</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. LAYOUT UTAMA (Dashboard Belanja) ---
# Membagi layar menjadi 2 kolom besar: Katalog Produk (Kiri) dan Bot + Keranjang (Kanan)
col_katalog, col_sistem = st.columns([11, 9], gap="large")

# ==========================================
# === KOLOM KIRI: KATALOG PRODUK INTERAKTIF ===
# ==========================================
with col_katalog:
    st.subheader("🌱 Katalog Produk Segar")
    st.caption("Klik tombol 'Tambah ke Keranjang' untuk memesan secara instan.")
    
    menu_items = st.session_state.bot.nlp.menu_data
    
    # Membuat grid 2 kolom untuk card produk
    grid_cols = st.columns(2)
    
    for index, (key, data) in enumerate(menu_items.items()):
        with grid_cols[index % 2]:
            # Menggunakan HTML tiruan card dan container Streamlit ber-border
            with st.container(border=True):
                st.markdown(f"### {data['emoji']} {key.capitalize()}")
                st.markdown(f"<span class='badge'>{data['desc']}</span>", unsafe_allow_html=True)
                st.write("")
                
                # Menampilkan harga dengan format rapi
                st.metric(label="Harga Resmi", value=f"Rp {data['price']:,}")
                
                # Tombol interaktif untuk menambah produk langsung tanpa ngetik chat
                if st.button(f"➕ Tambah {key.capitalize()}", key=f"btn_{key}"):
                    # Simulasikan teks ke dalam sistem FSM bot
                    simulated_input = f"pesan 1 {key}"
                    st.session_state.history.append({"role": "user", "content": f"Beli 1 {key} lewat katalog"})
                    
                    st.session_state.bot.step(simulated_input)
                    bot_reply = st.session_state.bot.get_response()
                    
                    st.session_state.history.append({"role": "assistant", "content": bot_reply})
                    st.rerun()

# ==========================================
# === KOLOM KANAN: CHATBOT & UTILITY ===
# ==========================================
with col_sistem:
    # Menggunakan sub-tab untuk merapikan Chat Asisten dan Detail Struk/Keranjang
    tab_chat, tab_invoice = st.tabs(["💬 Asisten Virtual", "🛒 Detail Keranjang & Status"])
    
    # --- SUB-TAB: CHAT ASISTEN ---
    with tab_chat:
        chat_container = st.container(height=380)
        
        with chat_container:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
        if prompt := st.chat_input("Ketik di sini (cth: 'kurangi 1 telur', 'bayar')..."):
            st.session_state.history.append({"role": "user", "content": prompt})
            st.session_state.bot.step(prompt)
            bot_reply = st.session_state.bot.get_response()
            st.session_state.history.append({"role": "assistant", "content": bot_reply})
            st.rerun()

    # --- SUB-TAB: DETAIL INVOICE & KERANJANG ---
    with tab_invoice:
        st.markdown("### Ringkasan Belanja")
        
        if st.session_state.bot.cart:
            total = 0
            for i, item in enumerate(st.session_state.bot.cart):
                subtotal = item['price'] * item['qty']
                total += subtotal
                st.markdown(f"**{i+1}. {item['emoji']} {item['item'].capitalize()}**")
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp; `{item['qty']}` x Rp {item['price']:,} = **Rp {subtotal:,}**")
            
            st.divider()
            st.metric("Total Tagihan", f"Rp {total:,}")
            
            if st.button("🗑️ Kosongkan Semua", use_container_width=True):
                st.session_state.bot.cart = []
                st.session_state.bot.step("kosongkan") # sinkronkan ke bot
                st.rerun()
        else:
            st.info("Belum ada produk di dalam keranjang.")
            
        st.divider()
        
        # Informasi Status System FSM di bagian bawah
        col_status, col_reset = st.columns([1, 1])
        with col_status:
            st.markdown(f"**Status FSM:** `{st.session_state.bot.state.name}`")
        with col_reset:
            if st.button("🔄 Reset Bot", type="secondary", use_container_width=True):
                st.session_state.clear()
                st.rerun()