from enum import Enum, auto
from engine import LivestockEngine

class State(Enum):
    IDLE = auto()
    ORDERING = auto()
    CONFIRMATION = auto()

class LivestockFSM:
    def __init__(self):
        self.state = State.IDLE
        self.nlp = LivestockEngine()
        self.cart = []
        self.response = ""

    def get_response(self):
        return self.response

    def calculate_total(self):
        return sum(item['price'] * item['qty'] for item in self.cart)

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)

        if intent == "RESET":
            self.__init__()
            self.response = "Keranjang dikosongkan. Halo! Mau pesan hasil ternak apa hari ini? 🌾"
            return

        if self.state == State.IDLE:
            self.state = State.ORDERING
            self.response = "Selamat datang di Berkah Ternak! 👨‍🌾 Kami menyediakan produk segar langsung dari peternakan lokal. Silakan pilih menu di samping atau ketik pesanan Anda!"
            
        elif self.state == State.ORDERING:
            if intent == "ASK_MENU":
                self.response = "Katalog Produk:\n" + "\n".join([f"- {d['emoji']} {k.capitalize()}: Rp {d['price']:,}" for k, d in self.nlp.menu_data.items()])
            elif intent == "CHECKOUT":
                if not self.cart:
                    self.response = "Keranjang Anda masih kosong. Silakan pilih produk terlebih dahulu."
                else:
                    self.state = State.CONFIRMATION
                    self.response = f"Total belanjaan Anda adalah **Rp {self.calculate_total():,}**. Apakah Anda ingin langsung melakukan pembayaran? (Ketik 'Ya/Bayar' atau klik tombol Selesai Belanja)"
            else:
                new_orders = self.nlp.parse_orders(user_input)
                if new_orders:
                    for order in new_orders:
                        existing = next((i for i in self.cart if i['item'] == order['item']), None)
                        if existing:
                            existing['qty'] += order['qty']
                        else:
                            self.cart.append(order)
                    self.response = f"✅ Ditambahkan ke keranjang! Total sementara: **Rp {self.calculate_total():,}**. Ada tambahan lagi?"
                else:
                    self.response = "Maaf, produk tidak dikenali. Coba ketik contoh: *'Pesan 2 susu dan 1 telur'*."

        elif self.state == State.CONFIRMATION:
            if intent == "CHECKOUT":
                total = self.calculate_total()
                self.response = f"🎉 **Pembayaran Sukses sebesar Rp {total:,}!** Terima kasih telah mendukung peternak lokal. Produk segar Anda akan segera dikirim! 🚚"
                self.state = State.IDLE
                self.cart = []
            else:
                self.response = "Mohon konfirmasi pembayaran Anda dengan mengetik 'Ya' atau klik tombol 'Konfirmasi & Bayar'."