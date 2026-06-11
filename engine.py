import re


class LivestockEngine:
    """
    NLP parsing layer: detects intent and extracts order items from raw text.
    Stateless — pure input → output.

    Sprint 2 addition: fuzzy alias mapping untuk typo umum bahasa Indonesia.
    """

    MENU_DATA: dict = {
        "susu":   {"price": 12000, "emoji": "🥛", "desc": "Susu Sapi Segar (1 Liter)"},
        "telur":  {"price": 26000, "emoji": "🥚", "desc": "Telur Ayam Pilihan (1 Kg)"},
        "daging": {"price": 35000, "emoji": "🍗", "desc": "Daging Ayam Segar (1 Kg)"},
        "madu":   {"price": 50000, "emoji": "🍯", "desc": "Madu Murni Alami (250ml)"},
    }

    # Alias → canonical key  (typo, singkatan, sinonim umum)
    _ALIASES: dict[str, str] = {
        # susu
        "sus": "susu", "susu sapi": "susu", "susu segar": "susu",
        # telur
        "telor": "telur", "tlur": "telur", "telur ayam": "telur",
        # daging
        "dagng": "daging", "ayam": "daging", "daging ayam": "daging",
        "ayam segar": "daging", "chicken": "daging",
        # madu
        "mdo": "madu", "honey": "madu", "madu murni": "madu",
    }

    # Intent keyword patterns — ordered most-specific first
    _INTENT_PATTERNS: list[tuple[str, str]] = [
        ("RESET",    r"\b(reset|ulang|batal|kosongkan)\b"),
        ("ASK_MENU", r"\b(produk|daftar|stok|list|menu|katalog|apa saja)\b"),
        ("CHECKOUT", r"\b(selesai|bayar|checkout|cukup|ya|oke|fix|confirm|konfirmasi)\b"),
    ]

    # Cart mutation intents (Sprint 1)
    _REDUCE_PATTERN  = re.compile(r"\b(kurang|kurangi|hapus|hilangkan|remove)\b", re.I)
    _REMOVE_PATTERN  = re.compile(r"\b(hapus semua|hapus seluruh|remove all)\b", re.I)

    # Qty validation limits
    MIN_QTY = 1
    MAX_QTY = 99

    def __init__(self) -> None:
        self.menu_data = self.MENU_DATA  # public alias

        # Build combined pattern: canonical keys + all alias keys
        all_keys = list(self.MENU_DATA.keys()) + list(self._ALIASES.keys())
        # Sort descending by length so multi-word aliases match before single-word
        all_keys.sort(key=len, reverse=True)
        _pattern = "|".join(re.escape(k) for k in all_keys)

        self._re_number = re.compile(r"\b(\d+)\b")
        self._re_menu   = re.compile(rf"\b({_pattern})\b", re.IGNORECASE)
        self._re_split  = re.compile(r"[,.]|\bdan\b|\b&\b", re.IGNORECASE)

        self._compiled_intents = [
            (label, re.compile(pattern, re.IGNORECASE))
            for label, pattern in self._INTENT_PATTERNS
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_intent(self, text: str) -> str:
        """Returns: RESET | ASK_MENU | CHECKOUT | REDUCE | ORDER"""
        lowered = text.lower().strip()
        # Check reduce/remove before general intents
        if self._REDUCE_PATTERN.search(lowered):
            return "REDUCE"
        for label, pattern in self._compiled_intents:
            if pattern.search(lowered):
                return label
        return "ORDER"

    def parse_orders(self, full_text: str) -> list[dict]:
        """Split on conjunctions, extract (item, qty, price, emoji) per segment."""
        segments = self._re_split.split(full_text)
        return [
            order
            for seg in segments
            if seg.strip()
            for order in [self._parse_segment(seg)]
            if order is not None
        ]

    def resolve_alias(self, raw_key: str) -> str:
        """Return canonical menu key, resolving aliases. Returns raw_key if not found."""
        raw_lower = raw_key.lower().strip()
        return self._ALIASES.get(raw_lower, raw_lower)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_segment(self, text: str) -> dict | None:
        text = text.lower().strip()
        item_match = self._re_menu.search(text)
        if not item_match:
            return None

        raw_key  = item_match.group(1)
        item_key = self.resolve_alias(raw_key)

        if item_key not in self.MENU_DATA:
            return None

        qty_match = self._re_number.search(text)
        qty = int(qty_match.group(1)) if qty_match else 1
        qty = max(self.MIN_QTY, min(self.MAX_QTY, qty))  # clamp 1–99

        return {
            "item":  item_key,
            "qty":   qty,
            "price": self.MENU_DATA[item_key]["price"],
            "emoji": self.MENU_DATA[item_key]["emoji"],
        }