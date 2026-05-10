"""Break‑Even Engine — Move SL to entry+fees once in profit."""
import config


class BreakEven:
    def __init__(self):
        self.activation_atr = config.BE_ATR

    def apply(self, pos: dict, price: float, atr: float) -> dict:
        if pos.get("be_done"):
            return pos

        d = pos["dir"]
        threshold = pos["entry"] + d * self.activation_atr * atr

        if (d == 1 and price >= threshold) or \
           (d == -1 and price <= threshold):
            # SL to entry + fees
            pos["sl"] = pos["entry"] + d * 0.0008
            if not pos.get("trail_activated"):
                pos["trail_sl"] = pos["sl"]
            pos["be_done"] = True

        return pos
