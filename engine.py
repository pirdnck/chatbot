import re


class LivestockEngine:
    """
    NLP parsing layer: detects intent and extracts order items from raw text.
    Kept stateless — no side effects, pure input → output.
    """

    MENU_DATA: dict = {
        "susu":   {"price": 12000, "emoji": "🥛", "desc": "Susu Sapi Segar (1 Liter)"},
        "telur":  {"price": 26000, "emoji": "🥚", "desc": "Telur Ayam Pilihan (1 Kg)"},
        "daging": {"price": 35000, "emoji": "🍗", "desc": "Daging Ayam Segar (1 Kg)"},
        "madu":   {"price": 50000, "emoji": "🍯", "desc": "Madu Murni Alami (250ml)"},
    }

    # Intent keywords — ordered from most specific to most general
    _INTENT_PATTERNS: list[tuple[str, str]] = [
        ("RESET",    r"\b(reset|ulang|batal|kosongkan)\b"),
        ("ASK_MENU", r"\b(produk|daftar|stok|list|menu|katalog|apa saja)\b"),
        ("CHECKOUT", r"\b(selesai|bayar|checkout|cukup|ya|oke|fix|confirm|konfirmasi)\b"),
    ]

    def __init__(self) -> None:
        self.menu_data = self.MENU_DATA  # public alias used by app.py

        _keys = "|".join(re.escape(k) for k in self.MENU_DATA)
        self._re_number = re.compile(r"\b(\d+)\b")
        self._re_menu   = re.compile(rf"\b({_keys})\b")
        self._re_split  = re.compile(r"[,.]|\bdan\b|\b&\b", re.IGNORECASE)

        self._compiled_intents = [
            (label, re.compile(pattern, re.IGNORECASE))
            for label, pattern in self._INTENT_PATTERNS
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_intent(self, text: str) -> str:
        """Returns intent label: RESET | ASK_MENU | CHECKOUT | ORDER."""
        lowered = text.lower().strip()
        for label, pattern in self._compiled_intents:
            if pattern.search(lowered):
                return label
        return "ORDER"

    def parse_orders(self, full_text: str) -> list[dict]:
        """
        Splits input on conjunctions/punctuation and extracts (item, qty, price, emoji)
        tuples. Returns empty list if nothing parseable.
        """
        segments = self._re_split.split(full_text)
        return [
            order
            for seg in segments
            if seg.strip()
            for order in [self._parse_segment(seg)]
            if order is not None
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_segment(self, text: str) -> dict | None:
        text = text.lower().strip()
        item_match = self._re_menu.search(text)
        if not item_match:
            return None

        item_key = item_match.group(1)
        qty_match = self._re_number.search(text)
        qty = max(1, int(qty_match.group(1))) if qty_match else 1

        return {
            "item":  item_key,
            "qty":   qty,
            "price": self.MENU_DATA[item_key]["price"],
            "emoji": self.MENU_DATA[item_key]["emoji"],
        }