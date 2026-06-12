from enum import Enum, auto
from engine import LivestockEngine
from datetime import datetime

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
        self.invoice_logs = []

    def get_response(self):
        return self.response

    def calculate_total(self):
        return sum(item['price'] * item['qty'] for item in self.cart)

    def get_menu_text(self):
        teks_menu = "**Daftar Produk livestockshop:**\n\n"
        for key, data in self.nlp.menu_data.items():
            teks_menu += f"- **{key.capitalize()}** (Rp {data['price']:,}): *{data['desc']}*\n"
        teks_menu += "\nSilakan ketik pesanan Anda (contoh: *Pesan 2 susu dan 1 telur*)."
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
                    message = f"**{item_to_reduce.capitalize()}** telah dihapus dari keranjang."
                else:
                    message = f"**{item_to_reduce.capitalize()}** dikurangi {qty_to_remove}. Sisa: {item['qty']}"
                break
        if not found:
            message = f"Gagal: **{item_to_reduce}** tidak ada di keranjang."
        return message

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)

        if intent == "RESET":
            self.__init__()
            self.response = "Sistem di-reset. Halo! Mau pesan hasil ternak apa?"
            return

        if self.state == State.IDLE:
            self.state = State.ORDERING
            self.response = "Selamat datang di livestockshop! Mau pesan hasil bumi dan ternak apa hari ini? Ketik 'produk' untuk melihat daftar harga."
            
        elif self.state == State.ORDERING:
            if intent == "ASK_MENU":
                self.response = self.get_menu_text()
            elif intent == "CANCEL_ALL" or user_input.lower() == "kosongkan":
                self.cart = []
                self.response = "Keranjang belanja dikosongkan. Mau pesan yang lain?"
            elif intent == "REDUCE_ITEM":
                items_to_remove = self.nlp.parse_orders(user_input)
                if items_to_remove:
                    results = [self.reduce_cart(itm['item'], itm['qty']) for itm in items_to_remove]
                    self.response = "\n".join(results)
                else:
                    self.response = "Produk apa yang ingin dikurangi? Contoh: *hapus 1 telur*."
            elif intent == "CHECKOUT":
                if not self.cart:
                    self.response = "Keranjang Anda masih kosong."
                else:
                    self.state = State.CONFIRMATION
                    self.response = f"Total belanjaan: **Rp {self.calculate_total():,}**. Lanjut ke pembayaran? (Ketik **'Ya'** untuk konfirmasi / **'Tidak'** untuk batal)"
            else:
                new_orders = self.nlp.parse_orders(user_input)
                if new_orders:
                    for order in new_orders:
                        existing = next((i for i in self.cart if i['item'] == order['item']), None)
                        if existing:
                            existing['qty'] += order['qty']
                        else:
                            self.cart.append(order)
                    self.response = "Produk ditambahkan ke keranjang. Ada tambahan? (Ketik 'bayar' jika sudah cukup)"
                else:
                    self.response = "Maaf, produk tidak dikenali. Coba ketik: *'pesan 2 susu, 1 daging'*."

        elif self.state == State.CONFIRMATION:
            if intent == "YES":
                self.state = State.PAYMENT
                self.step() 
            elif intent == "NO":
                self.state = State.ORDERING
                self.response = "Konfirmasi dibatalkan. Silakan kelola kembali pesanan Anda."
            else:
                self.response = "Mohon jawab dengan 'Ya' atau 'Tidak'."

        elif self.state == State.PAYMENT:
            total = self.calculate_total()
            id_nota = f"LS-{int(datetime.now().timestamp())}"
            waktu_cetak = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            nota_data = {
                "id": id_nota,
                "waktu": waktu_cetak,
                "items": list(self.cart),
                "total": total
            }
            self.invoice_logs.append(nota_data)
            self.response = f"Terima kasih telah berbelanja! Pembayaran Rp {total:,} sukses. Produk segar akan segera dikirim!"
            self.state = State.IDLE
            self.cart = []