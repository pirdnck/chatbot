from enum import Enum, auto
from engine import LivestockEngine


class State(Enum):
    IDLE         = auto()
    ORDERING     = auto()
    CONFIRMATION = auto()


class LivestockFSM:
    """
    FSM untuk Berkah Ternak chatbot.

    State transitions:
        IDLE ──(any input)──────────────► ORDERING  (fall-through processes input)
        ORDERING ──(checkout, cart > 0)─► CONFIRMATION
        ORDERING ──(reset)──────────────► IDLE
        CONFIRMATION ──(checkout/ya)────► IDLE  (cart cleared)
        CONFIRMATION ──(reset)──────────► IDLE  (cart cleared)

    Sprint 1: tambah cart_remove(item) dan cart_update_qty(item, delta)
              yang bisa dipanggil langsung dari UI tanpa melalui chat.
    """

    _WELCOME = (
        "Selamat datang di **Berkah Ternak** 👨‍🌾\n\n"
        "Kami menghadirkan produk segar langsung dari peternakan lokal. "
        "Pilih produk di samping atau ketik pesanan Anda!"
    )
    _EMPTY_CART     = "Keranjang masih kosong. Pilih produk terlebih dahulu. 🛒"
    _UNRECOGNIZED   = (
        "Produk tidak dikenali. Coba: *'pesan 2 susu dan 1 telur'* "
        "atau klik tombol produk di samping."
    )
    _CONFIRM_PROMPT = (
        "Ketik **Ya** atau klik *Konfirmasi & Bayar* untuk melanjutkan, "
        "atau **Reset** untuk membatalkan."
    )

    def __init__(self) -> None:
        self.state     = State.IDLE
        self.nlp       = LivestockEngine()
        self.cart:     list[dict] = []
        self.response: str = ""

    # ------------------------------------------------------------------
    # Public API — read
    # ------------------------------------------------------------------

    def get_response(self) -> str:
        return self.response

    def calculate_total(self) -> int:
        return sum(item["price"] * item["qty"] for item in self.cart)

    # ------------------------------------------------------------------
    # Public API — cart mutation (Sprint 1)
    # Dipanggil langsung dari tombol UI, tidak melalui chat step().
    # ------------------------------------------------------------------

    def cart_update_qty(self, item_key: str, delta: int) -> None:
        """
        Tambah (delta > 0) atau kurangi (delta < 0) qty item di cart.
        Otomatis hapus item jika qty ≤ 0.
        """
        existing = next((i for i in self.cart if i["item"] == item_key), None)
        if not existing:
            return
        existing["qty"] += delta
        if existing["qty"] <= 0:
            self.cart.remove(existing)

    def cart_remove(self, item_key: str) -> None:
        """Hapus item tertentu dari cart sepenuhnya."""
        self.cart = [i for i in self.cart if i["item"] != item_key]

    # ------------------------------------------------------------------
    # Public API — step (chat input)
    # ------------------------------------------------------------------

    def step(self, user_input: str = "") -> None:
        text   = user_input.strip()
        intent = self.nlp.detect_intent(text) if text else "NOOP"

        # Global RESET dari state manapun
        if intent == "RESET":
            self._reset("Keranjang dikosongkan. Halo lagi! Mau pesan apa hari ini? 🌾")
            return

        # --- IDLE ---
        if self.state == State.IDLE:
            if not text:
                self.response = self._WELCOME
                return
            self.state = State.ORDERING
            # fall-through ke ORDERING block

        # --- ORDERING --- (no elif — intentional fall-through dari IDLE)
        if self.state == State.ORDERING:
            if intent == "ASK_MENU":
                lines = "\n".join(
                    f"{d['emoji']} **{k.capitalize()}** — Rp {d['price']:,}  \n{d['desc']}"
                    for k, d in self.nlp.menu_data.items()
                )
                self.response = f"**Katalog Produk Kami:**\n\n{lines}"

            elif intent == "CHECKOUT":
                if not self.cart:
                    self.response = self._EMPTY_CART
                else:
                    self.state    = State.CONFIRMATION
                    self.response = (
                        f"Total belanjaan Anda: **Rp {self.calculate_total():,}**\n\n"
                        "Apakah Anda ingin melanjutkan pembayaran?"
                    )

            elif intent == "REDUCE":
                # Coba parse item yang mau dikurangi
                orders = self.nlp.parse_orders(text)
                if orders:
                    for o in orders:
                        self.cart_update_qty(o["item"], -o["qty"])
                    self.response = (
                        f"✅ Pesanan diperbarui. "
                        f"Total sementara: **Rp {self.calculate_total():,}**"
                        + ("  \nKeranjang kosong." if not self.cart else "")
                    )
                else:
                    self.response = "Sebutkan produk yang ingin dikurangi. Contoh: *'kurangi 1 susu'*."

            else:  # ORDER
                new_orders = self.nlp.parse_orders(text)
                if new_orders:
                    self._merge_orders(new_orders)
                    names = ", ".join(
                        f"{o['emoji']} {o['qty']}x {o['item'].capitalize()}"
                        for o in new_orders
                    )
                    self.response = (
                        f"✅ Ditambahkan: {names}\n\n"
                        f"Total sementara: **Rp {self.calculate_total():,}**  \n"
                        "Ada tambahan lagi, atau ketik *Selesai* untuk checkout?"
                    )
                else:
                    self.response = self._UNRECOGNIZED

        # --- CONFIRMATION ---
        elif self.state == State.CONFIRMATION:
            if intent == "CHECKOUT":
                total         = self.calculate_total()
                self.response = (
                    f"🎉 **Pembayaran sukses — Rp {total:,}!**\n\n"
                    "Terima kasih telah mendukung peternak lokal. "
                    "Pesanan segar Anda segera dikirim! 🚚"
                )
                self.state = State.IDLE
                self.cart  = []
            else:
                self.response = self._CONFIRM_PROMPT

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _merge_orders(self, new_orders: list[dict]) -> None:
        for order in new_orders:
            existing = next(
                (i for i in self.cart if i["item"] == order["item"]), None
            )
            if existing:
                existing["qty"] += order["qty"]
            else:
                self.cart.append(dict(order))

    def _reset(self, msg: str) -> None:
        self.__init__()
        self.response = msg