import streamlit as st
from fsm import LivestockFSM

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Berkah Ternak",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 2. DESIGN SYSTEM ──────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>
:root {
    --bg:         #F5F2EC;
    --surface:    #FFFFFF;
    --border:     #E4DDD1;
    --ink:        #1C2B22;
    --ink-muted:  #6B7566;
    --accent:     #2E6E4E;
    --accent-lt:  #EBF5EF;
    --accent-dim: #C5E0D0;
    --danger:     #DC2626;
    --danger-lt:  #FEF2F2;
    --radius-sm:  10px;
    --radius-md:  16px;
    --radius-lg:  24px;
    --shadow-sm:  0 1px 4px rgba(0,0,0,.06);
    --shadow-md:  0 4px 16px rgba(0,0,0,.08);
}

.stApp { background-color: var(--bg) !important; }
.block-container { padding-top: 2rem !important; }

/* Typography */
.site-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(1.6rem, 4vw, 2.4rem);
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.5px;
    margin: 0;
    line-height: 1.2;
}
.site-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--ink-muted);
    margin-top: 4px;
}
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-muted);
    margin-bottom: 12px;
    display: block;
}

/* Product card */
.product-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px 16px 16px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.product-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
    border-color: var(--accent-dim);
}
.card-emoji {
    font-size: 2.4rem;
    background: var(--accent-lt);
    width: 60px; height: 60px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 12px;
}
.card-name  { font-family:'Sora',sans-serif; font-size:1rem; font-weight:700; color:var(--ink); margin-bottom:2px; }
.card-desc  { font-family:'Inter',sans-serif; font-size:0.78rem; color:var(--ink-muted); margin-bottom:10px; line-height:1.4; }
.card-price { font-family:'Inter',sans-serif; font-size:0.95rem; font-weight:600; color:var(--accent); margin-bottom:14px; }

/* Buttons */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--accent) !important;
    background: var(--accent-lt) !important;
    border: 1px solid var(--accent-dim) !important;
    border-radius: var(--radius-sm) !important;
    padding: 7px 12px !important;
    width: 100% !important;
    transition: background .15s ease, transform .12s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--accent-dim) !important;
    transform: translateY(-1px) !important;
}

/* Cart qty control buttons — compact, no full-width */
.qty-btn .stButton > button {
    width: 32px !important;
    height: 32px !important;
    min-width: unset !important;
    padding: 0 !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    line-height: 1 !important;
}
.qty-btn-minus .stButton > button {
    background: var(--danger-lt) !important;
    color: var(--danger) !important;
    border-color: #FECACA !important;
}
.qty-btn-minus .stButton > button:hover { background: #FECACA !important; }

.qty-btn-delete .stButton > button {
    background: var(--danger-lt) !important;
    color: var(--danger) !important;
    border-color: #FECACA !important;
    font-size: 0.75rem !important;
}

/* Reset button */
.reset-btn .stButton > button {
    color: var(--ink-muted) !important;
    background: transparent !important;
    border: 1px solid var(--border) !important;
    font-size: 0.78rem !important;
}
.reset-btn .stButton > button:hover {
    background: var(--border) !important;
    transform: none !important;
}

/* Chat bubbles */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: var(--accent) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 10px 16px !important;
    max-width: 80%;
    margin-left: auto;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 10px 16px !important;
    max-width: 82%;
    box-shadow: var(--shadow-sm);
}
[data-testid="stChatInputContainer"] textarea {
    font-family: 'Inter', sans-serif !important;
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    background: var(--surface) !important;
}

/* State badge */
.state-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase;
    color: var(--ink-muted);
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 4px 10px; border-radius: 20px;
}

hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ── 3. SESSION INIT ───────────────────────────────────────────────────────────
if "bot" not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()
    st.session_state.history = [
        {"role": "assistant", "content": st.session_state.bot.get_response()}
    ]


# ── 4. HELPERS ────────────────────────────────────────────────────────────────
def _send(user_text: str) -> None:
    st.session_state.history.append({"role": "user", "content": user_text})
    st.session_state.bot.step(user_text)
    st.session_state.history.append(
        {"role": "assistant", "content": st.session_state.bot.get_response()}
    )
    st.rerun()


