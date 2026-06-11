from enum import Enum, auto
from engine import LivestockEngine


class State(Enum):
    IDLE         = auto()
    ORDERING     = auto()
    CONFIRMATION = auto()


class LivestockFSM:
    """
    Finite State Machine for the Berkah Ternak chatbot.

    State transitions:
        IDLE ──(any non-reset input)──► ORDERING
        ORDERING ──(checkout + cart not empty)──► CONFIRMATION
        ORDERING ──(reset)──► IDLE
        CONFIRMATION ──(checkout/yes)──► IDLE  (cart cleared)
        CONFIRMATION ──(reset)──► IDLE  (cart cleared)
        * IDLE state never auto-transitions on empty input
    """

    # Response templates — easier to maintain outside step()
    _WELCOME  = (
        "Selamat datang di **Berkah Ternak** 👨‍🌾\n\n"
        "Kami menghadirkan produk segar langsung dari peternakan lokal. "
        "Pilih produk di samping atau ketik pesanan Anda!"
    )
    _EMPTY_CART   = "Keranjang masih kosong. Pilih produk terlebih dahulu. 🛒"
    _UNRECOGNIZED = (
        "Produk tidak dikenali. Coba: *'pesan 2 susu dan 1 telur'* "
        "atau klik tombol produk di samping."
    )
    _CONFIRM_PROMPT = (
        "Ketik **Ya** atau klik *Konfirmasi & Bayar* untuk melanjutkan, "
        "atau **Reset** untuk membatalkan."
    )

    def __init__(self) -> None:
        self.state    = State.IDLE
        self.nlp      = LivestockEngine()
        self.cart:    list[dict] = []
        self.response: str = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_response(self) -> str:
        return self.response

    def calculate_total(self) -> int:
        return sum(item["price"] * item["qty"] for item in self.cart)

    def step(self, user_input: str = "") -> None:
        """
        Advance the FSM by one step given raw user text.
        Empty string on IDLE is safe — no state change occurs.
        """
        text   = user_input.strip()
        intent = self.nlp.detect_intent(text) if text else "NOOP"

        # Global RESET — valid from any state
        if intent == "RESET":
            self._reset("Keranjang dikosongkan. Halo lagi! Mau pesan apa hari ini? 🌾")
            return

        # --- IDLE -------------------------------------------------------
        if self.state == State.IDLE:
            if not text:
                # Called with empty string at app boot — just set welcome msg
                self.response = self._WELCOME
                return
            # Any real input kicks off ordering
            self.state    = State.ORDERING
            self.response = self._WELCOME

        # --- ORDERING ---------------------------------------------------
        elif self.state == State.ORDERING:
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

            else:  # ORDER intent
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

        # --- CONFIRMATION -----------------------------------------------
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
        """Upsert new orders into cart — increment qty if item exists."""
        for order in new_orders:
            existing = next(
                (i for i in self.cart if i["item"] == order["item"]), None
            )
            if existing:
                existing["qty"] += order["qty"]
            else:
                self.cart.append(dict(order))  # defensive copy

    def _reset(self, msg: str) -> None:
        self.__init__()
        self.response = msg