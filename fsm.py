from enum import Enum, auto
from engine import LivestockEngine

class State(Enum):
    IDLE = auto()
    ORDERING = auto()
    CONFIRMATION = auto()
    PAYMENT = auto()

class LivestockFSM:
    def __init__(self):
        self.state = State.IDLE
        self.nlp = LivestockEngine()
        self.cart = []
        self.response = ""
        self.discount = 0  # Potongan harga dalam Rupiah
        self.promo_applied = False

    def get_response(self):
        return self.response

    def calculate_subtotal(self):
        return sum(item['price'] * item['qty'] for item in self.cart)
        
    def calculate_total(self):
        total = self.calculate_subtotal() - self.discount
        return max(0, total)

    def get_menu_text(self):
        teks_menu = "🌿 **Katalog Hasil Ternak Segar:**\n\n"
        for key, data in self.nlp.menu_data.items():
            teks_menu += f"- {data['emoji']} **{key.capitalize()}** (Rp {data['price']:,}) \n &nbsp;&nbsp;&nbsp;&nbsp; *{data['desc']}*\n"
        
        teks_menu += "\n📦 **Paket Hemat Bundle (Ketik nama paket):**\n"
        for b_name, b_info in self.nlp.bundles.items():
            teks_menu += f"- 🛍️ **{b_name.upper()}** (Rp {b_info['price']:,}) \n &nbsp;&nbsp;&nbsp;&nbsp; *{b_info['desc']}*\n"
            
        teks_menu += "\n💡 *Gunakan kode kupon **TERNAKHEMAT** di chat untuk diskon Rp 5.000!*"
        return teks_menu

    def reduce_cart(self, item_to_reduce, qty_to_remove):
        found = False
        message = ""
        for item in self.cart:
            if item['item'] == item_to_reduce:
                item['qty'] -= qty_to_remove
                found = True
                if item['qty'] <= 0:
                    self.cart.remove(item)
                    message = f"❌ **{item_to_reduce.capitalize()}** berhasil dihapus dari keranjang."
                else:
                    message = f"📉 **{item_to_reduce.capitalize()}** dikurangi {qty_to_remove}. Sisa di keranjang: {item['qty']}x"
                break
        if not found:
            message = f"Gagal: **{item_to_reduce}** belum ada di keranjang Anda."
        return message

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)

        if intent == "RESET":
            self.__init__()
            self.response = "Sistem telah disegarkan kembali. Halo! Mau pesan hasil ternak segar apa hari ini? 🌾"
            return

        if self.state == State.IDLE:
            self.state = State.ORDERING
            self.response = "Selamat datang di Berkah Ternak Smart Hub! 👨‍🌾 Melayani produk segar langsung dari peternak lokal. Ketik **'katalog'** untuk melihat produk segar hari ini!"
            
        elif self.state == State.ORDERING:
            if intent == "ASK_MENU":
                self.response = self.get_menu_text()
            elif intent == "APPLY_PROMO":
                if self.promo_applied:
                    self.response = "⚠️ Anda sudah menggunakan kode promo pada keranjang ini."
                else:
                    self.discount = 5000
                    self.promo_applied = True
                    self.response = "🎉 Hore! Kupon **TERNAKHEMAT** berhasil dipasang. Anda mendapatkan potongan Rp 5,000! Kirim kata **'bayar'** untuk checkout."
            elif intent == "CANCEL_ALL":
                self.cart = []
                self.discount = 0
                self.promo_applied = False
                self.response = "🧺 Keranjang belanjaan Anda telah dikosongkan. Silakan pilih menu kembali!"
            elif intent == "REDUCE_ITEM":
                items_to_remove = self.nlp.parse_orders(user_input)
                if items_to_remove:
                    results = [self.reduce_cart(itm['item'], itm['qty']) for itm in items_to_remove]
                    self.response = "\n".join(results)
                else:
                    self.response = "Produk apa yang ingin dikurangi? Contoh: *'kurangi 1 telur'* atau *'hapus susu'*."
            elif intent == "CHECKOUT":
                if not self.cart:
                    self.response = "Keranjang Anda masih kosong. Yuk, pilih produk peternakan terbaik dulu!"
                else:
                    self.state = State.CONFIRMATION
                    self.response = f"📋 **Konfirmasi Pesanan**\nSubtotal: Rp {self.calculate_subtotal():,}\nDiskon: Rp {self.discount:,}\nTotal Tagihan: **Rp {self.calculate_total():,}**.\n\nApakah pesanan ini sudah benar? *(Ketik **Ya** untuk lanjut / **Tidak** untuk ubah)*"
            else:
                new_orders = self.nlp.parse_orders(user_input)
                if new_orders:
                    for order in new_orders:
                        existing = next((i for i in self.cart if i['item'] == order['item']), None)
                        if existing:
                            existing['qty'] += order['qty']
                        else:
                            self.cart.append(order)
                    self.response = "✅ Berhasil ditambahkan ke keranjang! Ada tambahan lain? Jika sudah cukup, silakan ketik **'bayar'**."
                else:
                    self.response = "🤖 Maaf, asisten tidak mengerti maksudmu. Coba ketik seperti ini: *'Pesan 2 susu dan 1 kg daging'* atau ketik *'katalog'*."

        elif self.state == State.CONFIRMATION:
            if intent == "YES":
                self.state = State.PAYMENT
                self.step() 
            elif intent == "NO":
                self.state = State.ORDERING
                self.response = "🔄 Konfirmasi dibatalkan. Silakan kelola atau tambahkan kembali pesanan Anda ke keranjang."
            else:
                self.response = "Mohon jawab dengan **'Ya'** untuk melanjutkan ke pembayaran, atau **'Tidak'** untuk mengubah pesanan."

        elif self.state == State.PAYMENT:
            total = self.calculate_total()
            self.response = f"🎉 **Pembayaran Berhasil!**\nTerima kasih telah mendukung kesejahteraan peternak lokal. Dana sebesar **Rp {total:,}** telah kami terima. Produk segar akan segera dikirim ke alamat Anda dalam 1 jam! 🚚💨"
            self.state = State.IDLE
            self.cart = []
            self.discount = 0
            self.promo_applied = False