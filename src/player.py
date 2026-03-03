class Player:
    """Håller bara spelarens position och symbol (ren ansvarsfördelning)."""

    def __init__(self, x: int, y: int, symbol: str = "@"):
        self.x = x
        self.y = y
        self.symbol = symbol

    def pos(self) -> tuple[int, int]:
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
