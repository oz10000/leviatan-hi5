"""Asset Rotation — Selects top‑N candidates from the universe."""


class AssetRotation:
    def __init__(self, top_n: int = 5):
        self.top_n = top_n

    def select(self, scored: list) -> list:
        """
        scored: list of (symbol, score) sorted descending.
        Returns top_n candidates.
        """
        return scored[: self.top_n]
