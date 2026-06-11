import re

class LivestockEngine:
    def __init__(self):
        # Database Produk Hasil Peternakan (Emoji & Harga Bersih)
        self.menu_data = {
            "susu": {"price": 12000, "emoji": "🥛", "desc": "Susu Sapi Segar (1 Liter)"},
            "telur": {"price": 26000, "emoji": "🥚", "desc": "Telur Ayam Pilihan (1 Kg)"},
            "daging": {"price": 35000, "emoji": "🍗", "desc": "Daging Ayam Segar (1 Kg)"},
            "madu": {"price": 50000, "emoji": "🍯", "desc": "Madu Murni Alami (250ml)"}
        }
        
        self.re_number = r"\b(\d+)\b"
        menu_keys = "|".join(self.menu_data.keys())
        self.re_menu = rf"\b({menu_keys})\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b"

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
        segments = re.split(self.re_split, full_text)
        found_orders = []
        for segment in segments:
            if segment.strip():
                order = self._parse_single_segment(segment)
                if order:
                    found_orders.append(order)
        return found_orders

    def detect_intent(self, text):
        text = text.lower().strip()
        if re.search(r"\b(reset|ulang|batal)\b", text):
            return "RESET"
        if re.search(r"(produk|daftar|stok|list|menu|katalog)", text):
            return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|cukup|ya|oke|fix)\b", text):
            return "CHECKOUT"
        return "ORDER"