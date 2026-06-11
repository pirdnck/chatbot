import re

class LivestockEngine:
    def __init__(self):
        # Database Produk Hasil Peternakan
        self.menu_data = {
            "susu": {"price": 12000, "emoji": "🥛", "desc": "Susu sapi segar literan murni"},
            "telur": {"price": 26000, "emoji": "🥚", "desc": "Telur ayam ras pilihan per kg"},
            "daging": {"price": 35000, "emoji": "🍗", "desc": "Daging ayam potong segar per kg"},
            "madu": {"price": 50000, "emoji": "🍯", "desc": "Madu hutan murni alami 250ml"}
        }
        
        # Database Paket Hemat (Bundle)
        self.bundles = {
            "paket sarapan": {"items": [("susu", 1), ("telur", 1)], "price": 35000, "desc": "1L Susu + 1kg Telur (Hemat Rp3.000)"},
            "paket imun": {"items": [("susu", 2), ("madu", 1)], "price": 70000, "desc": "2L Susu + 1_botol Madu (Hemat Rp4.000)"}
        }
        
        self.re_number = r"\b(\d+)\b"
        menu_keys = "|".join(self.menu_data.keys())
        self.re_menu = rf"\b({menu_keys})\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b"
        
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset keranjang|kosongkan)\b"
        self.re_reduce = r"\b(batalkan|kurangi|tidak jadi|hapus|cancel)\b"

    def _parse_single_segment(self, text):
        text = text.lower().strip()
        item_match = re.search(self.re_menu, text)
        if not item_match:
            return None
            
        item_key = item_match.group(1)
        qty_match = re.search(self.re_number, text)
        qty = int(qty_match.group(1)) if qty_match else 1
        
        return {
            "item": item_key,
            "qty": qty,
            "price": self.menu_data[item_key]['price'],
            "emoji": self.menu_data[item_key]['emoji']
        }

    def parse_orders(self, full_text):
        # Deteksi Paket Bundle terlebih dahulu
        full_text_lower = full_text.lower()
        for bundle_name, bundle_info in self.bundles.items():
            if bundle_name in full_text_lower:
                orders = []
                for item_key, qty in bundle_info['items']:
                    orders.append({
                        "item": item_key,
                        "qty": qty,
                        "price": self.menu_data[item_key]['price'],
                        "emoji": self.menu_data[item_key]['emoji']
                    })
                return orders

        # Jika bukan paket, parsing eceran biasa
        segments = re.split(self.re_split, full_text)
        found_orders = []
        for segment in segments:
            if segment.strip():
                order = self._parse_single_segment(segment)
                if order:
                    found_orders.append(order)
        return found_orders

    def detect_intent(self, text):
        text = text.lower()
        if re.search(r"\b(reset|ulang|batal semua)\b", text):
            return "RESET"
        if re.search(self.re_cancel_all, text):
            return "CANCEL_ALL"
        if re.search(self.re_reduce, text):
            return "REDUCE_ITEM"
        if re.search(r"(produk|daftar|stok|jual apa|list|menu|katalog)", text):
            return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|cukup)\b", text):
            return "CHECKOUT"
        if re.search(r"\b(ya|yes|oke|betul|siap|baik|lanjut)\b", text):
            return "YES"
        if re.search(r"\b(tidak|enggak|batal|no|salah)\b", text):
            return "NO"
        if re.search(r"\b(ternakhemat|promo46)\b", text):
            return "APPLY_PROMO"
        return "UNKNOWN"