def _render_cart(cart: list[dict], total: int, in_confirmation: bool) -> None:
    """
    Render cart dengan qty controls (+/−/🗑) per item.
    Controls dinonaktifkan saat state CONFIRMATION.
    """
    if not cart:
        st.caption("🛒 Keranjang masih kosong.")
        return

    for item in cart:
        key      = item["item"]
        subtotal = item["price"] * item["qty"]

        # Layout: emoji+nama | qty controls | harga
        col_name, col_ctrl, col_price = st.columns([4, 3, 3])

        with col_name:
            st.markdown(
                f"**{item['emoji']} {key.capitalize()}**  \n"
                f"<span style='font-size:0.75rem;color:#6B7566;'>"
                f"Rp {item['price']:,} / satuan</span>",
                unsafe_allow_html=True,
            )

        with col_ctrl:
            if not in_confirmation:
                b1, b2, b3 = st.columns([1, 1, 1])
                with b1:
                    st.markdown("<div class='qty-btn qty-btn-minus'>", unsafe_allow_html=True)
                    if st.button("−", key=f"minus_{key}"):
                        st.session_state.bot.cart_update_qty(key, -1)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with b2:
                    st.markdown(
                        f"<div style='text-align:center;font-weight:700;"
                        f"font-size:0.95rem;padding-top:5px;'>{item['qty']}</div>",
                        unsafe_allow_html=True,
                    )
                with b3:
                    st.markdown("<div class='qty-btn'>", unsafe_allow_html=True)
                    if st.button("+", key=f"plus_{key}"):
                        st.session_state.bot.cart_update_qty(key, +1)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div style='text-align:center;font-weight:700;"
                    f"font-size:0.95rem;padding-top:5px;'>{item['qty']}x</div>",
                    unsafe_allow_html=True,
                )

        with col_price:
            delete_col, price_col = st.columns([1, 2])
            with price_col:
                st.markdown(
                    f"<div style='text-align:right;font-weight:600;"
                    f"padding-top:5px;'>Rp {subtotal:,}</div>",
                    unsafe_allow_html=True,
                )
            with delete_col:
                if not in_confirmation:
                    st.markdown("<div class='qty-btn qty-btn-delete'>", unsafe_allow_html=True)
                    if st.button("🗑", key=f"del_{key}"):
                        st.session_state.bot.cart_remove(key)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    total_col1, total_col2 = st.columns([3, 2])
    with total_col1:
        st.markdown("**Total Belanja**")
    with total_col2:
        st.markdown(
            f"<div style='text-align:right;font-weight:700;color:#2E6E4E;"
            f"font-size:1.05rem;'>Rp {total:,}</div>",
            unsafe_allow_html=True,
        )


# ── 5. HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 8px 0 28px;">
    <div class="site-title">🌾 Berkah Ternak</div>
    <div class="site-sub">Produk segar peternakan lokal · Asisten pemesanan berbasis Otomata</div>
</div>
""", unsafe_allow_html=True)


# ── 6. MAIN LAYOUT ────────────────────────────────────────────────────────────
col_products, col_chat = st.columns([5, 5], gap="large")

# ════════════════════════════════════════
# LEFT — PRODUCT GRID
# ════════════════════════════════════════
with col_products:
    st.markdown("<span class='section-label'>Produk Pilihan</span>", unsafe_allow_html=True)

    items     = list(st.session_state.bot.nlp.menu_data.items())
    grid_rows = [items[i:i+2] for i in range(0, len(items), 2)]

    for row in grid_rows:
        cols = st.columns(len(row), gap="small")
        for col, (key, data) in zip(cols, row):
            with col:
                st.markdown(f"""
                <div class="product-card">
                    <div class="card-emoji">{data['emoji']}</div>
                    <div class="card-name">{key.capitalize()}</div>
                    <div class="card-desc">{data['desc']}</div>
                    <div class="card-price">Rp {data['price']:,}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"+ Pesan {key.capitalize()}", key=f"btn_{key}"):
                    _send(f"pesan 1 {key}")


# ════════════════════════════════════════
# RIGHT — CHAT + CART
# ════════════════════════════════════════
with col_chat:

    # ── Chat ──
    st.markdown("<span class='section-label'>Konsultasi & Pemesanan</span>", unsafe_allow_html=True)

    chat_box = st.container(height=290, border=False)
    with chat_box:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ketik: 'pesan 2 telur', 'kurangi 1 susu', 'menu'…"):
        _send(prompt)

    st.write("")

    # ── Cart Panel ──
    st.markdown("<span class='section-label'>Ringkasan Belanja</span>", unsafe_allow_html=True)

    cart          = st.session_state.bot.cart
    total         = st.session_state.bot.calculate_total()
    current_state = st.session_state.bot.state.name
    in_confirm    = current_state == "CONFIRMATION"

    with st.container(border=True):
        _render_cart(cart, total, in_confirm)

    st.write("")

    # ── Contextual action button ──
    if cart and current_state == "ORDERING":
        if st.button("🚀 Selesai & Checkout", key="btn_checkout"):
            _send("checkout")

    elif current_state == "CONFIRMATION":
        if st.button("💳 Konfirmasi & Bayar Sekarang", key="btn_pay"):
            _send("ya")

    # ── State badge + Reset ──
    badge_col, reset_col = st.columns([3, 1])
    with badge_col:
        st.markdown(
            f"<span class='state-badge'>⚙ {current_state}</span>",
            unsafe_allow_html=True,
        )
    with reset_col:
        st.markdown("<div class='reset-btn'>", unsafe_allow_html=True)
        if st.button("↺ Reset", key="btn_reset"):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)