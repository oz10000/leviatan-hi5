"""
Trailing Stop Engine – Mueve el stop loss dinámicamente.
"""
import config


class TrailingStop:
    def __init__(self):
        self.activation_atr = 0.8
        self.distance_atr = config.TRAIL_ATR

    def update(self, pos: dict, price: float, atr: float) -> dict:
        d = pos["dir"]
        entry = pos["entry"]

        # Activar trailing si el precio avanza lo suficiente
        if not pos.get("trail_activated"):
            threshold = entry + d * self.activation_atr * atr
            if (d == 1 and price >= threshold) or (d == -1 and price <= threshold):
                pos["trail_activated"] = True
                pos["trail_sl"] = price - d * self.distance_atr * atr

        # Actualizar el trailing stop ya activo
        if pos.get("trail_activated"):
            new_sl = price - d * self.distance_atr * atr
            if (d == 1 and new_sl > pos["trail_sl"]) or (d == -1 and new_sl < pos["trail_sl"]):
                pos["trail_sl"] = new_sl

        return pos
