import streamlit as st
from fsm import LivestockFSM

# ── 1. PAGE CONFIG ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Berkah Ternak",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 2. DESIGN SYSTEM ─────────────────────────────────────────────────────────
# Palette: warm parchment base + deep forest ink + moss accent
# Typography: Sora (display) + Inter (body) — both from Google Fonts
# Signature: frosted-glass cart panel with backdrop-filter blur

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* ── TOKENS ── */
:root {
    --bg:         #F5F2EC;
    --surface:    #FFFFFF;
    --border:     #E4DDD1;
    --ink:        #1C2B22;
    --ink-muted:  #6B7566;
    --accent:     #2E6E4E;
    --accent-lt:  #EBF5EF;
    --accent-dim: #C5E0D0;
    --warn:       #D97706;
    --radius-sm:  10px;
    --radius-md:  16px;
    --radius-lg:  24px;
    --shadow-sm:  0 1px 4px rgba(0,0,0,.06);
    --shadow-md:  0 4px 16px rgba(0,0,0,.08);
}

/* ── BASE ── */
.stApp { background-color: var(--bg) !important; }

/* Remove Streamlit default top padding */
.block-container { padding-top: 2rem !important; }

/* ── TYPOGRAPHY ── */
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

/* ── SECTION LABELS ── */
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

/* ── PRODUCT CARD ── */
.product-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px 16px 16px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    height: 100%;
}
.product-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
    border-color: var(--accent-dim);
}
.card-emoji {
    font-size: 2.4rem;
    background: var(--accent-lt);
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
    line-height: 1;
}
.card-name {
    font-family: 'Sora', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 2px;
}
.card-desc {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: var(--ink-muted);
    margin-bottom: 10px;
    line-height: 1.4;
}
.card-price {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 14px;
}

/* ── ORDER BUTTON ── */
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

/* Reset button override */
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

/* ── CHAT AREA ── */
/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: var(--accent) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 10px 16px !important;
    max-width: 80%;
    margin-left: auto;
    color: #fff !important;
}
/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 10px 16px !important;
    max-width: 82%;
    box-shadow: var(--shadow-sm);
}
/* Chat input */
[data-testid="stChatInputContainer"] textarea {
    font-family: 'Inter', sans-serif !important;
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    background: var(--surface) !important;
}

/* ── CART PANEL (glassmorphism) ── */
.cart-panel {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    box-shadow: var(--shadow-md);
}
.cart-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--ink);
}
.cart-row:last-of-type { border-bottom: none; }
.cart-qty-badge {
    font-size: 0.72rem;
    font-weight: 600;
    background: var(--accent-lt);
    color: var(--accent);
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 6px;
}
.cart-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    font-family: 'Sora', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--ink);
}
.cart-total-amount {
    color: var(--accent);
}
.empty-cart {
    text-align: center;
    padding: 20px 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--ink-muted);
}

/* ── STATE BADGE ── */
.state-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--ink-muted);
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 4px 10px;
    border-radius: 20px;
}

/* ── DIVIDERS ── */
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ── 3. SESSION INIT ───────────────────────────────────────────────────────────
if "bot" not in st.session_state:
    st.session_state.bot = LivestockFSM()
    st.session_state.bot.step()          # sets welcome message, stays IDLE
    st.session_state.history = [
        {"role": "assistant", "content": st.session_state.bot.get_response()}
    ]


# ── 4. HELPERS ────────────────────────────────────────────────────────────────
def _send(user_text: str) -> None:
    """Append user message, advance FSM, append bot reply, rerun."""
    st.session_state.history.append({"role": "user", "content": user_text})
    st.session_state.bot.step(user_text)
    st.session_state.history.append(
        {"role": "assistant", "content": st.session_state.bot.get_response()}
    )
    st.rerun()


def _render_cart_html(cart: list[dict], total: int) -> str:
    if not cart:
        return "<div class='empty-cart'>🛒 Keranjang masih kosong.</div>"

    rows = "".join(
        f"""
        <div class='cart-row'>
            <span>{item['emoji']} {item['item'].capitalize()}
                <span class='cart-qty-badge'>{item['qty']}x</span>
            </span>
            <span>Rp {item['price'] * item['qty']:,}</span>
        </div>
        """
        for item in cart
    )
    return f"""
    {rows}
    <div class='cart-total'>
        <span>Total</span>
        <span class='cart-total-amount'>Rp {total:,}</span>
    </div>
    """


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

    items      = list(st.session_state.bot.nlp.menu_data.items())
    grid_rows  = [items[i:i+2] for i in range(0, len(items), 2)]

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

    chat_box = st.container(height=310, border=False)
    with chat_box:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ketik: 'pesan 2 telur', 'menu', atau 'selesai'…"):
        _send(prompt)

    st.write("")

    # ── Cart Panel ──
    st.markdown("<span class='section-label'>Ringkasan Belanja</span>", unsafe_allow_html=True)

    cart  = st.session_state.bot.cart
    total = st.session_state.bot.calculate_total()

    st.markdown(
        f"<div class='cart-panel'>{_render_cart_html(cart, total)}</div>",
        unsafe_allow_html=True,
    )

    st.write("")

    # ── Contextual action button ──
    current_state = st.session_state.bot.state.name

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
        with st.container():
            st.markdown("<div class='reset-btn'>", unsafe_allow_html=True)
            if st.button("↺ Reset", key="btn_reset"):
                st.session_state.clear()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)