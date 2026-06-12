import streamlit as st
from fsm import LivestockFSM

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Berkah Ternak Hub - Modern Agribusiness", 
    page_icon="🚜", 
    layout="wide"
)

# --- 2. CUSTOM STYLING (CSS) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f3f7f0 0%, #e9f1e4 50%, #dfebd5 100%);
        background-attachment: fixed;
    }
    .main-title {
        color: #1b381b;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #4a613c;
        text-align: center;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 30px;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        color: #274e13 !important;
        font-weight: bold;
    }
    .status-box {
        background-color: rgba(255, 255, 255, 0.6);
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #4a613c;
        margin-bottom: 15px;
    }
    .receipt-box {
        background-color: #ffffff;
        border: 1px dashed #99a78f;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', Courier, monospace;
        margin-bottom: 15px;
        color: #222222;
    }
    div[data-testid="stContainer"] {
        background-color: rgba(255, 255, 255, 0.75);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .item-title { font-size: 18px; font-weight: bold; color: #222222; margin-bottom: 0px; }
    .item-caption { font-size: 13px; color: #666666; }
    .item-price { font-size: 16px; font-weight: bold; color: #222222; text-align: right; }
    .qty-display { font-size: 18px; font-weight: bold; text-align: center; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALIZATION SESSION STATE ---
if 'bot' not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()  
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# --- 4. HEADER UTAMA ---
st.markdown("<h1 class='main-title'>🚜 BERKAH TERNAK SMART HUB</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Platform Digital Komoditas Hasil Ternak Segar & Higienis</p>", unsafe_allow_html=True)

# --- 5. GRID LAYOUT UTAMA ---
col_meta, col_katalog, col_chatbox = st.columns([4, 9, 9], gap="medium")

# =========================================================
# === KOLOM 1 (KIRI): UTILITY & STATUS PETERNAKAN ===
# =========================================================
with col_meta:
    st.markdown("### 🌾 Info Peternakan")
    with st.container(border=True):
        st.markdown("**🏡 Lokasi:** Kandang Berkah, Secang")
        st.markdown("**⏱️ Jam Ambil:** 06:00 - 17:00 WIB")
        st.markdown("**🛡️ Jaminan:** 100% Organik & Segar")
    
    st.write("")
    st.markdown("### ⚙️ Mesin Sistem (FSM)")
    with st.container(border=True):
        st.markdown(
            f"<div class='status-box'>State Aktif:<br><strong>{st.session_state.bot.state.name}</strong></div>", 
            unsafe_allow_html=True
        )
        if st.button("🔄 Reset Total Sistem", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

# =========================================================
# === KOLOM 2 (TENGAH): KATALOG DIGITAL INTERAKTIF ===
# =========================================================
with col_katalog:
    st.markdown("### 🥩 Produk Unggulan Hari Ini")
    st.caption("Pilih produk segar di bawah ini untuk ditambahkan langsung ke dalam keranjang belanja.")
    
    menu_items = st.session_state.bot.nlp.menu_data
    sub_cols = st.columns(2)
    
    for index, (key, data) in enumerate(menu_items.items()):
        with sub_cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"#### {data['emoji']} {key.capitalize()}")
                st.markdown(f"*{data['desc']}*")
                st.metric(label="Harga per Satuan", value=f"Rp {data['price']:,}")
                
                is_disabled = st.session_state.bot.state.name in ["CONFIRMATION", "PAYMENT"]
                if st.button(f"🛒 Ambil {key.capitalize()}", key=f"shop_{key}", use_container_width=True, disabled=is_disabled):
                    st.session_state.history.append({"role": "user", "content": f"Menambahkan 1 {data['emoji']} {key.capitalize()} via katalog"})
                    st.session_state.bot.step(f"pesan 1 {key}")
                    st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                    st.rerun()

# =========================================================
# === KOLOM 3 (KANAN): ASISTEN VIRTUAL & RINGKASAN POS ===
# =========================================================
with col_chatbox:
    tab_bot_room, tab_nota_final = st.tabs(["💬 Asisten Virtual", "📜 Nota Keluar & Riwayat"])
    
    # --- SUB TAB 1: CHAT ROOM & RINGKASAN BELANJA AKTIF ---
    with tab_bot_room:
        if st.session_state.bot.cart:
            st.markdown("<p style='font-size: 14px; font-weight: bold; color: #555555; letter-spacing: 0.5px;'>RINGKASAN BELANJA</p>", unsafe_allow_html=True)
            
            with st.container(border=True):
                total_tagihan = 0
                for i, item in enumerate(st.session_state.bot.cart):
                    subtotal = item['price'] * item['qty']
                    total_tagihan += subtotal
                    
                    c_info, c_min, c_qty, c_plus, c_sub = st.columns([7, 2, 2, 2, 5])
                    with c_info:
                        st.markdown(f"<p class='item-title'>{item['emoji']} {item['item'].capitalize()}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='item-caption'>Rp {item['price']:,} / satuan</p>", unsafe_allow_html=True)
                    
                    with c_min:
                        if st.button("−", key=f"minus_{item['item']}_{i}", use_container_width=True):
                            st.session_state.bot.step(f"kurangi 1 {item['item']}")
                            st.rerun()
                    with c_qty:
                        st.markdown(f"<p class='qty-display'>{item['qty']}</p>", unsafe_allow_html=True)
                    with c_plus:
                        if st.button("＋", key=f"plus_{item['item']}_{i}", use_container_width=True):
                            st.session_state.bot.step(f"pesan 1 {item['item']}")
                            st.rerun()
                    with c_sub:
                        st.markdown(f"<p class='item-price'>Rp {subtotal:,}</p>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_{item['item']}_{i}", use_container_width=True):
                            st.session_state.bot.step(f"kurangi {item['qty']} {item['item']}")
                            st.rerun()
                st.divider()
                
                c_total_label, c_total_val = st.columns([12, 6])
                with c_total_label:
                    st.markdown("#### Total Belanja")
                with c_total_val:
                    st.markdown(f"<h4 style='text-align: right; color: #274e13;'>Rp {total_tagihan:,}</h4>", unsafe_allow_html=True)
            
            if st.button("🚀 Selesai & Checkout", use_container_width=True, type="primary"):
                st.session_state.history.append({"role": "user", "content": "checkout"})
                st.session_state.bot.step("checkout")
                st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
                st.rerun()

        # Area Obrolan Chat History
        box_obrolan = st.container(height=300)
        with box_obrolan:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
        if prompt := st.chat_input("Ketik pesanan baru atau ketik 'bayar'..."):
            st.session_state.history.append({"role": "user", "content": prompt})
            st.session_state.bot.step(prompt)
            st.session_state.history.append({"role": "assistant", "content": st.session_state.bot.get_response()})
            st.rerun()

    # --- SUB TAB 2: TEMPAT NOTA RESMI KELUAR ---
    with tab_nota_final:
        st.markdown("#### 📄 Dokumen Nota Resmi (Sukses Dibayar)")
        
        # Mengambil langsung dari array invoice_logs yang disimpan aman di dalam FSM
        if st.session_state.bot.invoice_logs:
            for nota in reversed(st.session_state.bot.invoice_logs):
                st.markdown(f"""
                <div class='receipt-box'>
                    <strong>BERKAH TERNAK HUB RECEIPT</strong><br>
                    --------------------------------<br>
                    No. Nota : {nota['id']}<br>
                    Waktu    : {nota['waktu']}<br>
                    --------------------------------<br>
                    {"<br>".join([f"{idx+1}. {item['item'].upper()} ({item['qty']}x) = Rp {item['price']*item['qty']:,}" for idx, item in enumerate(nota['items'])])}<br>
                    --------------------------------<br>
                    <strong>TOTAL NETT: Rp {nota['total']:,}</strong><br>
                    ================================<br>
                    <span style='font-size:11px;'>Status: LUNAS & SAH</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada nota keluar. Selesaikan transaksi hingga pembayaran sukses untuk mencetak nota.")